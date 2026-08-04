#!/usr/bin/env python3
"""Validate Product Alpha session exports before sealing one immutable cohort."""

from __future__ import annotations

import argparse
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence

import summarize as pilot_summary

CONTRACT = "principia-product-alpha-workspace-intake/0.1"
PREFLIGHT_CONTRACT = "principia-product-alpha-workspace-intake-preflight/0.1"
WORKSPACE_CONTRACT = "principia-product-alpha-pilot-workspace/0.1"
ALLOWED_SOURCE_SUFFIXES = {".json", ".jsonl"}
MAX_INCOMING_ENTRIES = pilot_summary.MAX_SESSION_RECORDS
MAX_SOURCE_FILE_BYTES = pilot_summary.MAX_INPUT_BYTES
MAX_TOTAL_SOURCE_BYTES = pilot_summary.MAX_INPUT_BYTES
MAX_JSON_OBJECT_BYTES = pilot_summary.MAX_INPUT_BYTES
MAX_COMBINED_BYTES = pilot_summary.MAX_INPUT_BYTES
REPO_ROOT = Path(__file__).resolve().parents[3]


@dataclass(frozen=True)
class WorkspaceIntakePlan:
    root: Path
    manifest: dict[str, Any]
    incoming: Path
    combined: Path
    intake: Path
    sessions: tuple[dict[str, Any], ...]
    source_records: tuple[dict[str, str], ...]
    combined_bytes: bytes
    summary: dict[str, Any]

    @property
    def combined_sha256(self) -> str:
        return hashlib.sha256(self.combined_bytes).hexdigest()

    @property
    def source_records_sha256(self) -> str:
        return hashlib.sha256(_canonical_json(list(self.source_records))).hexdigest()


def _canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _read_bounded_bytes(path: Path, label: str, limit: int) -> bytes:
    with path.open("rb") as stream:
        raw = stream.read(limit + 1)
    if len(raw) > limit:
        raise ValueError(f"{label}: exceeds the {limit}-byte limit")
    return raw


def _decode_strict_json(raw: bytes, label: str) -> Any:
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label}: must be UTF-8") from exc
    try:
        return json.loads(
            text,
            object_pairs_hook=pilot_summary._object_without_duplicates,
            parse_constant=pilot_summary._reject_nonfinite_constant,
        )
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label}: invalid JSON: {exc.msg}") from exc
    except ValueError as exc:
        raise ValueError(f"{label}: invalid JSON: {exc}") from exc


def _read_json_object(path: Path, label: str) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label}: must be a regular file")
    raw = _read_bounded_bytes(path, label, MAX_JSON_OBJECT_BYTES)
    value = _decode_strict_json(raw, label)
    if not isinstance(value, dict):
        raise ValueError(f"{label}: must contain one JSON object")
    return value


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _path_present(path: Path) -> bool:
    """Return whether a filesystem entry exists, including a broken symlink."""
    return path.is_symlink() or path.exists()


