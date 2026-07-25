#!/usr/bin/env python3
"""Validate the focused scientific review of Foundations Modules 01–05.

The gate checks that the reviewed Foundations files satisfy their content
contract, use direct source links recorded in the central ledger, avoid known
superseded claims and unsafe activities, and agree with INDEX.md and the Phase 6
review record. Downstream phases may explicitly allow Modules 06–12 to be
Reviewed while preserving the Phase 6 checks for Modules 01–05.
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = "2026-07-25"
FILENAMES = ("overview.md", "technology.md", "explore.md")
MODULES = {
    "01-scientific-reasoning": ("Scientific Reasoning", ()),
    "02-measurement-uncertainty": ("Measurement and Uncertainty", ("01-scientific-reasoning",)),
    "03-mathematical-models": ("Mathematical Models", ("01-scientific-reasoning",)),
    "04-probability-statistics": (
        "Probability and Statistics",
        ("01-scientific-reasoning", "03-mathematical-models"),
    ),
    "05-computation-algorithms": (
        "Computation and Algorithms",
        ("03-mathematical-models", "04-probability-statistics"),
    ),
}

REQUIRED_HEADINGS = {
    "overview.md": (
        "central questions", "observable phenomena", "essential concepts",
        "mechanisms and causal chains", "important quantities",
        "mathematical models and equations", "definitions of symbols and units",
        "assumptions and approximations", "spatial and temporal scales",
        "common misconceptions", "connections to other modules", "sources",
    ),
    "technology.md": (
        "scientific principles used", "the engineering problem", "main components",
        "how the components interact", "matter, energy, force, or information flow",
        "system architecture", "design constraints", "performance and efficiency",
        "reliability and failure modes", "safety principles",
        "environmental and lifecycle considerations", "connections to other technologies",
        "sources",
    ),
    "explore.md": (
        "observation prompts", "prediction questions", "worked reasoning examples",
        "thought experiments", "household and browser-based explorations",
        "model-building prompts", "self-explanation questions", "transfer questions",
        "suggested learning paths", "reasoning notes",
    ),
}

STALE_IDENTIFIERS = (
    "03-kinematics-dynamics", "04-thermodynamics", "04-classical-mechanics",
    "05-thermodynamics", "05-information-theory", "06-systems-thinking",
    "06-systems-control",
)

PROHIBITED_TEXT = {
    "without ethical constraints": "unsafe ethics framing",
    "suicides by hanging": "self-harm-related learning example",
    "while driving at a steady speed": "unsafe observation instruction",
    "weapons systems": "age-inappropriate high-stakes example",
    "A low p-value (typically < 0.05) suggests": "superseded p-value decision rule",
    "likely to contain the true population parameter": "superseded confidence-interval wording",
    "A measure of the average kinetic energy of particles": "superseded temperature definition",
    "The position of an electron is not deterministic but described by a probability density function (wavefunction)": "wavefunction/probability-density conflation",
    "Many causal discovery algorithms are NP-hard in the worst case": "unsupported blanket complexity claim",
    "the minimum energy required to flip a bit": "incorrect Landauer formulation",
    "A modern supercomputer can consume tens of megawatts": "unstable unsourced current-performance claim",
}

URL_RE = re.compile(r"https?://[^\s)\]>]+")
HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.MULTILINE)
INDEX_RE = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$", re.I)


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]

    @classmethod
    def empty(cls) -> "Result":
        return cls([], [])


def normalize_url(raw: str) -> str:
    raw = raw.rstrip(".,;:")
    parts = urlsplit(raw)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


def parse_frontmatter(text: str, path: Path, result: Result) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        result.errors.append(f"{path}: missing frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        result.errors.append(f"{path}: unterminated frontmatter")
        return {}, text
    raw = text[4:end]
    body = text[end + 5 :]
    data: dict[str, object] = {}
    for line_no, line in enumerate(raw.splitlines(), start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            result.errors.append(f"{path}:{line_no}: malformed frontmatter line")
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key] = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
        else:
            data[key] = value.strip("\"'")
    return data, body


def normalized_headings(body: str) -> set[str]:
    return {re.sub(r"[`*_]", "", match.group(1)).strip().lower() for match in HEADING_RE.finditer(body)}


def ledger_locators(result: Result) -> set[str]:
    path = ROOT / "sources" / "source-ledger.md"
    if not path.exists():
        result.errors.append("sources/source-ledger.md: missing")
        return set()
    locators: set[str] = set()
    table_started = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.startswith("| Title |"):
            table_started = True
            continue
        if not table_started or not line.startswith("|") or re.match(r"^\|\s*-", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            result.errors.append(f"sources/source-ledger.md:{line_no}: expected 8 columns")
            continue
        locator = cells[3]
        if locator.startswith(("https://", "http://")):
            locators.add(normalize_url(locator))
    return locators


def expected_slug(module_id: str, filename: str) -> str:
    if filename == "overview.md":
        return module_id
    return f"{module_id}-{filename.removesuffix('.md')}"


def check_documents(result: Result, ledger_urls: set[str]) -> None:
    seen_slugs: set[str] = set()
    all_foundation_text: list[tuple[Path, str]] = []
    for module_id, (_, prerequisites) in MODULES.items():
        module_path = ROOT / "foundations" / module_id
        for filename in FILENAMES:
            path = module_path / filename
            rel = path.relative_to(ROOT)
            if not path.exists():
                result.errors.append(f"{rel}: missing")
                continue
            text = path.read_text(encoding="utf-8")
            all_foundation_text.append((rel, text))
            fm, body = parse_frontmatter(text, rel, result)
            expected = {
                "slug": expected_slug(module_id, filename),
                "module": f"Module {module_id[:2]}",
                "domain": "foundations",
                "status": "reviewed",
                "last_reviewed": REVIEW_DATE,
                "content_license": "CC-BY-4.0",
            }
            for key, value in expected.items():
                if fm.get(key) != value:
                    result.errors.append(f"{rel}: {key}={fm.get(key)!r}, expected {value!r}")
            actual_prerequisites = fm.get("prerequisites")
            if actual_prerequisites != list(prerequisites):
                result.errors.append(f"{rel}: prerequisites={actual_prerequisites!r}, expected {list(prerequisites)!r}")
            connections = fm.get("connections")
            if not isinstance(connections, list) or not connections:
                result.errors.append(f"{rel}: connections must be a non-empty list")
            slug = str(fm.get("slug", ""))
            if slug in seen_slugs:
                result.errors.append(f"{rel}: duplicate slug {slug}")
            seen_slugs.add(slug)
            headings = normalized_headings(body)
            for required in REQUIRED_HEADINGS[filename]:
                if not any(required in heading for heading in headings):
                    result.errors.append(f"{rel}: missing heading containing '{required}'")
            if filename in {"overview.md", "technology.md"}:
                source_start = re.search(r"^##\s+(?:\d+\.\s*)?Sources\s*$", body, re.I | re.M)
                if not source_start:
                    result.errors.append(f"{rel}: direct source section missing")
                else:
                    source_body = body[source_start.end() :]
                    direct_urls = {normalize_url(url) for url in URL_RE.findall(source_body)}
                    if len(direct_urls) < 4:
                        result.errors.append(f"{rel}: only {len(direct_urls)} direct source URLs; minimum is 4")
                    for url in sorted(direct_urls - ledger_urls):
                        result.errors.append(f"{rel}: source URL absent from central ledger: {url}")
            if filename == "technology.md" and "→" not in body and "->" not in body:
                result.errors.append(f"{rel}: no explicit principle-to-system or information-flow chain")
            if filename == "explore.md" and len(body.split()) < 500:
                result.warnings.append(f"{rel}: exploration is unusually short")
    for rel, text in all_foundation_text:
        lower = text.lower()
        for identifier in STALE_IDENTIFIERS:
            if identifier.lower() in lower:
                result.errors.append(f"{rel}: stale identifier '{identifier}'")
        for phrase, reason in PROHIBITED_TEXT.items():
            if phrase.lower() in lower:
                result.errors.append(f"{rel}: {reason}: '{phrase}'")


def check_index(result: Result, allow_downstream_reviewed: bool) -> None:
    path = ROOT / "INDEX.md"
    if not path.exists():
        result.errors.append("INDEX.md: missing")
        return
    statuses: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in ("01", "02", "03", "04", "05"):
        if statuses.get(number) != "reviewed":
            result.errors.append(f"INDEX.md: Module {number} must be Reviewed")
    for value in range(6, 21):
        number = f"{value:02d}"
        expected = "reviewed" if allow_downstream_reviewed and value <= 12 else "draft"
        if statuses.get(number) != expected:
            result.errors.append(f"INDEX.md: Module {number} must be {expected.title()}")


def check_review_artifacts(result: Result) -> None:
    review_path = ROOT / "reports" / "phase-6-foundations-review.md"
    if not review_path.exists():
        result.errors.append("reports/phase-6-foundations-review.md: missing")
    else:
        text = review_path.read_text(encoding="utf-8")
        for number in ("01", "02", "03", "04", "05"):
            if f"Module {number}" not in text:
                result.errors.append(f"phase-6 review record: Module {number} section missing")
        if "Draft → Reviewed" not in text:
            result.errors.append("phase-6 review record: status transition missing")
    source_report = ROOT / "reports" / "phase-6-foundations-sources.json"
    if not source_report.exists():
        result.errors.append("reports/phase-6-foundations-sources.json: missing")
    registry = ROOT / "sources" / "foundations-review-sources.json"
    applicator = ROOT / "scripts" / "apply_foundations_review_sources.py"
    for path in (registry, applicator):
        if not path.exists():
            result.errors.append(f"{path.relative_to(ROOT)}: missing")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--allow-downstream-reviewed",
        action="store_true",
        help="Require Modules 06–12 Reviewed and Modules 13–20 Draft.",
    )
    args = parser.parse_args()
    result = Result.empty()
    urls = ledger_locators(result)
    check_documents(result, urls)
    check_index(result, args.allow_downstream_reviewed)
    check_review_artifacts(result)
    if result.warnings:
        print("Phase 6 review warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 6 foundations review errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 6 foundations review passed: 5 modules, 15 reviewed files, "
        f"{len(urls)} central source locators."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
