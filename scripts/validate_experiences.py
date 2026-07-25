#!/usr/bin/env python3
"""Validate applied learning experiences.

This validator is intentionally independent from the legacy module validator.
It provides a strict release gate for the experience layer while the original
60 module files continue through their separate audit.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent

EXPERIENCE_FILES = {
    "system-dossiers/refrigerator.md": "system-dossier",
    "failure-atlas/feedback-instability.md": "failure-pattern",
    "investigations/room-cooling.md": "investigation",
    "design-challenges/passive-cooler.md": "design-challenge",
}

INDEX_FILES = (
    "experiences/README.md",
    "system-dossiers/README.md",
    "failure-atlas/README.md",
    "investigations/README.md",
    "design-challenges/README.md",
)

TEMPLATE_FILES = (
    "templates/system-dossier.md",
    "templates/failure-pattern.md",
    "templates/investigation.md",
    "templates/design-challenge.md",
)

REQUIRED_FIELDS = (
    "title",
    "slug",
    "domain",
    "experience_type",
    "status",
    "prerequisites",
    "connections",
    "last_reviewed",
    "content_license",
)

VALID_STATUSES = {"draft", "reviewed", "complete", "blocked"}
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.MULTILINE)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
URL_RE = re.compile(r"https?://[^\s)>]+")

REQUIRED_HEADINGS = {
    "system-dossier": (
        "observable system",
        "system boundary and environment",
        "inputs, outputs, stores, and flows",
        "scientific principles",
        "components and functions",
        "interaction architecture",
        "quantitative model",
        "control and feedback",
        "failure modes",
        "efficiency and performance",
        "lifecycle consequences",
        "alternative designs",
        "principle-to-system chain",
        "unresolved questions",
        "sources and module links",
    ),
    "failure-pattern": (
        "normal operation",
        "disturbance",
        "hidden condition",
        "amplifying mechanism",
        "minimum model",
        "detection delay",
        "threshold crossing and propagation",
        "protective barriers",
        "why barriers fail",
        "redesign options",
        "transfer across domains",
        "questions for investigation",
        "sources and module links",
    ),
    "investigation": (
        "question",
        "why the answer is not obvious",
        "competing models",
        "variables and units",
        "safe observation or simulation method",
        "data-recording structure",
        "uncertainty and confounders",
        "analysis method",
        "interpretation limits",
        "model revision",
        "transfer questions",
        "sources and module links",
    ),
    "design-challenge": (
        "need and context",
        "stakeholders",
        "requirements and success measures",
        "hard safety constraints",
        "assumptions",
        "system boundary",
        "concept alternatives",
        "minimum quantitative model",
        "trade-off matrix",
        "failure modes and safeguards",
        "safe test plan",
        "selected concept and rationale",
        "evidence that could change the decision",
        "sources and module links",
    ),
}

CANONICAL_MODULES = {
    "01-scientific-reasoning",
    "02-measurement-uncertainty",
    "03-mathematical-models",
    "04-probability-statistics",
    "05-computation-algorithms",
    "06-matter-quantum",
    "07-chemical-bonding",
    "08-energy-thermodynamics",
    "09-motion-forces",
    "10-electricity-magnetism",
    "11-waves-signals",
    "12-fluids-materials",
    "13-cells-bioenergetics",
    "14-dna-evolution",
    "15-ecosystems-complex-systems",
    "16-earth-planetary",
    "17-materials-manufacturing",
    "18-semiconductors-electronics",
    "19-software-ai",
    "20-sensors-control-infrastructure",
}

CANONICAL_CONCEPTS = {
    "concept-patterns",
    "concept-cause-and-effect",
    "concept-scale-proportion-quantity",
    "concept-systems-and-models",
    "concept-energy-and-matter",
    "concept-structure-and-function",
    "concept-stability-and-change",
}


@dataclass
class Document:
    path: Path
    frontmatter: dict[str, object]
    content: str


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warn(self, message: str) -> None:
        self.warnings.append(message)


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return []
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [strip_quotes(item.strip()) for item in inner.split(",") if item.strip()]


def read_document(path: Path, report: Report) -> Document | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error(f"Cannot read {path.relative_to(ROOT)}: {exc}")
        return None

    if not text.startswith("---\n"):
        report.error(f"{path.relative_to(ROOT)}: missing YAML frontmatter")
        return None

    end = text.find("\n---\n", 4)
    if end == -1:
        report.error(f"{path.relative_to(ROOT)}: unterminated YAML frontmatter")
        return None

    frontmatter: dict[str, object] = {}
    for line_number, raw in enumerate(text[4:end].splitlines(), start=2):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            report.error(
                f"{path.relative_to(ROOT)}:{line_number}: malformed frontmatter"
            )
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        frontmatter[key.strip()] = (
            parse_list(value) if value.startswith("[") else strip_quotes(value)
        )
    return Document(path, frontmatter, text[end + 5 :])


def headings(content: str) -> set[str]:
    return {
        re.sub(r"[`*_]", "", match.group(1)).strip().lower()
        for match in HEADING_RE.finditer(content)
    }


def check_required_inventory(report: Report) -> None:
    for relative in (*EXPERIENCE_FILES, *INDEX_FILES, *TEMPLATE_FILES):
        if not (ROOT / relative).is_file():
            report.error(f"Missing required experience file: {relative}")


def check_documents(report: Report) -> dict[str, Document]:
    documents: dict[str, Document] = {}
    slugs: dict[str, str] = {}

    for relative, expected_type in EXPERIENCE_FILES.items():
        document = read_document(ROOT / relative, report)
        if not document:
            continue
        documents[relative] = document
        fm = document.frontmatter

        for field in REQUIRED_FIELDS:
            if field not in fm or fm[field] in ("", None):
                report.error(f"{relative}: frontmatter missing '{field}'")

        if fm.get("domain") != "experience":
            report.error(f"{relative}: domain must be 'experience'")
        if fm.get("experience_type") != expected_type:
            report.error(f"{relative}: experience_type must be '{expected_type}'")
        if fm.get("status") not in VALID_STATUSES:
            report.error(f"{relative}: invalid status '{fm.get('status')}'")
        if fm.get("content_license") != "CC-BY-4.0":
            report.error(f"{relative}: content_license must be CC-BY-4.0")

        slug = fm.get("slug")
        if isinstance(slug, str):
            if not SLUG_RE.fullmatch(slug):
                report.error(f"{relative}: malformed slug '{slug}'")
            if slug in slugs:
                report.error(f"{relative}: duplicate slug '{slug}' in {slugs[slug]}")
            slugs[slug] = relative
        else:
            report.error(f"{relative}: slug must be a string")

        reviewed = fm.get("last_reviewed")
        if isinstance(reviewed, str):
            try:
                date.fromisoformat(reviewed)
            except ValueError:
                report.error(f"{relative}: last_reviewed must use YYYY-MM-DD")

        for list_field in ("prerequisites", "connections"):
            if not isinstance(fm.get(list_field), list):
                report.error(f"{relative}: {list_field} must be a YAML list")

        present = headings(document.content)
        for required_heading in REQUIRED_HEADINGS[expected_type]:
            if not any(required_heading in item for item in present):
                report.error(f"{relative}: missing required heading '{required_heading}'")

        if not re.search(r"\$\$.*?\$\$", document.content, re.DOTALL):
            report.error(f"{relative}: no displayed quantitative model found")

        sources_section = document.content.lower().split("sources and module links", 1)
        if len(sources_section) != 2 or len(URL_RE.findall(sources_section[1])) < 1:
            report.error(f"{relative}: sources section needs at least one direct URL")

        if expected_type in {"investigation", "design-challenge"}:
            safety_terms = ("safe", "do not", "no fire", "hazard")
            if not any(term in document.content.lower() for term in safety_terms):
                report.error(f"{relative}: safety constraints are not explicit")

    valid_ids = CANONICAL_MODULES | CANONICAL_CONCEPTS | set(slugs)
    for relative, document in documents.items():
        own_slug = document.frontmatter.get("slug")
        for field in ("prerequisites", "connections"):
            values = document.frontmatter.get(field, [])
            if not isinstance(values, list):
                continue
            for value in values:
                if value == own_slug:
                    report.error(f"{relative}: {field} contains self-reference '{value}'")
                elif value not in valid_ids:
                    report.error(f"{relative}: {field} contains unknown identifier '{value}'")

    return documents


def check_links(report: Report, documents: dict[str, Document]) -> None:
    for relative, document in documents.items():
        for label, raw_url in LINK_RE.findall(document.content):
            url = raw_url.strip()
            if url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_text = unquote(url.split("#", 1)[0].split("?", 1)[0])
            target = (document.path.parent / target_text).resolve()
            try:
                target.relative_to(ROOT.resolve())
            except ValueError:
                report.error(f"{relative}: link escapes repository [{label}]({raw_url})")
                continue
            if not target.exists():
                report.error(f"{relative}: broken link [{label}]({raw_url})")


def check_source_ledger(report: Report, documents: dict[str, Document]) -> None:
    path = ROOT / "sources" / "experience-source-ledger.md"
    if not path.exists():
        report.error("Missing sources/experience-source-ledger.md")
        return

    rows: list[list[str]] = []
    for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.startswith("|") or number <= 6 or "---" in line:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            report.error(f"sources/experience-source-ledger.md:{number}: expected 8 columns")
            continue
        rows.append(cells)

    covered: set[str] = set()
    for cells in rows:
        for experience in cells[5].split(";"):
            if experience.strip():
                covered.add(experience.strip())

    for relative, document in documents.items():
        slug = document.frontmatter.get("slug")
        if isinstance(slug, str) and slug not in covered:
            report.error(f"sources/experience-source-ledger.md: no source row for '{slug}'")


def check_index_and_templates(report: Report) -> None:
    for relative in INDEX_FILES:
        document = read_document(ROOT / relative, report)
        if not document:
            continue
        if document.frontmatter.get("domain") != "experience":
            report.error(f"{relative}: domain must be 'experience'")
        if document.frontmatter.get("experience_type") != "index":
            report.error(f"{relative}: experience_type must be 'index'")

    for relative in TEMPLATE_FILES:
        text = (ROOT / relative).read_text(encoding="utf-8")
        for field in REQUIRED_FIELDS:
            if f"{field}:" not in text:
                report.error(f"{relative}: template missing field '{field}'")


def run(strict: bool) -> int:
    report = Report()
    check_required_inventory(report)
    documents = check_documents(report)
    check_links(report, documents)
    check_source_ledger(report, documents)
    check_index_and_templates(report)

    print(f"Validating experience layer at: {ROOT}\n")
    if report.warnings:
        print(f"WARNING: {len(report.warnings)} warning(s)")
        for warning in report.warnings:
            print(f"  - {warning}")
        print()
    if report.errors:
        print(f"ERROR: {len(report.errors)} error(s)")
        for error in report.errors:
            print(f"  - {error}")
        print("\nEXPERIENCE VALIDATION FAILED")
        return 1
    if strict and report.warnings:
        print("STRICT EXPERIENCE VALIDATION FAILED")
        return 1
    print(f"Experience validation passed ({len(report.warnings)} warnings, 0 errors)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    raise SystemExit(run(strict=args.strict))


if __name__ == "__main__":
    main()
