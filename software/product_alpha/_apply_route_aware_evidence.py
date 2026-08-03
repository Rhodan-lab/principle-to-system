#!/usr/bin/env python3
"""Apply the bounded Product Alpha route-aware evidence update."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


build = ROOT / "software" / "product_alpha" / "build.py"
replace_once(
    build,
    "from typing import Any\n",
    "from typing import Any\n\nimport route_identity\n",
    "build route identity import",
)
replace_once(
    build,
    'def prepare_static_asset(relative_path: str, data: bytes, route: str = DEFAULT_ROUTE) -> bytes:\n    """Apply bounded packaging repairs and reject ambiguous asset states."""\n    if relative_path == "index.html":',
    'def prepare_static_asset(relative_path: str, data: bytes, route: str = DEFAULT_ROUTE) -> bytes:\n    """Apply bounded packaging repairs and reject ambiguous asset states."""\n    evidence_route = route_identity.evidence_route_id(route)\n    if relative_path == "index.html":',
    "build evidence route binding",
)
replace_once(
    build,
    '    if relative_path == "facilitator.html":\n        for old, new, label in FACILITATOR_TRANSFORMS:',
    '    if relative_path == "evaluation/session-template.json":\n        template = json.loads(data.decode("utf-8"))\n        supported = template.get("supported_route_ids")\n        if supported != list(route_identity.SUPPORTED_EVIDENCE_ROUTES):\n            raise ValueError("session template supported_route_ids do not match route identity authority")\n        template["route_id"] = evidence_route\n        return json.dumps(template, indent=2, ensure_ascii=False).encode("utf-8") + b"\\n"\n    if relative_path == "facilitator.html":\n        for old, new, label in FACILITATOR_TRANSFORMS:',
    "build session template binding",
)
replace_once(
    build,
    '    if relative_path != "pilot-lab.html":\n        return data\n\n    data = _replace_once(',
    '    if relative_path != "pilot-lab.html":\n        return data\n\n    data = _replace_once(\n        data,\n        b\'const ROUTE_ID="refrigerator-v1"\',\n        f\'const ROUTE_ID="{evidence_route}"\'.encode("utf-8"),\n        "Pilot Lab route identity",\n    )\n    data = _replace_once(',
    "build Pilot Lab route binding",
)

summarize = ROOT / "software" / "product_alpha" / "evaluation" / "summarize.py"
replace_once(
    summarize,
    "import re\nfrom collections import Counter\nfrom pathlib import Path\nfrom typing import Any, Iterable\n\nROUTE_ID = \"refrigerator-v1\"",
    "import re\nimport sys\nfrom collections import Counter\nfrom pathlib import Path\nfrom typing import Any, Iterable\n\nPRODUCT_ALPHA_ROOT = Path(__file__).resolve().parents[1]\nif str(PRODUCT_ALPHA_ROOT) not in sys.path:\n    sys.path.insert(0, str(PRODUCT_ALPHA_ROOT))\nimport route_identity\n\nROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE",
    "summarizer route identity import",
)
replace_once(
    summarize,
    "def validate_session(session: dict[str, Any], line_number: int) -> dict[str, Any]:",
    "def validate_session(\n    session: dict[str, Any],\n    line_number: int,\n    expected_route_id: str | None = None,\n) -> dict[str, Any]:",
    "summarizer expected route signature",
)
replace_once(
    summarize,
    '    if session.get("route_id") != ROUTE_ID:\n        raise ValueError(f"line {line_number}: route_id must be {ROUTE_ID!r}")',
    '    try:\n        route_id = route_identity.validate_evidence_route_id(session.get("route_id"))\n    except ValueError as exc:\n        raise ValueError(f"line {line_number}: {exc}") from exc\n    if expected_route_id is not None and route_id != expected_route_id:\n        raise ValueError(\n            f"line {line_number}: route_id {route_id!r} does not match expected route {expected_route_id!r}"\n        )',
    "summarizer supported route validation",
)
replace_once(
    summarize,
    "    cohort_build_id: str | None = None\n",
    "    cohort_build_id: str | None = None\n    cohort_route_id: str | None = None\n",
    "summarizer cohort route state",
)
replace_once(
    summarize,
    '        session = validate_session(value, line_number)\n        session_id = session["session_id"]',
    '        session = validate_session(value, line_number, cohort_route_id)\n        if cohort_route_id is None:\n            cohort_route_id = session["route_id"]\n        session_id = session["session_id"]',
    "summarizer mixed route rejection",
)
replace_once(
    summarize,
    '    build_ids = {session.get("pilot_build_id") for session in sessions}\n    if len(build_ids) != 1:',
    '    route_ids = {session.get("route_id") for session in sessions}\n    if len(route_ids) != 1:\n        raise ValueError("route_id does not match across the cohort")\n    route_id = route_identity.validate_evidence_route_id(next(iter(route_ids)))\n    build_ids = {session.get("pilot_build_id") for session in sessions}\n    if len(build_ids) != 1:',
    "summarizer route aggregation",
)
replace_once(
    summarize,
    '        "route_id": ROUTE_ID,',
    '        "route_id": route_id,',
    "summarizer dynamic route output",
)

assemble = ROOT / "software" / "product_alpha" / "evaluation" / "assemble_workspace.py"
replace_once(
    assemble,
    '    if manifest.get("route_id") != pilot_summary.ROUTE_ID:\n        raise ValueError(\n            f"workspace.json route_id must be {pilot_summary.ROUTE_ID!r}"\n        )',
    '    try:\n        route_id = pilot_summary.route_identity.validate_evidence_route_id(\n            manifest.get("route_id")\n        )\n    except ValueError as exc:\n        raise ValueError(f"workspace.json {exc}") from exc\n    manifest["route_id"] = route_id',
    "workspace supported route validation",
)
replace_once(
    assemble,
    '            session = pilot_summary.validate_session(value, 1)',
    '            session = pilot_summary.validate_session(\n                value, 1, str(manifest["route_id"])\n            )',
    "workspace session route binding",
)

prepare_workspace = ROOT / "software" / "product_alpha" / "evaluation" / "prepare_workspace.py"
replace_once(
    prepare_workspace,
    "import shutil\nfrom pathlib import Path\nfrom typing import Sequence\n\nCONTRACT",
    "import shutil\nimport sys\nfrom pathlib import Path\nfrom typing import Sequence\n\nPRODUCT_ALPHA_ROOT = Path(__file__).resolve().parents[1]\nif str(PRODUCT_ALPHA_ROOT) not in sys.path:\n    sys.path.insert(0, str(PRODUCT_ALPHA_ROOT))\nimport route_identity\n\nCONTRACT",
    "workspace route identity import",
)
replace_once(
    prepare_workspace,
    'ROUTE_ID = "refrigerator-v1"',
    "ROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE",
    "workspace default route",
)
replace_once(
    prepare_workspace,
    'def _manifest(build_id: str, route_id: str) -> dict[str, object]:\n    return {',
    'def _manifest(build_id: str, route_id: str) -> dict[str, object]:\n    validated_route = route_identity.validate_evidence_route_id(route_id)\n    route_slug = route_identity.software_route_id(validated_route)\n    return {',
    "workspace manifest route validation",
)
replace_once(
    prepare_workspace,
    '        "route_id": route_id,',
    '        "route_id": validated_route,',
    "workspace manifest validated route",
)
replace_once(
    prepare_workspace,
    '            "review_output_prefix": "review/refrigerator-review",',
    '            "review_output_prefix": f"review/{route_slug}-review",',
    "workspace route review prefix",
)
replace_once(
    prepare_workspace,
    'def _readme(workspace: Path, build_id: str) -> str:\n    quote = shlex.quote',
    'def _readme(workspace: Path, build_id: str, route_id: str) -> str:\n    quote = shlex.quote\n    route_slug = route_identity.software_route_id(route_id)',
    "workspace README route signature",
)
replace_once(
    prepare_workspace,
    '        str(workspace / "handoff" / "refrigerator-product-change")',
    '        str(workspace / "handoff" / f"{route_slug}-product-change")',
    "workspace handoff route path",
)
replace_once(
    prepare_workspace,
    '- Route: `{ROUTE_ID}`',
    '- Route: `{route_id}`',
    "workspace README route display",
)
replace_once(
    prepare_workspace,
    '            _readme(destination, expected_build_id),',
    '            _readme(destination, expected_build_id, route_id),',
    "workspace README route call",
)
replace_once(
    prepare_workspace,
    '    parser.add_argument(\n        "--expect-build-id",\n        required=True,\n        help="full 64-character Pilot build ID printed by run_pilot.py",\n    )',
    '    parser.add_argument(\n        "--expect-build-id",\n        required=True,\n        help="full 64-character Pilot build ID printed by run_pilot.py",\n    )\n    parser.add_argument(\n        "--route",\n        default=route_identity.DEFAULT_SOFTWARE_ROUTE,\n        choices=route_identity.SUPPORTED_SOFTWARE_ROUTES,\n        help="packaged learner route bound to this workspace",\n    )',
    "workspace route CLI",
)
replace_once(
    prepare_workspace,
    '        manifest = prepare_workspace(args.workspace, args.expect_build_id)',
    '        manifest = prepare_workspace(\n            args.workspace,\n            args.expect_build_id,\n            route_id=route_identity.evidence_route_id(args.route),\n        )',
    "workspace route CLI call",
)

prepare_pilot = ROOT / "software" / "product_alpha" / "prepare_pilot.py"
replace_once(
    prepare_pilot,
    "import run_pilot\nfrom evaluation.prepare_workspace import prepare_workspace",
    "import run_pilot\nimport route_identity\nfrom evaluation.prepare_workspace import prepare_workspace",
    "pilot preparation route import",
)
replace_once(
    prepare_pilot,
    "def prepare_pilot(workspace: Path) -> dict[str, object]:",
    "def prepare_pilot(\n    workspace: Path, route: str = route_identity.DEFAULT_SOFTWARE_ROUTE\n) -> dict[str, object]:",
    "pilot preparation route signature",
)
replace_once(
    prepare_pilot,
    '    run_pilot.run_builder("check")',
    '    evidence_route = route_identity.evidence_route_id(route)\n    run_pilot.run_builder("check", route=route)',
    "pilot preparation route check",
)
replace_once(
    prepare_pilot,
    '        run_pilot.run_builder("build", output)',
    '        run_pilot.run_builder("build", output, route)',
    "pilot preparation route build",
)
replace_once(
    prepare_pilot,
    '        smoke = run_pilot.smoke_served_output(output, build_id)',
    '        smoke = run_pilot.smoke_served_output(output, build_id, route)',
    "pilot preparation route smoke",
)
replace_once(
    prepare_pilot,
    '    manifest = prepare_workspace(workspace, build_id)',
    '    manifest = prepare_workspace(workspace, build_id, route_id=evidence_route)',
    "pilot preparation route workspace",
)
replace_once(
    prepare_pilot,
    '        "pilot_build_id": build_id,',
    '        "pilot_build_id": build_id,\n        "route_id": evidence_route,',
    "pilot preparation route report",
)
replace_once(
    prepare_pilot,
    '    parser.add_argument(\n        "--workspace",\n        type=Path,\n        required=True,\n        help="new private cohort workspace outside this repository",\n    )',
    '    parser.add_argument(\n        "--workspace",\n        type=Path,\n        required=True,\n        help="new private cohort workspace outside this repository",\n    )\n    parser.add_argument(\n        "--route",\n        default=route_identity.DEFAULT_SOFTWARE_ROUTE,\n        choices=route_identity.SUPPORTED_SOFTWARE_ROUTES,\n        help="learner route to build, smoke, and bind",\n    )',
    "pilot preparation route CLI",
)
replace_once(
    prepare_pilot,
    '        report = prepare_pilot(args.workspace)',
    '        report = prepare_pilot(args.workspace, args.route)',
    "pilot preparation route CLI call",
)

launch = ROOT / "software" / "product_alpha" / "launch_workspace.py"
replace_once(
    launch,
    "import run_pilot\n\nCONTRACT",
    "import run_pilot\nimport route_identity\n\nCONTRACT",
    "workspace launcher route import",
)
replace_once(
    launch,
    'ROUTE_ID = "refrigerator-v1"',
    "ROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE",
    "workspace launcher default route",
)
replace_once(
    launch,
    '    route_id = manifest.get("route_id")\n    if route_id != ROUTE_ID:\n        raise ValueError(f"workspace.json route_id must be {ROUTE_ID!r}")',
    '    try:\n        route_id = route_identity.validate_evidence_route_id(manifest.get("route_id"))\n    except ValueError as exc:\n        raise ValueError(f"workspace.json {exc}") from exc',
    "workspace launcher supported route validation",
)
replace_once(
    launch,
    '    run_pilot.run_builder("build", destination)',
    '    software_route = route_identity.software_route_id(binding["route_id"])\n    run_pilot.run_builder("build", destination, software_route)',
    "workspace launcher route build",
)
replace_once(
    launch,
    '    urls = run_pilot.pilot_urls(actual_port, build_id)',
    '    urls = run_pilot.pilot_urls(actual_port, build_id)',
    "workspace launcher stable URL anchor",
)
