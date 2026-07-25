#!/usr/bin/env python3
"""Apply and verify authoritative sources used by the Phase 9 review."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import normalize_source_ledger as ledger_tool

ROOT = Path(__file__).resolve().parent.parent
REGISTRY = ROOT / "sources" / "phase-9-reviewed-sources.json"
LEDGER = ROOT / "sources" / "source-ledger.md"
REPORT = ROOT / "reports" / "phase-9-technology-sources.json"
REQUIRED_FIELDS = (
    "title",
    "author",
    "date",
    "locator",
    "type",
    "modules",
    "accessed",
    "relevance",
)
EXPECTED_BEFORE = 131
EXPECTED_ADDITIONS = 12
EXPECTED_AFTER = 143


def load_registry() -> list[dict[str, str]]:
    raw = json.loads(REGISTRY.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("Phase 9 source registry must be a list.")
    records: list[dict[str, str]] = []
    for index, item in enumerate(raw, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Registry record {index} is not an object.")
        missing = [field for field in REQUIRED_FIELDS if not str(item.get(field, "")).strip()]
        if missing:
            raise ValueError(f"Registry record {index} is missing: {', '.join(missing)}")
        records.append({field: str(item[field]).strip() for field in REQUIRED_FIELDS})
    locators = [record["locator"].rstrip("/") for record in records]
    if len(locators) != len(set(locators)):
        raise ValueError("Phase 9 source registry contains duplicate locators.")
    if len(records) != EXPECTED_ADDITIONS:
        raise ValueError(f"Expected {EXPECTED_ADDITIONS} Phase 9 records, found {len(records)}.")
    return records


def current_rows():
    text = LEDGER.read_text(encoding="utf-8")
    rows, report = ledger_tool.normalize_rows(text)
    errors = ledger_tool.structural_errors(report)
    if errors:
        raise ValueError("Central source ledger is not structurally valid: " + ", ".join(errors))
    return rows


def apply(records: list[dict[str, str]], write: bool) -> tuple[list[str], list[str], int, int]:
    rows = current_rows()
    before = len(rows)
    existing = {row.locator.rstrip("/") for row in rows}
    added: list[str] = []
    already: list[str] = []

    for record in records:
        locator_key = record["locator"].rstrip("/")
        if locator_key in existing:
            already.append(record["locator"])
            continue
        rows.append(
            ledger_tool.Row(
                title=record["title"],
                author=record["author"],
                published=record["date"],
                locator=record["locator"],
                source_type=record["type"],
                modules=record["modules"],
                accessed=record["accessed"],
                relevance=record["relevance"],
            )
        )
        existing.add(locator_key)
        added.append(record["locator"])

    rows.sort(key=lambda row: (ledger_tool.module_sort_key(row.modules), row.title.lower(), row.locator.lower()))
    if write:
        LEDGER.write_text(ledger_tool.render(rows), encoding="utf-8")
    return added, already, before, len(rows)


def verify(records: list[dict[str, str]]) -> list[str]:
    text = LEDGER.read_text(encoding="utf-8")
    errors: list[str] = []
    for record in records:
        if record["locator"] not in text:
            errors.append(f"missing locator in central ledger: {record['locator']}")
        if record["modules"] not in ledger_tool.MODULE_IDS:
            errors.append(f"invalid module identifier: {record['modules']}")
    rows = current_rows()
    if len(rows) != EXPECTED_AFTER:
        errors.append(f"central ledger has {len(rows)} records; expected {EXPECTED_AFTER}")
    return errors


def write_initial_report(added: list[str], already: list[str], before: int, after: int) -> None:
    if REPORT.exists():
        return
    if before != EXPECTED_BEFORE:
        raise ValueError(f"Initial Phase 9 ledger count is {before}; expected {EXPECTED_BEFORE}.")
    if len(added) != EXPECTED_ADDITIONS or already:
        raise ValueError(
            f"Initial Phase 9 application expected {EXPECTED_ADDITIONS} additions and no existing records; "
            f"got {len(added)} additions and {len(already)} existing."
        )
    if after != EXPECTED_AFTER:
        raise ValueError(f"Initial Phase 9 ledger result is {after}; expected {EXPECTED_AFTER}.")
    report = {
        "generated": "2026-07-26",
        "registry_records": EXPECTED_ADDITIONS,
        "ledger_records_before": EXPECTED_BEFORE,
        "records_added": added,
        "already_present": [],
        "ledger_records_after": EXPECTED_AFTER,
        "errors": [],
    }
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")


def verify_report(errors: list[str]) -> None:
    if not REPORT.exists():
        errors.append("Phase 9 source report is missing")
        return
    try:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"Phase 9 source report is invalid JSON: {exc}")
        return
    expected = {
        "registry_records": EXPECTED_ADDITIONS,
        "ledger_records_before": EXPECTED_BEFORE,
        "ledger_records_after": EXPECTED_AFTER,
        "errors": [],
    }
    for key, value in expected.items():
        if report.get(key) != value:
            errors.append(f"Phase 9 source report {key}={report.get(key)!r}; expected {value!r}")
    additions = report.get("records_added")
    if not isinstance(additions, list) or len(additions) != EXPECTED_ADDITIONS:
        errors.append("Phase 9 source report must preserve all twelve initial additions")


def main() -> int:
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    try:
        records = load_registry()
        added, already, before, after = apply(records, write=args.write)
        if args.write:
            write_initial_report(added, already, before, after)
        errors = verify(records)
        verify_report(errors)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"Phase 9 source validation passed for {len(records)} records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
