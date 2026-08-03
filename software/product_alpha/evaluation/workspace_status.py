#!/usr/bin/env python3
"""Report the current Product Alpha workspace stage and next valid action."""

from __future__ import annotations

import argparse
import json
import shlex
import sys
from pathlib import Path
from typing import Any, Sequence

PRODUCT_ALPHA_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ALPHA_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ALPHA_ROOT))
import route_identity

import assemble_workspace
import prepare_handoff
import prepare_review
import record_decision
import review_workspace

CONTRACT = "principia-product-alpha-workspace-status/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]


def _shell_command(parts: Sequence[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def _workspace_command(script: str, workspace: Path, *arguments: str) -> str:
    return _shell_command(
        (
            "python3",
            f"software/product_alpha/evaluation/{script}",
            *arguments,
            "--workspace",
            str(workspace),
        )
    )


def _handoff_command(
    workspace: Path,
    output_prefix: Path,
    command: str,
) -> str:
    return _shell_command(
        (
            "python3",
            "software/product_alpha/evaluation/prepare_handoff.py",
            command,
            "--workspace",
            str(workspace),
            "--output-prefix",
            str(output_prefix),
        )
    )


def _launch_command(workspace: Path) -> str:
    return _shell_command(
        (
            "python3",
            "software/product_alpha/launch_workspace.py",
            "--workspace",
            str(workspace),
            "--open",
        )
    )


def _paired_state(paths: Sequence[Path], label: str) -> bool:
    states = [prepare_review.path_present(path) for path in paths]
    if any(states) and not all(states):
        raise ValueError(f"{label} is incomplete")
    return all(states)


def _verified_cohort_complete(report: dict[str, object], label: str) -> bool:
    value = report.get("cohort_complete")
    if not isinstance(value, bool):
        raise ValueError(f"{label} cohort_complete must be boolean")
    return value


def _decision_paths(review_prefix: Path) -> tuple[Path, Path, Path]:
    expanded = review_prefix.expanduser()
    prefix = expanded.parent.resolve(strict=False) / expanded.name
    return (
        Path(f"{prefix}-decision.json"),
        Path(f"{prefix}-decision.md"),
        Path(f"{prefix}-decision-receipt.json"),
    )


def _artifact_state(
    combined: Path,
    intake: Path,
    review_json: Path,
    review_markdown: Path,
    decision_paths: Sequence[Path],
    handoff_paths: Sequence[Path],
) -> dict[str, bool]:
    return {
        "combined_jsonl": prepare_review.path_present(combined),
        "intake_manifest": prepare_review.path_present(intake),
        "review_json": prepare_review.path_present(review_json),
        "review_markdown": prepare_review.path_present(review_markdown),
        "decision_json": prepare_review.path_present(decision_paths[0]),
        "decision_markdown": prepare_review.path_present(decision_paths[1]),
        "decision_receipt": prepare_review.path_present(decision_paths[2]),
        "handoff_json": prepare_review.path_present(handoff_paths[0]),
        "handoff_markdown": prepare_review.path_present(handoff_paths[1]),
    }


def _base_report(
    root: Path,
    manifest: dict[str, Any],
    artifacts: dict[str, bool],
) -> dict[str, object]:
    return {
        "contract": CONTRACT,
        "decision": "workspace-status-reported",
        "workspace": str(root),
        "workspace_contract": manifest["contract"],
        "pilot_build_id": manifest["pilot_build_id"],
        "route_id": manifest["route_id"],
        "artifacts": artifacts,
        "writes_performed": False,
        "automatic_repository_mutation": False,
        "human_review_required": True,
        "observation_mode": "optional-descriptive",
        "roadmap_gate": False,
        "decision_authority": False,
    }


def inspect_workspace(
    workspace: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    """Verify the current stage and return one read-only next-action report."""
    root = workspace.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be a directory")
    repository = repo_root.resolve(strict=False)
    if assemble_workspace._is_within(root, repository):
        raise ValueError("workspace must be outside the repository")

    manifest, incoming, combined, intake = assemble_workspace._load_workspace(root)
    if incoming.is_symlink() or not incoming.is_dir():
        raise ValueError("incoming session directory must be a regular directory")
    paths = manifest.get("paths")
    if not isinstance(paths, dict):
        raise ValueError("workspace.json paths must be an object")
    route_id = route_identity.validate_evidence_route_id(manifest.get("route_id"))
    route_slug = route_identity.software_route_id(route_id)
    review_prefix = assemble_workspace._member(
        root,
        paths.get("review_output_prefix"),
        "review_output_prefix",
    )
    review_json = review_prefix.with_suffix(".json")
    review_markdown = review_prefix.with_suffix(".md")
    decision_paths = _decision_paths(review_prefix)
    handoff_prefix = root / "handoff" / f"{route_slug}-product-change"
    handoff_paths = prepare_handoff._output_paths(
        handoff_prefix,
        repo_root=repo_root,
    )
    artifacts = _artifact_state(
        combined,
        intake,
        review_json,
        review_markdown,
        decision_paths,
        handoff_paths,
    )
    report = _base_report(root, manifest, artifacts)

    intake_complete = _paired_state((combined, intake), "verified intake pair")
    review_complete = _paired_state(
        (review_json, review_markdown),
        "review packet pair",
    )
    decision_complete = _paired_state(decision_paths, "decision artifact trio")
    handoff_complete = _paired_state(handoff_paths, "repository handoff pair")

    if not intake_complete:
        if review_complete or decision_complete or handoff_complete:
            raise ValueError("downstream artifacts exist before immutable intake")
        entries = sorted(incoming.iterdir(), key=lambda path: path.name)
        if not entries:
            return {
                **report,
                "stage": "prepared",
                "sessions": 0,
                "minimum_cohort_size": assemble_workspace.pilot_summary.MIN_COHORT_SIZE,
                "cohort_complete": False,
                "evidence_status": "not-collected",
                "next_action": "collect-session-records",
                "next_command": _launch_command(root),
                "validation_command": _workspace_command(
                    "assemble_workspace.py",
                    root,
                    "check",
                ),
            }

        preflight = assemble_workspace.preflight_workspace(
            root,
            repo_root=repo_root,
        )
        return {
            **report,
            "stage": "ready-to-assemble",
            "sessions": preflight["sessions"],
            "minimum_cohort_size": preflight["minimum_cohort_size"],
            "cohort_complete": _verified_cohort_complete(preflight, "preflight"),
            "evidence_status": preflight["evidence_status"],
            "predicted_combined_sha256": preflight["predicted_combined_sha256"],
            "source_records_sha256": preflight["source_records_sha256"],
            "next_action": "assemble-immutable-intake",
            "next_command": _workspace_command("assemble_workspace.py", root),
            "validation_command": _workspace_command(
                "assemble_workspace.py",
                root,
                "check",
            ),
        }

    verification = review_workspace.verify_workspace_intake(
        root,
        repo_root=repo_root,
    )
    if not review_complete:
        if decision_complete or handoff_complete:
            raise ValueError("downstream artifacts exist before the review packet")
        return {
            **report,
            "stage": "intake-verified",
            "sessions": verification["sessions"],
            "cohort_complete": _verified_cohort_complete(
                verification,
                "workspace intake verification",
            ),
            "evidence_status": verification["evidence_status"],
            "combined_sha256": verification["combined_sha256"],
            "intake_manifest_sha256": verification["intake_manifest_sha256"],
            "source_records_sha256": verification["source_records_sha256"],
            "next_action": "create-review-packet",
            "next_command": _workspace_command("review_workspace.py", root),
            "validation_command": _workspace_command(
                "review_workspace.py",
                root,
                "check",
            ),
        }

    readiness = record_decision.validate_review_ready(root)
    verified_complete = _verified_cohort_complete(
        readiness,
        "advisory readiness",
    )
    if not decision_complete:
        if handoff_complete:
            raise ValueError("repository handoff exists before the human decision")
        return {
            **report,
            "stage": "review-ready-for-advisory",
            "sessions": readiness["sessions"],
            "cohort_complete": verified_complete,
            "evidence_status": readiness["evidence_status"],
            "planning_review_eligible": readiness["planning_review_eligible"],
            "review_json_sha256": readiness["review_json_sha256"],
            "review_markdown_sha256": readiness["review_markdown_sha256"],
            "next_action": "record-optional-advisory",
            "next_command": None,
            "next_command_template": _workspace_command(
                "record_decision.py",
                root,
                "--action",
                "<allowed-primary-action>",
                "--reviewer",
                "<role-or-initials>",
                "--review-date",
                "YYYY-MM-DD",
                "--rationale",
                "<de-identified-rationale>",
                "--next-checkpoint",
                "<next-checkpoint>",
            ),
            "validation_command": _workspace_command(
                "record_decision.py",
                root,
                "check",
            ),
        }

    decision = record_decision.verify_workspace_decision(root)
    action = str(decision["primary_action"])
    follow_up = "return-to-internal-multi-perspective-review"

    if not handoff_complete:
        return {
            **report,
            "stage": "advisory-verified",
            "sessions": decision["sessions"],
            "cohort_complete": verified_complete,
            "evidence_status": decision["evidence_status"],
            "primary_action": action,
            "planning_review_action_selected": decision[
                "planning_review_action_selected"
            ],
            "decision_record_sha256": decision["decision_record_sha256"],
            "decision_markdown_sha256": decision["decision_markdown_sha256"],
            "decision_receipt_sha256": decision["decision_receipt_sha256"],
            "post_handoff_action": follow_up,
            "handoff_output_prefix": str(handoff_prefix),
            "next_action": "prepare-deidentified-advisory-handoff",
            "next_command": _handoff_command(root, handoff_prefix, "prepare"),
            "validation_command": _handoff_command(root, handoff_prefix, "check"),
        }

    handoff = prepare_handoff.verify_handoff(
        root,
        handoff_prefix,
        repo_root=repo_root,
    )
    return {
        **report,
        "stage": "advisory-handoff-verified",
        "sessions": handoff["sessions"],
        "cohort_complete": verified_complete,
        "evidence_status": handoff["evidence_status"],
        "primary_action": action,
        "planning_review_action_selected": decision[
            "planning_review_action_selected"
        ],
        "decision_receipt_sha256": decision["decision_receipt_sha256"],
        "handoff_candidate_sha256": handoff["candidate_sha256"],
        "handoff_markdown_sha256": handoff["markdown_sha256"],
        "next_action": follow_up,
        "next_command": None,
        "validation_command": _handoff_command(root, handoff_prefix, "verify"),
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="private Product Alpha workspace outside the repository",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = inspect_workspace(args.workspace)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace status failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
