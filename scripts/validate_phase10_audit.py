#!/usr/bin/env python3
"""Validate Phase 10 audit history, status policy, and read-only CI."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MANIFEST = ROOT / "synthesis" / "phase-10-canonical-graph.json"
PERMANENT_WORKFLOW = ROOT / ".github" / "workflows" / "validate-phase-10-synthesis.yml"
TEMP_WORKFLOW = ROOT / ".github" / "workflows" / "apply-phase-10-synthesis.yml"
INDEX_RE = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$", re.I)
FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def ledger_count(errors: list[str]) -> int:
    count = 0
    path = ROOT / "sources" / "source-ledger.md"
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            continue
        if cells[0].lower() in {"module", "title", "---"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        count += 1
    if count != 143:
        fail(errors, f"sources/source-ledger.md: expected 143 records, found {count}")
    return count


def front_status(path: Path, errors: list[str]) -> str | None:
    text = path.read_text(encoding="utf-8")
    match = FRONT_RE.match(text)
    if not match:
        fail(errors, f"{path.relative_to(ROOT)}: missing frontmatter")
        return None
    for line in match.group(1).splitlines():
        if line.startswith("status:"):
            return line.split(":", 1)[1].strip().strip('"\'').lower()
    fail(errors, f"{path.relative_to(ROOT)}: missing status")
    return None


def main() -> int:
    errors: list[str] = []

    try:
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Phase 10 audit error: {exc}", file=sys.stderr)
        return 1

    if len(manifest.get("modules", {})) != 20:
        fail(errors, "canonical graph must contain 20 modules")
    expected_groups = {"pathways": 6, "concepts": 7, "maps": 3}
    synthesis_files: list[str] = []
    for group, expected in expected_groups.items():
        values = manifest.get(group)
        if not isinstance(values, list) or len(values) != expected:
            fail(errors, f"manifest {group} must contain {expected} files")
            continue
        synthesis_files.extend(str(value) for value in values)

    for rel in synthesis_files:
        path = ROOT / rel
        if not path.is_file():
            fail(errors, f"missing synthesis artifact: {rel}")
            continue
        if front_status(path, errors) != "reviewed":
            fail(errors, f"{rel}: synthesis artifact must remain Reviewed")

    statuses: dict[str, str] = {}
    for line in (ROOT / "INDEX.md").read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in [f"{value:02d}" for value in range(1, 21)]:
        if statuses.get(number) != "reviewed":
            fail(errors, f"INDEX.md: Module {number} must be Reviewed")
    if any(status == "complete" for status in statuses.values()):
        fail(errors, "INDEX.md: no core module may be Complete")

    ledger_count(errors)
    if manifest.get("ledger_records") != 143:
        fail(errors, "canonical graph must preserve ledger_records = 143")

    state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for marker in (
        "Phase 10 Synthesis Reconciliation implemented and validated on draft PR #11",
        "Modules 01–20: **Reviewed**",
        "6 pathways: **Reviewed**",
        "7 crosscutting concepts: **Reviewed**",
        "3 knowledge maps: **Reviewed**",
        "source ledger: **143 records**",
        "no core or synthesis artifact is Complete",
        "Phase 11",
    ):
        if marker not in state:
            fail(errors, f"PROJECT_STATE.md: missing marker: {marker}")

    required = (
        MANIFEST,
        ROOT / "reports" / "phase-10-synthesis-reconciliation.md",
        ROOT / "scripts" / "apply_phase10_synthesis.py",
        ROOT / "scripts" / "finalize_phase10_synthesis.py",
        ROOT / "scripts" / "normalize_phase10_reconciler.py",
        ROOT / "scripts" / "validate_phase10_synthesis.py",
        ROOT / "scripts" / "validate_phase10_audit.py",
        PERMANENT_WORKFLOW,
    )
    for path in required:
        if not path.is_file():
            fail(errors, f"missing Phase 10 audit artifact: {path.relative_to(ROOT)}")

    if TEMP_WORKFLOW.exists():
        fail(errors, "temporary Phase 10 write workflow must be removed")
    if PERMANENT_WORKFLOW.exists():
        workflow = PERMANENT_WORKFLOW.read_text(encoding="utf-8")
        for forbidden in ("contents: write", "git push", "git commit", "pull_request_target"):
            if forbidden in workflow:
                fail(errors, f"permanent Phase 10 workflow contains forbidden write capability: {forbidden}")
        if "contents: read" not in workflow:
            fail(errors, "permanent Phase 10 workflow must declare contents: read")

    report = (ROOT / "reports" / "phase-10-synthesis-reconciliation.md").read_text(encoding="utf-8")
    for marker in ("6 pathways", "7 crosscutting concepts", "3 knowledge maps", "preserve 143 records"):
        if marker not in report:
            fail(errors, f"Phase 10 report missing audit marker: {marker}")

    if errors:
        print("Phase 10 audit errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("Phase 10 audit passed: 20 reviewed modules, 16 reviewed synthesis files, 143 source records, read-only CI.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
