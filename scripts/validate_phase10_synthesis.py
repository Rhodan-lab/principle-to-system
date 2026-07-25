#!/usr/bin/env python3
"""Validate Phase 10 synthesis reconciliation without writing files."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = ROOT / "synthesis" / "phase-10-canonical-graph.json"
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EDGE_RE = re.compile(r"^\s*M(\d{2})\s*-->\|prerequisite for\|\s*M(\d{2})\s*$", re.M)

BANNED = (
    "status: complete",
    "complete dependency chain",
    "any gene in any organism",
    "infinite time for diffusion",
    "training GPT-scale models costs millions of dollars",
    "supply must instantaneously equal demand",
    "bandwidth is proportional to frequency",
    "energy in its phosphoanhydride bonds",
    "scale-free networks tolerate random failures",
    "structure determines function",
    "allows each layer to evolve independently",
    "arbitrarily low error probability",
)

REQUIRED_BOUNDARY = "## Phase 10 synthesis boundaries"


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]


def parse_frontmatter(path: Path, result: Result) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = FRONT_RE.match(text)
    if not match:
        result.errors.append(f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" in line:
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"\'')
    return values


def ledger_count(result: Result) -> int:
    path = ROOT / "sources" / "source-ledger.md"
    count = 0
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            continue
        if cells[0].lower() in {"module", "---"} or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        count += 1
    if count != 143:
        result.errors.append(f"sources/source-ledger.md: expected 143 records, found {count}")
    return count


def check_links(path: Path, text: str, result: Result) -> None:
    for target in LINK_RE.findall(text):
        target = unquote(target.split("#", 1)[0].strip())
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            result.errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            result.errors.append(f"{path.relative_to(ROOT)}: broken link: {target}")


def expected_edges(modules: dict[str, list[str]]) -> set[tuple[str, str]]:
    edges: set[tuple[str, str]] = set()
    for target, prereqs in modules.items():
        for source in prereqs:
            edges.add((source[:2], target[:2]))
    return edges


def check_maps(modules: dict[str, list[str]], result: Result) -> None:
    complete = (ROOT / "maps" / "complete-dependency-map.md").read_text(encoding="utf-8")
    actual = set(EDGE_RE.findall(complete))
    expected = expected_edges(modules)
    for edge in sorted(expected - actual):
        result.errors.append(f"complete map: missing prerequisite edge {edge[0]} -> {edge[1]}")
    for edge in sorted(actual - expected):
        result.errors.append(f"complete map: unexpected prerequisite edge {edge[0]} -> {edge[1]}")
    if "|requires|" in complete:
        result.errors.append("complete map: legacy ambiguous `requires` label remains")

    foundations = (ROOT / "maps" / "foundations-map.md").read_text(encoding="utf-8")
    foundation_expected = {edge for edge in expected if int(edge[0]) <= 5 and int(edge[1]) <= 5}
    foundation_actual = set(EDGE_RE.findall(foundations))
    if foundation_actual != foundation_expected:
        result.errors.append("foundations map: edges do not match canonical Modules 01–05 prerequisites")

    science = (ROOT / "maps" / "science-to-technology-map.md").read_text(encoding="utf-8")
    for label in ("enables", "constrains", "measures", "models", "controls"):
        if f"|{label}|" not in science:
            result.errors.append(f"science-to-technology map: missing relationship label `{label}`")
    if "|requires|" in science or "|prerequisite for|" in science:
        result.errors.append("science-to-technology map: prerequisite edges must remain in dependency maps")


def main() -> int:
    result = Result([], [])
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Phase 10 manifest error: {exc}", file=sys.stderr)
        return 1

    modules = manifest.get("modules")
    if not isinstance(modules, dict) or len(modules) != 20:
        result.errors.append("canonical graph must contain exactly 20 modules")
        modules = {}
    else:
        modules = {str(k): list(v) for k, v in modules.items()}

    expected_files: list[str] = []
    for key, expected_count in (("pathways", 6), ("concepts", 7), ("maps", 3)):
        values = manifest.get(key)
        if not isinstance(values, list) or len(values) != expected_count:
            result.errors.append(f"manifest `{key}` must contain {expected_count} files")
            continue
        expected_files.extend(str(value) for value in values)

    for rel in expected_files:
        path = ROOT / rel
        if not path.is_file():
            result.errors.append(f"missing synthesis file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        fm = parse_frontmatter(path, result)
        if fm.get("status") != "reviewed":
            result.errors.append(f"{rel}: status must be reviewed")
        if fm.get("last_reviewed") != "2026-07-26":
            result.errors.append(f"{rel}: last_reviewed must be 2026-07-26")
        if REQUIRED_BOUNDARY not in text:
            result.errors.append(f"{rel}: missing Phase 10 synthesis boundaries")
        lower = text.lower()
        for phrase in BANNED:
            if phrase.lower() in lower:
                result.errors.append(f"{rel}: prohibited legacy synthesis text: {phrase}")
        check_links(path, text, result)

    if modules:
        check_maps(modules, result)

    count = ledger_count(result)
    if manifest.get("ledger_records") != 143:
        result.errors.append("manifest must preserve ledger_records = 143")

    state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for marker in (
        "Phase 10 Synthesis Reconciliation implemented",
        "6 pathways: **Reviewed**",
        "7 crosscutting concepts: **Reviewed**",
        "3 knowledge maps: **Reviewed**",
        "source ledger: **143 records**",
        "no core or synthesis artifact is Complete",
    ):
        if marker not in state:
            result.errors.append(f"PROJECT_STATE.md: missing marker: {marker}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "`synthesis/`" not in readme or "undergoing normalization" in readme:
        result.errors.append("README.md: synthesis directory or normalized source state is not documented")

    audit = (ROOT / "AUDIT.md").read_text(encoding="utf-8")
    if "## Phase 10 synthesis disposition" not in audit:
        result.errors.append("AUDIT.md: Phase 10 disposition missing")

    report = ROOT / "reports" / "phase-10-synthesis-reconciliation.md"
    if not report.is_file():
        result.errors.append("reports/phase-10-synthesis-reconciliation.md: missing")

    if result.warnings:
        print("Phase 10 warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 10 synthesis errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 10 synthesis passed: 16 reviewed synthesis files, {len(expected_edges(modules))} prerequisite edges, {count} source records.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
