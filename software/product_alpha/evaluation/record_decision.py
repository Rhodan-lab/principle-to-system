#!/usr/bin/env python3
"""Record and verify one immutable human decision for a Product Alpha review."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
from pathlib import Path
from typing import Sequence

import prepare_review
import review_workspace

CONTRACT = "principia-product-alpha-human-decision/0.1"
RECEIPT_CONTRACT = "principia-product-alpha-human-decision-receipt/0.1"
VERIFICATION_CONTRACT = "principia-product-alpha-human-decision-verification/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]


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


def _decision_paths(review_prefix: Path) -> tuple[Path, Path, Path]:
    prefix = review_prefix.expanduser().resolve(strict=False)
    json_path = Path(f"{prefix}-decision.json")
    markdown_path = Path(f"{prefix}-decision.md")
    receipt_path = Path(f"{prefix}-decision-receipt.json")
    for path in (json_path, markdown_path, receipt_path):
        if _is_within(path, REPO_ROOT):
            raise ValueError("decision records must be written outside the repository")
    return json_path, markdown_path, receipt_path


def _read_canonical_object(raw: bytes, label: str) -> dict[str, object]:
    try:
        value = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"{label} must be UTF-8") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"{label} is invalid JSON: {exc.msg}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{label} must contain one object")
    if raw != prepare_review.canonical_json(value):
        raise ValueError(f"{label} is not canonical JSON")
    return value


def _expected_review_packet(
    verification: dict[str, object],
) -> dict[str, object]:
    combined = Path(str(verification["combined_jsonl"]))
    packet = prepare_review.build_review_packet(
        combined,
        str(verification["pilot_build_id"]),
    )
    evidence = packet.get("evidence_binding")
    if not isinstance(evidence, dict):
        raise ValueError("rebuilt review packet evidence_binding must be an object")
    evidence.update(
        {
            "workspace_contract": verification["workspace_contract"],
            "workspace_intake_contract": review_workspace.INTAKE_CONTRACT,
            "intake_manifest_sha256": verification["intake_manifest_sha256"],
            "source_records_sha256": verification["source_records_sha256"],
            "source_record_count": verification["source_record_count"],
            "raw_sources_verified": True,
        }
    )
    return packet


def validate_review_ready(workspace: Path) -> dict[str, object]:
    """Verify the unchanged workspace evidence and untouched generated review pair."""
    verification = review_workspace.verify_workspace_intake(workspace)
    review_prefix = Path(str(verification["review_output_prefix"]))
    review_json = review_prefix.with_suffix(".json")
    review_markdown = review_prefix.with_suffix(".md")

    packet_raw = _regular_bytes(review_json, "review packet JSON")
    markdown_raw = _regular_bytes(review_markdown, "review packet Markdown")
    packet = _read_canonical_object(packet_raw, "review packet JSON")

    expected_packet = _expected_review_packet(verification)
    if packet != expected_packet:
        raise ValueError("review packet JSON does not match verified workspace evidence")
    expected_markdown = prepare_review.render_markdown(expected_packet).encode("utf-8")
    if markdown_raw != expected_markdown:
        raise ValueError("review packet Markdown does not match the untouched packet")

    review = expected_packet.get("review")
    if not isinstance(review, dict):
        raise ValueError("review packet review section must be an object")
    planning_eligible = review.get("planning_review_eligible")
    if planning_eligible is not False:
        raise ValueError("optional review must not be planning-review eligible")
    for key, expected in (
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if review.get(key) is not expected:
            raise ValueError(f"optional review field {key!r} is invalid")

    decision_json, decision_markdown, decision_receipt = _decision_paths(review_prefix)
    return {
        **verification,
        "decision": "human-decision-ready",
        "review_packet_contract": expected_packet["contract"],
        "review_json": str(review_json),
        "review_markdown": str(review_markdown),
        "review_json_sha256": _sha256(packet_raw),
        "review_markdown_sha256": _sha256(markdown_raw),
        "planning_review_eligible": planning_eligible,
        "advisory_only": True,
        "roadmap_gate": False,
        "decision_authority": False,
        "decision_json": str(decision_json),
        "decision_markdown": str(decision_markdown),
        "decision_receipt": str(decision_receipt),
        "decision_outputs_exist": any(
            path.exists()
            for path in (decision_json, decision_markdown, decision_receipt)
        ),
    }


def _build_decision_record(
    readiness: dict[str, object],
    action: str,
    reviewer: str,
    review_date: str,
    rationale: str,
    next_checkpoint: str,
) -> dict[str, object]:
    if action not in prepare_review.ALLOWED_PRIMARY_ACTIONS:
        raise ValueError(f"unsupported primary action: {action!r}")
    planning_action_selected = False

    return {
        "contract": CONTRACT,
        "decision": "human-product-decision-recorded",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "evidence_status": readiness["evidence_status"],
        "sessions": readiness["sessions"],
        "observation_mode": "optional-descriptive",
        "advisory_only": True,
        "roadmap_gate": False,
        "decision_authority": False,
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
            "advisory_only": True,
            "roadmap_gate": False,
            "decision_authority": False,
            "reviewer": _single_line(reviewer, "reviewer", 120),
            "review_date": _review_date(review_date),
            "rationale": _long_text(rationale, "rationale", 20, 2000),
            "next_checkpoint": _long_text(
                next_checkpoint,
                "next checkpoint",
                3,
                500,
            ),
            "planning_review_action_selected": planning_action_selected,
        },
        "boundaries": {
            "human_supplied_decision": True,
            "advisory_only": True,
            "roadmap_gate": False,
            "decision_authority": False,
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


def build_decision_record(
    workspace: Path,
    action: str,
    reviewer: str,
    review_date: str,
    rationale: str,
    next_checkpoint: str,
) -> dict[str, object]:
    """Build one deterministic decision record from explicit human-supplied fields."""
    return _build_decision_record(
        validate_review_ready(workspace),
        action,
        reviewer,
        review_date,
        rationale,
        next_checkpoint,
    )


def render_markdown(record: dict[str, object]) -> str:
    decision = record["human_decision"]
    binding = record["review_packet_binding"]
    boundaries = record["boundaries"]
    if (
        not isinstance(decision, dict)
        or not isinstance(binding, dict)
        or not isinstance(boundaries, dict)
    ):
        raise ValueError("decision record sections are invalid")
    return "\n".join(
        [
            "# Product Alpha Optional Observation Advisory Record",
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
            "## Human advisory interpretation",
            "",
            f"- Primary action: `{decision['primary_action']}`",
            f"- Reviewer: {decision['reviewer']}",
            f"- Review date: {decision['review_date']}",
            (
                "- Planning review action selected: **"
                f"{str(decision['planning_review_action_selected']).lower()}**"
            ),
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
            "This record captures an optional advisory interpretation only. It cannot "
            "authorize or block roadmap work, create a planning review, modify the repository, "
            "authorize a second route or public release, prove learning effectiveness, or "
            "establish product-market fit. Internal multi-perspective review remains authoritative.",
            "",
        ]
    )


def _build_receipt(
    readiness: dict[str, object],
    record: dict[str, object],
    json_path: Path,
    markdown_path: Path,
    receipt_path: Path,
    json_bytes: bytes,
    markdown_bytes: bytes,
) -> dict[str, object]:
    decision = record.get("human_decision")
    if not isinstance(decision, dict):
        raise ValueError("decision record human_decision must be an object")
    return {
        "contract": RECEIPT_CONTRACT,
        "decision": "human-decision-artifacts-sealed",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "primary_action": decision["primary_action"],
        "advisory_only": True,
        "roadmap_gate": False,
        "decision_authority": False,
        "decision_json": str(json_path),
        "decision_markdown": str(markdown_path),
        "decision_receipt": str(receipt_path),
        "decision_json_sha256": _sha256(json_bytes),
        "decision_markdown_sha256": _sha256(markdown_bytes),
        "review_json_sha256": readiness["review_json_sha256"],
        "review_markdown_sha256": readiness["review_markdown_sha256"],
        "combined_sha256": readiness["combined_sha256"],
        "intake_manifest_sha256": readiness["intake_manifest_sha256"],
        "source_records_sha256": readiness["source_records_sha256"],
        "source_record_count": readiness["source_record_count"],
        "raw_sources_verified": True,
        "automatic_repository_mutation": False,
    }


def write_decision_outputs(
    review_prefix: Path,
    readiness: dict[str, object],
    record: dict[str, object],
) -> tuple[Path, Path, Path, str, str]:
    json_path, markdown_path, receipt_path = _decision_paths(review_prefix)
    for path in (json_path, markdown_path, receipt_path):
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing decision output: {path}")
    json_bytes = prepare_review.canonical_json(record)
    markdown_bytes = render_markdown(record).encode("utf-8")
    receipt = _build_receipt(
        readiness,
        record,
        json_path,
        markdown_path,
        receipt_path,
        json_bytes,
        markdown_bytes,
    )
    receipt_bytes = prepare_review.canonical_json(receipt)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    with json_path.open("xb") as stream:
        stream.write(json_bytes)
    try:
        with markdown_path.open("xb") as stream:
            stream.write(markdown_bytes)
        with receipt_path.open("xb") as stream:
            stream.write(receipt_bytes)
    except Exception:
        json_path.unlink(missing_ok=True)
        markdown_path.unlink(missing_ok=True)
        receipt_path.unlink(missing_ok=True)
        raise
    return (
        json_path,
        markdown_path,
        receipt_path,
        _sha256(json_bytes),
        _sha256(receipt_bytes),
    )


def record_workspace_decision(
    workspace: Path,
    action: str,
    reviewer: str,
    review_date: str,
    rationale: str,
    next_checkpoint: str,
) -> dict[str, object]:
    """Verify, build, and write one immutable private human decision record."""
    readiness = validate_review_ready(workspace)
    record = _build_decision_record(
        readiness,
        action,
        reviewer,
        review_date,
        rationale,
        next_checkpoint,
    )
    review_prefix = Path(str(readiness["review_output_prefix"]))
    (
        json_path,
        markdown_path,
        receipt_path,
        record_sha256,
        receipt_sha256,
    ) = write_decision_outputs(review_prefix, readiness, record)
    human_decision = record.get("human_decision")
    if not isinstance(human_decision, dict):
        raise ValueError("decision record human_decision must be an object")
    return {
        "contract": CONTRACT,
        "decision": "human-decision-record-created",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "primary_action": human_decision["primary_action"],
        "decision_json": str(json_path),
        "decision_markdown": str(markdown_path),
        "decision_receipt": str(receipt_path),
        "decision_record_sha256": record_sha256,
        "decision_receipt_sha256": receipt_sha256,
        "automatic_repository_mutation": False,
        "human_review_recorded": True,
    }


def _decision_fields(record: dict[str, object]) -> tuple[str, str, str, str, str]:
    human = record.get("human_decision")
    expected_keys = {
        "status",
        "primary_action",
        "advisory_only",
        "roadmap_gate",
        "decision_authority",
        "reviewer",
        "review_date",
        "rationale",
        "next_checkpoint",
        "planning_review_action_selected",
    }
    if not isinstance(human, dict) or set(human) != expected_keys:
        raise ValueError("decision record human_decision fields are invalid")
    if human.get("status") != "recorded":
        raise ValueError("decision record human_decision status must be 'recorded'")
    for key, expected in (
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if human.get(key) is not expected:
            raise ValueError(f"decision record advisory field {key!r} is invalid")
    planning = human.get("planning_review_action_selected")
    if not isinstance(planning, bool):
        raise ValueError(
            "decision record planning_review_action_selected must be boolean"
        )
    fields = (
        human.get("primary_action"),
        human.get("reviewer"),
        human.get("review_date"),
        human.get("rationale"),
        human.get("next_checkpoint"),
    )
    if not all(isinstance(value, str) for value in fields):
        raise ValueError("decision record human-supplied fields must be text")
    return fields  # type: ignore[return-value]


def verify_workspace_decision(workspace: Path) -> dict[str, object]:
    """Verify the complete decision artifact trio and current evidence bindings."""
    readiness = validate_review_ready(workspace)
    json_path = Path(str(readiness["decision_json"]))
    markdown_path = Path(str(readiness["decision_markdown"]))
    receipt_path = Path(str(readiness["decision_receipt"]))

    exists = [path.exists() for path in (json_path, markdown_path, receipt_path)]
    if any(exists) and not all(exists):
        raise ValueError("decision artifact trio is incomplete")
    if not all(exists):
        raise ValueError("decision artifacts do not exist")

    json_bytes = _regular_bytes(json_path, "decision record JSON")
    markdown_bytes = _regular_bytes(markdown_path, "decision record Markdown")
    receipt_bytes = _regular_bytes(receipt_path, "decision receipt JSON")
    record = _read_canonical_object(json_bytes, "decision record JSON")
    receipt = _read_canonical_object(receipt_bytes, "decision receipt JSON")

    action, reviewer, review_date, rationale, next_checkpoint = _decision_fields(record)
    expected_record = _build_decision_record(
        readiness,
        action,
        reviewer,
        review_date,
        rationale,
        next_checkpoint,
    )
    if record != expected_record:
        raise ValueError(
            "decision record JSON does not match the current review and evidence chain"
        )
    expected_markdown = render_markdown(expected_record).encode("utf-8")
    if markdown_bytes != expected_markdown:
        raise ValueError("decision record Markdown does not match the canonical record")

    expected_receipt = _build_receipt(
        readiness,
        expected_record,
        json_path,
        markdown_path,
        receipt_path,
        json_bytes,
        markdown_bytes,
    )
    if receipt != expected_receipt:
        raise ValueError(
            "decision receipt does not match the decision artifacts and evidence chain"
        )

    human = expected_record["human_decision"]
    if not isinstance(human, dict):
        raise ValueError("decision record human_decision must be an object")
    return {
        "contract": VERIFICATION_CONTRACT,
        "decision": "human-decision-record-verified",
        "workspace": readiness["workspace"],
        "pilot_build_id": readiness["pilot_build_id"],
        "route_id": readiness["route_id"],
        "evidence_status": readiness["evidence_status"],
        "sessions": readiness["sessions"],
        "primary_action": human["primary_action"],
        "planning_review_action_selected": human[
            "planning_review_action_selected"
        ],
        "decision_json": str(json_path),
        "decision_markdown": str(markdown_path),
        "decision_receipt": str(receipt_path),
        "decision_record_sha256": _sha256(json_bytes),
        "decision_markdown_sha256": _sha256(markdown_bytes),
        "decision_receipt_sha256": _sha256(receipt_bytes),
        "review_json_sha256": readiness["review_json_sha256"],
        "review_markdown_sha256": readiness["review_markdown_sha256"],
        "combined_sha256": readiness["combined_sha256"],
        "intake_manifest_sha256": readiness["intake_manifest_sha256"],
        "source_records_sha256": readiness["source_records_sha256"],
        "raw_sources_verified": True,
        "writes_performed": False,
        "automatic_repository_mutation": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("record", "check", "verify"),
        default="record",
        help=(
            "record a decision, check pre-record readiness, or verify existing "
            "decision artifacts"
        ),
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
        elif args.command == "verify":
            report = verify_workspace_decision(args.workspace)
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
                flags = ", ".join(
                    f"--{name.replace('_', '-')}" for name in missing
                )
                raise ValueError(f"record command requires: {flags}")
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
