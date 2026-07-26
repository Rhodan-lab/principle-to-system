#!/usr/bin/env python3
"""Export a Principia bridge manifest to Atlas's opaque external-dependent shape."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"
DEFAULT_OUTPUT = ROOT / "integration" / "principia-atlas" / "exports" / "feedback-instability.external-dependent.fixture.json"


def load_json(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return value


def build_export(manifest: dict[str, object]) -> dict[str, object]:
    principia = manifest.get("principia")
    atlas = manifest.get("atlas")
    export_policy = manifest.get("export")
    if not isinstance(principia, dict) or not isinstance(atlas, dict) or not isinstance(export_policy, dict):
        raise ValueError("manifest is missing principia, atlas, or export objects")
    dependencies = atlas.get("dependencies")
    if not isinstance(dependencies, list):
        raise ValueError("atlas.dependencies must be a list")

    ids: list[str] = []
    for index, dependency in enumerate(dependencies):
        if not isinstance(dependency, dict) or not isinstance(dependency.get("id"), str):
            raise ValueError(f"atlas.dependencies[{index}] is missing a string id")
        ids.append(dependency["id"])

    artifact_id = principia.get("artifact_id")
    repository = principia.get("repository")
    revision = principia.get("artifact_revision")
    kind = export_policy.get("kind")
    role = export_policy.get("role")
    if not isinstance(artifact_id, str) or not isinstance(repository, str):
        raise ValueError("principia artifact identity is incomplete")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        raise ValueError("principia artifact_revision must be a positive integer")
    if not isinstance(kind, str) or not isinstance(role, str):
        raise ValueError("export kind and role must be strings")

    return {
        "id": artifact_id,
        "kind": kind,
        "repository": repository,
        "revision": revision,
        "role": role,
        "depends_on": sorted(set(ids)),
    }


def render(value: dict[str, object]) -> str:
    return json.dumps(value, indent=2, ensure_ascii=False) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest.is_absolute() else ROOT / args.manifest
    output_path = args.output if args.output.is_absolute() else ROOT / args.output
    try:
        expected = render(build_export(load_json(manifest_path)))
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.write:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(expected, encoding="utf-8")
        print(f"Wrote Atlas external-dependent export: {output_path.relative_to(ROOT)}")
        return 0

    try:
        actual = output_path.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"ERROR: cannot read export {output_path}: {exc}", file=sys.stderr)
        return 1
    if actual != expected:
        print(f"ERROR: stale Atlas external-dependent export: {output_path.relative_to(ROOT)}", file=sys.stderr)
        return 1
    print(f"Atlas external-dependent export is deterministic: {output_path.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
