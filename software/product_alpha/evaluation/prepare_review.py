#!/usr/bin/env python3
"""Create a de-identified, hash-bound Product Alpha human-review packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
from typing import Any, Sequence

import verify_cohort

CONTRACT = "principia-product-alpha-pilot-review-packet/0.1"
REPO_ROOT = Path(__file__).resolve().parents[3]
ALLOWED_PRIMARY_ACTIONS = (
    "revise-current-route",
    "repeat-current-route-pilot",
    "hold-current-route",
    "advance-to-next-product-planning-review",
)


def canonical_json(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _is_within(path: Path, directory: Path) -> bool:
    try:
        path.resolve().relative_to(directory.resolve())
    except ValueError:
        return False
    return True


def review_output_paths(prefix: Path) -> tuple[Path, Path]:
    resolved = prefix.expanduser().resolve()
    json_path = resolved.with_suffix(".json")
    markdown_path = resolved.with_suffix(".md")
    for path in (json_path, markdown_path):
        if _is_within(path, REPO_ROOT):
            raise ValueError(
                "review packets must be written outside the repository in the "
                "private facilitator-controlled cohort folder"
            )
        if path.exists():
            raise FileExistsError(f"refusing to overwrite existing review output: {path}")
    return json_path, markdown_path


def build_review_packet(
    input_path: Path,
    expected_build_id: str,
) -> dict[str, Any]:
    """Verify one cohort and return a deterministic de-identified review packet."""
    raw_input = input_path.read_bytes()
    summary = verify_cohort.verify_cohort(input_path, expected_build_id)
    summary_bytes = canonical_json(summary)
    revision_signals = summary["revision_signals"]
    if not isinstance(revision_signals, list):
        raise ValueError("verified summary revision_signals must be a list")

    return {
        "contract": CONTRACT,
        "pilot_build_id": summary["pilot_build_id"],
        "route_id": summary["route_id"],
        "evidence_binding": {
            "input_sha256": sha256(raw_input),
            "input_byte_count": len(raw_input),
            "summary_contract": summary["contract"],
            "summary_sha256": sha256(summary_bytes),
        },
        "aggregate_summary": summary,
        "review": {
            "status": "human-review-required",
            "planning_review_eligible": summary["evidence_status"]
            == "ready-for-human-review",
            "allowed_primary_actions": list(ALLOWED_PRIMARY_ACTIONS),
            "primary_action": None,
            "rationale": None,
            "reviewer": None,
            "review_date": None,
            "next_checkpoint": None,
            "revision_signal_count": len(revision_signals),
        },
        "boundaries": {
            "raw_session_records_included": False,
            "facilitator_notes_included": False,
            "automatic_product_decision": False,
            "automatic_repository_mutation": False,
            "second_route_authorized": False,
            "public_release_authorized": False,
            "learning_effectiveness_claimed": False,
            "product_market_fit_claimed": False,
        },
    }


def render_markdown(packet: dict[str, Any]) -> str:
    summary = packet["aggregate_summary"]
    evidence = packet["evidence_binding"]
    review = packet["review"]
    lines = [
        "# Product Alpha Pilot Human Review",
        "",
        f"- Packet contract: `{packet['contract']}`",
        f"- Pilot build ID: `{packet['pilot_build_id']}`",
        f"- Route: `{packet['route_id']}`",
        f"- Evidence status: **{summary['evidence_status']}**",
        (
            f"- Valid sessions: {summary['sessions']} / minimum "
            f"{summary['minimum_cohort_size']}"
        ),
        f"- Planning review eligible: **{str(review['planning_review_eligible']).lower()}**",
        f"- Exact private input SHA-256: `{evidence['input_sha256']}`",
        f"- De-identified summary SHA-256: `{evidence['summary_sha256']}`",
        "",
        "> The hashes bind this worksheet to one verified local cohort. The raw "
        "session file and facilitator notes are not included and must remain private.",
        "",
        "## Aggregate evidence",
        "",
        f"- Started: {summary['started']}",
        f"- Finished: {summary['finished']}",
        f"- Completion rate: {summary['completion_rate']:.1%}",
        f"- Average duration: {summary['average_duration_minutes']:.2f} minutes",
        "",
        "### Learning scores",
        "",
        "| Measure | Average (0–2) |",
        "| --- | ---: |",
    ]
    for key, value in summary["score_averages"].items():
        lines.append(f"| {key.replace('_', ' ').title()} | {value:.2f} |")

    lines.extend(["", "### Confusion signals", ""])
    if summary["confusion_counts"]:
        for tag, count in summary["confusion_counts"].items():
            lines.append(f"- `{tag}`: {count}")
    else:
        lines.append("- None recorded")

    continuation = summary["voluntary_continue"]
    lines.extend(
        [
            "",
            "### Voluntary continuation",
            "",
            f"- Yes: {continuation['yes']}",
            f"- No: {continuation['no']}",
            f"- Unknown: {continuation['unknown']}",
            (
                f"- Yes rate among answered: "
                f"{continuation['yes_rate_among_answered']:.1%}"
            ),
            "",
            "## Revision signals",
            "",
        ]
    )
    if summary["revision_signals"]:
        for signal in summary["revision_signals"]:
            lines.append(f"- `{signal['code']}` — {signal['message']}")
    else:
        lines.append(
            "- No automatic revision trigger was detected. Human review is still required."
        )

    lines.extend(
        [
            "",
            "## Human decision",
            "",
            "Select exactly one primary action after reviewing the aggregate and the "
            "private facilitator notes:",
            "",
            "- [ ] `revise-current-route`",
            "- [ ] `repeat-current-route-pilot`",
            "- [ ] `hold-current-route`",
            "- [ ] `advance-to-next-product-planning-review`",
            "",
            "Reviewer:",
            "",
            "Review date:",
            "",
            "Rationale:",
            "",
            "Next checkpoint:",
            "",
            "## Decision boundary",
            "",
            "Completing this worksheet does not automatically modify the repository, "
            "authorize a second route, establish release readiness, prove learning "
            "effectiveness, or establish product-market fit. Any product change requires "
            "a separate reviewed repository change.",
            "",
        ]
    )
    return "\n".join(lines)


def write_review_outputs(
    prefix: Path,
    packet: dict[str, Any],
) -> tuple[Path, Path, str]:
    json_path, markdown_path = review_output_paths(prefix)
    json_bytes = canonical_json(packet)
    markdown_bytes = render_markdown(packet).encode("utf-8")
    json_path.parent.mkdir(parents=True, exist_ok=True)

    temporary_paths = (
        json_path.with_name(f".{json_path.name}.tmp-{os.getpid()}"),
        markdown_path.with_name(f".{markdown_path.name}.tmp-{os.getpid()}"),
    )
    for path in temporary_paths:
        if path.exists():
            raise FileExistsError(f"temporary review output already exists: {path}")

    try:
        temporary_paths[0].write_bytes(json_bytes)
        temporary_paths[1].write_bytes(markdown_bytes)
        os.replace(temporary_paths[0], json_path)
        os.replace(temporary_paths[1], markdown_path)
    finally:
        for path in temporary_paths:
            if path.exists():
                path.unlink()

    return json_path, markdown_path, sha256(json_bytes)


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="combined private JSONL pilot session file",
    )
    parser.add_argument(
        "--expect-build-id",
        required=True,
        help="full 64-character Pilot build ID printed by run_pilot.py",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        required=True,
        help="private output prefix; writes matching .json and .md files",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        required=True,
        help="combined private JSONL pilot session file",
    )
    parser.add_argument(
        "--expect-build-id",
        required=True,
        help="full 64-character Pilot build ID printed by run_pilot.py",
    )
    parser.add_argument(
        "--output-prefix",
        type=Path,
        required=True,
        help="private output prefix; writes matching .json and .md files",
    )
    args = parser.parse_args(argv)

    try:
        packet = build_review_packet(args.input, args.expect_build_id)
        json_path, markdown_path, packet_sha256 = write_review_outputs(
            args.output_prefix,
            packet,
        )
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    print("Product Alpha human-review packet created.")
    print(f"Pilot build ID: {packet['pilot_build_id']}")
    print(f"Packet SHA-256: {packet_sha256}")
    print(f"JSON: {json_path}")
    print(f"Markdown: {markdown_path}")
    print("Decision: human-review-required")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
