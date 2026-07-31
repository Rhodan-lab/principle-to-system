#!/usr/bin/env python3
"""Summarize anonymous Principia Product Alpha pilot sessions."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROUTE_ID = "refrigerator-v1"
STEPS = ["observe", "map", "model", "diagnose", "redesign"]
SCORE_KEYS = [
    "mechanism_explanation",
    "model_reasoning",
    "failure_diagnosis",
    "evidence_boundary",
    "redesign_tradeoff",
]
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


def _walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key).lower()
            yield from _walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk_keys(child)


def validate_session(session: dict[str, Any], line_number: int) -> dict[str, Any]:
    found_pii = sorted(PII_KEYS.intersection(_walk_keys(session)))
    if found_pii:
        raise ValueError(
            f"line {line_number}: personal-data fields are not allowed: {', '.join(found_pii)}"
        )

    if session.get("route_id") != ROUTE_ID:
        raise ValueError(f"line {line_number}: route_id must be {ROUTE_ID!r}")

    session_id = session.get("session_id")
    if not isinstance(session_id, str) or not session_id.strip():
        raise ValueError(f"line {line_number}: session_id must be a non-empty anonymous label")

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
    if duration < 0 or duration > 180:
        raise ValueError(f"line {line_number}: duration_minutes must be between 0 and 180")

    scores = session.get("scores")
    if not isinstance(scores, dict) or sorted(scores) != sorted(SCORE_KEYS):
        raise ValueError(
            f"line {line_number}: scores must contain exactly: {', '.join(SCORE_KEYS)}"
        )
    for key in SCORE_KEYS:
        value = scores[key]
        if not isinstance(value, int) or isinstance(value, bool) or value not in {0, 1, 2}:
            raise ValueError(f"line {line_number}: score {key!r} must be 0, 1, or 2")

    confusion_tags = session.get("confusion_tags")
    if not isinstance(confusion_tags, list) or not all(
        isinstance(tag, str) and tag.strip() for tag in confusion_tags
    ):
        raise ValueError(f"line {line_number}: confusion_tags must be non-empty strings")

    voluntary_continue = session.get("voluntary_continue")
    if voluntary_continue is not None and not isinstance(voluntary_continue, bool):
        raise ValueError(f"line {line_number}: voluntary_continue must be true, false, or null")

    notes = session.get("facilitator_notes")
    if not isinstance(notes, str):
        raise ValueError(f"line {line_number}: facilitator_notes must be text")

    return session


def load_sessions(path: Path) -> list[dict[str, Any]]:
    sessions: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip():
            continue
        try:
            value = json.loads(raw_line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"line {line_number}: invalid JSON: {exc.msg}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"line {line_number}: each session must be a JSON object")
        sessions.append(validate_session(value, line_number))
    if not sessions:
        raise ValueError("input contains no pilot sessions")
    return sessions


def summarize(sessions: list[dict[str, Any]]) -> dict[str, Any]:
    started = sum(session["started"] for session in sessions)
    finished = sum(session["completed_steps"] == STEPS for session in sessions)
    durations = [float(session["duration_minutes"]) for session in sessions if session["started"]]
    confusion = Counter(
        tag for session in sessions for tag in session["confusion_tags"]
    )
    continue_answers = [
        session["voluntary_continue"]
        for session in sessions
        if session["voluntary_continue"] is not None
    ]

    score_averages = {
        key: round(sum(session["scores"][key] for session in sessions) / len(sessions), 2)
        for key in SCORE_KEYS
    }

    return {
        "route_id": ROUTE_ID,
        "sessions": len(sessions),
        "started": started,
        "finished": finished,
        "completion_rate": round(finished / started, 3) if started else 0.0,
        "average_duration_minutes": round(sum(durations) / len(durations), 2)
        if durations
        else 0.0,
        "score_averages": score_averages,
        "confusion_counts": dict(sorted(confusion.items(), key=lambda item: (-item[1], item[0]))),
        "voluntary_continue": {
            "yes": sum(answer is True for answer in continue_answers),
            "no": sum(answer is False for answer in continue_answers),
            "unknown": len(sessions) - len(continue_answers),
            "yes_rate_among_answered": round(
                sum(answer is True for answer in continue_answers) / len(continue_answers), 3
            )
            if continue_answers
            else 0.0,
        },
    }


def render_markdown(summary: dict[str, Any]) -> str:
    lines = [
        "# Product Alpha Pilot Summary",
        "",
        f"- Route: `{summary['route_id']}`",
        f"- Sessions: {summary['sessions']}",
        f"- Started: {summary['started']}",
        f"- Finished: {summary['finished']}",
        f"- Completion rate: {summary['completion_rate']:.1%}",
        f"- Average duration: {summary['average_duration_minutes']:.2f} minutes",
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
            f"- Yes rate among answered: {continuation['yes_rate_among_answered']:.1%}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="JSONL pilot session file")
    parser.add_argument(
        "--format", choices=("markdown", "json"), default="markdown", help="output format"
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
