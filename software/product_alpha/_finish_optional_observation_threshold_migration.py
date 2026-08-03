#!/usr/bin/env python3
"""Finish compatibility updates for the optional observation no-threshold migration."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


handoff = Path("software/product_alpha/evaluation/prepare_handoff.py")
replace_once(
    handoff,
    '    "cohort_complete",\n    "started",',
    '    "cohort_complete",\n    "observation_mode",\n    "roadmap_gate",\n    "decision_authority",\n    "started",',
    "handoff safe summary authority fields",
)

for relative in (
    "software/tests/test_product_alpha_cohort_binding.py",
    "software/tests/test_product_alpha_verify_cohort.py",
):
    path = Path(relative)
    replace_once(
        path,
        "principia-product-alpha-pilot-summary/0.3",
        "principia-product-alpha-pilot-summary/0.4",
        f"{relative} summary contract",
    )

human_test = Path("software/tests/test_product_alpha_human_decision.py")
replace_once(
    human_test,
    '            self.assertTrue(report["planning_review_action_selected"])\n            decision = json.loads(Path(str(report["decision_json"])).read_text(encoding="utf-8"))',
    '            decision = json.loads(Path(str(report["decision_json"])).read_text(encoding="utf-8"))\n            self.assertTrue(decision["human_decision"]["planning_review_action_selected"])',
    "planning action assertion source",
)

pilot_lab = Path("software/product_alpha/pilot-lab.html")
replace_once(
    pilot_lab,
    '<p class="empty">No automatic revision trigger was detected. Human review is still required.</p>',
    '<p class="empty">No automatic product signal was detected. Optional review may still add context.</p>',
    "Pilot Lab empty signal wording",
)

# Confirm that exact-summary safety remains strict while accepting only the new public fields.
text = handoff.read_text(encoding="utf-8")
for field in ("observation_mode", "roadmap_gate", "decision_authority"):
    if text.count(f'    "{field}",') != 1:
        raise SystemExit(f"prepare_handoff.py: expected one safe field {field}")
