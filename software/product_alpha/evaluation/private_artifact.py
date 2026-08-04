#!/usr/bin/env python3
"""Read bounded private Product Alpha artifacts without following filesystem links."""

from __future__ import annotations

import errno
import os
import stat
from pathlib import Path

MAX_PRIVATE_ARTIFACT_BYTES = 16 * 1024 * 1024


def read_regular_bytes(
    path: Path,
    label: str,
    *,
    maximum_bytes: int = MAX_PRIVATE_ARTIFACT_BYTES,
) -> bytes:
    """Read one bounded regular-file snapshot without following symlinks."""
    if maximum_bytes < 0:
        raise ValueError("private artifact byte limit must be non-negative")

    flags = (
        os.O_RDONLY
        | getattr(os, "O_BINARY", 0)
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    elif path.is_symlink():
        raise ValueError(f"{label} must be a regular file")

    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        if exc.errno == errno.ELOOP:
            raise ValueError(f"{label} must be a regular file") from exc
        raise

    try:
        if not stat.S_ISREG(os.fstat(descriptor).st_mode):
            raise ValueError(f"{label} must be a regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read(maximum_bytes + 1)
    finally:
        os.close(descriptor)

    if len(raw) > maximum_bytes:
        raise ValueError(
            f"{label} exceeds the {maximum_bytes}-byte Product Alpha private artifact limit"
        )
    return raw
