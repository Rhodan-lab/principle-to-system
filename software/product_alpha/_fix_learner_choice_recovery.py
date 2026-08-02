#!/usr/bin/env python3
"""Make learner choice recovery safe for minimal runtime harnesses."""
from pathlib import Path

HTML_PATH = Path("software/product_alpha/index.html")

html = HTML_PATH.read_text(encoding="utf-8")
old = "const first=group.querySelector('input[type=\"radio\"]');if(first&&typeof first.focus===\"function\")first.focus()"
new = "const first=typeof group.querySelector===\"function\"?group.querySelector('input[type=\"radio\"]'):q(`${groupSelector} input[type=\"radio\"]`);if(first&&typeof first.focus===\"function\")first.focus()"
count = html.count(old)
if count != 1:
    raise SystemExit(f"choice focus compatibility: expected one anchor, found {count}")
HTML_PATH.write_text(html.replace(old, new, 1), encoding="utf-8")
