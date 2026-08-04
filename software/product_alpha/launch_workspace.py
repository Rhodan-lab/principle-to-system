#!/usr/bin/env python3
"""Build and launch Product Alpha only when it matches a prepared cohort workspace."""

from __future__ import annotations

import argparse
import json
import subprocess
import webbrowser
from pathlib import Path
from typing import Any, Sequence

import run_pilot
import route_identity

CONTRACT = "principia-product-alpha-workspace-launch/0.1"
WORKSPACE_CONTRACT = "principia-product-alpha-pilot-workspace/0.1"
ROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE
REQUIRED_PRIVACY_BOUNDARIES = {
    "participant_names_allowed": False,
    "raw_sessions_committed_to_repository": False,
    "repository_output_allowed": False,
}


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def load_workspace_binding(
    workspace: Path,
    *,
    repo_root: Path = run_pilot.REPO_ROOT,
) -> dict[str, str]:
    """Load and validate one repository-external Product Alpha workspace binding."""
    root = workspace.expanduser().resolve(strict=True)
    if not root.is_dir():
        raise ValueError("workspace must be a directory")
    repository = repo_root.expanduser().resolve(strict=False)
    if _is_within(root, repository):
        raise ValueError("workspace must be outside the repository")

    manifest_path = root / "workspace.json"
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("workspace.json must be a regular file")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"workspace.json is invalid JSON: {exc.msg}") from exc
    if not isinstance(manifest, dict):
        raise ValueError("workspace.json must contain one JSON object")
    if manifest.get("contract") != WORKSPACE_CONTRACT:
        raise ValueError(
            f"workspace.json contract must be {WORKSPACE_CONTRACT!r}"
        )

    build_id = manifest.get("pilot_build_id")
    if not isinstance(build_id, str):
        raise ValueError("workspace.json pilot_build_id must be text")
    expected_build_id = run_pilot.validate_build_id(build_id)
    try:
        route_id = route_identity.validate_evidence_route_id(manifest.get("route_id"))
    except ValueError as exc:
        raise ValueError(f"workspace.json {exc}") from exc

    privacy = manifest.get("privacy_boundaries")
    if not isinstance(privacy, dict):
        raise ValueError("workspace.json privacy_boundaries must be an object")
    for key, expected in REQUIRED_PRIVACY_BOUNDARIES.items():
        if privacy.get(key) is not expected:
            raise ValueError(
                f"workspace.json privacy boundary {key!r} must be {expected}"
            )

    return {
        "workspace": str(root),
        "pilot_build_id": expected_build_id,
        "route_id": route_id,
    }


def prepare_workspace_launch(
    workspace: Path,
    output: Path = run_pilot.DEFAULT_OUTPUT,
) -> dict[str, object]:
    """Build Product Alpha and prove that it matches the prepared workspace."""
    binding = load_workspace_binding(workspace)
    destination = output.expanduser().resolve()
    software_route = route_identity.software_route_id(binding["route_id"])
    run_pilot.run_builder("build", destination, software_route)
    run_pilot.verify_output(destination)
    actual_build_id = run_pilot.pilot_build_identity(destination)
    expected_build_id = binding["pilot_build_id"]
    if actual_build_id != expected_build_id:
        raise ValueError(
            "current Product Alpha build does not match workspace pilot_build_id: "
            f"expected {expected_build_id}, found {actual_build_id}"
        )

    return {
        "contract": CONTRACT,
        "decision": "workspace-build-bound",
        "workspace": binding["workspace"],
        "pilot_build_id": actual_build_id,
        "route_id": binding["route_id"],
        "output": str(destination),
        "host": run_pilot.LOOPBACK_HOST,
        "session_data_stored": False,
        "workspace_manifest_modified": False,
    }


def launch(
    workspace: Path,
    output: Path,
    port: int,
    open_browser: bool,
    quiet: bool,
) -> None:
    """Serve the exact workspace-bound build on loopback until interrupted."""
    run_pilot.validate_port(port)
    report = prepare_workspace_launch(workspace, output)
    build_id = str(report["pilot_build_id"])
    try:
        server = run_pilot.create_server(
            output.expanduser().resolve(),
            port,
            build_id,
            quiet=quiet,
        )
    except OSError as exc:
        raise OSError(
            f"could not bind local pilot server to {run_pilot.LOOPBACK_HOST}:{port}: {exc}"
        ) from exc

    actual_host = str(server.server_address[0])
    actual_port = int(server.server_address[1])
    if actual_host != run_pilot.LOOPBACK_HOST:
        server.server_close()
        raise ValueError(f"workspace pilot server escaped loopback: {actual_host}")

    urls = run_pilot.pilot_urls(actual_port, build_id)
    print("Principia Product Alpha workspace pilot is ready.")
    print(f"Workspace:            {report['workspace']}")
    print(f"Pilot build ID:       {build_id}")
    print(f"Learner route:        {urls['learner']}")
    print(f"Facilitator recorder: {urls['facilitator']}")
    print(f"Pilot Lab:            {urls['pilot_lab']}")
    print("Workspace binding: current build exactly matches workspace.json.")
    print("Boundary: loopback-only server; no session data is stored by this process.")
    print("Press Ctrl+C to stop.")

    if open_browser:
        webbrowser.open(urls["learner"], new=2)
        webbrowser.open(urls["facilitator"], new=2)
        webbrowser.open(urls["pilot_lab"], new=2)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping workspace-bound local pilot server.")
    finally:
        server.server_close()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "command",
        nargs="?",
        choices=("serve", "check"),
        default="serve",
        help="serve the workspace-bound pilot or only verify the build binding",
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="private cohort workspace created by prepare_pilot.py",
    )
    parser.add_argument(
        "--port",
        type=int,
        default=run_pilot.DEFAULT_PORT,
        help="loopback port; use 0 to select an available local port",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=run_pilot.DEFAULT_OUTPUT,
        help="static Product Alpha build directory",
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="open learner, recorder, and Pilot Lab in local browser tabs",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress HTTP request logs")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        run_pilot.validate_port(args.port)
        if args.command == "check":
            report = prepare_workspace_launch(args.workspace, args.output)
            print(json.dumps(report, sort_keys=True))
        else:
            launch(
                args.workspace,
                args.output,
                args.port,
                args.open_browser,
                args.quiet,
            )
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        raise SystemExit(f"workspace pilot launch failed: {exc}") from exc
    return 0


if __name__ == "__main__":
    raise SystemExit(main())