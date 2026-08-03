#!/usr/bin/env python3
"""Add reviewed distributed-information confusion tags to the safe aggregate vocabulary."""
from pathlib import Path

PATH = Path("software/product_alpha/evaluation/prepare_review.py")
text = PATH.read_text(encoding="utf-8")
old = '''        "energy-versus-cold",
        "model-controls",
'''
new = '''        "energy-versus-cold",
        "request-versus-operation",
        "queue-versus-service",
        "utilization-near-capacity",
        "retry-versus-recovery",
        "timeout-versus-cancellation",
        "model-controls",
'''
if text.count(old) != 1:
    raise SystemExit("safe confusion-tag vocabulary anchor changed")
PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
