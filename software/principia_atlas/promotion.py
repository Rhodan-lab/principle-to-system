#!/usr/bin/env python3
"""Prepare and verify Principia & Atlas GitHub release promotions."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

try:
    from software.principia_atlas import promotion_policy as policy, release
except ModuleNotFoundError:
    import sys
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from software.principia_atlas import promotion_policy as policy, release

PROMOTION_NAME = "principia-atlas-promotion.json"
INDEX_NAME = "principia-atlas-release-index.json"
NOTES_NAME = "RELEASE-NOTES.md"

# Public policy aliases used by tests and release tooling.
TAG_PREFIX, EMPTY_STATUS_SHA256 = policy.TAG_PREFIX, policy.EMPTY_STATUS_SHA256
canonical_json, channel_for, validate_tag = policy.canonical_json, policy.channel_for, policy.validate_tag
version_key, check_upgrade = policy.version_key, policy.check_upgrade
make_index, verify_index, verify_promotion, seal = policy.make_index, policy.verify_index, policy.verify_promotion, policy.seal


def _strict(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def decode(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw.decode(), object_pairs_hook=_strict,
                           parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError(f"{label} is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must be a JSON object")
    return value


def read_json(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2 * 1024 * 1024:
        raise ValueError(f"{label} must be a bounded regular file")
    return decode(path.read_bytes(), label)


def candidate_snapshot(archive: Path, tag: str) -> dict[str, object]:
    manifest = release.verify_archive(archive)
    _, entries, second = release._read_archive(archive)
    if manifest != second:
        raise ValueError("release archive verification returned inconsistent manifests")
    version = manifest.get("version")
    if not isinstance(version, str):
        raise ValueError("release manifest version is invalid")
    policy.validate_tag(tag, version)
    raw = entries.get("product.build-receipt.json")
    if raw is None:
        raise ValueError("release archive is missing its product receipt")
    receipt = release.decode_json(raw, "product build receipt")
    identities = [manifest.get(key) for key in ("release_id", "bundle_id", "receipt_id")]
    if not all(isinstance(value, str) and policy.SHA256.fullmatch(value) for value in identities):
        raise ValueError("release identity is invalid")
    if receipt.get("receipt_id") != manifest["receipt_id"]:
        raise ValueError("release receipt identity is inconsistent")
    digest = release._checksum(archive)
    if not policy.SHA256.fullmatch(digest):
        raise ValueError("release archive digest is invalid")
    return {
        "tag": tag,
        "version": version,
        "channel": policy.channel_for(version),
        "release": {
            "release_id": manifest["release_id"], "bundle_id": manifest["bundle_id"],
            "receipt_id": manifest["receipt_id"], "route_id": manifest.get("route_id"),
            "archive": {"name": archive.name, "sha256": digest,
                        "checksum_name": release.checksum_path(archive).name},
        },
        "sources": policy.clean_sources(receipt),
        "compatibility": policy.compatibility(manifest),
    }


def make_promotion(*, archive: Path, tag: str, history=()) -> dict[str, object]:
    return policy.make_promotion(candidate_snapshot(archive, tag), history)


def load_history(root: Path | None) -> list[dict[str, object]]:
    if root is None or not root.exists():
        return []
    if root.is_symlink() or not root.is_dir():
        raise ValueError("promotion history must be a directory")
    return [policy.verify_promotion(read_json(path, "promotion history"))
            for path in sorted(root.rglob(PROMOTION_NAME))]


def load_expected_tags(path: Path | None) -> set[str] | None:
    if path is None:
        return None
    if path.is_symlink() or not path.is_file():
        raise ValueError("expected tag list must be a regular file")
    tags: set[str] = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        tag = line.strip()
        if not tag:
            continue
        if tag in tags or not tag.startswith(policy.TAG_PREFIX):
            raise ValueError("expected tag list is invalid")
        policy.validate_tag(tag, tag[len(policy.TAG_PREFIX):])
        tags.add(tag)
    return tags


def verify_candidate(archive: Path, promotion: dict[str, object], index: dict[str, object]) -> None:
    promotion, index = policy.verify_promotion(promotion), policy.verify_index(index)
    snapshot = candidate_snapshot(archive, str(promotion["tag"]))
    for key in ("tag", "version", "channel", "release", "sources", "compatibility"):
        if promotion[key] != snapshot[key]:
            raise ValueError("promotion descriptor does not match the release archive")
    releases = index["releases"]
    assert isinstance(releases, dict)
    if releases.get(str(promotion["version"])) != policy.index_entry(promotion):
        raise ValueError("release index does not contain the promotion descriptor")


def release_notes(item: Mapping[str, object]) -> str:
    rel, sources, upgrade = item["release"], item["sources"], item["upgrade"]
    assert isinstance(rel, dict) and isinstance(sources, dict) and isinstance(upgrade, dict)
    lines = [f"# Principia & Atlas {item['version']}", "", f"Channel: `{item['channel']}`",
             f"Tag: `{item['tag']}`", f"Release ID: `{rel['release_id']}`", f"Bundle ID: `{rel['bundle_id']}`",
             f"Upgrade predecessor: `{upgrade.get('from_version') or 'none (first promoted release)'}`",
             f"Upgrade classification: `{upgrade['kind']}`", "", "## Exact sources", ""]
    for name in ("principia", "atlas"):
        state = sources[name]; assert isinstance(state, dict)
        lines.append(f"- {name.title()}: `{state['commit']}`")
    archive = rel["archive"]; assert isinstance(archive, dict)
    lines += ["", "## Verification", "", "```bash", f"sha256sum -c {archive['checksum_name']}",
              "python3 launcher.py verify", "```", "",
              "Principia learning authority and Atlas knowledge-status authority remain separate."]
    return "\n".join(lines) + "\n"


def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def prepare(archive: Path, tag: str, history_dir: Path | None, output_dir: Path,
            expected_tags: Path | None = None) -> tuple[dict[str, object], dict[str, object]]:
    history = load_history(history_dir)
    expected = load_expected_tags(expected_tags)
    if expected is not None and expected != {str(item["tag"]) for item in history}:
        raise ValueError("promotion history does not match immutable release tags")
    item = make_promotion(archive=archive, tag=tag, history=history)
    index = policy.make_index(history, item)
    verify_candidate(archive, item, index)
    output_dir.mkdir(parents=True, exist_ok=True)
    _write(output_dir / PROMOTION_NAME, policy.canonical_json(item))
    _write(output_dir / INDEX_NAME, policy.canonical_json(index))
    _write(output_dir / NOTES_NAME, release_notes(item).encode())
    return item, index


def parse_args(argv: Sequence[str] | None = None):
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    ready = subs.add_parser("prepare")
    ready.add_argument("--archive", type=Path, required=True); ready.add_argument("--tag", required=True)
    ready.add_argument("--history-dir", type=Path); ready.add_argument("--expected-tags", type=Path)
    ready.add_argument("--output-dir", type=Path, required=True)
    verify = subs.add_parser("verify")
    verify.add_argument("--archive", type=Path, required=True); verify.add_argument("--promotion", type=Path, required=True)
    verify.add_argument("--index", type=Path, required=True)
    upgrade = subs.add_parser("upgrade")
    upgrade.add_argument("--from-promotion", type=Path, required=True); upgrade.add_argument("--to-archive", type=Path, required=True)
    upgrade.add_argument("--tag", required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "prepare":
        item, index = prepare(args.archive, args.tag, args.history_dir, args.output_dir, args.expected_tags)
        print(f"Prepared {item['channel']} promotion {item['version']} ({item['promotion_id']})")
        print(f"Release index: {index['index_id']}")
    elif args.command == "verify":
        item, index = read_json(args.promotion, "promotion descriptor"), read_json(args.index, "release index")
        verify_candidate(args.archive, item, index)
        print(f"Verified promotion {item['version']} ({item['promotion_id']})")
    else:
        previous = policy.verify_promotion(read_json(args.from_promotion, "previous promotion"))
        print(json.dumps(policy.check_upgrade(previous, candidate_snapshot(args.to_archive, args.tag)), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
