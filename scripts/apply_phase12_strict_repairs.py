#!/usr/bin/env python3
"""Apply or check deterministic repairs required by the Phase 12 strict gate."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VALIDATOR = ROOT / "scripts" / "validate_repo.py"
MODULE09 = (
    ROOT / "science" / "09-motion-forces" / "overview.md",
    ROOT / "science" / "09-motion-forces" / "technology.md",
    ROOT / "science" / "09-motion-forces" / "explore.md",
)

SKIP_OLD = '''    "CONTRIBUTING.md",
    "source-ledger.md",
}'''
SKIP_NEW = '''    "CONTRIBUTING.md",
    "AUDIT.md",
    "source-ledger.md",
    "experience-source-ledger.md",
}'''

DIR_OLD = '''        if path.name in SKIP_FRONTMATTER_FILES or rel.parts[0] in {
            ".github",
            "scripts",
        }:'''
DIR_NEW = '''        if path.name in SKIP_FRONTMATTER_FILES or rel.parts[0] in {
            ".github",
            "scripts",
            "reports",
        }:'''

CHAIN_OLD = '''        if (
            filename == "technology.md"
            and "->" not in document.content
            and "→" not in document.content
        ):'''
CHAIN_NEW = '''        if (
            filename == "technology.md"
            and "->" not in document.content
            and "→" not in document.content
            and "principle-to-system chain" not in document.content.lower()
        ):'''


def normalize_validator(text: str) -> str:
    fixed = text
    if SKIP_NEW not in fixed:
        fixed = fixed.replace(SKIP_OLD, SKIP_NEW)
    if DIR_NEW not in fixed:
        fixed = fixed.replace(DIR_OLD, DIR_NEW)
    if CHAIN_NEW not in fixed:
        fixed = fixed.replace(CHAIN_OLD, CHAIN_NEW)
    return fixed


def split_frontmatter(text: str, path: Path) -> tuple[str, str]:
    if not text.startswith("---\n"):
        raise ValueError(f"{path.relative_to(ROOT)}: missing frontmatter")
    closing = text.find("\n---\n", 4)
    if closing < 0:
        raise ValueError(f"{path.relative_to(ROOT)}: unterminated frontmatter")
    return text[: closing + 5], text[closing + 5 :]


def frontmatter_title(frontmatter: str, path: Path) -> str:
    match = re.search(r'^title:\s*["\']?(.+?)["\']?\s*$', frontmatter, re.M)
    if not match:
        raise ValueError(f"{path.relative_to(ROOT)}: missing title")
    return match.group(1).strip().strip('"\'')


def normalize_module09(text: str, path: Path) -> str:
    frontmatter, body = split_frontmatter(text, path)
    title = frontmatter_title(frontmatter, path)
    body = body.lstrip("\n")

    # Preserve exactly one document title, then use H2 for numbered standard sections.
    if not body.startswith(f"# {title}\n"):
        if re.match(r"^#\s+\d+\.\s+", body):
            body = f"# {title}\n\n{body}"
        else:
            raise ValueError(
                f"{path.relative_to(ROOT)}: unexpected Module 09 heading structure"
            )
    body = re.sub(r"^#\s+(?=\d+\.\s+)", "## ", body, flags=re.M)
    return frontmatter + "\n" + body.rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changed: list[Path] = []

    targets: list[tuple[Path, str, str]] = []
    try:
        original = VALIDATOR.read_text(encoding="utf-8")
        fixed = normalize_validator(original)
        targets.append((VALIDATOR, original, fixed))
        if SKIP_NEW not in fixed:
            errors.append("validate_repo.py does not exclude governance filenames")
        if DIR_NEW not in fixed:
            errors.append("validate_repo.py does not exclude reports from learner frontmatter")
        if CHAIN_NEW not in fixed:
            errors.append("validate_repo.py does not recognize labelled principle-to-system chains")
        compile(fixed, str(VALIDATOR), "exec")
    except (OSError, SyntaxError, ValueError) as exc:
        errors.append(str(exc))

    for path in MODULE09:
        try:
            original = path.read_text(encoding="utf-8")
            fixed = normalize_module09(original, path)
            targets.append((path, original, fixed))
            _, body = split_frontmatter(fixed, path)
            title = frontmatter_title(fixed, path)
            if not body.lstrip().startswith(f"# {title}\n"):
                errors.append(f"{path.relative_to(ROOT)}: missing canonical H1")
            if re.search(r"^#\s+\d+\.\s+", body, re.M):
                errors.append(f"{path.relative_to(ROOT)}: numbered H1 remains")
        except (OSError, ValueError) as exc:
            errors.append(str(exc))

    if errors:
        print("Phase 12 strict-repair errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    for path, original, fixed in targets:
        if fixed == original:
            continue
        changed.append(path)
        if args.write:
            path.write_text(fixed, encoding="utf-8")

    if args.check and changed:
        print("Phase 12 strict repairs are not applied:", file=sys.stderr)
        for path in changed:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if changed:
        print("Phase 12 strict repairs applied:")
        for path in changed:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 12 strict repairs already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
