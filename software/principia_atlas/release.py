#!/usr/bin/env python3
"""Build, verify, and inspect versioned Principia & Atlas release archives."""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import stat
import tempfile
import uuid
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Mapping, Sequence

try:
    from software.principia_atlas import orchestrate
except ModuleNotFoundError:
    import sys

    REPO_BOOTSTRAP = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO_BOOTSTRAP))
    from software.principia_atlas import orchestrate

CONTRACT = "principia-atlas-release/0.1"
PRODUCT = "Principia & Atlas"
DEFAULT_VERSION = "0.1.0-alpha.1"
MANIFEST_NAME = "RELEASE-MANIFEST.json"
CHECKSUM_SUFFIX = ".sha256"
MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_FILES = 4096
MAX_MANIFEST_BYTES = 1024 * 1024
VERSION = re.compile(
    r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
SHA256 = re.compile(r"^[0-9a-f]{64}$")
FIXED_ZIP_TIME = (1980, 1, 1, 0, 0, 0)

PRINCIPIA_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATLAS_REPO = PRINCIPIA_ROOT.parent / "Atlas"
DEFAULT_RELEASE_DIR = PRINCIPIA_ROOT.parent
RUNTIME_PATH = Path(__file__).with_name("release_runtime.py")


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def decode_json(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict_object,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value: {token}")
            ),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def validate_version(version: str) -> str:
    if not VERSION.fullmatch(version):
        raise ValueError("release version must be valid SemVer")
    return version


def release_root(version: str) -> str:
    return f"principia-atlas-{validate_version(version)}"


def checksum_path(archive: Path) -> Path:
    return archive.with_name(archive.name + CHECKSUM_SUFFIX)


def default_archive(version: str) -> Path:
    return DEFAULT_RELEASE_DIR / f"{release_root(version)}.zip"


def _safe_relative(path: str) -> PurePosixPath:
    if not path or "\\" in path or path.startswith("/"):
        raise ValueError(f"unsafe release path: {path!r}")
    candidate = PurePosixPath(path)
    if any(part in {"", ".", ".."} for part in candidate.parts):
        raise ValueError(f"unsafe release path: {path!r}")
    if candidate.as_posix() != path:
        raise ValueError(f"non-canonical release path: {path!r}")
    return candidate


def _read_regular(path: Path, label: str, limit: int) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    size = path.stat().st_size
    if size > limit:
        raise ValueError(f"{label} exceeds {limit} bytes")
    raw = path.read_bytes()
    if len(raw) != size:
        raise ValueError(f"{label} changed while reading")
    return raw


def snapshot_tree(root: Path, prefix: str) -> dict[str, bytes]:
    source = _absolute(root)
    if source.is_symlink() or not source.is_dir():
        raise ValueError("release product must be a regular directory")
    files: dict[str, bytes] = {}
    total = 0
    for path in sorted(source.rglob("*")):
        if path.is_symlink():
            raise ValueError(f"release product contains a symlink: {path}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"release product contains a non-regular entry: {path}")
        relative = path.relative_to(source).as_posix()
        key = f"{prefix}/{relative}"
        _safe_relative(key)
        raw = _read_regular(path, key, MAX_FILE_BYTES)
        total += len(raw)
        if len(files) + 1 > MAX_FILES or total > MAX_TOTAL_BYTES:
            raise ValueError("release product exceeds archive resource limits")
        files[key] = raw
    if not files:
        raise ValueError("release product must not be empty")
    return files


def launch_sh() -> bytes:
    return b'''#!/bin/sh
set -eu
SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
PYTHON=${PYTHON:-python3}
exec "$PYTHON" "$SCRIPT_DIR/launcher.py" run "$@"
'''


def launch_command() -> bytes:
    return launch_sh()


def launch_cmd() -> bytes:
    return b'''@echo off\r\nsetlocal\r\nwhere py >nul 2>nul\r\nif errorlevel 1 goto python\r\npy -3 "%~dp0launcher.py" run %*\r\nexit /b %errorlevel%\r\n:python\r\npython "%~dp0launcher.py" run %*\r\n'''


def release_readme(version: str) -> bytes:
    text = f"""Principia & Atlas {version}\n\nThis is a local-only, versioned release package.\n\nVerify after extraction:\n  python3 launcher.py verify\n\nRun on Linux/macOS:\n  ./launch.sh\n\nRun on macOS by double-clicking:\n  launch.command\n\nRun on Windows:\n  launch.cmd\n\nThe server binds only to 127.0.0.1. No account, cloud storage, or external network is required.\nPrincipia learning authority and Atlas knowledge-status authority remain separate.\n"""
    return text.encode("utf-8")


def _generated_payload(version: str) -> dict[str, bytes]:
    return {
        "README.txt": release_readme(version),
        "launcher.py": _read_regular(RUNTIME_PATH, "release runtime", MAX_FILE_BYTES),
        "launch.sh": launch_sh(),
        "launch.command": launch_command(),
        "launch.cmd": launch_cmd(),
    }


def make_manifest(
    *,
    version: str,
    product_manifest: Mapping[str, Any],
    receipt: Mapping[str, object],
    payload: Mapping[str, bytes],
) -> dict[str, object]:
    files = {
        path: {"sha256": sha256(raw), "size": len(raw)}
        for path, raw in sorted(payload.items())
    }
    unsigned: dict[str, object] = {
        "contract": CONTRACT,
        "product": PRODUCT,
        "version": validate_version(version),
        "bundle_id": product_manifest["bundle_id"],
        "receipt_id": receipt["receipt_id"],
        "route_id": product_manifest["principia"]["route_id"],
        "entrypoints": {
            "verify": "launcher.py verify",
            "run": "launcher.py run",
            "linux_macos": "launch.sh",
            "macos_double_click": "launch.command",
            "windows": "launch.cmd",
        },
        "runtime": {
            "host": "127.0.0.1",
            "external_network_required": False,
            "python": ">=3.10",
        },
        "boundaries": {
            "authorities_separate": True,
            "status_inheritance": "prohibited",
            "live_cross_repository_dependency": False,
            "canonical_mutation": False,
        },
        "payload": {
            "file_count": len(files),
            "total_bytes": sum(item["size"] for item in files.values()),
            "files": files,
        },
    }
    manifest = dict(unsigned)
    manifest["release_id"] = sha256(canonical_json(unsigned))
    return manifest


def _zip_info(path: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(path, FIXED_ZIP_TIME)
    info.create_system = 3
    info.compress_type = zipfile.ZIP_STORED
    info.flag_bits = 0x800
    executable = path.endswith(("/launcher.py", "/launch.sh", "/launch.command"))
    permissions = 0o755 if executable else 0o644
    info.external_attr = (stat.S_IFREG | permissions) << 16
    return info


def archive_bytes(
    version: str,
    payload: Mapping[str, bytes],
    manifest: Mapping[str, object],
) -> bytes:
    root = release_root(version)
    entries = dict(payload)
    entries[MANIFEST_NAME] = canonical_json(manifest)
    output = io.BytesIO()
    with zipfile.ZipFile(
        output,
        "w",
        compression=zipfile.ZIP_STORED,
        allowZip64=False,
    ) as archive:
        for relative, raw in sorted(entries.items()):
            _safe_relative(relative)
            archive.writestr(_zip_info(f"{root}/{relative}"), raw)
    raw = output.getvalue()
    if len(raw) > MAX_ARCHIVE_BYTES:
        raise ValueError("release archive exceeds resource limit")
    return raw


def _write_temp(path: Path, raw: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(
        prefix=f".{path.name}.",
        suffix=".tmp",
        dir=path.parent,
    )
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
    except BaseException:
        temporary.unlink(missing_ok=True)
        raise
    return temporary


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def _publish_release(archive: Path, raw: bytes) -> None:
    target = _absolute(archive)
    checksum = checksum_path(target)
    if target.is_symlink() or checksum.is_symlink():
        raise ValueError("release archive and checksum must not be symlinks")
    archive_exists = target.exists()
    checksum_exists = checksum.exists()
    if archive_exists != checksum_exists:
        raise ValueError("existing release archive and checksum must be a complete pair")
    if archive_exists and not target.is_file():
        raise ValueError("release archive must be a regular file")
    if checksum_exists and not checksum.is_file():
        raise ValueError("release checksum must be a regular file")
    checksum_raw = f"{sha256(raw)}  {target.name}\n".encode("ascii")
    archive_temp = _write_temp(target, raw)
    checksum_temp = _write_temp(checksum, checksum_raw)
    token = uuid.uuid4().hex
    archive_backup = target.parent / f".{target.name}.backup-{token}"
    checksum_backup = checksum.parent / f".{checksum.name}.backup-{token}"
    if archive_exists:
        target.replace(archive_backup)
        try:
            checksum.replace(checksum_backup)
        except BaseException:
            archive_backup.replace(target)
            _remove(archive_temp)
            _remove(checksum_temp)
            raise
    try:
        archive_temp.replace(target)
        checksum_temp.replace(checksum)
        verify_archive(target)
    except BaseException:
        _remove(target)
        _remove(checksum)
        if archive_exists:
            archive_backup.replace(target)
            checksum_backup.replace(checksum)
        _remove(archive_temp)
        _remove(checksum_temp)
        raise
    else:
        _remove(archive_backup)
        _remove(checksum_backup)


def _archive_for_product(
    product: Path,
    version: str,
) -> tuple[bytes, dict[str, object]]:
    product_path = _absolute(product)
    product_manifest, receipt = orchestrate.verify_product(product_path)
    payload = snapshot_tree(product_path, "product")
    receipt_file = orchestrate.receipt_path(product_path)
    payload["product.build-receipt.json"] = _read_regular(
        receipt_file,
        "product build receipt",
        orchestrate.MAX_RECEIPT_BYTES,
    )
    payload.update(_generated_payload(version))
    manifest = make_manifest(
        version=version,
        product_manifest=product_manifest,
        receipt=receipt,
        payload=payload,
    )
    return archive_bytes(version, payload, manifest), manifest


def pack_product(
    *,
    product: Path,
    version: str,
    output: Path,
) -> dict[str, object]:
    target = _absolute(output)
    product_path = _absolute(product)
    if (
        target == product_path
        or product_path in target.parents
        or target in product_path.parents
    ):
        raise ValueError("release archive must remain outside the product directory")
    with orchestrate.build_lock(target):
        raw, manifest = _archive_for_product(
            product_path,
            validate_version(version),
        )
        _publish_release(target, raw)
    return manifest


def _checksum(archive: Path) -> str:
    target = _absolute(archive)
    raw = _read_regular(target, "release archive", MAX_ARCHIVE_BYTES)
    sidecar = _read_regular(checksum_path(target), "release checksum", 4096)
    try:
        text = sidecar.decode("ascii")
    except UnicodeDecodeError as exc:
        raise ValueError("release checksum must be ASCII") from exc
    expected_line = f"{sha256(raw)}  {target.name}\n"
    if text != expected_line:
        raise ValueError("release checksum does not match the archive")
    return sha256(raw)


def _read_archive(
    archive: Path,
) -> tuple[str, dict[str, bytes], dict[str, object]]:
    target = _absolute(archive)
    _checksum(target)
    entries: dict[str, bytes] = {}
    roots: set[str] = set()
    total = 0
    with zipfile.ZipFile(target, "r") as source:
        infos = source.infolist()
        if len(infos) > MAX_FILES + 1:
            raise ValueError("release archive contains too many files")
        for info in infos:
            if info.is_dir():
                raise ValueError("release archive must not contain directory entries")
            if info.flag_bits & 0x1:
                raise ValueError("encrypted release entries are not supported")
            if info.compress_type != zipfile.ZIP_STORED:
                raise ValueError("release archive uses unsupported compression")
            mode = (info.external_attr >> 16) & 0o170000
            if mode == stat.S_IFLNK:
                raise ValueError("release archive contains a symlink")
            name = info.filename
            if "\\" in name or name.startswith("/"):
                raise ValueError("release archive contains an unsafe path")
            parts = PurePosixPath(name).parts
            if len(parts) < 2 or any(part in {"", ".", ".."} for part in parts):
                raise ValueError("release archive contains an unsafe path")
            roots.add(parts[0])
            relative = PurePosixPath(*parts[1:]).as_posix()
            _safe_relative(relative)
            if relative in entries:
                raise ValueError("release archive contains duplicate paths")
            if info.file_size > MAX_FILE_BYTES:
                raise ValueError("release archive entry exceeds resource limit")
            raw = source.read(info)
            if len(raw) != info.file_size:
                raise ValueError("release archive entry changed while reading")
            total += len(raw)
            if total > MAX_TOTAL_BYTES:
                raise ValueError("release archive exceeds expanded resource limit")
            entries[relative] = raw
    if len(roots) != 1:
        raise ValueError("release archive must contain exactly one root directory")
    root = next(iter(roots))
    manifest_raw = entries.pop(MANIFEST_NAME, None)
    if manifest_raw is None or len(manifest_raw) > MAX_MANIFEST_BYTES:
        raise ValueError("release manifest is missing or too large")
    manifest = decode_json(manifest_raw, "release manifest")
    version = manifest.get("version")
    if not isinstance(version, str) or root != release_root(version):
        raise ValueError("release root does not match its version")
    return root, entries, manifest


def verify_archive(archive: Path) -> dict[str, object]:
    root, entries, manifest = _read_archive(archive)
    if manifest.get("contract") != CONTRACT or manifest.get("product") != PRODUCT:
        raise ValueError("release manifest contract is invalid")
    release_id = manifest.get("release_id")
    unsigned = dict(manifest)
    unsigned.pop("release_id", None)
    if (
        not isinstance(release_id, str)
        or not SHA256.fullmatch(release_id)
        or sha256(canonical_json(unsigned)) != release_id
    ):
        raise ValueError("release manifest seal is invalid")
    payload = manifest.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), dict):
        raise ValueError("release payload manifest is invalid")
    expected = payload["files"]
    actual = {
        path: {"sha256": sha256(raw), "size": len(raw)}
        for path, raw in sorted(entries.items())
    }
    if actual != expected:
        raise ValueError("release payload does not match its manifest")
    if payload.get("file_count") != len(actual) or payload.get("total_bytes") != sum(
        item["size"] for item in actual.values()
    ):
        raise ValueError("release payload counters are invalid")
    required = {
        "README.txt",
        "launcher.py",
        "launch.sh",
        "launch.command",
        "launch.cmd",
        "product.build-receipt.json",
        "product/index.html",
    }
    if not required.issubset(entries):
        raise ValueError("release entrypoints are incomplete")
    with tempfile.TemporaryDirectory() as temporary:
        extracted = Path(temporary) / root
        for relative, raw in entries.items():
            destination = extracted.joinpath(*PurePosixPath(relative).parts)
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(raw)
        product_manifest, receipt = orchestrate.verify_product(
            extracted / "product"
        )
    if (
        manifest.get("bundle_id") != product_manifest["bundle_id"]
        or manifest.get("receipt_id") != receipt["receipt_id"]
        or manifest.get("route_id")
        != product_manifest["principia"]["route_id"]
    ):
        raise ValueError("release identity does not match the bundled product")
    return manifest


def check_archive_determinism(*, product: Path, version: str) -> str:
    first, first_manifest = _archive_for_product(
        product,
        validate_version(version),
    )
    second, second_manifest = _archive_for_product(
        product,
        validate_version(version),
    )
    if first != second or first_manifest != second_manifest:
        raise ValueError("release archive build is not deterministic")
    return str(first_manifest["release_id"])


def build_release(
    *,
    principia_root: Path,
    atlas_repo: Path,
    route: str,
    version: str,
    output: Path,
    product_output: Path | None,
    allow_dirty: bool = False,
    expected_principia_commit: str | None = None,
    expected_atlas_commit: str | None = None,
) -> dict[str, object]:
    validate_version(version)
    roots = orchestrate._source_roots(principia_root, atlas_repo)
    target = _absolute(output)
    for root in roots:
        if orchestrate._contains(root, target) or orchestrate._contains(target, root):
            raise ValueError("release output must remain outside source checkouts")
    if product_output is not None:
        product = _absolute(product_output)
        orchestrate.build_product(
            principia_root=principia_root,
            atlas_repo=atlas_repo,
            route=route,
            output=product,
            allow_dirty=allow_dirty,
            expected_principia_commit=expected_principia_commit,
            expected_atlas_commit=expected_atlas_commit,
        )
        return pack_product(product=product, version=version, output=target)
    with tempfile.TemporaryDirectory() as temporary:
        product = Path(temporary) / "product"
        orchestrate.build_product(
            principia_root=principia_root,
            atlas_repo=atlas_repo,
            route=route,
            output=product,
            allow_dirty=allow_dirty,
            expected_principia_commit=expected_principia_commit,
            expected_atlas_commit=expected_atlas_commit,
        )
        return pack_product(product=product, version=version, output=target)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser(
        "build",
        help="build product and versioned release archive",
    )
    build.add_argument("--principia-root", type=Path, default=PRINCIPIA_ROOT)
    build.add_argument("--atlas-repo", type=Path, default=DEFAULT_ATLAS_REPO)
    build.add_argument("--route", default=orchestrate.principia_build.DEFAULT_ROUTE)
    build.add_argument("--version", default=DEFAULT_VERSION)
    build.add_argument("--output", type=Path)
    build.add_argument("--product-output", type=Path)
    build.add_argument("--expected-principia-commit")
    build.add_argument("--expected-atlas-commit")
    build.add_argument("--allow-dirty", action="store_true")

    pack = subparsers.add_parser(
        "pack",
        help="package an existing verified product",
    )
    pack.add_argument("--product", type=Path, required=True)
    pack.add_argument("--version", default=DEFAULT_VERSION)
    pack.add_argument("--output", type=Path)

    check = subparsers.add_parser(
        "check",
        help="verify deterministic archive bytes",
    )
    check.add_argument("--product", type=Path, required=True)
    check.add_argument("--version", default=DEFAULT_VERSION)

    verify = subparsers.add_parser(
        "verify",
        help="verify archive checksum, manifest, and product",
    )
    verify.add_argument("--output", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "verify":
        manifest = verify_archive(args.output)
        print(
            f"Verified Principia & Atlas release {manifest['version']} "
            f"({manifest['release_id']})"
        )
        return 0
    if args.command == "check":
        release_id = check_archive_determinism(
            product=args.product,
            version=args.version,
        )
        print(f"Principia & Atlas release archive is deterministic: {release_id}")
        return 0
    output = args.output or default_archive(args.version)
    if args.command == "pack":
        manifest = pack_product(
            product=args.product,
            version=args.version,
            output=output,
        )
    else:
        manifest = build_release(
            principia_root=args.principia_root,
            atlas_repo=args.atlas_repo,
            route=args.route,
            version=args.version,
            output=output,
            product_output=args.product_output,
            allow_dirty=args.allow_dirty,
            expected_principia_commit=args.expected_principia_commit,
            expected_atlas_commit=args.expected_atlas_commit,
        )
    print(
        f"Built Principia & Atlas release {manifest['version']} -> "
        f"{_absolute(output)}"
    )
    print(f"Release checksum: {checksum_path(_absolute(output))}")
    print(f"Release ID: {manifest['release_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
