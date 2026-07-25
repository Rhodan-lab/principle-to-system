#!/usr/bin/env python3
"""Apply inspected Phase 5 source replacements to the normalized ledger."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
LEDGER_PATH = REPO_ROOT / "sources" / "source-ledger.md"
BASELINE_PATH = REPO_ROOT / "sources" / "verified-source-baseline.json"
REPORT_PATH = REPO_ROOT / "reports" / "phase-5-source-replacements.json"
MODULE_RE = re.compile(r"^(?:0[1-9]|1[0-9]|20)-[a-z0-9-]+$")


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


def split_markdown_row(line: str) -> list[str]:
    body = line.strip().strip("|")
    parts = re.split(r"(?<!\\)\|", body)
    return [part.replace("\\|", "|").strip() for part in parts]


def escape(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip()
    return value.replace("|", "\\|")


def parse_ledger(text: str) -> tuple[str, list[Row]]:
    lines = text.splitlines()
    header_index = next(
        (
            index
            for index, line in enumerate(lines)
            if line.startswith("|") and "Title" in line and "Relevance" in line
        ),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        raise ValueError("Could not find normalized ledger table header.")

    prefix = "\n".join(lines[:header_index]).rstrip() + "\n\n"
    rows: list[Row] = []
    for line_no, line in enumerate(lines[header_index + 2 :], start=header_index + 3):
        if not line.strip():
            continue
        cells = split_markdown_row(line)
        if len(cells) != 8:
            raise ValueError(f"Ledger line {line_no} has {len(cells)} cells, expected 8.")
        rows.append(Row(*cells))
    return prefix, rows


def parse_baseline() -> list[dict[str, object]]:
    raw = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Verified source baseline must be a JSON array.")
    required = {
        "title",
        "author",
        "date",
        "locator",
        "type",
        "modules",
        "accessed",
        "relevance",
        "replaces",
    }
    records: list[dict[str, object]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Baseline item {index} must be an object.")
        missing = required - set(item)
        if missing:
            raise ValueError(f"Baseline item {index} missing fields: {sorted(missing)}")
        modules = str(item["modules"])
        for module in [part.strip() for part in modules.split(",") if part.strip()]:
            if not MODULE_RE.fullmatch(module):
                raise ValueError(f"Baseline item {index} has malformed module ID {module!r}.")
        if not isinstance(item["replaces"], list):
            raise ValueError(f"Baseline item {index} replaces must be a list.")
        records.append(item)
    return records


def row_key(row: Row) -> tuple[str, str]:
    return row.locator.lower().rstrip("/"), re.sub(r"\W+", " ", row.title.lower()).strip()


def sort_key(row: Row) -> tuple[int, str, str]:
    first = row.modules.split(",", 1)[0].strip()
    number = int(first[:2]) if MODULE_RE.fullmatch(first) else 999
    return number, row.title.lower(), row.locator.lower()


def render(prefix: str, rows: list[Row]) -> str:
    header = (
        "| Title | Author / Institution | Date | URL or DOI | Type | Modules | Accessed | Relevance |\n"
        "| --- | --- | --- | --- | --- | --- | --- | --- |\n"
    )
    body = "\n".join("| " + " | ".join(escape(cell) for cell in row.cells()) + " |" for row in rows)
    return prefix + header + body + "\n"


def apply(rows: list[Row], baseline: list[dict[str, object]]) -> tuple[list[Row], dict[str, object]]:
    replacement_locators = {
        str(locator).strip().lower().rstrip("/")
        for item in baseline
        for locator in item["replaces"]
        if str(locator).strip()
    }

    kept: list[Row] = []
    removed: list[dict[str, str]] = []
    for row in rows:
        locator_key = row.locator.lower().rstrip("/")
        if locator_key in replacement_locators:
            removed.append({"title": row.title, "locator": row.locator, "modules": row.modules})
        else:
            kept.append(row)

    existing = {row_key(row) for row in kept}
    added: list[dict[str, str]] = []
    already_present: list[dict[str, str]] = []
    for item in baseline:
        row = Row(
            title=str(item["title"]),
            author=str(item["author"]),
            published=str(item["date"]),
            locator=str(item["locator"]),
            source_type=str(item["type"]),
            modules=str(item["modules"]),
            accessed=str(item["accessed"]),
            relevance=str(item["relevance"]),
        )
        key = row_key(row)
        if key in existing:
            already_present.append({"title": row.title, "locator": row.locator})
            continue
        kept.append(row)
        existing.add(key)
        added.append({"title": row.title, "locator": row.locator, "modules": row.modules})

    kept.sort(key=sort_key)
    report: dict[str, object] = {
        "baseline_records": len(baseline),
        "records_before": len(rows),
        "records_removed": removed,
        "records_added": added,
        "baseline_already_present": already_present,
        "records_after": len(kept),
        "replacement_locators_declared": len(replacement_locators),
        "replacement_locators_matched": len({item["locator"].lower().rstrip("/") for item in removed}),
    }
    return kept, report


def main() -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true")
    mode.add_argument("--check", action="store_true")
    args = parser.parse_args()

    if not LEDGER_PATH.exists() or not BASELINE_PATH.exists():
        print("Missing source ledger or verified baseline.", file=sys.stderr)
        return 1

    try:
        original = LEDGER_PATH.read_text(encoding="utf-8")
        prefix, rows = parse_ledger(original)
        baseline = parse_baseline()
        updated_rows, report = apply(rows, baseline)
        rendered = render(prefix, updated_rows)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    matched = int(report["replacement_locators_matched"])
    declared = int(report["replacement_locators_declared"])
    missing = declared - matched

    if args.write:
        LEDGER_PATH.write_text(rendered, encoding="utf-8")
        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    elif original != rendered:
        print("Verified source replacements are not fully applied; run with --write.", file=sys.stderr)
        return 1

    print(
        f"Verified baseline: {len(baseline)} records; removed {len(report['records_removed'])}; "
        f"added {len(report['records_added'])}; {len(report['baseline_already_present'])} already present."
    )
    if missing:
        print(
            f"WARNING: {missing} declared replacement locators were not present in the current ledger.",
            file=sys.stderr,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
