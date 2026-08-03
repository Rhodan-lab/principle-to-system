#!/usr/bin/env python3
"""Bind Product Alpha route configs and packages to route-specific rubrics."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


rubrics = {
    "refrigerator": "software/product_alpha/evaluation/rubric.json",
    "distributed-information": (
        "software/product_alpha/evaluation/rubrics/"
        "distributed-information-v1.json"
    ),
}
for route, rubric_path in rubrics.items():
    path = ROOT / "software" / "product_alpha" / "routes" / f"{route}.json"
    config = json.loads(path.read_text(encoding="utf-8"))
    existing = config.get("evaluation")
    expected = {"rubric": rubric_path}
    if existing not in (None, expected):
        raise SystemExit(f"{route}: unexpected evaluation config: {existing!r}")
    config["evaluation"] = expected
    path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

build = ROOT / "software" / "product_alpha" / "build.py"
replace_once(
    build,
    '    required = {"id", "title", "sources", "steps", "model", "atlas_references"}',
    '    required = {"id", "title", "sources", "steps", "model", "evaluation", "atlas_references"}',
    "route evaluation requirement",
)
replace_once(
    build,
    '    if not isinstance(model.get("parameters"), list) or not model["parameters"]:\n        raise ValueError("Product Alpha route model parameters are required")\n    return config',
    '    if not isinstance(model.get("parameters"), list) or not model["parameters"]:\n        raise ValueError("Product Alpha route model parameters are required")\n    evaluation = config.get("evaluation")\n    if not isinstance(evaluation, dict):\n        raise ValueError("Product Alpha route evaluation config is required")\n    rubric_path = evaluation.get("rubric")\n    if (\n        not isinstance(rubric_path, str)\n        or not rubric_path.startswith("software/product_alpha/evaluation/")\n        or not (root / rubric_path).is_file()\n    ):\n        raise ValueError("Product Alpha route rubric path is invalid")\n    return config',
    "route rubric validation",
)
replace_once(
    build,
    '    evidence_route = route_identity.evidence_route_id(route)\n    if relative_path == "index.html":',
    '    evidence_route = route_identity.evidence_route_id(route)\n    if relative_path == "evaluation/rubric.json":\n        rubric = json.loads(data.decode("utf-8"))\n        if rubric.get("route_id") != evidence_route:\n            raise ValueError(\n                f"rubric route_id must be {evidence_route!r} for route {route!r}"\n            )\n        return data\n    if relative_path == "index.html":',
    "packaged rubric route validation",
)
replace_once(
    build,
    'def copy_static_files(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> list[dict[str, str]]:\n    assets = root / "software" / "product_alpha"\n    copied: list[dict[str, str]] = []\n    for relative_path in (*STATIC_ASSETS, *EVALUATION_ASSETS):\n        source = assets / relative_path',
    'def copy_static_files(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> list[dict[str, str]]:\n    assets = root / "software" / "product_alpha"\n    config = load_config(root, route)\n    rubric_source = root / config["evaluation"]["rubric"]\n    copied: list[dict[str, str]] = []\n    for relative_path in (*STATIC_ASSETS, *EVALUATION_ASSETS):\n        source = (\n            rubric_source\n            if relative_path == "evaluation/rubric.json"\n            else assets / relative_path\n        )',
    "route rubric source selection",
)
