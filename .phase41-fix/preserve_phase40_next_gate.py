#!/usr/bin/env python3
from pathlib import Path

path = Path("PROJECT_STATE.md")
text = path.read_text(encoding="utf-8")
old = "Historical Phase 41 target marker: `offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate`"
new = old + "\n\nHistorical Phase 40 next-gate marker: Next gate: **offline-consequence-plan-review-response-intake-envelope-validation-execution-authorization-decision-candidate-preparation-readiness-candidate**."
count = text.count(old)
if count != 1:
    raise SystemExit(f"expected one historical target marker, found {count}")
path.write_text(text.replace(old, new, 1), encoding="utf-8")
print("Preserved the exact Phase 40 historical next-gate marker.")
