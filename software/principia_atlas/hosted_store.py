#!/usr/bin/env python3
"""Materialize verified Principia & Atlas releases into an immutable hosted store."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import tempfile
import uuid
from pathlib import Path, PurePosixPath
from typing import Mapping, Sequence

try:
    from software.principia_atlas import (
        hosted_catalog,
        orchestrate,
        promotion_policy as policy,
        release,
    )
except ModuleNotFoundError:
    import sys

    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from software.principia_atlas import (
        hosted_catalog,
        orchestrate,
        promotion_policy as policy,
        release,
    )

CONTRACT = "principia-atlas-hosted-store/0.1"
PRODUCT = "Principia & Atlas"
MANIFEST_NAME = "HOSTED-STORE-MANIFEST.json"
OBJECTS_DIR = "objects"
MAX_MANIFEST_BYTES = 8 * 1024 * 1024
MAX_FILES = 4096
MAX_FILE_BYTES = release.MAX_FILE_BYTES
MAX_TOTAL_BYTES = release.MAX_TOTAL_BYTES
SHA256 = policy.SHA256
BOUNDARIES = {
    "archive_parsing_in_web_runtime": False,
    "archives_verified_before_materialization": True,
    "content_addressed": True,
    "read_only_runtime": True,
    "symlinks": False,
    "tenant_authorization_required": True,
}


def canonical_json(value: object) -> bytes:
    return policy.canonical_json(value)


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _strict(pairs: list[tuple[str, object]]) -> dict[str, object]:
    output: dict[str, object] = {}
    for key, value in pairs:
        if key in output:
            raise ValueError(f"duplicate JSON key: {key}")
        output[key] = value
    return output


def decode(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_strict,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def _read_regular(path: Path, label: str, limit: int) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_BINARY", 0) | getattr(os, "O_CLOEXEC", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if nofollow:
        flags |= nofollow
    elif path.is_symlink():
        raise ValueError(f"{label} must be a regular file")
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ValueError(f"{label} must be a regular file") from exc
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > limit:
            raise ValueError(f"{label} must be a bounded regular file")
        with os.fdopen(descriptor, "rb", closefd=False) as stream:
            raw = stream.read(limit + 1)
        after = os.fstat(descriptor)
        if len(raw) > limit or after.st_size != before.st_size or len(raw) != before.st_size:
            raise ValueError(f"{label} changed while reading")
        return raw
    finally:
        os.close(descriptor)


def read_manifest(root: Path) -> dict[str, object]:
    return decode(
        _read_regular(root / MANIFEST_NAME, "hosted store manifest", MAX_MANIFEST_BYTES),
        "hosted store manifest",
    )


def _safe_relative(value: str, label: str) -> str:
    if not value or "\\" in value or value.startswith("/"):
        raise ValueError(f"{label} path is unsafe")
    path = PurePosixPath(value)
    if path.as_posix() != value or any(part in {"", ".", ".."} for part in path.parts):
        raise ValueError(f"{label} path is unsafe")
    return value


def _exact(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} fields are invalid")
    return value


def _write_file(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() or path.is_symlink():
        raise ValueError(f"hosted store path already exists: {path}")
    with path.open("xb") as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _remove(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink(missing_ok=True)
    elif path.is_dir():
        shutil.rmtree(path)


def _tree_files(root: Path) -> set[str]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("hosted store must be a regular directory")
    output: set[str] = set()
    for path in root.rglob("*"):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            raise ValueError(f"hosted store contains a symlink: {relative}")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError(f"hosted store contains a non-regular entry: {relative}")
        output.add(relative)
    return output


def _release_entry(
    *,
    version: str,
    catalog_entry: Mapping[str, object],
    archive: Path,
    stage: Path,
) -> dict[str, object]:
    release_manifest = release.verify_archive(archive)
    raw_archive = _read_regular(archive, "release archive", release.MAX_ARCHIVE_BYTES)
    archive_sha = sha256(raw_archive)
    release_identity = _exact(
        catalog_entry.get("release"),
        {"release_id", "bundle_id", "receipt_id", "route_id", "archive"},
        "hosted catalog release",
    )
    archive_identity = _exact(
        release_identity.get("archive"),
        {"name", "sha256", "checksum_name"},
        "hosted catalog archive",
    )
    expected = {
        "version": version,
        "release_id": release_identity["release_id"],
        "bundle_id": release_identity["bundle_id"],
        "receipt_id": release_identity["receipt_id"],
        "route_id": release_identity["route_id"],
    }
    for key, value in expected.items():
        if release_manifest.get(key) != value:
            raise ValueError(f"release {version} does not match hosted catalog field {key}")
    if archive_identity["sha256"] != archive_sha or archive_identity["name"] != archive.name:
        raise ValueError(f"release {version} archive identity does not match hosted catalog")

    _, entries, _ = release._read_archive(archive)
    product_entries = {
        path.removeprefix("product/"): raw
        for path, raw in entries.items()
        if path.startswith("product/") and path != "product/"
    }
    if not product_entries or "index.html" not in product_entries:
        raise ValueError(f"release {version} does not contain a hosted product entrypoint")

    object_root = f"{OBJECTS_DIR}/{archive_sha}/product"
    files: dict[str, dict[str, object]] = {}
    total = 0
    for relative, raw in sorted(product_entries.items()):
        _safe_relative(relative, "hosted product")
        if len(raw) > MAX_FILE_BYTES:
            raise ValueError("hosted product file exceeds resource limit")
        total += len(raw)
        if len(files) + 1 > MAX_FILES or total > MAX_TOTAL_BYTES:
            raise ValueError("hosted product exceeds resource limits")
        _write_file(stage.joinpath(*PurePosixPath(object_root, relative).parts), raw)
        files[relative] = {"sha256": sha256(raw), "size": len(raw)}

    return {
        "release_id": release_identity["release_id"],
        "bundle_id": release_identity["bundle_id"],
        "receipt_id": release_identity["receipt_id"],
        "route_id": release_identity["route_id"],
        "archive_sha256": archive_sha,
        "object_root": object_root,
        "entrypoint": "index.html",
        "file_count": len(files),
        "total_bytes": total,
        "files": files,
    }


def make_store(
    *,
    catalog: Mapping[str, object],
    archives: Path,
    stage: Path,
) -> dict[str, object]:
    verified_catalog = hosted_catalog.verify_catalog(dict(catalog))
    archive_root = _absolute(archives)
    if archive_root.is_symlink() or not archive_root.is_dir():
        raise ValueError("release archive source must be a regular directory")
    releases = verified_catalog["releases"]
    assert isinstance(releases, dict)
    materialized: dict[str, object] = {}
    for version in sorted(releases, key=policy.version_key):
        catalog_entry = releases[version]
        assert isinstance(catalog_entry, dict)
        release_identity = catalog_entry["release"]
        assert isinstance(release_identity, dict)
        archive_identity = release_identity["archive"]
        assert isinstance(archive_identity, dict)
        archive = archive_root / str(archive_identity["name"])
        checksum = release.checksum_path(archive)
        if archive.parent != archive_root or checksum.parent != archive_root:
            raise ValueError("hosted catalog archive path escapes source directory")
        materialized[version] = _release_entry(
            version=version,
            catalog_entry=catalog_entry,
            archive=archive,
            stage=stage,
        )
    unsigned: dict[str, object] = {
        "contract": CONTRACT,
        "product": PRODUCT,
        "catalog_id": verified_catalog["catalog_id"],
        "release_count": len(materialized),
        "releases": materialized,
        "boundaries": dict(BOUNDARIES),
    }
    manifest = dict(unsigned)
    manifest["store_id"] = sha256(canonical_json(unsigned))
    return manifest


def verify_store(root: Path, catalog: Mapping[str, object] | None = None) -> dict[str, object]:
    store_root = _absolute(root)
    manifest = read_manifest(store_root)
    _exact(
        manifest,
        {"contract", "product", "catalog_id", "release_count", "releases", "boundaries", "store_id"},
        "hosted store manifest",
    )
    if manifest["contract"] != CONTRACT or manifest["product"] != PRODUCT:
        raise ValueError("hosted store contract is invalid")
    unsigned = dict(manifest)
    store_id = unsigned.pop("store_id")
    if not isinstance(store_id, str) or not SHA256.fullmatch(store_id) or sha256(canonical_json(unsigned)) != store_id:
        raise ValueError("hosted store seal is invalid")
    if manifest["boundaries"] != BOUNDARIES:
        raise ValueError("hosted store boundaries are invalid")
    releases = manifest["releases"]
    if not isinstance(releases, dict) or manifest["release_count"] != len(releases):
        raise ValueError("hosted store release inventory is invalid")

    verified_catalog = None
    if catalog is not None:
        verified_catalog = hosted_catalog.verify_catalog(dict(catalog))
        if manifest["catalog_id"] != verified_catalog["catalog_id"]:
            raise ValueError("hosted store catalog identity is stale")
        if set(releases) != set(verified_catalog["releases"]):
            raise ValueError("hosted store release set does not match catalog")

    expected_paths = {MANIFEST_NAME}
    object_roots: set[str] = set()
    for version, raw_entry in releases.items():
        if not isinstance(version, str):
            raise ValueError("hosted store version is invalid")
        policy.version_key(version)
        entry = _exact(
            raw_entry,
            {
                "release_id", "bundle_id", "receipt_id", "route_id", "archive_sha256",
                "object_root", "entrypoint", "file_count", "total_bytes", "files",
            },
            "hosted store release",
        )
        for key in ("release_id", "bundle_id", "receipt_id", "archive_sha256"):
            if not isinstance(entry[key], str) or not SHA256.fullmatch(entry[key]):
                raise ValueError("hosted store release identity is invalid")
        expected_root = f"{OBJECTS_DIR}/{entry['archive_sha256']}/product"
        if entry["object_root"] != expected_root or expected_root in object_roots:
            raise ValueError("hosted store object root is invalid or duplicated")
        object_roots.add(expected_root)
        if entry["entrypoint"] != "index.html":
            raise ValueError("hosted store entrypoint is invalid")
        files = entry["files"]
        if not isinstance(files, dict) or entry["file_count"] != len(files) or "index.html" not in files:
            raise ValueError("hosted store file inventory is invalid")
        total = 0
        for relative, raw_meta in files.items():
            _safe_relative(relative, "hosted store")
            meta = _exact(raw_meta, {"sha256", "size"}, "hosted store file")
            if (
                not isinstance(meta["sha256"], str)
                or not SHA256.fullmatch(meta["sha256"])
                or not isinstance(meta["size"], int)
                or isinstance(meta["size"], bool)
                or meta["size"] < 0
                or meta["size"] > MAX_FILE_BYTES
            ):
                raise ValueError("hosted store file metadata is invalid")
            path = f"{expected_root}/{relative}"
            expected_paths.add(path)
            raw = _read_regular(
                store_root.joinpath(*PurePosixPath(path).parts),
                f"hosted store file {version}:{relative}",
                MAX_FILE_BYTES,
            )
            if len(raw) != meta["size"] or sha256(raw) != meta["sha256"]:
                raise ValueError("hosted store file does not match manifest")
            total += len(raw)
        if total != entry["total_bytes"] or total > MAX_TOTAL_BYTES:
            raise ValueError("hosted store byte counter is invalid")
        if verified_catalog is not None:
            catalog_entry = verified_catalog["releases"][version]
            assert isinstance(catalog_entry, dict)
            catalog_release = catalog_entry["release"]
            assert isinstance(catalog_release, dict)
            archive = catalog_release["archive"]
            assert isinstance(archive, dict)
            expected_identity = {
                "release_id": catalog_release["release_id"],
                "bundle_id": catalog_release["bundle_id"],
                "receipt_id": catalog_release["receipt_id"],
                "route_id": catalog_release["route_id"],
                "archive_sha256": archive["sha256"],
            }
            if any(entry[key] != value for key, value in expected_identity.items()):
                raise ValueError("hosted store release identity does not match catalog")

    if _tree_files(store_root) != expected_paths:
        raise ValueError("hosted store file set does not match manifest")
    return manifest


def _build_stage(*, catalog: Mapping[str, object], archives: Path, stage: Path) -> dict[str, object]:
    if stage.exists() or stage.is_symlink():
        raise ValueError("hosted store staging path must not exist")
    stage.mkdir(parents=True)
    try:
        manifest = make_store(catalog=catalog, archives=archives, stage=stage)
        _write_file(stage / MANIFEST_NAME, canonical_json(manifest))
        verify_store(stage, catalog)
        return manifest
    except BaseException:
        _remove(stage)
        raise


def _publish(target: Path, stage: Path, catalog: Mapping[str, object]) -> None:
    output = _absolute(target)
    existed = output.exists() or output.is_symlink()
    if existed:
        verify_store(output)
    backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
    if existed:
        output.replace(backup)
    try:
        stage.replace(output)
        verify_store(output, catalog)
    except BaseException:
        _remove(output)
        if existed:
            backup.replace(output)
        _remove(stage)
        raise
    else:
        _remove(backup)


def build_store(*, catalog_path: Path, archives: Path, output: Path) -> dict[str, object]:
    catalog = hosted_catalog.verify_catalog(hosted_catalog.read_json(catalog_path, "hosted catalog"))
    target = _absolute(output)
    archive_root = _absolute(archives)
    if target == archive_root or target in archive_root.parents or archive_root in target.parents:
        raise ValueError("hosted store output must remain separate from release archives")
    target.parent.mkdir(parents=True, exist_ok=True)
    with orchestrate.build_lock(target):
        stage = target.parent / f".{target.name}.stage-{uuid.uuid4().hex}"
        manifest = _build_stage(catalog=catalog, archives=archive_root, stage=stage)
        _publish(target, stage, catalog)
    return manifest


def check_store(*, catalog_path: Path, archives: Path) -> str:
    catalog = hosted_catalog.verify_catalog(hosted_catalog.read_json(catalog_path, "hosted catalog"))
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        first = root / "first"
        second = root / "second"
        first_manifest = _build_stage(catalog=catalog, archives=archives, stage=first)
        second_manifest = _build_stage(catalog=catalog, archives=archives, stage=second)
        first_snapshot = {
            path.relative_to(first).as_posix(): path.read_bytes()
            for path in sorted(first.rglob("*"))
            if path.is_file()
        }
        second_snapshot = {
            path.relative_to(second).as_posix(): path.read_bytes()
            for path in sorted(second.rglob("*"))
            if path.is_file()
        }
        if first_manifest != second_manifest or first_snapshot != second_snapshot:
            raise ValueError("hosted store build is not deterministic")
        return str(first_manifest["store_id"])


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    build = subs.add_parser("build")
    build.add_argument("--catalog", type=Path, required=True)
    build.add_argument("--archives", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    verify = subs.add_parser("verify")
    verify.add_argument("--store", type=Path, required=True)
    verify.add_argument("--catalog", type=Path)
    check = subs.add_parser("check")
    check.add_argument("--catalog", type=Path, required=True)
    check.add_argument("--archives", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        manifest = build_store(catalog_path=args.catalog, archives=args.archives, output=args.output)
        print(f"Built hosted store {manifest['store_id']} -> {args.output}")
    elif args.command == "verify":
        catalog = None if args.catalog is None else hosted_catalog.read_json(args.catalog, "hosted catalog")
        manifest = verify_store(args.store, catalog)
        print(f"Verified hosted store {manifest['store_id']}")
    else:
        store_id = check_store(catalog_path=args.catalog, archives=args.archives)
        print(f"Hosted store is deterministic: {store_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
