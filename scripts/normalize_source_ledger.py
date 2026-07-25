#!/usr/bin/env python3
"""Normalize and audit the legacy Principle to System source ledger.

The historical ledger contains multiple logical records concatenated onto single
Markdown table lines. This utility recovers those records deterministically,
normalizes module identifiers, removes exact duplicates, and reports source
quality without fabricating missing bibliographic information.

Modes:
  --write   rewrite the ledger and write the audit report
  --check   fail when the ledger is not in normalized form
  --strict  additionally require baseline source coverage for every module
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "sources" / "source-ledger.md"
REPORT_PATH = REPO_ROOT / "reports" / "phase-5-source-audit.json"

MODULE_IDS = (
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
)
MODULE_BY_NUMBER = {module[:2]: module for module in MODULE_IDS}
MODULE_RE = re.compile(r"\b(?:0[1-9]|1[0-9]|20)-[a-z0-9-]+\b")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
URL_RE = re.compile(r"^(?:https?://|doi:|10\.\d{4,9}/)", re.I)

HEADER = (
    "| Title | Author / Institution | Date | URL or DOI | Type | Modules | Accessed | Relevance |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
)
INTRO = """# Source Ledger

Central record of every source used in the repository, per [`SOURCE_POLICY.md`](../SOURCE_POLICY.md).

This ledger is machine-readable: every source occupies exactly one eight-column Markdown row. A row's presence records provenance; it does not by itself certify that every claim using the source has completed scientific review.

