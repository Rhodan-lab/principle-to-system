#!/usr/bin/env python3
"""Correct the Phase 42 historical and current next-gate markers."""
from pathlib import Path

path = Path("PROJECT_STATE.md")
text = path.read_text(encoding="utf-8")
previous_gate = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-assurance-candidate"
current_gate = "offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-assembly-readiness-candidate"
wrong_historical = f"Historical Phase 41 next-gate marker: Next gate: **{current_gate}**."
right_historical = f"Historical Phase 41 next-gate marker: Next gate: **{previous_gate}**."
assert wrong_historical in text and right_historical not in text
text = text.replace(wrong_historical, right_historical, 1)
head, marker, tail = text.rpartition("## Next phase")
assert marker and f"Next gate: **{previous_gate}**." in tail
assert f"Next gate: **{current_gate}**." not in tail
tail = tail.replace(f"Next gate: **{previous_gate}**.", f"Next gate: **{current_gate}**.", 1)
path.write_text(head + marker + tail, encoding="utf-8")
