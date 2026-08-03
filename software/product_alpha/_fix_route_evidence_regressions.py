#!/usr/bin/env python3
"""Fix route-identity import and explicit workspace route test expectations."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    if text.count(old) != 1:
        raise SystemExit(f"{label}: expected one anchor")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("software/product_alpha/build.py"),
    "import route_identity\n",
    "try:\n    from software.product_alpha import route_identity\nexcept ModuleNotFoundError:\n    import route_identity\n",
    "build route identity dual import",
)
replace_once(
    Path("software/tests/test_product_alpha_workspace_launch.py"),
    '            build.assert_called_once_with("build", output.resolve())',
    '            build.assert_called_once_with("build", output.resolve(), "refrigerator")',
    "workspace explicit refrigerator build",
)
