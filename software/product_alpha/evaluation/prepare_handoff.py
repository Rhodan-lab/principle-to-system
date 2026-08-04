#!/usr/bin/env python3
"""Prepare and verify a de-identified Product Alpha repository handoff candidate."""

from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
from typing import Any, Sequence

import prepare_review
import record_decision

CONTRACT = "principia-product-alpha-repository-handoff/0.1"
VERIFICATION_CONTRACT = "principia-product-alpha-repository-handoff-verification/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]
SAFE_SUMMARY_KEYS = {
    "contract",
    "pilot_build_id",
    "route_id",
    "sessions",
    "minimum_cohort_size",
    "cohort_complete",
    "observation_mode",
    "roadmap_gate",
    "decision_authority",
    "started",
    "finished",
    "completion_rate",
    "average_duration_minutes",
    "score_averages",
    "confusion_counts",
    "voluntary_continue",
    "revision_signals",
    "evidence_status",
}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def _output_paths(
    output_prefix: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> tuple[Path, Path]:
    expanded = output_prefix.expanduser()
    prefix = expanded.parent.resolve(strict=False) / expanded.name
    json_path = prefix.with_suffix(".json")
    markdown_path = prefix.with_suffix(".md")
    repository = repo_root.resolve(strict=False)
    for path in (json_path, markdown_path):
        if _is_within(path, repository):
            raise ValueError(
                "handoff candidates must be prepared outside the repository for "
                "separate human review"
            )
    return json_path, markdown_path


def _regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    return path.read_bytes()


def _canonical_object(raw: bytes, label: str) -> dict[str, Any]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one JSON object")
    if raw != prepare_review.canonical_json(value):
        raise ValueError(f"{label} is not canonical JSON")
    return value


def _review_packet(readiness: dict[str, object]) -> dict[str, Any]:
    review_path = Path(str(readiness["review_json"]))
    raw = _regular_bytes(review_path, "review packet JSON")
    packet = _canonical_object(raw, "review packet JSON")
    summary = packet.get("aggregate_summary")
    review = packet.get("review")
    boundaries = packet.get("boundaries")
    if not isinstance(summary, dict) or set(summary) != SAFE_SUMMARY_KEYS:
        raise ValueError("review packet aggregate summary fields are not handoff-safe")
    if not isinstance(review, dict):
        raise ValueError("review packet review must be an object")
    for key, expected in (
        ("planning_review_eligible", False),
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if review.get(key) is not expected:
            raise ValueError(f"review packet advisory field {key!r} is invalid")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")
    required_false = (
        "raw_session_records_included",
        "facilitator_notes_included",
        "custom_confusion_tag_text_included",
        "automatic_product_decision",
        "automatic_repository_mutation",
        "second_route_authorized",
        "public_release_authorized",
        "learning_effectiveness_claimed",
        "product_market_fit_claimed",
    )
    for key in required_false:
        if boundaries.get(key) is not False:
            raise ValueError(f"review packet boundary {key!r} must be false")
    return packet


def build_handoff_candidate(workspace: Path) -> dict[str, object]:
    """Verify the private decision chain and return a safe repository candidate."""
    decision = record_decision.verify_workspace_decision(workspace)
    readiness = record_decision.validate_review_ready(workspace)
    packet = _review_packet(readiness)
    summary = packet["aggregate_summary"]
    if not isinstance(summary, dict):
        raise ValueError("review packet aggregate summary must be an object")

    return {
        "contract": CONTRACT,
        "decision": "repository-handoff-candidate-prepared",
        "pilot_build_id": decision["pilot_build_id"],
        "route_id": decision["route_id"],
        "evidence_status": decision["evidence_status"],
        "sessions": decision["sessions"],
        "primary_action": decision["primary_action"],
        "planning_review_action_selected": decision[
            "planning_review_action_selected"
        ],
        "advisory_only": True,
        "roadmap_gate": False,
        "decision_authority": False,
        "aggregate_summary": copy.deepcopy(summary),
        "evidence_binding": {
            "decision_record_sha256": decision["decision_record_sha256"],
            "decision_markdown_sha256": decision["decision_markdown_sha256"],
            "decision_receipt_sha256": decision["decision_receipt_sha256"],
            "review_json_sha256": decision["review_json_sha256"],
            "review_markdown_sha256": decision["review_markdown_sha256"],
            "combined_sha256": decision["combined_sha256"],
            "intake_manifest_sha256": decision["intake_manifest_sha256"],
            "source_records_sha256": decision["source_records_sha256"],
            "source_record_count": readiness["source_record_count"],
            "raw_sources_verified": True,
        },
        "boundaries": {
            "human_decision_verified": True,
            "advisory_only": True,
            "roadmap_gate": False,
            "decision_authority": False,
            "raw_session_records_included": False,
            "session_identifiers_included": False,
            "facilitator_notes_included": False,
            "custom_confusion_tag_text_included": False,
            "reviewer_identity_included": False,
            "review_date_included": False,
            "human_rationale_included": False,
            "next_checkpoint_text_included": False,
            "local_workspace_paths_included": False,
            "automatic_product_decision": False,
            "automatic_repository_mutation": False,
            "repository_change_authorized": False,
            "second_route_authorized": False,
            "public_release_authorized": False,
            "learning_effectiveness_claimed": False,
            "product_market_fit_claimed": False,
        },
    }


def render_markdown(candidate: dict[str, object]) -> str:
    summary = candidate.get("aggregate_summary")
    binding = candidate.get("evidence_binding")
    boundaries = candidate.get("boundaries")
    if not isinstance(summary, dict):
        raise ValueError("handoff aggregate_summary must be an object")
    if not isinstance(binding, dict):
        raise ValueError("handoff evidence_binding must be an object")
    if not isinstance(boundaries, dict):
        raise ValueError("handoff boundaries must be an object")
    scores = summary.get("score_averages")
    confusion = summary.get("confusion_counts")
    continuation = summary.get("voluntary_continue")
    signals = summary.get("revision_signals")
    if not isinstance(scores, dict):
        raise ValueError("handoff score_averages must be an object")
    if not isinstance(confusion, dict):
        raise ValueError("handoff confusion_counts must be an object")
    if not isinstance(continuation, dict):
        raise ValueError("handoff voluntary_continue must be an object")
    if not isinstance(signals, list):
        raise ValueError("handoff revision_signals must be a list")

    lines = [
        "# Product Alpha Repository Handoff Candidate",
        "",
        f"- Contract: `{candidate['contract']}`",
        f"- Pilot build ID: `{candidate['pilot_build_id']}`",
        f"- Route: `{candidate['route_id']}`",
        f"- Evidence status: **{candidate['evidence_status']}**",
        f"- Valid observations: {candidate['sessions']}",
        f"- Verified advisory action: `{candidate['primary_action']}`",
        (
            "- Planning-review action selected: **"
            f"{str(candidate['planning_review_action_selected']).lower()}**"
        ),
        f"- Decision receipt SHA-256: `{binding['decision_receipt_sha256']}`",
        f"- Review JSON SHA-256: `{binding['review_json_sha256']}`",
        f"- Intake manifest SHA-256: `{binding['intake_manifest_sha256']}`",
        f"- Source-record set SHA-256: `{binding['source_records_sha256']}`",
        "",
        "> This candidate is de-identified advisory context for the internal "
        "multi-perspective review. It is not roadmap authority, a repository-change "
        "authorization, a publication action, or proof of learning effectiveness.",
        "",
        "## Aggregate evidence",
        "",
        f"- Started: {summary['started']}",
        f"- Finished: {summary['finished']}",
        f"- Completion rate: {float(summary['completion_rate']):.1%}",
        (
            "- Average duration: "
            f"{float(summary['average_duration_minutes']):.2f} minutes"
        ),
        "",
        "### Learning scores",
        "",
        "| Measure | Average (0–2) |",
        "| --- | ---: |",
    ]
    for key, value in scores.items():
        lines.append(f"| {str(key).replace('_', ' ').title()} | {float(value):.2f} |")

    lines.extend(["", "### Confusion signals", ""])
    if confusion:
        for tag, count in confusion.items():
            lines.append(f"- `{tag}`: {count}")
    else:
        lines.append("- None recorded")

    lines.extend(
        [
            "",
            "### Voluntary continuation",
            "",
            f"- Yes: {continuation['yes']}",
            f"- No: {continuation['no']}",
            f"- Unknown: {continuation['unknown']}",
            (
                "- Yes rate among answered: "
                f"{float(continuation['yes_rate_among_answered']):.1%}"
            ),
            "",
            "## Revision signals",
            "",
        ]
    )
    if signals:
        for signal in signals:
            if not isinstance(signal, dict):
                raise ValueError("handoff revision signal must be an object")
            lines.append(f"- `{signal['code']}` — {signal['message']}")
    else:
        lines.append(
            "- No automatic revision trigger was detected. The internal "
            "multi-perspective review remains the product decision authority."
        )

    lines.extend(
        [
            "",
            "## Privacy and authority boundary",
            "",
            "This candidate excludes raw sessions, anonymous session identifiers, "
            "facilitator notes, custom confusion-tag text, reviewer identity, review "
            "date, private rationale, checkpoint text, and local workspace paths.",
            "",
            "It does not mutate the repository, authorize a repository change, authorize "
            "another route or public release, prove learning effectiveness, or establish "
            "product-market fit. Copying any part into the repository requires a separate "
            "human review and normal pull-request validation.",
            "",
        ]
    )
    return "\n".join(lines)


def check_handoff(
    workspace: Path,
    output_prefix: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    json_path, markdown_path = _output_paths(output_prefix, repo_root=repo_root)
    output_states = (
        prepare_review.path_present(json_path),
        prepare_review.path_present(markdown_path),
    )
    if any(output_states) and not all(output_states):
        raise ValueError("handoff output pair is incomplete")

    candidate = build_handoff_candidate(workspace)
    outputs_complete = all(output_states)
    return {
        "contract": CONTRACT,
        "decision": "repository-handoff-candidate-ready",
        "pilot_build_id": candidate["pilot_build_id"],
        "route_id": candidate["route_id"],
        "evidence_status": candidate["evidence_status"],
        "sessions": candidate["sessions"],
        "primary_action": candidate["primary_action"],
        "output_json": str(json_path),
        "output_markdown": str(markdown_path),
        "outputs_exist": outputs_complete,
        "outputs_complete": outputs_complete,
        "candidate_sha256": prepare_review.sha256(
            prepare_review.canonical_json(candidate)
        ),
        "writes_performed": False,
        "automatic_repository_mutation": False,
    }


def write_handoff(
    workspace: Path,
    output_prefix: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    candidate = build_handoff_candidate(workspace)
    json_path, markdown_path = _output_paths(output_prefix, repo_root=repo_root)
    for path in (json_path, markdown_path):
        if prepare_review.path_present(path):
            raise FileExistsError(f"refusing to overwrite existing handoff output: {path}")

    json_bytes = prepare_review.canonical_json(candidate)
    markdown_bytes = render_markdown(candidate).encode("utf-8")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    temporary_paths = (
        json_path.with_name(f".{json_path.name}.tmp-{os.getpid()}"),
        markdown_path.with_name(f".{markdown_path.name}.tmp-{os.getpid()}"),
    )
    for path in temporary_paths:
        if prepare_review.path_present(path):
            raise FileExistsError(f"temporary handoff output already exists: {path}")

    staged: list[Path] = []
    published: list[Path] = []
    try:
        with temporary_paths[0].open("xb") as stream:
            staged.append(temporary_paths[0])
            stream.write(json_bytes)
        with temporary_paths[1].open("xb") as stream:
            staged.append(temporary_paths[1])
            stream.write(markdown_bytes)
        prepare_review.publish_exclusive(temporary_paths[0], json_path)
        published.append(json_path)
        prepare_review.publish_exclusive(temporary_paths[1], markdown_path)
        published.append(markdown_path)
    except Exception:
        for path in reversed(published):
            path.unlink(missing_ok=True)
        raise
    finally:
        for path in reversed(staged):
            path.unlink(missing_ok=True)

    return {
        "contract": CONTRACT,
        "decision": "repository-handoff-candidate-created",
        "pilot_build_id": candidate["pilot_build_id"],
        "route_id": candidate["route_id"],
        "evidence_status": candidate["evidence_status"],
        "sessions": candidate["sessions"],
        "primary_action": candidate["primary_action"],
        "output_json": str(json_path),
        "output_markdown": str(markdown_path),
        "candidate_sha256": prepare_review.sha256(json_bytes),
        "markdown_sha256": prepare_review.sha256(markdown_bytes),
        "automatic_repository_mutation": False,
    }


def verify_handoff(
    workspace: Path,
    output_prefix: Path,
    *,
    repo_root: Path = REPO_ROOT,
) -> dict[str, object]:
    expected = build_handoff_candidate(workspace)
    json_path, markdown_path = _output_paths(output_prefix, repo_root=repo_root)
    exists = (
        prepare_review.path_present(json_path),
        prepare_review.path_present(markdown_path),
    )
    if any(exists) and not all(exists):
        raise ValueError("handoff output pair is incomplete")
    if not all(exists):
        raise ValueError("handoff outputs do not exist")

    json_bytes = _regular_bytes(json_path, "handoff JSON")
    markdown_bytes = _regular_bytes(markdown_path, "handoff Markdown")
    actual = _canonical_object(json_bytes, "handoff JSON")
    if actual != expected:
        raise ValueError("handoff JSON does not match the current verified decision chain")
    expected_markdown = render_markdown(expected).encode("utf-8")
    if markdown_bytes != expected_markdown:
        raise ValueError("handoff Markdown does not match the canonical candidate")

    return {
        "contract": VERIFICATION_CONTRACT,
        "decision": "repository-handoff-candidate-verified",
        "pilot_build_id": expected["pilot_build_id"],
        "route_id": expected["route_id"],
        "evidence_status": expected["evidence_status"],
        "sessions": expected["sessions"],
        "primary_action": expected["primary_action"],
        "output_json": str(json_path),
        "output_markdown": str(markdown_path),
        "candidate_sha256": prepare_review.sha256(json_bytes),
        "markdown_sha256": prepare_review.sha256(markdown_bytes),
        "writes_performed": False,
        "automatic_repository_mutation": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("prepare", "check", "verify"),
        default="prepare",
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--output-prefix", type=Path, required=True)
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "check":
            report = check_handoff(args.workspace, args.output_prefix)
        elif args.command == "verify":
            report = verify_handoff(args.workspace, args.output_prefix)
        else:
            report = write_handoff(args.workspace, args.output_prefix)
    except (OSError, ValueError) as exc:
        raise SystemExit(f"repository handoff failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
