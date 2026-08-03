#!/usr/bin/env python3
"""Fix route-identity imports and explicit route test expectations."""
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

asset_test = Path("software/tests/test_product_alpha.py")
text = asset_test.read_text(encoding="utf-8")
old = 'with self.assertRaisesRegex(ValueError, "exactly one canonical state"):'
new = 'with self.assertRaisesRegex(ValueError, "route identity must occur exactly once"):'
if text.count(old) != 2:
    raise SystemExit("static asset guard assertions: expected two anchors")
asset_test.write_text(text.replace(old, new), encoding="utf-8")
