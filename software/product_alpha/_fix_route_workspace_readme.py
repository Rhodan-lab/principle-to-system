#!/usr/bin/env python3
"""Make generated Product Alpha workspace artifact names route-specific."""
from pathlib import Path

PATH = Path("software/product_alpha/evaluation/prepare_workspace.py")
text = PATH.read_text(encoding="utf-8")
replacements = (
    (
        "`review/refrigerator-review.json` and `review/refrigerator-review.md`",
        "`review/{route_slug}-review.json` and `review/{route_slug}-review.md`",
    ),
    (
        "`review/refrigerator-review-decision.json`, `review/refrigerator-review-decision.md`, and `review/refrigerator-review-decision-receipt.json`",
        "`review/{route_slug}-review-decision.json`, `review/{route_slug}-review-decision.md`, and `review/{route_slug}-review-decision-receipt.json`",
    ),
)
for old, new in replacements:
    if text.count(old) != 1:
        raise SystemExit(f"workspace README route filename anchor changed: {old}")
    text = text.replace(old, new, 1)
PATH.write_text(text, encoding="utf-8")
