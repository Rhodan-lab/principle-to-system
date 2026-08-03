#!/usr/bin/env python3
"""Repair narrow anchors in the temporary advisory-only migration transformer."""
from pathlib import Path

path = Path("software/product_alpha/_make_optional_observation_advisory_only.py")
text = path.read_text(encoding="utf-8")


def replace_once(old: str, new: str, label: str) -> None:
    global text
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    text = text.replace(old, new, 1)


replace_once(
    'if path != product_state and "advance-to-next-product-planning-review" in text:',
    'if path in (review, record, handoff, status, workspace) and "advance-to-next-product-planning-review" in text:',
    "transformer scan guard",
)

replace_once(
    '''replace_once(
    record,
    '        "evidence_status": readiness["evidence_status"],\\n        "sessions": readiness["sessions"],',
    '        "evidence_status": readiness["evidence_status"],\\n        "sessions": readiness["sessions"],\\n        "observation_mode": "optional-descriptive",\\n        "advisory_only": True,\\n        "roadmap_gate": False,\\n        "decision_authority": False,',
    "decision top-level advisory fields",
)''',
    '''replace_once(
    record,
    '        "evidence_status": readiness["evidence_status"],\\n        "sessions": readiness["sessions"],\\n        "review_packet_binding": {',
    '        "evidence_status": readiness["evidence_status"],\\n        "sessions": readiness["sessions"],\\n        "observation_mode": "optional-descriptive",\\n        "advisory_only": True,\\n        "roadmap_gate": False,\\n        "decision_authority": False,\\n        "review_packet_binding": {',
    "decision top-level advisory fields",
)''',
    "decision record transformer block",
)

replace_once(
    '''replace_once(
    handoff,
    ''' + "'''" + '''    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")''' + "'''" + ''',
    ''' + "'''" + '''    review = packet.get("review")
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
    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")''' + "'''" + ''',
    "handoff review advisory validation",
)''',
    '''replace_once(
    handoff,
    ''' + "'''" + '''    summary = packet.get("aggregate_summary")
    boundaries = packet.get("boundaries")
    if not isinstance(summary, dict) or set(summary) != SAFE_SUMMARY_KEYS:
        raise ValueError("review packet aggregate summary fields are not handoff-safe")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")''' + "'''" + ''',
    ''' + "'''" + '''    summary = packet.get("aggregate_summary")
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
        raise ValueError("review packet boundaries must be an object")''' + "'''" + ''',
    "handoff review advisory validation",
)''',
    "handoff transformer block",
)

replace_once(
    '''replace_once(status_test, '            self.assertEqual(report["stage"], "handoff-verified")', '            self.assertEqual(report["stage"], "advisory-handoff-verified")', "workspace final advisory stage test")''',
    '''replace_once(status_test, '            self.assertEqual(report["stage"], "handoff-verified")\\n            self.assertEqual(report["primary_action"], "revise-current-route")', '            self.assertEqual(report["stage"], "advisory-handoff-verified")\\n            self.assertEqual(report["primary_action"], "revise-current-route")', "workspace final advisory stage test")''',
    "workspace final advisory stage transformer block",
)

path.write_text(text, encoding="utf-8")