"""

OFFICIAL_OR_HIGH_TIER_HOSTS = {
    "bipm.org",
    "www.bipm.org",
    "nist.gov",
    "www.nist.gov",
    "nasa.gov",
    "www.nasa.gov",
    "science.nasa.gov",
    "noaa.gov",
    "www.noaa.gov",
    "usgs.gov",
    "www.usgs.gov",
    "nih.gov",
    "www.nih.gov",
    "ncbi.nlm.nih.gov",
    "cern.ch",
    "home.cern",
    "esa.int",
    "www.esa.int",
    "ipcc.ch",
    "www.ipcc.ch",
    "nationalacademies.org",
    "www.nationalacademies.org",
    "nap.nationalacademies.org",
    "iupac.org",
    "www.iupac.org",
    "goldbook.iupac.org",
    "openstax.org",
    "www.openstax.org",
    "ocw.mit.edu",
    "mitpress.mit.edu",
    "ieee.org",
    "www.ieee.org",
    "standards.ieee.org",
    "python.org",
    "www.python.org",
    "docs.python.org",
}
WEAK_HOST_MARKERS = (
    "wikipedia.org",
    "khanacademy.org",
    "britannica.com",
    "thoughtco.com",
    "medium.com",
)
STRONG_TYPE_MARKERS = (
    "primary",
    "journal",
    "review",
    "standard",
    "government",
    "consensus",
    "technical report",
    "course material",
    "open textbook",
    "textbook",
)


@dataclass(frozen=True)
class Row:
    title: str
    author: str
    published: str
    locator: str
    source_type: str
    modules: str
    accessed: str
    relevance: str

    def cells(self) -> tuple[str, ...]:
        return (
            self.title,
            self.author,
            self.published,
            self.locator,
            self.source_type,
            self.modules,
            self.accessed,
            self.relevance,
        )


def clean_cell(value: str) -> str:
    value = value.replace("\n", " ").replace("\r", " ")
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("|", "\\|")


def unescape_cell(value: str) -> str:
    return value.replace("\\|", "|").strip()


def parse_data_cells(text: str) -> tuple[list[str], list[str]]:
    lines = text.splitlines()
    separator_index = None
    for index, line in enumerate(lines):
        lowered = line.lower()
        if line.startswith("|") and "title" in lowered and "relevance" in lowered:
            if index + 1 < len(lines):
                separator_index = index + 1
                break
    if separator_index is None:
        return [], ["Could not find the source-ledger table header."]

    cells: list[str] = []
    errors: list[str] = []
    for line_no, line in enumerate(lines[separator_index + 1 :], start=separator_index + 2):
        if not line.strip():
            continue
        if not line.lstrip().startswith("|"):
            errors.append(f"Line {line_no} is outside the Markdown table and was ignored.")
            continue
        parts = line.strip().strip("|").split("|")
        cells.extend(unescape_cell(part) for part in parts)

    if len(cells) % 8:
        errors.append(
            f"Recovered {len(cells)} table cells, which is not divisible by eight; "
            "the trailing incomplete record cannot be normalized safely."
        )
    return cells, errors


def normalize_modules(raw: str, relevance: str) -> tuple[str, str, list[str]]:
    notes: list[str] = []
    found: list[str] = []

    for match in MODULE_RE.findall(raw):
        if match in MODULE_IDS and match not in found:
            found.append(match)

    for number in re.findall(r"(?<!\d)(?:0[1-9]|1[0-9]|20)(?!\d)", raw):
        module = MODULE_BY_NUMBER[number]
        if module not in found:
            found.append(module)

    # Some malformed historical rows appended the module slug to relevance.
    trailing = MODULE_RE.search(relevance)
    if trailing and trailing.group(0) in MODULE_IDS:
        module = trailing.group(0)
        if module not in found:
            found.append(module)
        relevance = re.sub(
            rf"\s*{re.escape(module)}\s*$", "", relevance
        ).strip()
        notes.append(f"Recovered trailing module identifier {module} from relevance.")

    if not found and raw.strip():
        notes.append(f"Unrecognized module field preserved for audit: {raw.strip()}")
        return raw.strip(), relevance, notes

    return ", ".join(sorted(found)), relevance, notes


def canonical_locator(locator: str) -> str:
    locator = locator.strip().rstrip(".,;")
    if locator.lower().startswith("doi:"):
        locator = "https://doi.org/" + locator[4:].strip()
    elif re.match(r"^10\.\d{4,9}/", locator, re.I):
        locator = "https://doi.org/" + locator
    return locator


def dedupe_key(row: Row) -> tuple[str, str]:
    locator = row.locator.lower().rstrip("/")
    title = re.sub(r"\W+", " ", row.title.lower()).strip()
    return locator, title


def source_tier(row: Row) -> tuple[int, str]:
    locator = row.locator.lower()
    source_type = row.source_type.lower()
    host = urlparse(locator).hostname or ""

    if any(marker in host for marker in WEAK_HOST_MARKERS) or "encyclopedia" in source_type:
        return 4, "general-reference or encyclopedia source"
    if "doi.org/" in locator or any(marker in source_type for marker in ("primary", "journal", "review")):
        return 1, "primary literature or review"
    if host in OFFICIAL_OR_HIGH_TIER_HOSTS or any(marker in source_type for marker in STRONG_TYPE_MARKERS):
        return 2, "standard, agency, institution, university, or textbook"
    if locator.startswith("https://") and row.author and row.title:
        return 3, "other traceable publication"
    return 4, "weak or incomplete source record"


def module_list(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip() in MODULE_IDS]


def normalize_rows(text: str) -> tuple[list[Row], dict[str, object]]:
    cells, parse_errors = parse_data_cells(text)
    rows: list[Row] = []
    notes: list[str] = []
    duplicates: list[dict[str, str]] = []
    invalid_dates: list[dict[str, str]] = []
    invalid_locators: list[dict[str, str]] = []
    unmapped_modules: list[dict[str, str]] = []
    seen: dict[tuple[str, str], Row] = {}

    usable = len(cells) - (len(cells) % 8)
    for offset in range(0, usable, 8):
        raw = [clean_cell(cell) for cell in cells[offset : offset + 8]]
        modules, relevance, module_notes = normalize_modules(raw[5], raw[7])
        notes.extend(module_notes)
        locator = canonical_locator(raw[3])
        row = Row(
            title=raw[0],
            author=raw[1],
            published=raw[2],
            locator=locator,
            source_type=raw[4],
            modules=modules,
            accessed=raw[6],
            relevance=clean_cell(relevance),
        )

        key = dedupe_key(row)
        if key in seen:
            duplicates.append({"title": row.title, "locator": row.locator})
            continue
        seen[key] = row
        rows.append(row)

        if row.accessed and (not DATE_RE.fullmatch(row.accessed) or not valid_iso_date(row.accessed)):
            invalid_dates.append({"title": row.title, "accessed": row.accessed})
        if row.locator and not URL_RE.match(row.locator):
            invalid_locators.append({"title": row.title, "locator": row.locator})
        if row.modules and not module_list(row.modules):
            unmapped_modules.append({"title": row.title, "modules": row.modules})

    rows.sort(key=lambda item: (module_sort_key(item.modules), item.title.lower(), item.locator.lower()))

    tier_counts: Counter[int] = Counter()
    module_total: Counter[str] = Counter()
    module_strong: Counter[str] = Counter()
    weak_rows: list[dict[str, object]] = []
    for row in rows:
        tier, reason = source_tier(row)
        tier_counts[tier] += 1
        modules = module_list(row.modules)
        for module in modules:
            module_total[module] += 1
            if tier <= 2:
                module_strong[module] += 1
        if tier >= 4:
            weak_rows.append(
                {
                    "title": row.title,
                    "locator": row.locator,
                    "modules": modules,
                    "reason": reason,
                }
            )

    report: dict[str, object] = {
        "generated": date.today().isoformat(),
        "input_cells": len(cells),
        "logical_rows_recovered": usable // 8,
        "normalized_rows": len(rows),
        "duplicates_removed": duplicates,
        "parse_errors": parse_errors,
        "normalization_notes": notes,
        "invalid_access_dates": invalid_dates,
        "invalid_locators": invalid_locators,
        "unmapped_module_fields": unmapped_modules,
        "tier_counts": {str(key): value for key, value in sorted(tier_counts.items())},
        "module_coverage": {
            module: {
                "total_sources": module_total[module],
                "policy_tier_1_or_2": module_strong[module],
                "target_total": 4,
                "minimum_strong": 2,
            }
            for module in MODULE_IDS
        },
        "weak_rows": weak_rows,
    }
    return rows, report


def module_sort_key(raw: str) -> tuple[int, str]:
    modules = module_list(raw)
    if not modules:
        return 999, raw.lower()
    return int(modules[0][:2]), raw.lower()


def valid_iso_date(value: str) -> bool:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return False


def render(rows: list[Row]) -> str:
    lines = [INTRO.rstrip(), "", HEADER.rstrip()]
    for row in rows:
        lines.append("| " + " | ".join(row.cells()) + " |")
    return "\n".join(lines).rstrip() + "\n"


def structural_errors(report: dict[str, object]) -> list[str]:
    errors: list[str] = []
    for key in ("parse_errors", "invalid_access_dates", "invalid_locators", "unmapped_module_fields"):
        values = report.get(key, [])
        if values:
            errors.append(f"{key}: {len(values)}")
    if report.get("normalized_rows", 0) == 0:
        errors.append("No source rows were recovered.")
    return errors


def strict_errors(report: dict[str, object]) -> list[str]:
    errors = structural_errors(report)
    coverage = report.get("module_coverage", {})
    assert isinstance(coverage, dict)
    for module in MODULE_IDS:
        item = coverage.get(module, {})
        if not isinstance(item, dict):
            errors.append(f"{module}: missing coverage record")
            continue
        total = int(item.get("total_sources", 0))
        strong = int(item.get("policy_tier_1_or_2", 0))
        if total < 4:
            errors.append(f"{module}: only {total} total sources; target is at least 4")
        if strong < 2:
            errors.append(f"{module}: only {strong} policy-tier sources; minimum is 2")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    if not LEDGER_PATH.exists():
        print(f"ERROR: missing {LEDGER_PATH.relative_to(REPO_ROOT)}", file=sys.stderr)
        return 1

    original = LEDGER_PATH.read_text(encoding="utf-8")
    rows, report = normalize_rows(original)
    normalized = render(rows)

    errors = strict_errors(report) if args.strict else structural_errors(report)

    if args.write:
        LEDGER_PATH.write_text(normalized, encoding="utf-8")
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    else:
        if original != normalized:
            errors.append("sources/source-ledger.md is not normalized; run with --write")

    print(
        f"Recovered {report['logical_rows_recovered']} rows; "
        f"wrote {report['normalized_rows']} unique normalized rows; "
        f"removed {len(report['duplicates_removed'])} duplicates."
    )
    coverage = report["module_coverage"]
    assert isinstance(coverage, dict)
    for module in MODULE_IDS:
        item = coverage[module]
        assert isinstance(item, dict)
        print(
            f"{module}: {item['total_sources']} total, "
            f"{item['policy_tier_1_or_2']} policy-tier"
        )

    if errors:
        print("\nPhase 5 source-ledger errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
