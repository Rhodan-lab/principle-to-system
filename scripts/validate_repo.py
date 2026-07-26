#!/usr/bin/env python3
"""Validate the Principle to System repository.

The validator has two modes:

* default: structural errors fail; editorial warnings are reported
* --strict: warnings also fail (for release/readiness checks)

Only the Python standard library is required.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable
from urllib.parse import unquote

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_TOP_FILES = (
    "README.md",
    "INDEX.md",
    "PROJECT_STATE.md",
    "CONTENT_GUIDE.md",
    "SOURCE_POLICY.md",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "LICENSE",
    "LICENSE-CONTENT",
)

MODULES = {
    "01-scientific-reasoning": ("foundations", ()),
    "02-measurement-uncertainty": ("foundations", ("01-scientific-reasoning",)),
    "03-mathematical-models": ("foundations", ("01-scientific-reasoning",)),
    "04-probability-statistics": (
        "foundations",
        ("01-scientific-reasoning", "03-mathematical-models"),
    ),
    "05-computation-algorithms": (
        "foundations",
        ("03-mathematical-models", "04-probability-statistics"),
    ),
    "06-matter-quantum": (
        "science",
        (
            "01-scientific-reasoning",
            "02-measurement-uncertainty",
            "03-mathematical-models",
        ),
    ),
    "07-chemical-bonding": ("science", ("06-matter-quantum",)),
    "08-energy-thermodynamics": (
        "science",
        ("03-mathematical-models", "06-matter-quantum"),
    ),
    "09-motion-forces": ("science", ("03-mathematical-models",)),
    "10-electricity-magnetism": (
        "science",
        ("03-mathematical-models", "06-matter-quantum"),
    ),
    "11-waves-signals": (
        "science",
        ("03-mathematical-models", "09-motion-forces"),
    ),
    "12-fluids-materials": (
        "science",
        ("03-mathematical-models", "08-energy-thermodynamics", "09-motion-forces"),
    ),
    "13-cells-bioenergetics": (
        "science",
        ("07-chemical-bonding", "08-energy-thermodynamics"),
    ),
    "14-dna-evolution": (
        "science",
        ("07-chemical-bonding", "13-cells-bioenergetics"),
    ),
    "15-ecosystems-complex-systems": (
        "science",
        ("04-probability-statistics", "13-cells-bioenergetics", "14-dna-evolution"),
    ),
    "16-earth-planetary": (
        "science",
        (
            "08-energy-thermodynamics",
            "09-motion-forces",
            "12-fluids-materials",
            "15-ecosystems-complex-systems",
        ),
    ),
    "17-materials-manufacturing": (
        "technology",
        ("06-matter-quantum", "07-chemical-bonding", "12-fluids-materials"),
    ),
    "18-semiconductors-electronics": (
        "technology",
        ("06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing"),
    ),
    "19-software-ai": (
        "technology",
        ("04-probability-statistics", "05-computation-algorithms", "18-semiconductors-electronics"),
    ),
    "20-sensors-control-infrastructure": (
        "technology",
        (
            "10-electricity-magnetism",
            "11-waves-signals",
            "18-semiconductors-electronics",
            "19-software-ai",
        ),
    ),
}

MODULE_FILES = ("overview.md", "technology.md", "explore.md")
VALID_STATUSES = {"draft", "reviewed", "complete", "blocked"}
REQUIRED_FRONTMATTER_FIELDS = (
    "title",
    "slug",
    "module",
    "domain",
    "status",
    "prerequisites",
    "connections",
    "last_reviewed",
    "content_license",
)
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.MULTILINE)
MD_LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
INDEX_ROW_RE = re.compile(
    r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$",
    re.I,
)

REQUIRED_SECTIONS = {
    "overview.md": (
        "central questions",
        "observable phenomena",
        "essential concepts",
        "mechanisms and causal chains",
        "important quantities",
        "mathematical models and equations",
        "definitions of symbols and units",
        "assumptions and approximations",
        "spatial and temporal scales",
        "common misconceptions",
        "connections to other modules",
        "sources",
    ),
    "technology.md": (
        "scientific principles used",
        "the engineering problem",
        "main components",
        "how the components interact",
        "matter, energy, force, or information flow",
        "system architecture",
        "design constraints",
        "performance and efficiency",
        "reliability and failure modes",
        "safety principles",
        "environmental and lifecycle considerations",
        "connections to other technologies",
        "sources",
    ),
    "explore.md": (
        "observation prompts",
        "prediction questions",
        "worked reasoning examples",
        "thought experiments",
        "household and browser-based explorations",
        "model-building prompts",
        "self-explanation questions",
        "transfer questions",
        "suggested learning paths",
        "reasoning notes",
    ),
}

SKIP_FRONTMATTER_FILES = {
    "README.md",
    "INDEX.md",
    "PROJECT_STATE.md",
    "CONTENT_GUIDE.md",
    "SOURCE_POLICY.md",
    "CONTRIBUTING.md",
    "AUDIT.md",
    "source-ledger.md",
    "experience-source-ledger.md",
}


@dataclass(frozen=True)
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


def module_dir(module_id: str) -> Path:
    domain, _ = MODULES[module_id]
    return REPO_ROOT / domain / module_id


def strip_quotes(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    return value


def parse_list(value: str) -> list[str]:
    value = value.strip()
    if not (value.startswith("[") and value.endswith("]")):
        return [] if not value else [strip_quotes(value)]
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [strip_quotes(part.strip()) for part in inner.split(",") if part.strip()]


def read_document(path: Path, report: Report) -> Document | None:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.error(f"Cannot read {path.relative_to(REPO_ROOT)}: {exc}")
        return None

    if not text.startswith("---\n"):
        report.warn(f"{path.relative_to(REPO_ROOT)}: no YAML frontmatter")
        return Document(path, {}, text)

    closing = text.find("\n---\n", 4)
    if closing == -1:
        report.error(f"{path.relative_to(REPO_ROOT)}: unterminated YAML frontmatter")
        return Document(path, {}, text)

    raw = text[4:closing]
    content = text[closing + 5 :]
    frontmatter: dict[str, object] = {}
    for line_no, raw_line in enumerate(raw.splitlines(), start=2):
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if ":" not in line:
            report.error(
                f"{path.relative_to(REPO_ROOT)}:{line_no}: malformed frontmatter line"
            )
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        frontmatter[key] = parse_list(value) if value.startswith("[") else strip_quotes(value)
    return Document(path, frontmatter, content)


def iter_module_documents(report: Report) -> Iterable[tuple[str, str, Document]]:
    for module_id in MODULES:
        for filename in MODULE_FILES:
            path = module_dir(module_id) / filename
            if not path.exists():
                report.error(f"Missing module file: {path.relative_to(REPO_ROOT)}")
                continue
            document = read_document(path, report)
            if document is not None:
                yield module_id, filename, document


def check_required_files(report: Report) -> None:
    for filename in REQUIRED_TOP_FILES:
        if not (REPO_ROOT / filename).is_file():
            report.error(f"Missing required file: {filename}")


def check_frontmatter(
    report: Report, documents: list[tuple[str, str, Document]]
) -> None:
    slug_owners: dict[str, Path] = {}
    all_slugs = {
        slug
        for _, _, document in documents
        if isinstance((slug := document.frontmatter.get("slug")), str) and slug
    }
    valid_references = set(MODULES) | all_slugs

    for module_id, filename, document in documents:
        rel = document.path.relative_to(REPO_ROOT)
        fm = document.frontmatter
        for field in REQUIRED_FRONTMATTER_FIELDS:
            if field not in fm or fm[field] in ("", None):
                report.error(f"{rel}: frontmatter missing '{field}'")

        slug = fm.get("slug")
        if isinstance(slug, str) and slug:
            if not SLUG_RE.fullmatch(slug):
                report.error(f"{rel}: malformed slug '{slug}'")
            if slug in slug_owners:
                report.error(
                    f"{rel}: duplicate slug '{slug}' (also in {slug_owners[slug]})"
                )
            else:
                slug_owners[slug] = rel

        status = fm.get("status")
        if status not in VALID_STATUSES:
            report.error(f"{rel}: invalid status '{status}'")

        reviewed = fm.get("last_reviewed")
        if isinstance(reviewed, str):
            try:
                date.fromisoformat(reviewed)
            except ValueError:
                report.error(f"{rel}: last_reviewed must use YYYY-MM-DD")

        if fm.get("content_license") != "CC-BY-4.0":
            report.error(f"{rel}: content_license must be CC-BY-4.0")

        expected_domain = MODULES[module_id][0]
        actual_domain = fm.get("domain")
        if actual_domain != expected_domain:
            report.warn(
                f"{rel}: domain is '{actual_domain}', expected subject domain '{expected_domain}'"
            )

        expected_number = module_id[:2]
        module_field = fm.get("module")
        if not isinstance(module_field, str) or f"Module {expected_number}" not in module_field:
            report.error(f"{rel}: module field must identify Module {expected_number}")

        prerequisites = fm.get("prerequisites")
        if not isinstance(prerequisites, list):
            report.error(f"{rel}: prerequisites must be a YAML list")
            prerequisites = []
        connections = fm.get("connections")
        if not isinstance(connections, list):
            report.error(f"{rel}: connections must be a YAML list")
            connections = []

        canonical = set(MODULES[module_id][1])
        actual = set(prerequisites)
        if filename == "overview.md" and actual != canonical:
            report.warn(
                f"{rel}: prerequisites {sorted(actual)} do not match INDEX {sorted(canonical)}"
            )

        for field_name, references in (
            ("prerequisites", prerequisites),
            ("connections", connections),
        ):
            for reference in references:
                if reference == module_id or reference == slug:
                    report.warn(
                        f"{rel}: {field_name} contains a self-reference '{reference}'"
                    )
                elif reference not in valid_references:
                    report.warn(
                        f"{rel}: {field_name} contains unknown identifier '{reference}'"
                    )


def normalized_headings(content: str) -> set[str]:
    return {
        re.sub(r"[`*_]", "", match.group(1)).strip().lower()
        for match in HEADING_RE.finditer(content)
    }


def check_sections(
    report: Report, documents: list[tuple[str, str, Document]]
) -> None:
    for _, filename, document in documents:
        headings = normalized_headings(document.content)
        rel = document.path.relative_to(REPO_ROOT)
        for required in REQUIRED_SECTIONS[filename]:
            if not any(required in heading for heading in headings):
                report.warn(f"{rel}: missing expected section heading '{required}'")
        if (
            filename == "technology.md"
            and "->" not in document.content
            and "→" not in document.content
            and "principle-to-system chain" not in document.content.lower()
        ):
            report.warn(f"{rel}: no explicit principle-to-system chain found")


def check_internal_links(report: Report) -> None:
    for path in REPO_ROOT.rglob("*.md"):
        try:
            content = path.read_text(encoding="utf-8")
        except OSError as exc:
            report.error(f"Cannot read {path.relative_to(REPO_ROOT)}: {exc}")
            continue
        for text, raw_url in MD_LINK_RE.findall(content):
            url = raw_url.strip()
            if not url or url.startswith(("http://", "https://", "mailto:", "#")):
                continue
            target_text = unquote(url.split("#", 1)[0].split("?", 1)[0])
            target = (path.parent / target_text).resolve()
            try:
                target.relative_to(REPO_ROOT.resolve())
            except ValueError:
                report.warn(
                    f"{path.relative_to(REPO_ROOT)}: link escapes repository [{text}]({raw_url})"
                )
                continue
            if not target.exists():
                report.warn(
                    f"{path.relative_to(REPO_ROOT)}: broken link [{text}]({raw_url})"
                )


def parse_index_statuses(report: Report) -> dict[str, str]:
    path = REPO_ROOT / "INDEX.md"
    if not path.exists():
        return {}
    statuses: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = INDEX_ROW_RE.match(line)
        if not match:
            continue
        number, status = match.groups()
        module_id = next(
            (item for item in MODULES if item.startswith(number + "-")), None
        )
        if module_id:
            statuses[module_id] = status.lower()
    if len(statuses) != len(MODULES):
        report.warn(
            f"INDEX.md: found statuses for {len(statuses)} of {len(MODULES)} modules"
        )
    return statuses


def aggregate_status(statuses: list[str]) -> str:
    if "blocked" in statuses:
        return "blocked"
    if statuses and all(status == "complete" for status in statuses):
        return "complete"
    if statuses and all(status in {"reviewed", "complete"} for status in statuses):
        return "reviewed"
    return "draft"


def check_index_statuses(
    report: Report, documents: list[tuple[str, str, Document]]
) -> None:
    index_statuses = parse_index_statuses(report)
    by_module: dict[str, list[str]] = {module_id: [] for module_id in MODULES}
    for module_id, _, document in documents:
        status = document.frontmatter.get("status")
        if isinstance(status, str):
            by_module[module_id].append(status)
    for module_id, statuses in by_module.items():
        expected = aggregate_status(statuses)
        actual = index_statuses.get(module_id)
        if actual is not None and actual != expected:
            report.warn(
                f"INDEX.md: {module_id} is '{actual}' but learner files aggregate to '{expected}'"
            )


def check_source_ledger(report: Report) -> None:
    path = REPO_ROOT / "sources" / "source-ledger.md"
    if not path.exists():
        report.error("Missing sources/source-ledger.md")
        return

    lines = path.read_text(encoding="utf-8").splitlines()
    data_rows: list[tuple[int, list[str]]] = []
    weak_sources = 0
    for line_no, line in enumerate(lines, start=1):
        if not line.startswith("|") or line_no <= 8:
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            report.error(
                f"sources/source-ledger.md:{line_no}: expected 8 columns, "
                f"found {len(cells)}; use one source per row"
            )
            continue
        data_rows.append((line_no, cells))
        source_type = cells[4].lower()
        url = cells[3].lower()
        if "wikipedia" in url or "encyclopedia" in source_type:
            weak_sources += 1
        if not cells[5]:
            report.warn(
                f"sources/source-ledger.md:{line_no}: missing module identifier"
            )

    if len(data_rows) < 80:
        report.warn(f"Source ledger has only {len(data_rows)} valid rows")
    if weak_sources:
        report.warn(
            f"Source ledger contains {weak_sources} encyclopedia/Wikipedia rows; "
            "replace them with higher-tier sources before marking modules complete"
        )


def check_all_markdown_frontmatter(report: Report) -> None:
    for path in REPO_ROOT.rglob("*.md"):
        rel = path.relative_to(REPO_ROOT)
        if path.name in SKIP_FRONTMATTER_FILES or rel.parts[0] in {
            ".github",
            "scripts",
            "reports",
        }:
            continue
        if (
            len(rel.parts) >= 2
            and rel.parts[0] in {"foundations", "science", "technology"}
        ):
            continue
        document = read_document(path, report)
        if document and not document.frontmatter:
            report.warn(f"{rel}: non-module learning file has no frontmatter")


def run(strict: bool) -> int:
    report = Report()
    check_required_files(report)
    documents = list(iter_module_documents(report))
    check_frontmatter(report, documents)
    check_sections(report, documents)
    check_internal_links(report)
    check_index_statuses(report, documents)
    check_source_ledger(report)
    check_all_markdown_frontmatter(report)

    print(f"Validating repository at: {REPO_ROOT}\n")
    if report.warnings:
        print(f"WARNING: {len(report.warnings)} warning(s)")
        for warning in report.warnings:
            print(f"  - {warning}")
        print()
    if report.errors:
        print(f"ERROR: {len(report.errors)} error(s)")
        for error in report.errors:
            print(f"  - {error}")
        print("\nVALIDATION FAILED")
        return 1
    if strict and report.warnings:
        print("STRICT VALIDATION FAILED")
        return 1
    print(f"Validation passed ({len(report.warnings)} warnings, 0 errors)")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="fail when editorial warnings are present",
    )
    args = parser.parse_args()
    raise SystemExit(run(strict=args.strict))


if __name__ == "__main__":
    main()
