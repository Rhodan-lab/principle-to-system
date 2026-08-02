#!/usr/bin/env python3
"""Verify a Product Alpha workspace intake and create its bound review packet."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import assemble_workspace
import prepare_review
import verify_cohort

CONTRACT = "principia-product-alpha-workspace-review/0.1"
INTAKE_CONTRACT = "principia-product-alpha-workspace-intake/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _read_json_object(path: Path, label: str) -> tuple[dict[str, Any], bytes]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    raw = path.read_bytes()
    try:
        value = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one JSON object")
    return value, raw


def _validate_hash(value: object, label: str) -> str:
    if (
        not isinstance(value, str)
        or len(value) != 64
        or any(character not in "0123456789abcdef" for character in value)
    ):
        raise ValueError(f"{label} must be a 64-character lowercase SHA-256")
    return value


def _source_records(
    incoming: Path,
    expected_build_id: str,
) -> list[dict[str, str]]:
    if not incoming.is_dir():
        raise ValueError("incoming session directory is missing")
    entries = sorted(incoming.iterdir(), key=lambda path: path.name)
    if not entries:
        raise ValueError("incoming session directory contains no exports")

    records: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for path in entries:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unexpected incoming entry: {path.name}")
        if path.suffix.lower() not in assemble_workspace.ALLOWED_SOURCE_SUFFIXES:
            raise ValueError(f"unsupported incoming file type: {path.name}")
        raw = path.read_bytes()
        try:
            value = json.loads(raw.decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise ValueError(f"{path.name}: file must be UTF-8") from exc
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path.name}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path.name}: session export must contain one JSON object")
        try:
            session = verify_cohort.pilot_summary.validate_session(value, 1)
        except ValueError as exc:
            detail = str(exc).removeprefix("line 1: ")
            raise ValueError(f"{path.name}: {detail}") from exc
        if session["pilot_build_id"] != expected_build_id:
            raise ValueError(
                f"{path.name}: pilot_build_id does not match workspace build"
            )
        session_id = session["session_id"]
        if session_id in seen_ids:
            raise ValueError(f"{path.name}: duplicate session_id {session_id!r}")
        seen_ids.add(session_id)
        records.append(
            {
                "session_id": session_id,
                "sha256": _sha256(raw),
            }
        )
    return sorted(records, key=lambda item: item["session_id"])


def _intake_source_records(value: object) -> list[dict[str, str]]:
    if not isinstance(value, list) or not value:
        raise ValueError("intake manifest source_records must be a non-empty list")
    records: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, dict) or set(item) != {"session_id", "sha256"}:
            raise ValueError(
                f"intake manifest source record {index} must contain session_id and sha256"
            )
        session_id = item.get("session_id")
        if not isinstance(session_id, str) or not session_id.startswith("anonymous-"):
            raise ValueError(
                f"intake manifest source record {index} has an invalid session_id"
            )
        if session_id in seen_ids:
            raise ValueError(
                f"intake manifest source_records duplicate session_id {session_id!r}"
            )
        seen_ids.add(session_id)
        records.append(
            {
                "session_id": session_id,
                "sha256": _validate_hash(
                    item.get("sha256"),
                    f"intake manifest source record {index} sha256",
                ),
            }
        )
    return sorted(records, key=lambda item: item["session_id"])


def verify_workspace_intake(
    workspace: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    """Verify workspace, raw sources, intake manifest, combined bytes, and summary."""
    root = workspace.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be a directory")
    repository = repo_root.resolve(strict=False)
    if assemble_workspace._is_within(root, repository):
        raise ValueError("workspace must be outside the repository")
    workspace_manifest_path = root / "workspace.json"
    if workspace_manifest_path.is_symlink() or not workspace_manifest_path.is_file():
        raise ValueError("workspace.json must be a regular file")

    manifest, incoming, combined, intake_path = assemble_workspace._load_workspace(root)
    paths = manifest.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("workspace.json paths must be an object")
    review_prefix = assemble_workspace._member(
        root,
        paths.get("review_output_prefix"),
        "review_output_prefix",
    )

    intake, intake_bytes = _read_json_object(
        intake_path,
        "verified intake manifest",
    )
    if intake.get("contract") != INTAKE_CONTRACT:
        raise ValueError(f"intake manifest contract must be {INTAKE_CONTRACT!r}")
    if intake.get("decision") != "workspace-intake-assembled":
        raise ValueError("intake manifest decision must be 'workspace-intake-assembled'")
    if intake.get("workspace") != str(root):
        raise ValueError("intake manifest workspace does not match this workspace")
    if intake.get("pilot_build_id") != manifest["pilot_build_id"]:
        raise ValueError("intake manifest pilot_build_id does not match workspace")
    if intake.get("route_id") != manifest["route_id"]:
        raise ValueError("intake manifest route_id does not match workspace")
    if intake.get("combined_jsonl") != str(combined):
        raise ValueError("intake manifest combined_jsonl path does not match workspace")
    if intake.get("raw_source_files_modified") is not False:
        raise ValueError("intake manifest must declare raw_source_files_modified=false")
    if intake.get("human_review_required") is not True:
        raise ValueError("intake manifest must declare human_review_required=true")

    if combined.is_symlink() or not combined.is_file():
        raise ValueError("combined cohort must be a regular file")
    actual_combined_bytes = combined.read_bytes()
    expected_combined_sha256 = _validate_hash(
        intake.get("combined_sha256"),
        "intake manifest combined_sha256",
    )
    actual_combined_sha256 = _sha256(actual_combined_bytes)
    if actual_combined_sha256 != expected_combined_sha256:
        raise ValueError("combined cohort SHA-256 does not match intake manifest")

    expected_sources = _intake_source_records(intake.get("source_records"))
    actual_sources = _source_records(incoming, manifest["pilot_build_id"])
    if actual_sources != expected_sources:
        raise ValueError("raw incoming exports do not match intake manifest hashes")

    sessions = intake.get("sessions")
    if not isinstance(sessions, int) or isinstance(sessions, bool) or sessions < 1:
        raise ValueError("intake manifest sessions must be a positive integer")
    if sessions != len(expected_sources):
        raise ValueError("intake manifest sessions does not match source record count")

    summary = verify_cohort.verify_cohort(combined, manifest["pilot_build_id"])
    if summary["sessions"] != sessions:
        raise ValueError("verified cohort session count does not match intake manifest")
    if summary["route_id"] != manifest["route_id"]:
        raise ValueError("verified cohort route does not match workspace")
    if summary["contract"] != intake.get("summary_contract"):
        raise ValueError("verified summary contract does not match intake manifest")
    if summary["evidence_status"] != intake.get("evidence_status"):
        raise ValueError("verified evidence status does not match intake manifest")

    return {
        "contract": CONTRACT,
        "decision": "workspace-intake-verified",
        "workspace": str(root),
        "workspace_contract": manifest["contract"],
        "pilot_build_id": manifest["pilot_build_id"],
        "route_id": manifest["route_id"],
        "incoming": str(incoming),
        "combined_jsonl": str(combined),
        "intake_manifest": str(intake_path),
        "review_output_prefix": str(review_prefix),
        "sessions": sessions,
        "evidence_status": summary["evidence_status"],
        "summary_contract": summary["contract"],
        "combined_sha256": actual_combined_sha256,
        "intake_manifest_sha256": _sha256(intake_bytes),
        "source_records_sha256": _sha256(
            prepare_review.canonical_json(expected_sources)
        ),
        "source_record_count": len(expected_sources),
        "raw_sources_verified": True,
        "human_review_required": True,
    }


def prepare_workspace_review(workspace: Path) -> dict[str, object]:
    """Verify the workspace intake and write its bound private review packet."""
    verification = verify_workspace_intake(workspace)
    combined = Path(str(verification["combined_jsonl"]))
    output_prefix = Path(str(verification["review_output_prefix"]))
    packet = prepare_review.build_review_packet(
        combined,
        str(verification["pilot_build_id"]),
    )
    evidence = packet.get("evidence_binding")
    if not isinstance(evidence, dict):
        raise ValueError("review packet evidence_binding must be an object")
    evidence.update(
        {
            "workspace_contract": verification["workspace_contract"],
            "workspace_intake_contract": INTAKE_CONTRACT,
            "intake_manifest_sha256": verification["intake_manifest_sha256"],
            "source_records_sha256": verification["source_records_sha256"],
            "source_record_count": verification["source_record_count"],
            "raw_sources_verified": True,
        }
    )
    json_path, markdown_path, packet_sha256 = prepare_review.write_review_outputs(
        output_prefix,
        packet,
    )
    return {
        **verification,
        "decision": "workspace-review-packet-created",
        "review_json": str(json_path),
        "review_markdown": str(markdown_path),
        "review_packet_sha256": packet_sha256,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("prepare", "check"),
        default="prepare",
        help="prepare the review packet or only verify the workspace evidence chain",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="private cohort workspace with assembled verified evidence",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "check":
            report = verify_workspace_intake(args.workspace)
        else:
            report = prepare_workspace_review(args.workspace)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace review failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
