#!/usr/bin/env python3
"""Validate and summarize anonymous Principia Product Alpha pilot sessions."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

PRODUCT_ALPHA_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ALPHA_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ALPHA_ROOT))
import route_identity

ROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE
MIN_COHORT_SIZE = 0  # compatibility sentinel: optional observation has no minimum
BUILD_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SESSION_ID_PATTERN = re.compile(r"^anonymous-[A-Za-z0-9-]+$")
MAX_SESSION_ID_LENGTH = 120
MAX_CONFUSION_TAGS = 32
MAX_CONFUSION_TAG_LENGTH = 80
MAX_FACILITATOR_NOTES_LENGTH = 1200
MAX_INPUT_BYTES = 16 * 1024 * 1024
MAX_SESSION_RECORDS = 500
STEPS = ["observe", "map", "model", "diagnose", "redesign"]
SCORE_KEYS = [
    "mechanism_explanation",
    "model_reasoning",
    "failure_diagnosis",
    "evidence_boundary",
    "redesign_tradeoff",
]
SESSION_KEYS = {
    "pilot_build_id",
    "session_id",
    "route_id",
    "started",
    "completed_steps",
    "duration_minutes",
    "scores",
    "confusion_tags",
    "voluntary_continue",
    "facilitator_notes",
}
REVISION_SCORE_KEYS = (
    "mechanism_explanation",
    "failure_diagnosis",
    "evidence_boundary",
)
PII_KEYS = {
    "name",
    "full_name",
    "email",
    "phone",
    "address",
    "date_of_birth",
    "birthdate",
    "school",
    "username",
}
PII_TEXT_PATTERNS = (
    re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.IGNORECASE),
    re.compile(
        r"\b(?:name|school|username|phone|email|address|birthdate|date of birth)\s*:",
        re.IGNORECASE,
    ),
    re.compile(r"(?:\+?\d[\s().-]*){7,}"),
)


def _object_without_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, child in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = child
    return value


def _reject_nonfinite_constant(value: str) -> Any:
    raise ValueError(f"unsupported non-finite number {value!r}")


def _contains_unsupported_control(value: str, *, allow_multiline: bool) -> bool:
    allowed = "\n\t" if allow_multiline else ""
    return any(
        (ord(character) < 32 and character not in allowed) or ord(character) == 127
        for character in value
    )


def _contains_personal_data_text(value: str) -> bool:
    return any(pattern.search(value) for pattern in PII_TEXT_PATTERNS)


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_session(
    session: dict[str, Any],
    line_number: int,
    expected_route_id: str | None = None,
) -> dict[str, Any]:
    found_pii = sorted(PII_KEYS.intersection(_walk_keys(session)))
    if found_pii:
        raise ValueError(
            f"line {line_number}: personal-data fields are not allowed: {', '.join(found_pii)}"
        )

    unknown_fields = sorted(set(session).difference(SESSION_KEYS))
    if unknown_fields:
        raise ValueError(
            f"line {line_number}: unsupported session fields: {', '.join(unknown_fields)}"
        )
    missing_fields = sorted(SESSION_KEYS.difference(session))
    if missing_fields:
        raise ValueError(
            f"line {line_number}: missing session fields: {', '.join(missing_fields)}"
        )

    build_id = session.get("pilot_build_id")
    if not isinstance(build_id, str) or not BUILD_ID_PATTERN.fullmatch(build_id):
        raise ValueError(
            f"line {line_number}: pilot_build_id must be a 64-character lowercase SHA-256"
        )

    try:
        route_id = route_identity.validate_evidence_route_id(session.get("route_id"))
    except ValueError as exc:
        raise ValueError(f"line {line_number}: {exc}") from exc
    if expected_route_id is not None and route_id != expected_route_id:
        raise ValueError(
            f"line {line_number}: route_id {route_id!r} does not match expected route {expected_route_id!r}"
        )

    session_id = session.get("session_id")
    if (
        not isinstance(session_id, str)
        or len(session_id) > MAX_SESSION_ID_LENGTH
        or not SESSION_ID_PATTERN.fullmatch(session_id)
    ):
        raise ValueError(
            f"line {line_number}: session_id must be an anonymous label containing only letters, numbers, and hyphens"
        )

    started = session.get("started")
    if not isinstance(started, bool):
        raise ValueError(f"line {line_number}: started must be true or false")

    completed_steps = session.get("completed_steps")
    if not isinstance(completed_steps, list) or not all(
        isinstance(step, str) for step in completed_steps
    ):
        raise ValueError(f"line {line_number}: completed_steps must be a string list")
    if completed_steps != STEPS[: len(completed_steps)]:
        raise ValueError(
            f"line {line_number}: completed_steps must be an ordered route prefix"
        )
    if completed_steps and not started:
        raise ValueError(f"line {line_number}: a session with progress must be started")

    duration = session.get("duration_minutes")
    if not isinstance(duration, (int, float)) or isinstance(duration, bool):
        raise ValueError(f"line {line_number}: duration_minutes must be numeric")
    if not math.isfinite(float(duration)):
        raise ValueError(f"line {line_number}: duration_minutes must be finite")
    if duration < 0 or duration > 180:
        raise ValueError(
            f"line {line_number}: duration_minutes must be between 0 and 180"
        )

    scores = session.get("scores")
    if not isinstance(scores, dict) or sorted(scores) != sorted(SCORE_KEYS):
        raise ValueError(
            f"line {line_number}: scores must contain exactly: {', '.join(SCORE_KEYS)}"
        )
    for key in SCORE_KEYS:
        value = scores[key]
        if (
            not isinstance(value, int)
            or isinstance(value, bool)
            or value not in {0, 1, 2}
        ):
            raise ValueError(f"line {line_number}: score {key!r} must be 0, 1, or 2")

    confusion_tags = session.get("confusion_tags")
    if not isinstance(confusion_tags, list):
        raise ValueError(f"line {line_number}: confusion_tags must be a string list")
    if len(confusion_tags) > MAX_CONFUSION_TAGS:
        raise ValueError(
            f"line {line_number}: confusion_tags must contain at most {MAX_CONFUSION_TAGS} entries"
        )
    seen_tags: set[str] = set()
    for tag in confusion_tags:
        if not isinstance(tag, str) or not tag:
            raise ValueError(
                f"line {line_number}: confusion_tags must be non-empty strings"
            )
        if tag != tag.strip():
            raise ValueError(
                f"line {line_number}: confusion_tags must not have surrounding whitespace"
            )
        if len(tag) > MAX_CONFUSION_TAG_LENGTH:
            raise ValueError(
                f"line {line_number}: confusion tag must be at most {MAX_CONFUSION_TAG_LENGTH} characters"
            )
        if _contains_unsupported_control(tag, allow_multiline=False):
            raise ValueError(
                f"line {line_number}: confusion tag contains unsupported control characters"
            )
        if _contains_personal_data_text(tag):
            raise ValueError(
                f"line {line_number}: confusion tag contains possible personal data"
            )
        if tag in seen_tags:
            raise ValueError(
                f"line {line_number}: duplicate confusion tag {tag!r} is not allowed"
            )
        seen_tags.add(tag)

    voluntary_continue = session.get("voluntary_continue")
    if voluntary_continue is not None and not isinstance(voluntary_continue, bool):
        raise ValueError(
            f"line {line_number}: voluntary_continue must be true, false, or null"
        )

    notes = session.get("facilitator_notes")
    if not isinstance(notes, str):
        raise ValueError(f"line {line_number}: facilitator_notes must be text")
    if len(notes) > MAX_FACILITATOR_NOTES_LENGTH:
        raise ValueError(
            f"line {line_number}: facilitator_notes must be at most {MAX_FACILITATOR_NOTES_LENGTH} characters"
        )
    if _contains_unsupported_control(notes, allow_multiline=True):
        raise ValueError(
            f"line {line_number}: facilitator_notes contains unsupported control characters"
        )
    if _contains_personal_data_text(notes):
        raise ValueError(
            f"line {line_number}: facilitator_notes contains possible personal data"
        )

    return session


def read_session_input(path: Path) -> bytes:
    """Read one bounded Product Alpha JSONL input snapshot."""
    with path.open("rb") as stream:
        raw = stream.read(MAX_INPUT_BYTES + 1)
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(
            f"input exceeds the {MAX_INPUT_BYTES}-byte Product Alpha session limit"
        )
    return raw


def load_sessions_bytes(raw: bytes) -> list[dict[str, Any]]:
    """Decode and validate one bounded Product Alpha JSONL byte snapshot."""
    if len(raw) > MAX_INPUT_BYTES:
        raise ValueError(
            f"input exceeds the {MAX_INPUT_BYTES}-byte Product Alpha session limit"
        )
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("input must be UTF-8") from exc

    sessions: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    cohort_build_id: str | None = None
    cohort_route_id: str | None = None
    record_count = 0
    for line_number, raw_line in enumerate(text.splitlines(), 1):
        if not raw_line.strip():
            continue
        record_count += 1
        if record_count > MAX_SESSION_RECORDS:
            raise ValueError(
                f"input contains more than {MAX_SESSION_RECORDS} Product Alpha sessions"
            )
        try:
            value = json.loads(
                raw_line,
                object_pairs_hook=_object_without_duplicates,
                parse_constant=_reject_nonfinite_constant,
            )
        except json.JSONDecodeError as exc:
            raise ValueError(
                f"line {line_number}: invalid JSON: {exc.msg}"
            ) from exc
        except ValueError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: each session must be a JSON object")
        session = validate_session(value, line_number, cohort_route_id)
        if cohort_route_id is None:
            cohort_route_id = session["route_id"]
        session_id = session["session_id"]
        if session_id in seen_ids:
            raise ValueError(
                f"line {line_number}: duplicate session_id {session_id!r}"
            )
        if cohort_build_id is None:
            cohort_build_id = session["pilot_build_id"]
        elif session["pilot_build_id"] != cohort_build_id:
            raise ValueError(
                f"line {line_number}: pilot_build_id does not match the cohort build"
            )
        seen_ids.add(session_id)
        sessions.append(session)
    if not sessions:
        raise ValueError("input contains no pilot sessions")
    return sessions


def load_sessions(path: Path) -> list[dict[str, Any]]:
    return load_sessions_bytes(read_session_input(path))


def revision_signals(summary: dict[str, Any]) -> list[dict[str, str]]:
    signals: list[dict[str, str]] = []
    if summary["started"] and summary["completion_rate"] < 0.5:
        signals.append(
            {
                "code": "low-completion",
                "message": "Fewer than half of started sessions reached redesign.",
            }
        )
    for key in REVISION_SCORE_KEYS:
        average = summary["score_averages"][key]
        if average < 1.25:
            signals.append(
                {
                    "code": f"low-{key.replace('_', '-')}",
                    "message": (
                        f"{key.replace('_', ' ').title()} averaged "
                        f"{average:.2f}, below 1.25."
                    ),
                }
            )
    for tag, count in summary["confusion_counts"].items():
        if count >= 2:
            signals.append(
                {
                    "code": f"recurring-confusion:{tag}",
                    "message": f"Confusion tag {tag!r} appeared in {count} sessions.",
                }
            )
    continuation = summary["voluntary_continue"]
    if (
        summary["finished"]
        and continuation["answered"]
        and continuation["yes"] == 0
    ):
        signals.append(
            {
                "code": "no-voluntary-continuation",
                "message": (
                    "At least one session finished, but no answered session "
                    "chose to continue."
                ),
            }
        )
    return signals


def summarize(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    if not sessions:
        raise ValueError("cannot summarize an empty cohort")
    route_ids = {session.get("route_id") for session in sessions}
    if len(route_ids) != 1:
        raise ValueError("route_id does not match across the cohort")
    route_id = route_identity.validate_evidence_route_id(next(iter(route_ids)))
    build_ids = {session.get("pilot_build_id") for session in sessions}
    if len(build_ids) != 1:
        raise ValueError("pilot_build_id does not match across the cohort")
    pilot_build_id = next(iter(build_ids))
    if not isinstance(pilot_build_id, str) or not BUILD_ID_PATTERN.fullmatch(
        pilot_build_id
    ):
        raise ValueError("pilot_build_id must be a 64-character lowercase SHA-256")

    started = sum(session["started"] for session in sessions)
    finished = sum(session["completed_steps"] == STEPS for session in sessions)
    durations = [
        float(session["duration_minutes"]) for session in sessions if session["started"]
    ]
    confusion = Counter(
        tag for session in sessions for tag in session["confusion_tags"]
    )
    continue_answers = [
        session["voluntary_continue"]
        for session in sessions
        if session["voluntary_continue"] is not None
    ]

    score_averages = {
        key: round(
            sum(session["scores"][key] for session in sessions) / len(sessions), 2
        )
        for key in SCORE_KEYS
    }
    continuation = {
        "yes": sum(answer is True for answer in continue_answers),
        "no": sum(answer is False for answer in continue_answers),
        "unknown": len(sessions) - len(continue_answers),
        "answered": len(continue_answers),
        "yes_rate_among_answered": round(
            sum(answer is True for answer in continue_answers)
            / len(continue_answers),
            3,
        )
        if continue_answers
        else 0.0,
    }

    summary: dict[str, Any] = {
        "contract": "principia-product-alpha-pilot-summary/0.4",
        "pilot_build_id": pilot_build_id,
        "route_id": route_id,
        "sessions": len(sessions),
        "minimum_cohort_size": MIN_COHORT_SIZE,
        "cohort_complete": True,
        "observation_mode": "optional-descriptive",
        "roadmap_gate": False,
        "decision_authority": False,
        "started": started,
        "finished": finished,
        "completion_rate": round(finished / started, 3) if started else 0.0,
        "average_duration_minutes": (
            round(sum(durations) / len(durations), 2) if durations else 0.0
        ),
        "score_averages": score_averages,
        "confusion_counts": dict(
            sorted(confusion.items(), key=lambda item: (-item[1], item[0]))
        ),
        "voluntary_continue": continuation,
    }
    summary["revision_signals"] = revision_signals(summary)
    summary["evidence_status"] = "ready-for-human-review"
    return summary


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Product Alpha Pilot Summary",
        "",
        f"- Evidence status: **{summary['evidence_status']}**",
        f"- Pilot build ID: `{summary['pilot_build_id']}`",
        f"- Route: `{summary['route_id']}`",
        f"- Valid observations: {summary['sessions']} (no minimum count)",
        f"- Started: {summary['started']}",
        f"- Finished: {summary['finished']}",
        f"- Completion rate: {summary['completion_rate']:.1%}",
        (
            f"- Average duration: "
            f"{summary['average_duration_minutes']:.2f} minutes"
        ),
        "",
        (
            "> This aggregate is descriptive formative evidence. It does not "
            "establish general learning effectiveness, public-release readiness, "
            "or product-market fit."
        ),
        "",
        "## Learning scores",
        "",
        "| Measure | Average (0–2) |",
        "| --- | ---: |",
    ]
    for key in SCORE_KEYS:
        label = key.replace("_", " ").title()
        lines.append(f"| {label} | {summary['score_averages'][key]:.2f} |")

    lines.extend(["", "## Confusion signals", ""])
    if summary["confusion_counts"]:
        for tag, count in summary["confusion_counts"].items():
            lines.append(f"- `{tag}`: {count}")
    else:
        lines.append("- None recorded")

    continuation = summary["voluntary_continue"]
    lines.extend(
        [
            "",
            "## Voluntary continuation",
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
            "- No automatic product signal was detected. Optional review may still add context."
        )

    lines.extend(
        [
            "",
            "## Decision boundary",
            "",
            (
                "These optional aggregates may inform a product discussion, but they "
                "never authorize or block roadmap progress. Do not commit raw session "
                "records or identifiable notes. A tool-generated status never authorizes "
                "a second route, public release, SaaS expansion, or a learning-effectiveness claim."
            ),
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, required=True, help="JSONL pilot session file"
    )
    parser.add_argument(
        "--format",
        choices=("markdown", "json"),
        default="markdown",
        help="output format",
    )
    args = parser.parse_args()

    try:
        summary = summarize(load_sessions(args.input))
    except (OSError, ValueError) as exc:
        parser.error(str(exc))

    if args.format == "json":
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(render_markdown(summary), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
