#!/usr/bin/env python3
"""Apply and validate Product Alpha path scoping for GitHub Actions workflows."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
WORKFLOW_DIR = REPO_ROOT / ".github" / "workflows"
POLICY_PATH = REPO_ROOT / "ci" / "workflow-scope-policy.json"

PRODUCT_PATHS = (
    "software/product_alpha/**",
    "software/tests/test_product_alpha*.py",
)
PRODUCT_FIXTURE_PATHS = (
    "software/product_alpha/index.html",
    "software/tests/test_product_alpha_evaluation.py",
)
EXEMPT_WORKFLOWS = {
    "validate-product-alpha.yml",
    "validate-workflow-scope.yml",
    "apply-ci-product-alpha-scope.yml",
}
TEMP_WORKFLOW = WORKFLOW_DIR / "apply-ci-product-alpha-scope.yml"


class ScopeError(RuntimeError):
    """Raised when workflow scope is unsupported or inconsistent."""


def workflow_paths(root: Path = WORKFLOW_DIR) -> list[Path]:
    return sorted([*root.glob("*.yml"), *root.glob("*.yaml")])


def _render_event(event: str, indent: str = "  ") -> list[str]:
    lines = [f"{indent}{event}:\n"]
    if event in {"pull_request", "push"}:
        lines.append(f"{indent}  paths-ignore:\n")
        for pattern in PRODUCT_PATHS:
            lines.append(f"{indent}    - '{pattern}'\n")
    return lines


def _replace_inline_on(line: str) -> list[str] | None:
    list_match = re.fullmatch(r"on:\s*\[([^\]]+)\]\s*\n?", line)
    if list_match:
        events = [item.strip() for item in list_match.group(1).split(",") if item.strip()]
        if not {"pull_request", "push"} & set(events):
            return [line if line.endswith("\n") else line + "\n"]
        output = ["on:\n"]
        for event in events:
            output.extend(_render_event(event))
        return output

    scalar_match = re.fullmatch(r"on:\s*(pull_request|push)\s*\n?", line)
    if scalar_match:
        return ["on:\n", *_render_event(scalar_match.group(1))]
    return None


def _on_block(lines: list[str]) -> tuple[int, int] | None:
    try:
        start = next(i for i, line in enumerate(lines) if re.fullmatch(r"on:\s*\n?", line))
    except StopIteration:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].strip() and not lines[idx].startswith((" ", "\t")):
            end = idx
            break
    return start, end


def _event_sections(
    lines: list[str], start: int, end: int
) -> list[tuple[str, int, int]]:
    sections: list[tuple[str, int, int]] = []
    current_name: str | None = None
    current_start: int | None = None
    for idx in range(start + 1, end):
        match = re.match(r"^  ([A-Za-z0-9_-]+):(?:\s*(.*))?$", lines[idx])
        if not match:
            continue
        if current_name is not None and current_start is not None:
            sections.append((current_name, current_start, idx))
        current_name = match.group(1)
        current_start = idx
    if current_name is not None and current_start is not None:
        sections.append((current_name, current_start, end))
    return sections


def _has_path_filter(section: list[str]) -> bool:
    return any(re.match(r"^    paths(?:-ignore)?:\s*$", line) for line in section[1:])


def _expand_empty_event(line: str, event: str) -> list[str]:
    if not re.fullmatch(rf"  {re.escape(event)}:\s*(?:\{{\}})?\s*\n?", line):
        raise ScopeError(
            f"unsupported inline configuration for event {event!r}: {line.rstrip()}"
        )
    return _render_event(event)


def transform_workflow(text: str, filename: str) -> str:
    """Return workflow text with Product Alpha-only changes ignored by legacy events."""
    if filename in EXEMPT_WORKFLOWS:
        return text

    lines = text.splitlines(keepends=True)
    for idx, line in enumerate(lines):
        inline = _replace_inline_on(line)
        if inline is not None and inline != [line]:
            return "".join(lines[:idx] + inline + lines[idx + 1 :])

    bounds = _on_block(lines)
    if bounds is None:
        return text
    on_start, on_end = bounds

    replacements: list[tuple[int, int, list[str]]] = []
    for event, section_start, section_end in _event_sections(lines, on_start, on_end):
        if event not in {"pull_request", "push"}:
            continue
        section = lines[section_start:section_end]
        if _has_path_filter(section):
            continue

        event_line = section[0]
        if event_line.strip() not in {f"{event}:", f"{event}: {{}}"}:
            raise ScopeError(
                f"{filename}: unsupported {event} event configuration: "
                f"{event_line.rstrip()}"
            )

        if len(section) == 1 or all(not item.strip() for item in section[1:]):
            replacement = _expand_empty_event(event_line, event)
            replacement.extend(section[1:])
        else:
            trailing_blank: list[str] = []
            while len(section) > 1 and not section[-1].strip():
                trailing_blank.insert(0, section.pop())
            replacement = section + ["    paths-ignore:\n"]
            replacement.extend(f"      - '{pattern}'\n" for pattern in PRODUCT_PATHS)
            replacement.extend(trailing_blank)
        replacements.append((section_start, section_end, replacement))

    if not replacements:
        return text

    result = lines[:]
    for start, stop, replacement in reversed(replacements):
        result[start:stop] = replacement
    return "".join(result)


def apply(root: Path = WORKFLOW_DIR, write: bool = False) -> list[str]:
    changed: list[str] = []
    for path in workflow_paths(root):
        text = path.read_text(encoding="utf-8")
        updated = transform_workflow(text, path.name)
        if updated == text:
            continue
        changed.append(path.name)
        if write:
            path.write_text(updated, encoding="utf-8")
    return changed


def _strip_pattern(line: str) -> str | None:
    match = re.match(r"^\s*-\s*['\"]?([^'\"]+)['\"]?\s*$", line)
    return match.group(1).strip() if match else None


def event_path_filters(text: str, event: str) -> dict[str, list[str]] | None:
    """Extract simple paths/paths-ignore lists for one workflow event."""
    lines = text.splitlines(keepends=True)

    for line in lines:
        list_match = re.fullmatch(r"on:\s*\[([^\]]+)\]\s*\n?", line)
        if list_match:
            events = {item.strip() for item in list_match.group(1).split(",")}
            return {} if event in events else None
        scalar_match = re.fullmatch(r"on:\s*(pull_request|push)\s*\n?", line)
        if scalar_match:
            return {} if scalar_match.group(1) == event else None

    bounds = _on_block(lines)
    if bounds is None:
        return None
    start, end = bounds
    sections = {
        name: lines[section_start:section_end]
        for name, section_start, section_end in _event_sections(lines, start, end)
    }
    section = sections.get(event)
    if section is None:
        return None

    result: dict[str, list[str]] = {}
    current: str | None = None
    for line in section[1:]:
        key_match = re.match(r"^    (paths|paths-ignore):\s*$", line)
        if key_match:
            current = key_match.group(1)
            result[current] = []
            continue
        if current is not None:
            pattern = _strip_pattern(line)
            if pattern is not None:
                result[current].append(pattern)
                continue
            if line.strip() and not line.startswith("      "):
                current = None
    return result


def _matches_positive_patterns(path: str, patterns: list[str]) -> bool:
    matched = False
    for pattern in patterns:
        negative = pattern.startswith("!")
        candidate = pattern[1:] if negative else pattern
        if fnmatch.fnmatchcase(path, candidate):
            matched = not negative
    return matched


def event_runs_for_paths(text: str, event: str, changed_paths: tuple[str, ...]) -> bool:
    filters = event_path_filters(text, event)
    if filters is None:
        return False
    positive = filters.get("paths")
    ignored = filters.get("paths-ignore")
    if positive is not None:
        return any(_matches_positive_patterns(path, positive) for path in changed_paths)
    if ignored is not None:
        return not all(
            any(fnmatch.fnmatchcase(path, pattern) for pattern in ignored)
            for path in changed_paths
        )
    return True


def validate_policy(root: Path = REPO_ROOT) -> dict[str, Any]:
    policy_path = root / POLICY_PATH.relative_to(REPO_ROOT)
    policy = json.loads(policy_path.read_text(encoding="utf-8"))

    expected_paths = tuple(policy["product_alpha_only_paths"])
    if expected_paths != PRODUCT_PATHS:
        raise ScopeError(
            f"policy path drift: expected {PRODUCT_PATHS!r}, found {expected_paths!r}"
        )
    if set(policy["exempt_workflows"]) != EXEMPT_WORKFLOWS:
        raise ScopeError("policy exempt workflow set does not match implementation")

    workflow_root = root / ".github" / "workflows"
    drift: list[str] = []
    unexpected_fixture_checks: list[str] = []
    checked_events = 0

    for path in workflow_paths(workflow_root):
        text = path.read_text(encoding="utf-8")
        if path.name not in EXEMPT_WORKFLOWS:
            updated = transform_workflow(text, path.name)
            if updated != text:
                drift.append(path.name)

        for event in ("pull_request", "push"):
            if event_path_filters(text, event) is None:
                continue
            checked_events += 1
            if (
                path.name not in EXEMPT_WORKFLOWS
                and event_runs_for_paths(text, event, PRODUCT_FIXTURE_PATHS)
            ):
                unexpected_fixture_checks.append(f"{path.name}:{event}")

    if drift:
        raise ScopeError("workflow scope drift: " + ", ".join(drift))
    if unexpected_fixture_checks:
        raise ScopeError(
            "Product Alpha-only fixture would trigger legacy checks: "
            + ", ".join(unexpected_fixture_checks)
        )

    expected_checks = set(policy["product_alpha_only_expected_checks"])
    actual_checks: set[str] = set()
    for path in workflow_paths(workflow_root):
        text = path.read_text(encoding="utf-8")
        if event_runs_for_paths(text, "pull_request", PRODUCT_FIXTURE_PATHS):
            actual_checks.add(path.name)
    if actual_checks != expected_checks:
        raise ScopeError(
            "Product Alpha-only expected-check drift: "
            f"expected {sorted(expected_checks)}, found {sorted(actual_checks)}"
        )

    return {
        "schema": policy["schema"],
        "workflow_files": len(workflow_paths(workflow_root)),
        "checked_events": checked_events,
        "product_alpha_only_expected_checks": sorted(actual_checks),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="rewrite workflows in place")
    mode.add_argument("--check", action="store_true", help="fail when rewrites are required")
    args = parser.parse_args()

    changed = apply(write=args.write)
    if args.write:
        if TEMP_WORKFLOW.exists():
            TEMP_WORKFLOW.unlink()
            changed.append(TEMP_WORKFLOW.name)
        print(f"Updated {len(changed)} workflow file(s)")
        for name in changed:
            print(f"  - {name}")
        return

    if changed:
        for name in changed:
            print(f"needs Product Alpha scope: {name}")
        raise SystemExit(1)

    print(json.dumps(validate_policy(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
