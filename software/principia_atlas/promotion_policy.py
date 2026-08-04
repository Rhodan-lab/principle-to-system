"""Immutable release-channel and upgrade policy for Principia & Atlas."""
from __future__ import annotations

import hashlib
import json
import re
from typing import Mapping, Sequence

from software.principia_atlas import release

CONTRACT = "principia-atlas-promotion/0.1"
INDEX_CONTRACT = "principia-atlas-release-index/0.1"
PRODUCT = "Principia & Atlas"
TAG_PREFIX = "principia-atlas-v"
CHANNELS = ("alpha", "beta", "stable")
EMPTY_STATUS_SHA256 = hashlib.sha256(b"").hexdigest()
SHA256 = re.compile(r"^[0-9a-f]{64}$")
PYTHON_FLOOR = re.compile(r"^>=(\d+)\.(\d+)$")
BOUNDARIES = {
    "authorities_separate": True,
    "status_inheritance": "prohibited",
    "live_cross_repository_dependency": False,
    "canonical_mutation": False,
}


def canonical_json(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode()


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def version_info(version: str) -> dict[str, object]:
    match = release.VERSION.fullmatch(version)
    if not match:
        raise ValueError("promotion version must be valid SemVer")
    if match.group(5) is not None:
        raise ValueError("promoted versions must not use SemVer build metadata")
    prerelease = match.group(4)
    if prerelease is None:
        channel, rank, sequence = "stable", 2, 0
    else:
        parts = prerelease.split(".")
        if len(parts) != 2 or parts[0] not in {"alpha", "beta"}:
            raise ValueError("prerelease versions must use alpha.N or beta.N")
        if not parts[1].isdigit() or (len(parts[1]) > 1 and parts[1][0] == "0"):
            raise ValueError("prerelease sequence must be a canonical integer")
        channel, rank, sequence = parts[0], 0 if parts[0] == "alpha" else 1, int(parts[1])
    return {
        "version": version,
        "major": int(match.group(1)),
        "minor": int(match.group(2)),
        "patch": int(match.group(3)),
        "channel": channel,
        "rank": rank,
        "sequence": sequence,
    }


def version_key(version: str) -> tuple[int, int, int, int, int]:
    info = version_info(version)
    return tuple(int(info[key]) for key in ("major", "minor", "patch", "rank", "sequence"))


def channel_for(version: str) -> str:
    return str(version_info(version)["channel"])


def validate_tag(tag: str, version: str) -> str:
    expected = TAG_PREFIX + version
    if tag != expected:
        raise ValueError(f"release tag must be exactly {expected}")
    return tag


def _floor(value: object) -> tuple[int, int]:
    if not isinstance(value, str) or not (match := PYTHON_FLOOR.fullmatch(value)):
        raise ValueError("release runtime Python floor must use >=MAJOR.MINOR")
    return int(match.group(1)), int(match.group(2))


def compatibility(manifest: Mapping[str, object]) -> dict[str, object]:
    entrypoints, runtime, boundaries = (manifest.get(key) for key in ("entrypoints", "runtime", "boundaries"))
    route = manifest.get("route_id")
    if not all(isinstance(value, dict) for value in (entrypoints, runtime, boundaries)) or not isinstance(route, str) or not route:
        raise ValueError("release compatibility fields are invalid")
    assert isinstance(runtime, dict) and isinstance(boundaries, dict) and isinstance(entrypoints, dict)
    if runtime.get("host") != "127.0.0.1" or runtime.get("external_network_required") is not False:
        raise ValueError("release runtime boundary is invalid")
    _floor(runtime.get("python"))
    if boundaries != BOUNDARIES:
        raise ValueError("release authority boundary is invalid")
    return {
        "release_contract": manifest.get("contract"),
        "route_id": route,
        "entrypoints": dict(entrypoints),
        "runtime": dict(runtime),
        "boundaries": dict(boundaries),
    }


def clean_sources(receipt: Mapping[str, object]) -> dict[str, object]:
    if receipt.get("contract") != "principia-atlas-orchestration-receipt/0.2":
        raise ValueError("promotion requires orchestration receipt contract 0.2")
    sources = receipt.get("sources")
    if not isinstance(sources, dict) or set(sources) != {"principia", "atlas"}:
        raise ValueError("promotion source identity is invalid")
    result: dict[str, object] = {}
    for name in ("principia", "atlas"):
        state = sources[name]
        if not isinstance(state, dict):
            raise ValueError("promotion source identity is invalid")
        commit, repository = state.get("commit"), state.get("repository")
        valid_commit = isinstance(commit, str) and len(commit) in {40, 64} and all(c in "0123456789abcdef" for c in commit)
        if not isinstance(repository, str) or not valid_commit or state.get("clean") is not True or state.get("status_sha256") != EMPTY_STATUS_SHA256:
            raise ValueError("promoted releases require exact clean source checkouts")
        result[name] = {"repository": repository, "commit": commit, "clean": True, "status_sha256": EMPTY_STATUS_SHA256}
    return result


def seal(unsigned: Mapping[str, object], field: str) -> dict[str, object]:
    result = dict(unsigned)
    result[field] = sha256(canonical_json(unsigned))
    return result


def check_upgrade(previous: Mapping[str, object] | None, candidate: Mapping[str, object]) -> dict[str, object]:
    target, current = candidate.get("version"), candidate.get("compatibility")
    if not isinstance(target, str) or not isinstance(current, dict):
        raise ValueError("candidate compatibility snapshot is invalid")
    if previous is None:
        return {"from_version": None, "to_version": target, "kind": "first-release", "compatible": True,
                "checks": ["authority-boundaries", "loopback-runtime", "clean-sources"]}
    source, old = previous.get("version"), previous.get("compatibility")
    if not isinstance(source, str) or not isinstance(old, dict):
        raise ValueError("previous promotion compatibility snapshot is invalid")
    if version_key(target) <= version_key(source):
        raise ValueError("upgrade target must have higher SemVer precedence")
    if current.get("boundaries") != old.get("boundaries"):
        raise ValueError("upgrade changes authority boundaries")
    current_runtime, old_runtime = current.get("runtime"), old.get("runtime")
    if not isinstance(current_runtime, dict) or not isinstance(old_runtime, dict):
        raise ValueError("upgrade runtime snapshot is invalid")
    if current_runtime.get("host") != old_runtime.get("host"):
        raise ValueError("upgrade changes the loopback host boundary")
    same_major = version_info(target)["major"] == version_info(source)["major"]
    checks = ["authority-boundaries", "loopback-runtime"]
    if same_major:
        pairs = (("release_contract", "release contract"), ("route_id", "route identity"), ("entrypoints", "required entrypoints"))
        for key, label in pairs:
            if current.get(key) != old.get(key):
                raise ValueError(f"non-major upgrade changes the {label}")
        if _floor(current_runtime.get("python")) > _floor(old_runtime.get("python")):
            raise ValueError("non-major upgrade raises the Python runtime floor")
        checks += ["release-contract", "route-identity", "entrypoints", "python-floor"]
    else:
        checks.append("major-version-boundary")
    return {"from_version": source, "to_version": target, "kind": "non-breaking" if same_major else "major",
            "compatible": True, "checks": checks}


def _predecessor(value: object, version: str, same_channel: bool) -> dict[str, object] | None:
    if value is None:
        return None
    if not isinstance(value, dict) or set(value) != {"version", "tag", "promotion_id"}:
        raise ValueError("promotion predecessor is invalid")
    old, tag, identity = value.get("version"), value.get("tag"), value.get("promotion_id")
    if not isinstance(old, str) or not isinstance(tag, str) or not isinstance(identity, str) or not SHA256.fullmatch(identity):
        raise ValueError("promotion predecessor is invalid")
    validate_tag(tag, old)
    if version_key(old) >= version_key(version) or (same_channel and channel_for(old) != channel_for(version)):
        raise ValueError("promotion predecessor is invalid")
    return value


def verify_promotion(value: dict[str, object]) -> dict[str, object]:
    required = {"contract", "product", "tag", "version", "channel", "release", "sources", "compatibility",
                "predecessor", "channel_predecessor", "upgrade", "promotion_id"}
    if set(value) != required or value.get("contract") != CONTRACT or value.get("product") != PRODUCT:
        raise ValueError("promotion descriptor contract is invalid")
    version, tag = value.get("version"), value.get("tag")
    if not isinstance(version, str) or not isinstance(tag, str):
        raise ValueError("promotion version or tag is invalid")
    validate_tag(tag, version)
    if value.get("channel") != channel_for(version):
        raise ValueError("promotion channel does not match its version")
    identity = value.get("promotion_id")
    unsigned = dict(value); unsigned.pop("promotion_id")
    if not isinstance(identity, str) or not SHA256.fullmatch(identity) or sha256(canonical_json(unsigned)) != identity:
        raise ValueError("promotion descriptor seal is invalid")
    rel = value.get("release")
    if not isinstance(rel, dict) or set(rel) != {"release_id", "bundle_id", "receipt_id", "route_id", "archive"}:
        raise ValueError("promotion release identity is invalid")
    for key in ("release_id", "bundle_id", "receipt_id"):
        if not isinstance(rel.get(key), str) or not SHA256.fullmatch(str(rel[key])):
            raise ValueError("promotion release identity is invalid")
    archive = rel.get("archive")
    if not isinstance(archive, dict) or set(archive) != {"name", "sha256", "checksum_name"}:
        raise ValueError("promotion archive identity is invalid")
    name = archive.get("name")
    if not isinstance(name, str) or not name or "/" in name or "\\" in name or archive.get("checksum_name") != name + release.CHECKSUM_SUFFIX or not isinstance(archive.get("sha256"), str) or not SHA256.fullmatch(str(archive["sha256"])):
        raise ValueError("promotion archive identity is invalid")
    sources = clean_source_snapshot(value.get("sources"))
    comp = compatibility_snapshot(value.get("compatibility"))
    if rel.get("route_id") != comp.get("route_id"):
        raise ValueError("promotion route identity is inconsistent")
    predecessor = _predecessor(value.get("predecessor"), version, False)
    _predecessor(value.get("channel_predecessor"), version, True)
    upgrade = value.get("upgrade")
    if not isinstance(upgrade, dict) or set(upgrade) != {"from_version", "to_version", "kind", "compatible", "checks"}:
        raise ValueError("promotion upgrade result is invalid")
    expected_from = None if predecessor is None else predecessor["version"]
    checks = upgrade.get("checks")
    if upgrade.get("from_version") != expected_from or upgrade.get("to_version") != version or upgrade.get("compatible") is not True or not isinstance(checks, list) or not checks or not all(isinstance(item, str) and item for item in checks):
        raise ValueError("promotion upgrade result is invalid")
    expected_kind = "first-release" if predecessor is None else ("non-breaking" if version_info(str(predecessor["version"]))["major"] == version_info(version)["major"] else "major")
    if upgrade.get("kind") != expected_kind:
        raise ValueError("promotion upgrade classification is invalid")
    value["sources"], value["compatibility"] = sources, comp
    return value


def clean_source_snapshot(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"principia", "atlas"}:
        raise ValueError("promotion source snapshot is invalid")
    fake = {"contract": "principia-atlas-orchestration-receipt/0.2", "sources": value}
    return clean_sources(fake)


def compatibility_snapshot(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {"release_contract", "route_id", "entrypoints", "runtime", "boundaries"}:
        raise ValueError("promotion compatibility snapshot is invalid")
    normalized = compatibility({"contract": value.get("release_contract"), "route_id": value.get("route_id"),
                                "entrypoints": value.get("entrypoints"), "runtime": value.get("runtime"),
                                "boundaries": value.get("boundaries")})
    if normalized != value or value.get("release_contract") != release.CONTRACT:
        raise ValueError("promotion compatibility snapshot is invalid")
    return normalized


def make_promotion(snapshot: Mapping[str, object], history: Sequence[Mapping[str, object]]) -> dict[str, object]:
    old = [verify_promotion(dict(item)) for item in history]
    version, tag, channel = str(snapshot["version"]), str(snapshot["tag"]), str(snapshot["channel"])
    versions = [str(item["version"]) for item in old]
    if len(versions) != len(set(versions)) or tag in {item["tag"] for item in old} or version in versions:
        raise ValueError("promotion history contains a duplicate version or tag")
    predecessor = max(old, key=lambda item: version_key(str(item["version"]))) if old else None
    if predecessor and version_key(version) <= version_key(str(predecessor["version"])):
        raise ValueError("promotion version must advance the global release history")
    channel_old = [item for item in old if item["channel"] == channel]
    channel_predecessor = max(channel_old, key=lambda item: version_key(str(item["version"]))) if channel_old else None
    def ref(item):
        return None if item is None else {key: item[key] for key in ("version", "tag", "promotion_id")}
    unsigned = {"contract": CONTRACT, "product": PRODUCT, **snapshot, "predecessor": ref(predecessor),
                "channel_predecessor": ref(channel_predecessor), "upgrade": check_upgrade(predecessor, snapshot)}
    return seal(unsigned, "promotion_id")


def index_entry(item: Mapping[str, object]) -> dict[str, object]:
    rel, sources = item["release"], item["sources"]
    assert isinstance(rel, dict) and isinstance(sources, dict) and isinstance(rel["archive"], dict)
    return {"tag": item["tag"], "channel": item["channel"], "promotion_id": item["promotion_id"],
            "release_id": rel["release_id"], "bundle_id": rel["bundle_id"], "receipt_id": rel["receipt_id"],
            "archive": dict(rel["archive"]), "sources": {name: {"repository": state["repository"], "commit": state["commit"]}
            for name, state in sources.items() if isinstance(state, dict)}}


def make_index(history: Sequence[Mapping[str, object]], candidate: Mapping[str, object]) -> dict[str, object]:
    items = [verify_promotion(dict(item)) for item in history] + [verify_promotion(dict(candidate))]
    versions = [str(item["version"]) for item in items]
    if len(versions) != len(set(versions)):
        raise ValueError("release index contains duplicate versions")
    releases = {str(item["version"]): index_entry(item) for item in sorted(items, key=lambda item: version_key(str(item["version"])))}
    channels: dict[str, object] = {}
    for channel in CHANNELS:
        matches = [item for item in items if item["channel"] == channel]
        latest = max(matches, key=lambda item: version_key(str(item["version"]))) if matches else None
        channels[channel] = None if latest is None else {key: latest[key] for key in ("version", "tag", "promotion_id")}
    return seal({"contract": INDEX_CONTRACT, "product": PRODUCT, "release_count": len(releases),
                 "releases": releases, "channels": channels}, "index_id")


def verify_index(value: dict[str, object]) -> dict[str, object]:
    if set(value) != {"contract", "product", "release_count", "releases", "channels", "index_id"} or value.get("contract") != INDEX_CONTRACT or value.get("product") != PRODUCT:
        raise ValueError("release index contract is invalid")
    identity = value.get("index_id"); unsigned = dict(value); unsigned.pop("index_id")
    if not isinstance(identity, str) or not SHA256.fullmatch(identity) or sha256(canonical_json(unsigned)) != identity:
        raise ValueError("release index seal is invalid")
    releases, channels = value.get("releases"), value.get("channels")
    if not isinstance(releases, dict) or not isinstance(channels, dict) or set(channels) != set(CHANNELS) or value.get("release_count") != len(releases):
        raise ValueError("release index fields are invalid")
    tags: set[str] = set(); promotion_ids: set[str] = set(); grouped = {channel: [] for channel in CHANNELS}
    for version, entry in releases.items():
        if not isinstance(version, str) or not isinstance(entry, dict) or entry.get("channel") != channel_for(version):
            raise ValueError("release index entry is invalid")
        if set(entry) != {"tag", "channel", "promotion_id", "release_id", "bundle_id", "receipt_id", "archive", "sources"}:
            raise ValueError("release index entry is invalid")
        validate_tag(str(entry.get("tag")), version)
        for key in ("promotion_id", "release_id", "bundle_id", "receipt_id"):
            if not isinstance(entry.get(key), str) or not SHA256.fullmatch(str(entry[key])):
                raise ValueError("release index identity is invalid")
        if entry["tag"] in tags or entry["promotion_id"] in promotion_ids:
            raise ValueError("release index contains duplicate identities")
        tags.add(str(entry["tag"])); promotion_ids.add(str(entry["promotion_id"])); grouped[channel_for(version)].append(version)
    for channel, versions in grouped.items():
        if not versions:
            if channels[channel] is not None:
                raise ValueError("empty release channel has a pointer")
            continue
        latest = max(versions, key=version_key); entry = releases[latest]
        expected = {"version": latest, "tag": entry["tag"], "promotion_id": entry["promotion_id"]}
        if channels[channel] != expected:
            raise ValueError("release channel pointer is not the latest version")
    return value
