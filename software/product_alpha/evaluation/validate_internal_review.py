#!/usr/bin/env python3
"""Validate the Product Alpha internal multi-perspective review without writing."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[3]
REVIEW_JSON = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.json"
REVIEW_MD = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.md"

PERSPECTIVE_LABELS = {
    "product-strategy": "product strategy",
    "pedagogy": "pedagogy",
    "scientific-integrity": "scientific integrity",
    "ux-accessibility": "ux and accessibility",
    "privacy-security": "privacy and security",
    "operational-reliability": "operational reliability",
    "evidence-provenance": "evidence and provenance",
    "maintainability-governance": "maintainability and governance",
}
REQUIRED_PERSPECTIVES = set(PERSPECTIVE_LABELS)
ALLOWED_STATUSES = {"pass", "conditional-pass"}
EXPECTED_DECISION = "advance-to-next-product-planning-review"
REQUIRED_NON_CLAIMS = {
    "empirical learning effectiveness",
    "retention",
    "transfer",
    "product-market fit",
    "public production readiness",
}


class ReviewValidationError(ValueError):
    """Raised when the internal review authority is incomplete or inconsistent."""


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ReviewValidationError(message)


def _load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ReviewValidationError(f"cannot load review JSON: {exc}") from exc
    _require(isinstance(value, dict), "review JSON must be an object")
    return value


def _validate_evidence_path(raw_path: Any, perspective_id: str) -> str:
    _require(
        isinstance(raw_path, str) and raw_path.strip(),
        f"{perspective_id}: invalid evidence path",
    )
    path = Path(raw_path)
    _require(
        not path.is_absolute(),
        f"{perspective_id}: evidence path must be repository-relative",
    )
    _require(
        ".." not in path.parts,
        f"{perspective_id}: evidence path may not escape the repository",
    )
    resolved = REPO_ROOT / path
    _require(
        resolved.is_file(),
        f"{perspective_id}: missing evidence file {raw_path}",
    )
    return raw_path


def validate_review() -> dict[str, Any]:
    review = _load_json(REVIEW_JSON)
    markdown = REVIEW_MD.read_text(encoding="utf-8")
    lowered_markdown = markdown.lower()

    _require(review.get("schema_version") == 1, "unsupported review schema")
    _require(
        review.get("review_date") == "2026-08-03",
        "review date must match the current authority",
    )
    _require(
        review.get("authority") == "internal-multi-perspective-review",
        "incorrect decision authority",
    )

    decision = review.get("decision")
    _require(isinstance(decision, dict), "decision must be an object")
    _require(
        decision.get("action") == EXPECTED_DECISION,
        "unexpected product decision",
    )
    for key in ("rationale", "authorized_next_work", "not_authorized"):
        _require(decision.get(key), f"decision.{key} is required")

    perspectives = review.get("perspectives")
    _require(isinstance(perspectives, list), "perspectives must be a list")
    _require(
        len(perspectives) == len(REQUIRED_PERSPECTIVES),
        "exactly eight perspectives are required",
    )

    seen: set[str] = set()
    for perspective in perspectives:
        _require(
            isinstance(perspective, dict),
            "each perspective must be an object",
        )
        perspective_id = perspective.get("id")
        _require(
            perspective_id in REQUIRED_PERSPECTIVES,
            f"unknown perspective: {perspective_id}",
        )
        _require(
            perspective_id not in seen,
            f"duplicate perspective: {perspective_id}",
        )
        seen.add(perspective_id)
        _require(
            perspective.get("status") in ALLOWED_STATUSES,
            f"{perspective_id}: invalid status",
        )
        for key in ("summary", "strengths", "residual_risk", "next_action"):
            _require(
                perspective.get(key),
                f"{perspective_id}: {key} is required",
            )
        evidence = perspective.get("evidence")
        _require(
            isinstance(evidence, list) and len(evidence) >= 2,
            f"{perspective_id}: at least two evidence files are required",
        )
        for raw_path in evidence:
            _validate_evidence_path(raw_path, perspective_id)
        label = PERSPECTIVE_LABELS[perspective_id]
        _require(
            label in lowered_markdown,
            f"Markdown review must name perspective {label}",
        )

    _require(
        seen == REQUIRED_PERSPECTIVES,
        "review perspective set is incomplete",
    )

    claim_boundary = review.get("claim_boundary")
    _require(
        isinstance(claim_boundary, dict),
        "claim_boundary must be an object",
    )
    does_not_establish = claim_boundary.get("does_not_establish")
    _require(
        isinstance(does_not_establish, list),
        "claim_boundary.does_not_establish must be a list",
    )
    lowered_non_claims = {str(item).lower() for item in does_not_establish}
    _require(
        REQUIRED_NON_CLAIMS <= lowered_non_claims,
        "required empirical claim boundaries are missing",
    )

    _require(
        EXPECTED_DECISION in lowered_markdown,
        "Markdown review must contain the product decision",
    )
    for non_claim in REQUIRED_NON_CLAIMS:
        _require(
            non_claim in lowered_markdown,
            f"Markdown review must preserve non-claim boundary: {non_claim}",
        )
    _require(
        "external participant sessions as a prerequisite" in lowered_markdown,
        "Markdown must remove participant sessions as a roadmap prerequisite",
    )

    return review


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",), nargs="?", default="check")
    parser.parse_args()
    review = validate_review()
    print(
        "internal-multi-perspective-review-passed: "
        f"{review['decision']['action']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
