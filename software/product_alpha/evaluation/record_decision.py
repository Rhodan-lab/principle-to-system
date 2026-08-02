#!/usr/bin/env python3
"""Record one immutable human decision for a verified Product Alpha workspace review."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Any, Sequence

import prepare_review
import review_workspace

CONTRACT = "principia-product-alpha-human-decision/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]
REQUIRED_PACKET_BOUNDARIES = {
    "raw_session_records_included": False,
    "facilitator_notes_included": False,
    "custom_confusion_tag_text_included": False,
    "automatic_product_decision": False,
    "automatic_repository_mutation": False,
    "second_route_authorized": False,
    "public_release_authorized": False,
    "learning_effectiveness_claimed": False,
    "product_market_fit_claimed": False,
}


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _single_line(value: str, label: str, maximum: int) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{label} must not be empty")
    if "\n" in cleaned or "\r" in cleaned:
        raise ValueError(f"{label} must be a single line")
    if len(cleaned) > maximum:
        raise ValueError(f"{label} must be at most {maximum} characters")
    return cleaned


def _long_text(value: str, label: str, minimum: int, maximum: int) -> str:
    cleaned = value.strip()
    if len(cleaned) < minimum:
        raise ValueError(f"{label} must be at least {minimum} characters")
    if len(cleaned) > maximum:
        raise ValueError(f"{label} must be at most {maximum} characters")
    if any(ord(character) < 32 and character not in "\n\t" for character in cleaned):
        raise ValueError(f"{label} contains unsupported control characters")
    return cleaned


def _review_date(value: str) -> str:
    cleaned = _single_line(value, "review date", 10)
    try:
        parsed = dt.date.fromisoformat(cleaned)
    except ValueError as exc:
        raise ValueError("review date must use YYYY-MM-DD") from exc
    if parsed.isoformat() != cleaned:
        raise ValueError("review date must use YYYY-MM-DD")
    return cleaned


def _regular_bytes(path: Path, label: str) -> bytes:
    if path.is_symlink() or not path.is_file():
        raise ValueError(f"{label} must be a regular file")
    return path.read_bytes()


def _decision_paths(review_prefix: Path) -> tuple[Path, Path]:
    prefix = review_prefix.expanduser().resolve(strict=False)
    json_path = Path(f"{prefix}-decision.json")
    markdown_path = Path(f"{prefix}-decision.md")
    for path in (json_path, markdown_path):
        if _is_within(path, REPO_ROOT):
            raise ValueError("decision records must be written outside the repository")
    return json_path, markdown_path


def validate_review_ready(workspace: Path) -> dict[str, object]:
    """Verify the unchanged workspace evidence and untouched generated review pair."""
    verification = review_workspace.verify_workspace_intake(workspace)
    review_prefix = Path(str(verification["review_output_prefix"]))
    review_json = review_prefix.with_suffix(".json")
    review_markdown = review_prefix.with_suffix(".md")

    packet_raw = _regular_bytes(review_json, "review packet JSON")
    markdown_raw = _regular_bytes(review_markdown, "review packet Markdown")
    try:
        packet = json.loads(packet_raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError("review packet JSON must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"review packet JSON is invalid: {exc.msg}") from exc
    if not isinstance(packet, dict):
        raise ValueError("review packet JSON must contain one object")
    if packet_raw != prepare_review.canonical_json(packet):
        raise ValueError("review packet JSON is not the untouched canonical packet")
    expected_markdown = prepare_review.render_markdown(packet).encode("utf-8")
    if markdown_raw != expected_markdown:
        raise ValueError("review packet Markdown does not match the untouched packet")

    if packet.get("contract") != prepare_review.CONTRACT:
        raise ValueError(f"review packet contract must be {prepare_review.CONTRACT!r}")
    if packet.get("pilot_build_id") != verification["pilot_build_id"]:
        raise ValueError("review packet pilot_build_id does not match workspace")
    if packet.get("route_id") != verification["route_id"]:
        raise ValueError("review packet route_id does not match workspace")

    evidence = packet.get("evidence_binding")
    if not isinstance(evidence, dict):
        raise ValueError("review packet evidence_binding must be an object")
    expected_evidence = {
        "input_sha256": verification["combined_sha256"],
        "workspace_contract": verification["workspace_contract"],
        "workspace_intake_contract": review_workspace.INTAKE_CONTRACT,
        "intake_manifest_sha256": verification["intake_manifest_sha256"],
        "source_records_sha256": verification["source_records_sha256"],
        "source_record_count": verification["source_record_count"],
        "raw_sources_verified": True,
    }
    for key, expected in expected_evidence.items():
        if evidence.get(key) != expected:
            raise ValueError(f"review packet evidence binding {key!r} is inconsistent")

    summary = packet.get("aggregate_summary")
    if not isinstance(summary, dict):
        raise ValueError("review packet aggregate_summary must be an object")
    if summary.get("pilot_build_id") != verification["pilot_build_id"]:
        raise ValueError("review packet summary build does not match workspace")
    if summary.get("route_id") != verification["route_id"]:
        raise ValueError("review packet summary route does not match workspace")
    if summary.get("sessions") != verification["sessions"]:
        raise ValueError("review packet summary session count does not match workspace")
    if summary.get("evidence_status") != verification["evidence_status"]:
        raise ValueError("review packet summary evidence status does not match workspace")

    review = packet.get("review")
    if not isinstance(review, dict):
        raise ValueError("review packet review section must be an object")
    if review.get("status") != "human-review-required":
        raise ValueError("review packet status must remain human-review-required")
    if review.get("allowed_primary_actions") != list(prepare_review.ALLOWED_PRIMARY_ACTIONS):
        raise ValueError("review packet allowed_primary_actions are inconsistent")
    for field in ("primary_action", "rationale", "reviewer", "review_date", "next_checkpoint"):
        if review.get(field) is not None:
            raise ValueError(f"review packet field {field!r} must remain unmodified")
    planning_eligible = verification["evidence_status"] == "ready-for-human-review"
    if review.get("planning_review_eligible") is not planning_eligible:
        raise ValueError("review packet planning_review_eligible is inconsistent")

    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")
    for key, expected in REQUIRED_PACKET_BOUNDARIES.items():
        if boundaries.get(key) is not expected:
            raise ValueError(f"review packet boundary {key!r} is inconsistent")

    decision_json, decision_markdown = _decision_paths(review_prefix)
    return {
        **verification,
        "decision": "human-decision-ready",
        "review_packet_contract": packet["contract"],
        "review_json": str(review_json),
        "review_markdown": str(review_markdown),
        "review_json_sha256": _sha256(packet_raw),
        "review_markdown_sha256": _sha256(markdown_raw),
        "planning_review_eligible": planning_eligible,
        "decision_json": str(decision_json),
        "decision_markdown": str(decision_markdown),
        "decision_outputs_exist": decision_json.exists() or decision_markdown.exists(),
    }


def build_decision_record(
    workspace: Path,
    action: str,
    reviewer: str,
    review_date: str,
    rationale: str,
    next_checkpoint: str,
) -> dict[str, object]:
    """Build one deterministic decision record from explicit human-supplied fields."""
    readiness = validate_review_ready(workspace)
    if action not in prepare_review.ALLOWED_PRIMARY_ACTIONS:
        raise ValueError(f"unsupported primary action: {action!r}")
    if (
        action == "advance-to-next-product-planning-review"
        and readiness["planning_review_eligible"] is not True
    ):
        raise ValueError(
            "advance-to-next-product-planning-review requires ready-for-human-review evidence"
        )

    return {
        "contract": CONTRACT,
        "decision": "human-product-decision-recorded",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "evidence_status": readiness["evidence_status"],
        "sessions": readiness["sessions"],
        "review_packet_binding": {
            "contract": readiness["review_packet_contract"],
            "json_sha256": readiness["review_json_sha256"],
            "markdown_sha256": readiness["review_markdown_sha256"],
            "combined_sha256": readiness["combined_sha256"],
            "intake_manifest_sha256": readiness["intake_manifest_sha256"],
            "source_records_sha256": readiness["source_records_sha256"],
            "source_record_count": readiness["source_record_count"],
            "raw_sources_verified": True,
        },
        "human_decision": {
            "status": "recorded",
            "primary_action": action,
            "reviewer": _single_line(reviewer, "reviewer", 120),
            "review_date": _review_date(review_date),
            "rationale": _long_text(rationale, "rationale", 20, 2000),
            "next_checkpoint": _long_text(
                next_checkpoint,
                "next checkpoint",
                3,
                500,
            ),
            "planning_review_opened": action
            == "advance-to-next-product-planning-review",
        },
        "boundaries": {
            "human_supplied_decision": True,
            "automatic_product_decision": False,
            "automatic_repository_mutation": False,
            "second_route_authorized": False,
            "public_release_authorized": False,
            "learning_effectiveness_claimed": False,
            "product_market_fit_claimed": False,
            "raw_session_records_included": False,
            "facilitator_notes_included": False,
        },
    }


def render_markdown(record: dict[str, object]) -> str:
    decision = record["human_decision"]
    binding = record["review_packet_binding"]
    boundaries = record["boundaries"]
    if not isinstance(decision, dict) or not isinstance(binding, dict) or not isinstance(boundaries, dict):
        raise ValueError("decision record sections are invalid")
    return "\n".join(
        [
            "# Product Alpha Human Decision Record",
            "",
            f"- Contract: `{record['contract']}`",
            f"- Pilot build ID: `{record['pilot_build_id']}`",
            f"- Route: `{record['route_id']}`",
            f"- Evidence status: **{record['evidence_status']}**",
            f"- Sessions: {record['sessions']}",
            f"- Review packet JSON SHA-256: `{binding['json_sha256']}`",
            f"- Review packet Markdown SHA-256: `{binding['markdown_sha256']}`",
            f"- Intake manifest SHA-256: `{binding['intake_manifest_sha256']}`",
            f"- Source-record set SHA-256: `{binding['source_records_sha256']}`",
            "",
            "## Human decision",
            "",
            f"- Primary action: `{decision['primary_action']}`",
            f"- Reviewer: {decision['reviewer']}",
            f"- Review date: {decision['review_date']}",
            f"- Planning review opened: **{str(decision['planning_review_opened']).lower()}**",
            "",
            "### Rationale",
            "",
            str(decision["rationale"]),
            "",
            "### Next checkpoint",
            "",
            str(decision["next_checkpoint"]),
            "",
            "## Decision boundary",
            "",
            "This record captures a human product action only. It does not automatically "
            "modify the repository, authorize a second route or public release, prove "
            "learning effectiveness, or establish product-market fit.",
            "",
        ]
    )


def write_decision_outputs(
    review_prefix: Path,
    record: dict[str, object],
) -> tuple[Path, Path, str]:
    json_path, markdown_path = _decision_paths(review_prefix)
    for path in (json_path, markdown_path):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing decision output: {path}")
    json_bytes = prepare_review.canonical_json(record)
    markdown_bytes = render_markdown(record).encode("utf-8")
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("xb") as stream:
        stream.write(json_bytes)
    try:
        with markdown_path.open("xb") as stream:
            stream.write(markdown_bytes)
    except Exception:
        json_path.unlink(missing_ok=True)
        raise
    return json_path, markdown_path, _sha256(json_bytes)


def record_workspace_decision(
    workspace: Path,
    action: str,
    reviewer: str,
    review_date: str,
    rationale: str,
    next_checkpoint: str,
) -> dict[str, object]:
    """Verify, build, and write one immutable private human decision record."""
    record = build_decision_record(
        workspace,
        action,
        reviewer,
        review_date,
        rationale,
        next_checkpoint,
    )
    readiness = validate_review_ready(workspace)
    review_prefix = Path(str(readiness["review_output_prefix"]))
    json_path, markdown_path, record_sha256 = write_decision_outputs(
        review_prefix,
        record,
    )
    return {
        "contract": CONTRACT,
        "decision": "human-decision-record-created",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "primary_action": record["human_decision"]["primary_action"],
        "decision_json": str(json_path),
        "decision_markdown": str(markdown_path),
        "decision_record_sha256": record_sha256,
        "automatic_repository_mutation": False,
        "human_review_recorded": True,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("record", "check"),
        default="record",
        help="record a human decision or only verify decision readiness",
    )
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--action", choices=prepare_review.ALLOWED_PRIMARY_ACTIONS)
    parser.add_argument("--reviewer")
    parser.add_argument("--review-date")
    parser.add_argument("--rationale")
    parser.add_argument("--next-checkpoint")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        if args.command == "check":
            report = validate_review_ready(args.workspace)
        else:
            missing = [
                name
                for name in (
                    "action",
                    "reviewer",
                    "review_date",
                    "rationale",
                    "next_checkpoint",
                )
                if getattr(args, name) is None
            ]
            if missing:
                raise ValueError(
                    "record command requires: " + ", ".join(f"--{name.replace('_', '-')}" for name in missing)
                )
            report = record_workspace_decision(
                args.workspace,
                args.action,
                args.reviewer,
                args.review_date,
                args.rationale,
                args.next_checkpoint,
            )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace decision failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
