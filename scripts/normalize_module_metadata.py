#!/usr/bin/env python3
"""Normalize frontmatter metadata across the 60 core learner files.

The script is intentionally limited to metadata. It does not rewrite educational
prose or change review statuses. In check mode it reports files that would
change. With --write it updates them and writes a machine-readable audit report.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = date.today().isoformat()

MODULES: dict[str, tuple[str, tuple[str, ...]]] = {
    "01-scientific-reasoning": ("foundations", ()),
    "02-measurement-uncertainty": ("foundations", ("01-scientific-reasoning",)),
    "03-mathematical-models": ("foundations", ("01-scientific-reasoning",)),
    "04-probability-statistics": ("foundations", ("01-scientific-reasoning", "03-mathematical-models")),
    "05-computation-algorithms": ("foundations", ("03-mathematical-models", "04-probability-statistics")),
    "06-matter-quantum": ("science", ("01-scientific-reasoning", "02-measurement-uncertainty", "03-mathematical-models")),
    "07-chemical-bonding": ("science", ("06-matter-quantum",)),
    "08-energy-thermodynamics": ("science", ("03-mathematical-models", "06-matter-quantum")),
    "09-motion-forces": ("science", ("03-mathematical-models",)),
    "10-electricity-magnetism": ("science", ("03-mathematical-models", "06-matter-quantum")),
    "11-waves-signals": ("science", ("03-mathematical-models", "09-motion-forces")),
    "12-fluids-materials": ("science", ("03-mathematical-models", "08-energy-thermodynamics", "09-motion-forces")),
    "13-cells-bioenergetics": ("science", ("07-chemical-bonding", "08-energy-thermodynamics")),
    "14-dna-evolution": ("science", ("07-chemical-bonding", "13-cells-bioenergetics")),
    "15-ecosystems-complex-systems": ("science", ("04-probability-statistics", "13-cells-bioenergetics", "14-dna-evolution")),
    "16-earth-planetary": ("science", ("08-energy-thermodynamics", "09-motion-forces", "12-fluids-materials", "15-ecosystems-complex-systems")),
    "17-materials-manufacturing": ("technology", ("06-matter-quantum", "07-chemical-bonding", "12-fluids-materials")),
    "18-semiconductors-electronics": ("technology", ("06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing")),
    "19-software-ai": ("technology", ("04-probability-statistics", "05-computation-algorithms", "18-semiconductors-electronics")),
    "20-sensors-control-infrastructure": ("technology", ("10-electricity-magnetism", "11-waves-signals", "18-semiconductors-electronics", "19-software-ai")),
}
FILES = ("overview.md", "technology.md", "explore.md")
ROLE_SUFFIX = {"overview.md": "", "technology.md": "-technology", "explore.md": "-explore"}
TARGET_KEYS = {"slug", "module", "domain", "prerequisites", "connections"}
LINE_RE = re.compile(r"^(?P<indent>\s*)(?P<key>[A-Za-z0-9_-]+)\s*:\s*(?P<value>.*)$")


def parse_list(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw.startswith("[") or not raw.endswith("]"):
        return [] if not raw else [raw.strip("\"'")]
    inner = raw[1:-1].strip()
    if not inner:
        return []
    return [part.strip().strip("\"'") for part in inner.split(",") if part.strip()]


def frontmatter_parts(text: str) -> tuple[list[str], str]:
    if not text.startswith("---\n"):
        raise ValueError("missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("missing closing frontmatter delimiter")
    return text[4:end].splitlines(), text[end + 5 :]


def normalize_reference(value: str) -> str | None:
    candidate = value.strip().strip("\"'")
    if candidate in MODULES:
        return candidate
    for suffix in ("-technology", "-explore", "-overview"):
        if candidate.endswith(suffix) and candidate[: -len(suffix)] in MODULES:
            return candidate[: -len(suffix)]
    # Recover identifiers embedded in older descriptive names.
    for module_id in MODULES:
        if candidate.startswith(module_id) or module_id in candidate:
            return module_id
    return None


def reverse_dependencies() -> dict[str, set[str]]:
    result: dict[str, set[str]] = defaultdict(set)
    for module_id, (_, prereqs) in MODULES.items():
        for prereq in prereqs:
            result[prereq].add(module_id)
    return result


def format_list(values: list[str] | tuple[str, ...]) -> str:
    return "[" + ", ".join(values) + "]"


def normalize_file(path: Path, module_id: str, filename: str, downstream: dict[str, set[str]]) -> tuple[str, dict[str, object]]:
    original = path.read_text(encoding="utf-8")
    lines, body = frontmatter_parts(original)
    existing: dict[str, str] = {}
    order: list[str] = []
    passthrough: list[str] = []
    for line in lines:
        match = LINE_RE.match(line)
        if not match:
            passthrough.append(line)
            continue
        key = match.group("key")
        existing[key] = match.group("value").strip()
        order.append(key)

    old_connections = parse_list(existing.get("connections", "[]"))
    kept: set[str] = set()
    removed: list[str] = []
    remapped: dict[str, str] = {}
    for reference in old_connections:
        normalized = normalize_reference(reference)
        if normalized is None or normalized == module_id:
            removed.append(reference)
            continue
        kept.add(normalized)
        if normalized != reference:
            remapped[reference] = normalized

    # Connections describe valid neighbouring modules. Canonical prerequisites
    # remain in their own field; downstream dependants make navigation useful.
    connections = sorted(kept | downstream.get(module_id, set()))
    domain, prereqs = MODULES[module_id]
    desired = {
        "slug": module_id + ROLE_SUFFIX[filename],
        "module": f'"Module {module_id[:2]}"',
        "domain": domain,
        "prerequisites": format_list(prereqs),
        "connections": format_list(connections),
    }

    rebuilt: list[str] = []
    written: set[str] = set()
    for line in lines:
        match = LINE_RE.match(line)
        if not match:
            rebuilt.append(line)
            continue
        key = match.group("key")
        if key in TARGET_KEYS:
            if key not in written:
                rebuilt.append(f"{key}: {desired[key]}")
                written.add(key)
            continue
        rebuilt.append(line)
    for key in ("slug", "module", "domain", "prerequisites", "connections"):
        if key not in written:
            rebuilt.append(f"{key}: {desired[key]}")

    updated = "---\n" + "\n".join(rebuilt) + "\n---\n" + body
    report = {
        "path": str(path.relative_to(ROOT)),
        "changed": updated != original,
        "old": {key: existing.get(key) for key in TARGET_KEYS},
        "new": desired,
        "removed_connections": removed,
        "remapped_connections": remapped,
    }
    return updated, report


def run(write: bool) -> int:
    downstream = reverse_dependencies()
    records: list[dict[str, object]] = []
    errors: list[str] = []
    for module_id, (domain, _) in MODULES.items():
        for filename in FILES:
            path = ROOT / domain / module_id / filename
            try:
                updated, record = normalize_file(path, module_id, filename, downstream)
            except (OSError, ValueError) as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
                continue
            records.append(record)
            if write and record["changed"]:
                path.write_text(updated, encoding="utf-8")

    changed = [record for record in records if record["changed"]]
    report = {
        "generated": TODAY,
        "mode": "write" if write else "check",
        "module_files_expected": len(MODULES) * len(FILES),
        "module_files_processed": len(records),
        "files_changed": len(changed),
        "errors": errors,
        "records": records,
    }
    report_path = ROOT / "reports" / "phase-4-metadata-normalization.json"
    if write:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")

    print(f"Processed {len(records)} of {len(MODULES) * len(FILES)} learner files")
    print(f"Files requiring normalization: {len(changed)}")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    if not write and changed:
        for record in changed:
            print(f"WOULD CHANGE: {record['path']}")
        return 1
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true", help="apply changes and write the audit report")
    args = parser.parse_args()
    return run(args.write)


if __name__ == "__main__":
    raise SystemExit(main())
