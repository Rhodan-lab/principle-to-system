#!/usr/bin/env python3
"""Finish advisory-only runtime verifier compatibility after the bounded migration."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


record = Path("software/product_alpha/evaluation/record_decision.py")
replace_once(
    record,
    '''        "status",
        "primary_action",
        "reviewer",''',
    '''        "status",
        "primary_action",
        "advisory_only",
        "roadmap_gate",
        "decision_authority",
        "reviewer",''',
    "human decision advisory exact fields",
)
replace_once(
    record,
    '''    if human.get("status") != "recorded":
        raise ValueError("decision record human_decision status must be 'recorded'")
    planning = human.get("planning_review_action_selected")''',
    '''    if human.get("status") != "recorded":
        raise ValueError("decision record human_decision status must be 'recorded'")
    for key, expected in (
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if human.get(key) is not expected:
            raise ValueError(f"decision record advisory field {key!r} is invalid")
    planning = human.get("planning_review_action_selected")''',
    "human decision advisory value validation",
)

review_test = Path("software/tests/test_product_alpha_review_packet.py")
replace_once(
    review_test,
    '        self.assertIn("does not automatically modify the repository", markdown)',
    '        self.assertIn("cannot authorize or block roadmap work", markdown)\n        self.assertIn("internal multi-perspective review remains the product decision authority", markdown)',
    "review advisory boundary wording assertion",
)
