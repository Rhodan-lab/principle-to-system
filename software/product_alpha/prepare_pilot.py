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
from evaluation.prepare_workspace import prepare_workspace

CONTRACT = "principia-product-alpha-pilot-preparation/0.1"


def prepare_pilot(workspace: Path) -> dict[str, object]:
    """Pass the real loopback smoke gate, then create one empty private workspace."""
    run_pilot.run_builder("check")
    with tempfile.TemporaryDirectory() as directory:
        output = Path(directory)
        run_pilot.run_builder("build", output)
        run_pilot.verify_output(output)
        build_id = run_pilot.pilot_build_identity(output)
        smoke = run_pilot.smoke_served_output(output, build_id)

    manifest = prepare_workspace(workspace, build_id)
    destination = workspace.expanduser().resolve(strict=False)
    return {
        "contract": CONTRACT,
        "decision": "pilot-preparation-passed",
        "pilot_build_id": build_id,
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        report = prepare_pilot(args.workspace)
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"pilot preparation failed: {exc}") from exc
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
