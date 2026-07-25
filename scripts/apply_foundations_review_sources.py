#!/usr/bin/env python3
"""Apply and verify the reviewed source records used by Foundations Modules 01–05.

This script is intentionally separate from the legacy-ledger recovery tools. Phase 5
recovered and normalized historical provenance; Phase 6 adds only sources opened and
used during the focused scientific review.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEDGER = ROOT / "sources" / "source-ledger.md"
REGISTRY = ROOT / "sources" / "foundations-review-sources.json"
REPORT = ROOT / "reports" / "phase-6-foundations-sources.json"
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

INTRO = """# Source Ledger

Central record of every source used in the repository, per [`SOURCE_POLICY.md`](../SOURCE_POLICY.md).

This ledger is machine-readable: every source occupies exactly one eight-column Markdown row. A row's presence records provenance; it does not by itself certify that every claim using the source has completed scientific review.

"""
HEADER = (
    "| Title | Author / Institution | Date | URL or DOI | Type | Modules | Accessed | Relevance |\n"
    "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
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


def clean(value: object) -> str:
    text = re.sub(r"\s+", " ", str(value)).strip()
    return text.replace("|", "\\|")


def unescape(value: str) -> str:
    return value.replace("\\|", "|").strip()


def split_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for char in body:
        if escaped:
            current.append(char)
            escaped = False
        elif char == "\\":
            current.append(char)
            escaped = True
        elif char == "|":
            cells.append(unescape("".join(current)))
            current = []
        else:
            current.append(char)
    cells.append(unescape("".join(current)))
    return [cell.strip() for cell in cells]


def parse_ledger(text: str) -> tuple[list[Row], list[str]]:
    rows: list[Row] = []
    errors: list[str] = []
    header_seen = False
    separator_seen = False
    for line_no, line in enumerate(text.splitlines(), start=1):
        if not line.startswith("|"):
            continue
        lower = line.lower()
        if "title" in lower and "relevance" in lower:
            header_seen = True
            continue
        if header_seen and not separator_seen and re.match(r"^\|\s*-", line):
            separator_seen = True
            continue
        if not separator_seen:
            continue
        cells = split_row(line)
        if len(cells) != 8:
            errors.append(f"line {line_no}: expected 8 cells, found {len(cells)}")
            continue
        rows.append(Row(*cells))
    if not header_seen or not separator_seen:
        errors.append("source-ledger table header or separator is missing")
    return rows, errors


def load_registry() -> tuple[list[Row], list[str]]:
    errors: list[str] = []
    try:
        data = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [], [f"cannot load registry: {exc}"]
    if not isinstance(data, list):
        return [], ["registry root must be a list"]

    rows: list[Row] = []
    required = (
        "title",
        "author",
        "date",
        "locator",
        "type",
        "modules",
        "accessed",
        "relevance",
    )
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            errors.append(f"registry item {index}: must be an object")
            continue
        missing = [key for key in required if not item.get(key)]
        if missing:
            errors.append(f"registry item {index}: missing {', '.join(missing)}")
            continue
        accessed = str(item["accessed"])
        try:
            date.fromisoformat(accessed)
        except ValueError:
            errors.append(f"registry item {index}: invalid accessed date {accessed}")
        locator = str(item["locator"])
        if not locator.startswith(("https://", "http://")):
            errors.append(f"registry item {index}: locator must be an HTTP(S) URL")
        rows.append(
            Row(
                clean(item["title"]),
                clean(item["author"]),
                clean(item["date"]),
                clean(locator),
                clean(item["type"]),
                clean(item["modules"]),
                clean(accessed),
                clean(item["relevance"]),
            )
        )
    return rows, errors


def key(row: Row) -> tuple[str, str]:
    return row.locator.rstrip("/").lower(), row.title.lower()


def sort_key(row: Row) -> tuple[int, str, str]:
    match = re.match(r"^(\d{2})-", row.modules)
    number = int(match.group(1)) if match else 999
    return number, row.title.lower(), row.locator.lower()


def render(rows: list[Row]) -> str:
    lines = [INTRO.rstrip(), "", HEADER.rstrip()]
    for row in sorted(rows, key=sort_key):
        lines.append("| " + " | ".join(row.cells()) + " |")
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not LEDGER.exists() or not REGISTRY.exists():
        print("ERROR: source ledger or Foundations source registry is missing", file=sys.stderr)
        return 1

    existing, ledger_errors = parse_ledger(LEDGER.read_text(encoding="utf-8"))
    reviewed, registry_errors = load_registry()
    errors = ledger_errors + registry_errors

    by_key = {key(row): row for row in existing}
    by_locator = {row.locator.rstrip("/").lower(): row for row in existing}
    added: list[Row] = []
    already_present: list[Row] = []
    conflicts: list[str] = []

    for row in reviewed:
        locator_key = row.locator.rstrip("/").lower()
        if key(row) in by_key:
            already_present.append(row)
            continue
        if locator_key in by_locator:
            current = by_locator[locator_key]
            conflicts.append(
                f"locator {row.locator} already belongs to '{current.title}', not '{row.title}'"
            )
            continue
        existing.append(row)
        by_key[key(row)] = row
        by_locator[locator_key] = row
        added.append(row)

    errors.extend(conflicts)
    final_text = render(existing)
    current_text = LEDGER.read_text(encoding="utf-8")

    required_locators = {row.locator.rstrip("/").lower() for row in reviewed}
    final_locators = {row.locator.rstrip("/").lower() for row in existing}
    missing = sorted(required_locators - final_locators)
    if missing:
        errors.extend(f"missing reviewed locator: {locator}" for locator in missing)

    report = {
        "generated": date.today().isoformat(),
        "registry_records": len(reviewed),
        "ledger_records_before": len(existing) - len(added),
        "records_added": [row.locator for row in added],
        "already_present": [row.locator for row in already_present],
        "ledger_records_after": len(existing),
        "errors": errors,
    }

    if args.write:
        REPORT.parent.mkdir(parents=True, exist_ok=True)
        LEDGER.write_text(final_text, encoding="utf-8")
        REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    if args.check:
        if current_text != final_text:
            errors.append("ledger differs from the deterministic reviewed-source result")
        if not REPORT.exists():
            errors.append("phase-6 source report is missing")

    if errors:
        print("Phase 6 source errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    mode = "write" if args.write else "check" if args.check else "inspect"
    print(
        f"Phase 6 sources ({mode}): {len(reviewed)} registry records, "
        f"{len(added)} additions, {len(existing)} final ledger records."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
