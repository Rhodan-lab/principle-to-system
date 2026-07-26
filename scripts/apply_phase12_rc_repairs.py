#!/usr/bin/env python3
"""Apply or check final Phase 12 RC accessibility and semantic repairs."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_phase12_release_candidate.py"
TARGET_MODULES = (
    ("science", "06-matter-quantum"),
    ("science", "11-waves-signals"),
    ("science", "13-cells-bioenergetics"),
    ("science", "14-dna-evolution"),
    ("technology", "18-semiconductors-electronics"),
)
FILENAMES = ("overview.md", "technology.md", "explore.md")

BATTERY_OLD = '    "battery-energy-balance": ("\\\\eta_c", "P_c"),'
BATTERY_NEW = '    "battery-energy-balance": ("\\\\eta_c", "\\\\eta_d"),'

TERMS_OLD = '''    scan = "\\n".join(path.read_text(encoding="utf-8") for path in documents if path.is_file()).lower()
    for phrase in shortcuts:
        if isinstance(phrase, str) and phrase.lower() in scan:
            result.error(f"repository content contains forbidden semantic shortcut: {phrase}")'''

TERMS_NEW = '''    negation_markers = (
        "does not",
        "do not",
        "must not",
        "cannot",
        "not establish",
        "not imply",
        "not automatically",
        "misconception",
        "myth",
        "forbidden",
    )
    for path in documents:
        if not path.is_file():
            continue
        scan = path.read_text(encoding="utf-8").lower()
        for phrase in shortcuts:
            if not isinstance(phrase, str):
                continue
            target = phrase.lower()
            start = 0
            while True:
                position = scan.find(target, start)
                if position < 0:
                    break
                context = scan[max(0, position - 120) : position + len(target) + 220]
                if not any(marker in context for marker in negation_markers):
                    result.error(
                        f"{path.relative_to(ROOT)}: contains affirmative forbidden semantic shortcut: {phrase}"
                    )
                start = position + len(target)'''


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError(f"{path.relative_to(ROOT)}: unterminated frontmatter")
    return text[: closing + 5], text[closing + 5 :]


def extract_title(frontmatter: str, path: Path) -> str:
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.M)
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)}: missing title")
    return match.group(1).strip().strip('"\'')


def normalize_document(text: str, path: Path) -> str:
    frontmatter, body = split_frontmatter(text, path)
    title = extract_title(frontmatter, path)
    body = body.lstrip("\n")
    h1_matches = re.findall(r"^#\s+(.+?)\s*$", body, re.M)
    if not h1_matches:
        body = f"# {title}\n\n{body}"
    elif len(h1_matches) == 1 and h1_matches[0].strip() == title:
        pass
    else:
        raise ValueError(
            f"{path.relative_to(ROOT)}: unexpected H1 structure {h1_matches!r}"
        )
    return frontmatter + "\n" + body.rstrip() + "\n"


def normalize_validator(text: str) -> str:
    fixed = text
    if BATTERY_NEW not in fixed:
        fixed = fixed.replace(BATTERY_OLD, BATTERY_NEW)
    if TERMS_NEW not in fixed:
        fixed = fixed.replace(TERMS_OLD, TERMS_NEW)
    return fixed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []

    try:
        original = VALIDATOR.read_text(encoding="utf-8")
        fixed = normalize_validator(original)
        compile(fixed, str(VALIDATOR), "exec")
        if BATTERY_NEW not in fixed:
            errors.append("Phase 12 validator does not use shared battery efficiency markers")
        if TERMS_NEW not in fixed:
            errors.append("Phase 12 validator does not use context-aware terminology scanning")
        if fixed != original:
            changes.append((VALIDATOR, fixed))
    except (OSError, SyntaxError) as exc:
        errors.append(str(exc))

    for family, module in TARGET_MODULES:
        for filename in FILENAMES:
            path = ROOT / family / module / filename
            try:
                original = path.read_text(encoding="utf-8")
                fixed = normalize_document(original, path)
                _, body = split_frontmatter(fixed, path)
                h1_matches = re.findall(r"^#\s+(.+?)\s*$", body, re.M)
                if len(h1_matches) != 1:
                    errors.append(
                        f"{path.relative_to(ROOT)}: expected one H1, found {len(h1_matches)}"
                    )
                if fixed != original:
                    changes.append((path, fixed))
            except (OSError, ValueError) as exc:
                errors.append(str(exc))

    if errors:
        print("Phase 12 RC-repair errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.check and changes:
        print("Phase 12 RC repairs are not applied:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if args.write:
        for path, fixed in changes:
            path.write_text(fixed, encoding="utf-8")

    if changes:
        print("Phase 12 RC repairs applied:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 12 RC repairs already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
