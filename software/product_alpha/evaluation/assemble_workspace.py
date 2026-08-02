#!/usr/bin/env python3
"""Validate individual Product Alpha session exports and assemble one cohort JSONL."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import summarize as pilot_summary

CONTRACT = "principia-product-alpha-workspace-intake/0.1"
WORKSPACE_CONTRACT = "principia-product-alpha-pilot-workspace/0.1"
ALLOWED_SOURCE_SUFFIXES = {".json", ".jsonl"}


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}: invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label}: session export must contain one JSON object")
    return value


def _member(workspace: Path, relative: object, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"workspace manifest {label} path must be non-empty text")
    candidate = (workspace / relative).resolve(strict=False)
    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise ValueError(
            f"workspace manifest {label} path escapes the workspace"
        ) from exc
    return candidate


def _load_workspace(
    workspace: Path,
) -> tuple[dict[str, Any], Path, Path, Path]:
    manifest = _read_json_object(workspace / "workspace.json", "workspace.json")
    if manifest.get("contract") != WORKSPACE_CONTRACT:
        raise ValueError(
            f"workspace.json contract must be {WORKSPACE_CONTRACT!r}"
        )

    build_id = manifest.get("pilot_build_id")
    if not isinstance(build_id, str) or not pilot_summary.BUILD_ID_PATTERN.fullmatch(
        build_id
    ):
        raise ValueError(
            "workspace.json pilot_build_id must be a 64-character lowercase SHA-256"
        )
    if manifest.get("route_id") != pilot_summary.ROUTE_ID:
        raise ValueError(
            f"workspace.json route_id must be {pilot_summary.ROUTE_ID!r}"
        )

    paths = manifest.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("workspace.json paths must be an object")
    incoming = _member(
        workspace,
        paths.get("incoming_sessions"),
        "incoming_sessions",
    )
    combined = _member(
        workspace,
        paths.get("combined_jsonl"),
        "combined_jsonl",
    )
    intake = _member(
        workspace,
        paths.get("intake_manifest", "verified/intake-manifest.json"),
        "intake_manifest",
    )
    return manifest, incoming, combined, intake


def assemble_workspace(workspace: Path) -> dict[str, object]:
    """Validate private incoming exports and write one immutable cohort intake."""
    root = workspace.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be a directory")

    manifest, incoming, combined, intake = _load_workspace(root)
    if not incoming.is_dir():
        raise ValueError("incoming session directory is missing")
    if combined.exists():
        raise FileExistsError(f"combined cohort already exists: {combined}")
    if intake.exists():
        raise FileExistsError(f"intake manifest already exists: {intake}")

    entries = sorted(incoming.iterdir(), key=lambda path: path.name)
    if not entries:
        raise ValueError("incoming session directory contains no exports")

    sessions: list[dict[str, Any]] = []
    source_records: list[dict[str, str]] = []
    seen_ids: set[str] = set()

    for path in entries:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unexpected incoming entry: {path.name}")
        if path.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            raise ValueError(f"unsupported incoming file type: {path.name}")

        raw = path.read_bytes()
        try:
            value = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"{path.name}: file must be UTF-8") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(
                f"{path.name}: session export must contain one JSON object"
            )

        try:
            session = pilot_summary.validate_session(value, 1)
        except ValueError as exc:
            detail = str(exc).removeprefix("line 1: ")
            raise ValueError(f"{path.name}: {detail}") from exc

        if session["pilot_build_id"] != manifest["pilot_build_id"]:
            raise ValueError(
                f"{path.name}: pilot_build_id does not match workspace build"
            )
        session_id = session["session_id"]
        if session_id in seen_ids:
            raise ValueError(
                f"{path.name}: duplicate session_id {session_id!r}"
            )

        seen_ids.add(session_id)
        sessions.append(session)
        source_records.append(
            {
                "session_id": session_id,
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )

    sessions.sort(key=lambda item: item["session_id"])
    source_records.sort(key=lambda item: item["session_id"])
    combined_bytes = "".join(
        json.dumps(session, sort_keys=True, separators=(",", ":")) + "\n"
        for session in sessions
    ).encode("utf-8")
    summary = pilot_summary.summarize(sessions)

    report: dict[str, object] = {
        "contract": CONTRACT,
        "decision": "workspace-intake-assembled",
        "pilot_build_id": manifest["pilot_build_id"],
        "route_id": manifest["route_id"],
        "sessions": len(sessions),
        "evidence_status": summary["evidence_status"],
        "summary_contract": summary["contract"],
        "combined_jsonl": str(combined),
        "combined_sha256": hashlib.sha256(combined_bytes).hexdigest(),
        "source_records": source_records,
        "raw_source_files_modified": False,
        "human_review_required": True,
    }
    intake_text = json.dumps(report, indent=2, sort_keys=True) + "\n"

    combined.parent.mkdir(parents=True, exist_ok=True)
    intake.parent.mkdir(parents=True, exist_ok=True)
    with combined.open("xb") as stream:
        stream.write(combined_bytes)
    try:
        with intake.open("x", encoding="utf-8") as stream:
            stream.write(intake_text)
    except Exception:
        combined.unlink(missing_ok=True)
        raise
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="existing private cohort workspace created by prepare_pilot.py",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = assemble_workspace(args.workspace)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace intake failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
