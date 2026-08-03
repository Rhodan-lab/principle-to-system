#!/usr/bin/env python3
"""Make packaged Pilot Lab route binding safe when the default marker is unchanged."""
from pathlib import Path

PATH = Path("software/product_alpha/build.py")
text = PATH.read_text(encoding="utf-8")
old = '''    data = _replace_once(
        data,
        b'const ROUTE_ID="refrigerator-v1"',
        f'const ROUTE_ID="{evidence_route}"'.encode("utf-8"),
        "Pilot Lab route identity",
    )
'''
new = '''    default_route_marker = b'const ROUTE_ID="refrigerator-v1"'
    if data.count(default_route_marker) != 1:
        raise ValueError("Pilot Lab route identity must occur exactly once")
    if evidence_route != route_identity.DEFAULT_EVIDENCE_ROUTE:
        data = data.replace(
            default_route_marker,
            f'const ROUTE_ID="{evidence_route}"'.encode("utf-8"),
            1,
        )
'''
if text.count(old) != 1:
    raise SystemExit("generated Pilot Lab route binding anchor changed")
PATH.write_text(text.replace(old, new, 1), encoding="utf-8")
