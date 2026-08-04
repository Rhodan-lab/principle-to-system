#!/usr/bin/env python3
"""Verify a Product Alpha cohort against one recorded pilot build ID."""

from __future__ import annotations

import argparse
import errno
import json
import os
import stat
from pathlib import Path
from typing import Sequence

import summarize as pilot_summary


def validate_expected_build_id(value: str) -> str:
    """Return a valid lowercase SHA-256 build ID or raise ValueError."""
    if not pilot_summary.BUILD_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "expected pilot build ID must be a 64-character lowercase SHA-256"
        )
    return value


def verify_cohort_bytes(
    raw_input: bytes,
    expected_build_id: str,
) -> dict[str, object]:
    """Summarize and bind one exact cohort byte snapshot to a launcher build."""
    expected = validate_expected_build_id(expected_build_id)
    summary = pilot_summary.summarize(pilot_summary.load_sessions_bytes(raw_input))
    actual = summary["pilot_build_id"]
    if actual != expected:
        raise ValueError(
            "cohort pilot_build_id does not match the expected launcher build: "
            f"expected {expected}, found {actual}"
        )
    return summary


def read_cohort_input(input_path: Path) -> bytes:
    """Open and read one bounded regular-file cohort snapshot without following links."""
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    elif input_path.is_symlink():
        raise ValueError("cohort input must be a regular file")

    try:
        descriptor = os.open(input_path, flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError("cohort input must be a regular file") from exc
        raise

    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError("cohort input must be a regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read(pilot_summary.MAX_INPUT_BYTES + 1)
    finally:
        os.close(descriptor)

    if len(raw) > pilot_summary.MAX_INPUT_BYTES:
        raise ValueError(
            "input exceeds the "
            f"{pilot_summary.MAX_INPUT_BYTES}-byte Product Alpha session limit"
        )
    return raw


def verify_cohort(
    input_path: Path,
    expected_build_id: str,
) -> dict[str, object]:
    """Load one bounded snapshot and bind it to the recorded launcher build."""
    raw_input = read_cohort_input(input_path)
    return verify_cohort_bytes(raw_input, expected_build_id)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="combined JSONL pilot session file",
    )
    parser.add_argument(
        "--expect-build-id",
        required=True,
        help="full 64-character Pilot build ID printed by run_pilot.py",
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        summary = verify_cohort(args.input, args.expect_build_id)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"cohort verification failed: {exc}") from exc

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(pilot_summary.render_markdown(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
