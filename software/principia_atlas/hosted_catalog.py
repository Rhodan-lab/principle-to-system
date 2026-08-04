#!/usr/bin/env python3
"""Build and verify the immutable catalog consumed by the hosted control plane."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Mapping, Sequence

try:
    from software.principia_atlas import promotion, promotion_policy as policy
except ModuleNotFoundError:
    import sys
    ROOT = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(ROOT))
    from software.principia_atlas import promotion, promotion_policy as policy

CONTRACT = "principia-atlas-hosted-catalog/0.1"
PRODUCT = "Principia & Atlas"
MAX_BYTES = 2 * 1024 * 1024


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


def read_json(path: Path, label: str) -> dict[str, object]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > MAX_BYTES:
        raise ValueError(f"{label} must be a bounded regular file")
    return decode(path.read_bytes(), label)


def _source(value: object) -> dict[str, str]:
    if not isinstance(value, dict) or set(value) != {
        "repository", "commit", "clean", "status_sha256"
    }:
        raise ValueError("promotion source state is invalid")
    repository, commit = value.get("repository"), value.get("commit")
    if not isinstance(repository, str) or not isinstance(commit, str):
        raise ValueError("promotion source identity is invalid")
    return {"repository": repository, "commit": commit}


def catalog_entry(value: Mapping[str, object]) -> dict[str, object]:
    item = policy.verify_promotion(dict(value))
    release = item["release"]
    sources = item["sources"]
    compatibility = item["compatibility"]
    assert isinstance(release, dict)
    assert isinstance(sources, dict)
    assert isinstance(compatibility, dict)
    return {
        "tag": item["tag"],
        "channel": item["channel"],
        "promotion_id": item["promotion_id"],
        "release": {
            "release_id": release["release_id"],
            "bundle_id": release["bundle_id"],
            "receipt_id": release["receipt_id"],
            "route_id": release["route_id"],
            "archive": dict(release["archive"]),
        },
        "sources": {
            "principia": _source(sources["principia"]),
            "atlas": _source(sources["atlas"]),
        },
        "compatibility": dict(compatibility),
    }


def make_catalog(values: Sequence[Mapping[str, object]]) -> dict[str, object]:
    promotions = [policy.verify_promotion(dict(value)) for value in values]
    versions = [str(item["version"]) for item in promotions]
    if len(versions) != len(set(versions)):
        raise ValueError("hosted catalog contains duplicate versions")
    releases = {
        str(item["version"]): catalog_entry(item)
        for item in sorted(promotions, key=lambda item: policy.version_key(str(item["version"])))
    }
    channels: dict[str, object] = {}
    for channel in policy.CHANNELS:
        matching = [item for item in promotions if item["channel"] == channel]
        latest = max(
            matching,
            key=lambda item: policy.version_key(str(item["version"])),
            default=None,
        )
        channels[channel] = (
            None
            if latest is None
            else {
                "version": latest["version"],
                "tag": latest["tag"],
                "promotion_id": latest["promotion_id"],
            }
        )
    unsigned: dict[str, object] = {
        "contract": CONTRACT,
        "product": PRODUCT,
        "release_count": len(releases),
        "releases": releases,
        "channels": channels,
    }
    return policy.seal(unsigned, "catalog_id")


def _exact(value: object, fields: set[str], label: str) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != fields:
        raise ValueError(f"{label} fields are invalid")
    return value


def _verify_source(value: object) -> None:
    state = _exact(value, {"repository", "commit"}, "hosted catalog source")
    repository, commit = state["repository"], state["commit"]
    if (
        not isinstance(repository, str)
        or "/" not in repository
        or not isinstance(commit, str)
        or len(commit) not in {40, 64}
        or any(character not in "0123456789abcdef" for character in commit)
    ):
        raise ValueError("hosted catalog source identity is invalid")


def verify_catalog(value: dict[str, object]) -> dict[str, object]:
    _exact(
        value,
        {"contract", "product", "release_count", "releases", "channels", "catalog_id"},
        "hosted catalog",
    )
    if value["contract"] != CONTRACT or value["product"] != PRODUCT:
        raise ValueError("hosted catalog contract is invalid")
    identity = value["catalog_id"]
    unsigned = dict(value)
    unsigned.pop("catalog_id")
    if (
        not isinstance(identity, str)
        or not policy.SHA256.fullmatch(identity)
        or policy.sha256(policy.canonical_json(unsigned)) != identity
    ):
        raise ValueError("hosted catalog seal is invalid")
    releases = value["releases"]
    channels = value["channels"]
    if (
        not isinstance(releases, dict)
        or not isinstance(channels, dict)
        or set(channels) != set(policy.CHANNELS)
        or value["release_count"] != len(releases)
    ):
        raise ValueError("hosted catalog fields are invalid")
    grouped: dict[str, list[str]] = {channel: [] for channel in policy.CHANNELS}
    tags: set[str] = set()
    promotion_ids: set[str] = set()
    for version, raw_entry in releases.items():
        if not isinstance(version, str):
            raise ValueError("hosted catalog version is invalid")
        channel = policy.channel_for(version)
        entry = _exact(
            raw_entry,
            {"tag", "channel", "promotion_id", "release", "sources", "compatibility"},
            "hosted catalog entry",
        )
        policy.validate_tag(str(entry["tag"]), version)
        promotion_id = entry["promotion_id"]
        if (
            entry["channel"] != channel
            or not isinstance(promotion_id, str)
            or not policy.SHA256.fullmatch(promotion_id)
            or entry["tag"] in tags
            or promotion_id in promotion_ids
        ):
            raise ValueError("hosted catalog entry identity is invalid")
        tags.add(str(entry["tag"]))
        promotion_ids.add(promotion_id)
        release = _exact(
            entry["release"],
            {"release_id", "bundle_id", "receipt_id", "route_id", "archive"},
            "hosted catalog release",
        )
        for key in ("release_id", "bundle_id", "receipt_id"):
            if not isinstance(release[key], str) or not policy.SHA256.fullmatch(release[key]):
                raise ValueError("hosted catalog release identity is invalid")
        archive = _exact(
            release["archive"], {"name", "sha256", "checksum_name"}, "hosted catalog archive"
        )
        if (
            not isinstance(archive["name"], str)
            or "/" in archive["name"]
            or "\\" in archive["name"]
            or archive["checksum_name"] != archive["name"] + ".sha256"
            or not isinstance(archive["sha256"], str)
            or not policy.SHA256.fullmatch(archive["sha256"])
        ):
            raise ValueError("hosted catalog archive identity is invalid")
        sources = _exact(entry["sources"], {"principia", "atlas"}, "hosted catalog sources")
        _verify_source(sources["principia"])
        _verify_source(sources["atlas"])
        compatibility = policy.compatibility_snapshot(entry["compatibility"])
        if compatibility["route_id"] != release["route_id"]:
            raise ValueError("hosted catalog route identity is inconsistent")
        grouped[channel].append(version)
    for channel, versions in grouped.items():
        pointer = channels[channel]
        if not versions:
            if pointer is not None:
                raise ValueError("empty hosted channel has a pointer")
            continue
        latest = max(versions, key=policy.version_key)
        entry = releases[latest]
        assert isinstance(entry, dict)
        expected = {
            "version": latest,
            "tag": entry["tag"],
            "promotion_id": entry["promotion_id"],
        }
        if pointer != expected:
            raise ValueError("hosted channel pointer is stale")
    return value


def load_promotions(root: Path) -> list[dict[str, object]]:
    if root.is_symlink() or not root.is_dir():
        raise ValueError("promotion history must be a directory")
    return [
        policy.verify_promotion(read_json(path, "promotion descriptor"))
        for path in sorted(root.rglob(promotion.PROMOTION_NAME))
    ]


def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest="command", required=True)
    build = subs.add_parser("build")
    build.add_argument("--promotions", type=Path, required=True)
    build.add_argument("--output", type=Path, required=True)
    verify = subs.add_parser("verify")
    verify.add_argument("--catalog", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "build":
        catalog = verify_catalog(make_catalog(load_promotions(args.promotions)))
        _write(args.output, policy.canonical_json(catalog))
        print(f"Built hosted catalog {catalog['catalog_id']} -> {args.output}")
    else:
        catalog = verify_catalog(read_json(args.catalog, "hosted catalog"))
        print(f"Verified hosted catalog {catalog['catalog_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
