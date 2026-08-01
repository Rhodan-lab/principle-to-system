#!/usr/bin/env python3
"""Build and serve the Principia Product Alpha pilot on loopback only."""

from __future__ import annotations

import argparse
import subprocess
import sys
import webbrowser
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Sequence

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "software" / "product_alpha" / "build.py"
DEFAULT_OUTPUT = REPO_ROOT / "software" / "product_alpha" / "dist"
REQUIRED_OUTPUTS = (
    "index.html",
    "facilitator.html",
    "pilot-lab.html",
    "evaluation/rubric.json",
    "evaluation/session-template.json",
)


class PilotRequestHandler(SimpleHTTPRequestHandler):
    """Serve static pilot assets with no-store response headers."""

    quiet_logs = False

    def end_headers(self) -> None:
        self.send_header("Cache-Control", "no-store")
        self.send_header("Pragma", "no-cache")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        if not self.quiet_logs:
            super().log_message(format, *args)


def validate_port(value: int) -> int:
    if not 0 <= value <= 65535:
        raise ValueError("port must be between 0 and 65535")
    return value


def pilot_urls(port: int) -> dict[str, str]:
    base = f"http://{LOOPBACK_HOST}:{port}"
    return {
        "learner": f"{base}/",
        "facilitator": f"{base}/facilitator.html",
        "pilot_lab": f"{base}/pilot-lab.html",
    }


def run_builder(command: str, output: Path = DEFAULT_OUTPUT) -> None:
    args = [sys.executable, str(BUILD_SCRIPT), command, "--root", str(REPO_ROOT)]
    if command == "build":
        args.extend(["--output", str(output)])
    subprocess.run(args, check=True)


def verify_output(output: Path) -> None:
    missing = [relative for relative in REQUIRED_OUTPUTS if not (output / relative).is_file()]
    if missing:
        raise FileNotFoundError("Product Alpha build is missing required pilot assets: " + ", ".join(missing))


def create_server(output: Path, port: int, quiet: bool = False) -> ThreadingHTTPServer:
    validate_port(port)

    class Handler(PilotRequestHandler):
        quiet_logs = quiet

    return ThreadingHTTPServer((LOOPBACK_HOST, port), partial(Handler, directory=str(output)))


def serve(output: Path, port: int, open_browser: bool, quiet: bool) -> None:
    run_builder("build", output)
    verify_output(output)
    try:
        server = create_server(output, port, quiet=quiet)
    except OSError as exc:
        raise SystemExit(f"Could not bind the local pilot server to {LOOPBACK_HOST}:{port}: {exc}") from exc
    actual_port = int(server.server_address[1])
    urls = pilot_urls(actual_port)
    print("Principia Product Alpha pilot is ready.")
    print(f"Learner route:        {urls['learner']}")
    print(f"Facilitator recorder: {urls['facilitator']}")
    print(f"Pilot Lab:            {urls['pilot_lab']}")
    print("Boundary: loopback-only server; no session data is stored by this process.")
    print("Press Ctrl+C to stop.")
    if open_browser:
        webbrowser.open(urls["learner"], new=2)
        webbrowser.open(urls["facilitator"], new=2)
        webbrowser.open(urls["pilot_lab"], new=2)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping local pilot server.")
    finally:
        server.server_close()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", nargs="?", choices=("serve", "check"), default="serve", help="serve the local pilot or verify its deterministic build")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="loopback port; use 0 to select an available local port")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="static build directory")
    parser.add_argument("--open", action="store_true", dest="open_browser", help="open the learner, recorder, and Pilot Lab in local browser tabs")
    parser.add_argument("--quiet", action="store_true", help="suppress HTTP request logs")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        validate_port(args.port)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    output = args.output.resolve()
    if args.command == "check":
        run_builder("check", output)
        print(f"Product Alpha pilot launcher check passed: host={LOOPBACK_HOST}, required_assets={len(REQUIRED_OUTPUTS)}")
        return 0
    serve(output, args.port, args.open_browser, args.quiet)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
