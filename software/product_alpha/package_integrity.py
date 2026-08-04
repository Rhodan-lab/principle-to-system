#!/usr/bin/env python3
"""Verify one exact Product Alpha build package against its manifest."""

from __future__ import annotations

import errno
import hashlib
import json
import os
import re
import stat
from pathlib import Path, PurePosixPath
from typing import Any

BUILD_MANIFEST = "build-manifest.json"
BUILD_CONTRACT = "principia-product-alpha-build/0.1"
SUPPORTED_ROUTES = ("refrigerator", "distributed-information")
REQUIRED_STATIC_FILES = (
    "index.html",
    "model-adapters.js",
    "facilitator.html",
    "pilot-lab.html",
    "evaluation/rubric.json",
    "evaluation/session-template.json",
)
SHA256_PATTERN = re.compile(r"^[0-9a-f]{64}$")
MAX_MANIFEST_BYTES = 1024 * 1024
MAX_ASSET_BYTES = 16 * 1024 * 1024


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key!r}")
        result[key] = value
    return result


def _reject_nonfinite_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant is not allowed: {value}")


def _read_regular_bytes(path: Path, label: str, maximum_bytes: int) -> bytes:
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
        raise ValueError(f"{label} exceeds the {maximum_bytes}-byte build package limit")
    return raw


def _decode_manifest(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_object_without_duplicates,
            parse_constant=_reject_nonfinite_constant,
        )
    except UnicodeDecodeError as exc:
        raise ValueError("Product Alpha build manifest is not valid UTF-8 JSON") from exc
    except json.JSONDecodeError as exc:
        raise ValueError("Product Alpha build manifest is not valid UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("Product Alpha build manifest must be a JSON object")
    return value


def _manifest_path(value: object) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError("Product Alpha build manifest file path is invalid")
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or value != path.as_posix()
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in value
        or value == BUILD_MANIFEST
    ):
        raise ValueError(f"Product Alpha build manifest file path is unsafe: {value!r}")
    return value


def _declared_files(manifest: dict[str, Any]) -> dict[str, str]:
    files = manifest.get("files")
    if not isinstance(files, list) or manifest.get("file_count") != len(files):
        raise ValueError("Product Alpha build manifest file_count is inconsistent")

    declared: dict[str, str] = {}
    for entry in files:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise ValueError("Product Alpha build manifest file entry is invalid")
        relative = _manifest_path(entry.get("path"))
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
            raise ValueError(
                f"Product Alpha build manifest SHA-256 is invalid for {relative!r}"
            )
        if relative in declared:
            raise ValueError(
                f"Product Alpha build manifest repeats file path: {relative!r}"
            )
        declared[relative] = digest
    return declared


def _actual_files(output: Path) -> set[str]:
    if output.is_symlink() or not output.is_dir():
        raise ValueError("Product Alpha build output must be a regular directory")

    actual: set[str] = set()
    for path in output.rglob("*"):
        relative = path.relative_to(output).as_posix()
        if path.is_symlink():
            raise ValueError(
                f"Product Alpha build package entry must not be a symlink: {relative}"
            )
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(
                f"Product Alpha build package entry must be a regular file: {relative}"
            )
        actual.add(relative)
    return actual


def verify_build_package(output: Path) -> tuple[dict[str, Any], bytes]:
    """Verify the exact package file set and every manifest-bound asset hash."""
    manifest_path = output / BUILD_MANIFEST
    try:
        raw = _read_regular_bytes(
            manifest_path,
            "Product Alpha build manifest",
            MAX_MANIFEST_BYTES,
        )
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"Product Alpha build is missing {BUILD_MANIFEST}"
        ) from exc
    manifest = _decode_manifest(raw)
    if set(manifest) != {
        "contract",
        "route_id",
        "file_count",
        "files",
        "deterministic",
    }:
        raise ValueError("Product Alpha build manifest fields are invalid")
    if manifest.get("contract") != BUILD_CONTRACT:
        raise ValueError("Product Alpha build manifest contract is invalid")
    if manifest.get("deterministic") is not True:
        raise ValueError("Product Alpha build manifest must declare deterministic=true")
    route = manifest.get("route_id")
    if route not in SUPPORTED_ROUTES:
        raise ValueError("Product Alpha build manifest route_id is invalid")

    declared = _declared_files(manifest)
    required = set(REQUIRED_STATIC_FILES) | {f"data/{route}.json"}
    missing_required = sorted(required - declared.keys())
    if missing_required:
        raise ValueError(
            "Product Alpha build manifest is missing required package files: "
            + ", ".join(missing_required)
        )

    expected_actual = set(declared) | {BUILD_MANIFEST}
    actual = _actual_files(output)
    if actual != expected_actual:
        missing = sorted(expected_actual - actual)
        extra = sorted(actual - expected_actual)
        details: list[str] = []
        if missing:
            details.append("missing=" + ",".join(missing))
        if extra:
            details.append("undeclared=" + ",".join(extra))
        raise ValueError(
            "Product Alpha build package file set does not match the manifest: "
            + "; ".join(details)
        )

    for relative, expected_digest in declared.items():
        data = _read_regular_bytes(
            output.joinpath(*PurePosixPath(relative).parts),
            f"Product Alpha build asset {relative}",
            MAX_ASSET_BYTES,
        )
        actual_digest = hashlib.sha256(data).hexdigest()
        if actual_digest != expected_digest:
            raise ValueError(
                f"Product Alpha build asset SHA-256 does not match manifest: {relative}"
            )
    return manifest, raw


def pilot_build_identity(output: Path) -> str:
    """Return the manifest identity only after verifying the exact build package."""
    _, raw = verify_build_package(output)
    return hashlib.sha256(raw).hexdigest()
