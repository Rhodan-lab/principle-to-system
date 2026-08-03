#!/usr/bin/env python3
"""Smoke-test Product Alpha and create a private build-bound cohort workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Sequence

import run_pilot
import route_identity
from evaluation.prepare_workspace import prepare_workspace

CONTRACT = "principia-product-alpha-pilot-preparation/0.1"


def prepare_pilot(
    workspace: Path, route: str = route_identity.DEFAULT_SOFTWARE_ROUTE
) -> dict[str, object]:
    """Pass the real loopback smoke gate, then create one empty private workspace."""
    evidence_route = route_identity.evidence_route_id(route)
    run_pilot.run_builder("check", route=route)
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        run_pilot.run_builder("build", output, route)
        run_pilot.verify_output(output)
        build_id = run_pilot.pilot_build_identity(output)
        smoke = run_pilot.smoke_served_output(output, build_id, route)

    manifest = prepare_workspace(workspace, build_id, route_id=evidence_route)
    destination = workspace.expanduser().resolve(strict=False)
    return {
        "contract": CONTRACT,
        "decision": "pilot-preparation-passed",
        "pilot_build_id": build_id,
        "route_id": evidence_route,
        "smoke_contract": smoke["contract"],
        "smoke_decision": smoke["decision"],
        "workspace_contract": manifest["contract"],
        "workspace": str(destination),
        "session_data_stored": False,
        "placeholder_evidence_created": False,
    }


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="new private cohort workspace outside this repository",
    )
    parser.add_argument(
        "--route",
        default=route_identity.DEFAULT_SOFTWARE_ROUTE,
        choices=route_identity.SUPPORTED_SOFTWARE_ROUTES,
        help="learner route to build, smoke, and bind",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = prepare_pilot(args.workspace, args.route)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"pilot preparation failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