def _member(workspace: Path, relative: object, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip():
        raise ValueError(f"workspace manifest {label} path must be non-empty text")
    path_text = relative.strip()
    if "\\" in path_text:
        raise ValueError(
            f"workspace manifest {label} path must use normalized relative components"
        )
    components = path_text.split("/")
    if any(component in {"", ".", ".."} for component in components):
        raise ValueError(
            f"workspace manifest {label} path must use normalized relative components"
        )

    relative_path = Path(path_text)
    if relative_path.is_absolute():
        raise ValueError(f"workspace manifest {label} path must be relative")

    unresolved = workspace / relative_path
    candidate = unresolved.parent.resolve(strict=False) / unresolved.name
    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise ValueError(
            f"workspace manifest {label} path escapes the workspace"
        ) from exc
    return candidate


def _validate_workspace_path_layout(
    incoming: Path,
    combined: Path,
    intake: Path,
    review_prefix: Path,
) -> None:
    review_json = review_prefix.with_suffix(".json")
    review_markdown = review_prefix.with_suffix(".md")
    artifacts = (combined, intake, review_json, review_markdown)
    if len(set(artifacts)) != len(artifacts):
        raise ValueError("workspace manifest artifact paths must be distinct")
    for artifact in artifacts:
        if _is_within(artifact, incoming):
            raise ValueError(
                "workspace manifest artifact paths must be outside incoming_sessions"
            )


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
    try:
        route_id = pilot_summary.route_identity.validate_evidence_route_id(
            manifest.get("route_id")
        )
    except ValueError as exc:
        raise ValueError(f"workspace.json {exc}") from exc
    manifest["route_id"] = route_id

    privacy = manifest.get("privacy_boundaries")
    if not isinstance(privacy, dict):
        raise ValueError("workspace.json privacy_boundaries must be an object")
    required_privacy = {
        "participant_names_allowed": False,
        "raw_sessions_committed_to_repository": False,
        "repository_output_allowed": False,
    }
    for key, expected in required_privacy.items():
        if privacy.get(key) is not expected:
            raise ValueError(
                f"workspace.json privacy boundary {key!r} must be false"
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
    review_prefix = _member(
        workspace,
        paths.get("review_output_prefix"),
        "review_output_prefix",
    )
    _validate_workspace_path_layout(
        incoming,
        combined,
        intake,
        review_prefix,
    )
    return manifest, incoming, combined, intake


def _incoming_entries(incoming: Path) -> list[Path]:
    entries: list[Path] = []
    for count, path in enumerate(incoming.iterdir(), 1):
        if count > MAX_INCOMING_ENTRIES:
            raise ValueError(
                "incoming session directory contains more than "
                f"{MAX_INCOMING_ENTRIES} entries"
            )
        entries.append(path)
    entries.sort(key=lambda path: path.name)
    if not entries:
        raise ValueError("incoming session directory contains no exports")
    return entries


def _build_plan(
    workspace: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> WorkspaceIntakePlan:
    root = workspace.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be a directory")
    repository = repo_root.resolve(strict=False)
    if _is_within(root, repository):
        raise ValueError("workspace must be outside the repository")

    manifest, incoming, combined, intake = _load_workspace(root)
    if incoming.is_symlink() or not incoming.is_dir():
        raise ValueError("incoming session directory must be a regular directory")

    entries = _incoming_entries(incoming)
    sessions: list[dict[str, Any]] = []
    source_records: list[dict[str, str]] = []
    seen_ids: set[str] = set()
    total_source_bytes = 0

    for path in entries:
        if path.is_symlink() or not path.is_file():
            raise ValueError(f"unexpected incoming entry: {path.name}")
        if path.suffix.lower() not in ALLOWED_SOURCE_SUFFIXES:
            raise ValueError(f"unsupported incoming file type: {path.name}")

        raw = _read_bounded_bytes(path, path.name, MAX_SOURCE_FILE_BYTES)
        total_source_bytes += len(raw)
        if total_source_bytes > MAX_TOTAL_SOURCE_BYTES:
            raise ValueError(
                "incoming session exports exceed the "
                f"{MAX_TOTAL_SOURCE_BYTES}-byte total limit"
            )
        value = _decode_strict_json(raw, path.name)
        if not isinstance(value, dict):
            raise ValueError(
                f"{path.name}: session export must contain one JSON object"
            )

        try:
            session = pilot_summary.validate_session(
                value, 1, str(manifest["route_id"])
            )
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
    if len(combined_bytes) > MAX_COMBINED_BYTES:
        raise ValueError(
            f"canonical combined cohort exceeds the {MAX_COMBINED_BYTES}-byte limit"
        )
    summary = pilot_summary.summarize(sessions)

    return WorkspaceIntakePlan(
        root=root,
        manifest=manifest,
        incoming=incoming,
        combined=combined,
        intake=intake,
        sessions=tuple(sessions),
        source_records=tuple(source_records),
        combined_bytes=combined_bytes,
        summary=summary,
    )


def _intake_report(plan: WorkspaceIntakePlan) -> dict[str, object]:
    return {
        "contract": CONTRACT,
        "decision": "workspace-intake-assembled",
        "pilot_build_id": plan.manifest["pilot_build_id"],
        "route_id": plan.manifest["route_id"],
        "workspace": str(plan.root),
        "sessions": len(plan.sessions),
        "minimum_cohort_size": pilot_summary.MIN_COHORT_SIZE,
        "cohort_complete": bool(plan.summary["cohort_complete"]),
        "evidence_status": plan.summary["evidence_status"],
        "summary_contract": plan.summary["contract"],
        "combined_jsonl": str(plan.combined),
        "combined_sha256": plan.combined_sha256,
        "source_records_sha256": plan.source_records_sha256,
        "source_records": list(plan.source_records),
        "incomplete_assembly_authorized": False,
        "observation_mode": "optional-descriptive",
        "roadmap_gate": False,
        "decision_authority": False,
        "raw_source_files_modified": False,
        "human_review_required": True,
    }


def _verified_output_state(plan: WorkspaceIntakePlan) -> dict[str, bool]:
    states = {
        "combined_jsonl": _path_present(plan.combined),
        "intake_manifest": _path_present(plan.intake),
    }
    if any(states.values()) and not all(states.values()):
        raise ValueError("verified intake output pair is incomplete")
    if not all(states.values()):
        return states

    if plan.combined.is_symlink() or not plan.combined.is_file():
        raise ValueError("existing combined cohort must be a regular file")
    existing_combined = _read_bounded_bytes(
        plan.combined,
        "existing combined cohort",
        MAX_COMBINED_BYTES,
    )
    if existing_combined != plan.combined_bytes:
        raise ValueError("existing combined cohort does not match current raw exports")

    existing_intake = _read_json_object(
        plan.intake,
        "existing intake manifest",
    )
    if existing_intake != _intake_report(plan):
        raise ValueError("existing intake manifest does not match current intake prediction")
    return states


def preflight_workspace(
    workspace: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    """Validate all incoming exports and predict immutable intake bytes without writing."""
    plan = _build_plan(workspace, repo_root=repo_root)
    complete = bool(plan.summary["cohort_complete"])
    output_state = _verified_output_state(plan)
    return {
        "contract": PREFLIGHT_CONTRACT,
        "decision": "workspace-intake-preflight-passed",
        "pilot_build_id": plan.manifest["pilot_build_id"],
        "route_id": plan.manifest["route_id"],
        "workspace": str(plan.root),
        "sessions": len(plan.sessions),
        "minimum_cohort_size": pilot_summary.MIN_COHORT_SIZE,
        "cohort_complete": complete,
        "evidence_status": plan.summary["evidence_status"],
        "summary_contract": plan.summary["contract"],
        "combined_jsonl": str(plan.combined),
        "intake_manifest": str(plan.intake),
        "predicted_combined_sha256": plan.combined_sha256,
        "source_records_sha256": plan.source_records_sha256,
        "source_records": list(plan.source_records),
        "verified_outputs_exist": output_state,
        "verified_outputs_match_prediction": all(output_state.values()),
        "ready_for_default_assembly": complete and not any(output_state.values()),
        "incomplete_assembly_requires_override": not complete,
        "writes_performed": False,
        "raw_source_files_modified": False,
        "human_review_required": True,
        "observation_mode": "optional-descriptive",
        "roadmap_gate": False,
        "decision_authority": False,
    }


def assemble_workspace(
    workspace: Path,
    *,
    allow_incomplete: bool = False,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    """Validate private exports and write one immutable cohort intake."""
    plan = _build_plan(workspace, repo_root=repo_root)

    if _path_present(plan.combined):
        raise FileExistsError(f"combined cohort already exists: {plan.combined}")
    if _path_present(plan.intake):
        raise FileExistsError(f"intake manifest already exists: {plan.intake}")

    report = _intake_report(plan)
    intake_text = json.dumps(report, indent=2, sort_keys=True) + "\n"

    plan.combined.parent.mkdir(parents=True, exist_ok=True)
    plan.intake.parent.mkdir(parents=True, exist_ok=True)
    try:
        with plan.combined.open("xb") as stream:
            stream.write(plan.combined_bytes)
        with plan.intake.open("x", encoding="utf-8") as stream:
            stream.write(intake_text)
    except Exception:
        plan.combined.unlink(missing_ok=True)
        plan.intake.unlink(missing_ok=True)
        raise
    return report


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("assemble", "check"),
        default="assemble",
        help="assemble immutable intake or validate and predict it without writing",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="existing private cohort workspace created by prepare_pilot.py",
    )
    parser.add_argument(
        "--allow-incomplete",
        action="store_true",
        help="deprecated compatibility flag; optional observation has no minimum",
    )
    args = parser.parse_args(argv)
    if args.command == "check" and args.allow_incomplete:
        parser.error("--allow-incomplete is only valid for assemble")
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "check":
            report = preflight_workspace(args.workspace)
        else:
            report = assemble_workspace(
                args.workspace,
                allow_incomplete=args.allow_incomplete,
            )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace intake failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
