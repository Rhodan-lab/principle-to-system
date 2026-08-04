#!/usr/bin/env python3
"""Build and serve the Principia Product Alpha pilot on loopback only."""

from __future__ import annotations

import argparse
import hashlib
import http.client
import json
import re
import subprocess
import sys
import tempfile
import threading
import time
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Sequence

try:
    from software.product_alpha import package_integrity, snapshot_server
except ModuleNotFoundError:
    import package_integrity
    import snapshot_server

LOOPBACK_HOST = "127.0.0.1"
DEFAULT_PORT = 8000
DEFAULT_ROUTE = "refrigerator"
REPO_ROOT = Path(__file__).resolve().parents[2]
BUILD_SCRIPT = REPO_ROOT / "software" / "product_alpha" / "build.py"
DEFAULT_OUTPUT = REPO_ROOT / "software" / "product_alpha" / "dist"
BUILD_MANIFEST = package_integrity.BUILD_MANIFEST
BUILD_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")
SUPPORTED_ROUTES = ("refrigerator", "distributed-information")
if SUPPORTED_ROUTES != package_integrity.SUPPORTED_ROUTES:
    raise RuntimeError("launcher routes do not match package integrity authority")
REQUIRED_OUTPUTS = (*package_integrity.REQUIRED_STATIC_FILES, BUILD_MANIFEST)
CONTENT_SECURITY_POLICY = (
    "default-src 'self'; "
    "base-uri 'none'; "
    "connect-src 'self'; "
    "form-action 'none'; "
    "frame-ancestors 'none'; "
    "img-src 'self' data:; "
    "object-src 'none'; "
    "script-src 'self' 'unsafe-inline'; "
    "style-src 'self' 'unsafe-inline'"
)
PERMISSIONS_POLICY = (
    "camera=(), display-capture=(), geolocation=(), microphone=(), "
    "payment=(), serial=(), usb=()"
)
PILOT_RESPONSE_HEADERS = {
    "cache-control": "no-store",
    "pragma": "no-cache",
    "x-content-type-options": "nosniff",
    "referrer-policy": "no-referrer",
    "cross-origin-opener-policy": "same-origin",
    "cross-origin-resource-policy": "same-origin",
    "x-frame-options": "DENY",
    "content-security-policy": CONTENT_SECURITY_POLICY,
    "permissions-policy": PERMISSIONS_POLICY,
}
SMOKE_REQUIRED_HEADERS = dict(PILOT_RESPONSE_HEADERS)
SMOKE_TARGETS = (
    ("learner", "/", b"<title>Principia Product Alpha</title>"),
    (
        "facilitator",
        "/facilitator.html?build_id={build_id}",
        b"pilot_build_id:pilotBuildId",
    ),
    (
        "pilot_lab",
        "/pilot-lab.html?build_id={build_id}",
        b'EXPECTED_BUILD_ID=query?.get("build_id")',
    ),
    (
        "route",
        "/data/{route_id}.json",
        b'"contract":"principia-product-alpha-route/0.1"',
    ),
    (
        "manifest",
        f"/{BUILD_MANIFEST}",
        b'"contract":"principia-product-alpha-build/0.1"',
    ),
)


class PilotRequestHandler(SimpleHTTPRequestHandler):
    """Serve static pilot assets only for the exact loopback host."""

    quiet_logs = False

    def _trusted_host(self) -> bool:
        actual_port = int(self.server.server_address[1])
        return self.headers.get("Host", "") in {
            LOOPBACK_HOST,
            f"{LOOPBACK_HOST}:{actual_port}",
        }

    def _reject_untrusted_host(self) -> bool:
        if self._trusted_host():
            return False
        self.send_error(421, "Loopback Host header required")
        return True

    def do_GET(self) -> None:
        if not self._reject_untrusted_host():
            super().do_GET()

    def do_HEAD(self) -> None:
        if not self._reject_untrusted_host():
            super().do_HEAD()

    def end_headers(self) -> None:
        for header, value in PILOT_RESPONSE_HEADERS.items():
            self.send_header(header, value)
        super().end_headers()

    def log_message(self, format: str, *args: object) -> None:
        if not self.quiet_logs:
            super().log_message(format, *args)


def validate_port(value: int) -> int:
    if not 0 <= value <= 65535:
        raise ValueError("port must be between 0 and 65535")
    return value


def validate_build_id(value: str) -> str:
    if not BUILD_ID_PATTERN.fullmatch(value):
        raise ValueError("build ID must be a 64-character lowercase SHA-256")
    return value


def pilot_urls(port: int, build_id: str | None = None) -> dict[str, str]:
    base = f"http://{LOOPBACK_HOST}:{port}"
    suffix = ""
    if build_id is not None:
        suffix = f"?build_id={validate_build_id(build_id)}"
    return {
        "learner": f"{base}/",
        "facilitator": f"{base}/facilitator.html{suffix}",
        "pilot_lab": f"{base}/pilot-lab.html{suffix}",
    }


def run_builder(command: str, output: Path = DEFAULT_OUTPUT, route: str = DEFAULT_ROUTE) -> None:
    args = [sys.executable, str(BUILD_SCRIPT), command, "--root", str(REPO_ROOT)]
    if route != DEFAULT_ROUTE:
        args.extend(["--route", route])
    if command == "build":
        args.extend(["--output", str(output)])
    subprocess.run(args, check=True)


def verify_output(output: Path) -> None:
    missing = [relative for relative in REQUIRED_OUTPUTS if not (output / relative).is_file()]
    if missing:
        raise FileNotFoundError(
            "Product Alpha build is missing required pilot assets: " + ", ".join(missing)
        )


def pilot_build_identity(output: Path) -> str:
    """Return the manifest identity after verifying every packaged asset."""
    return validate_build_id(package_integrity.pilot_build_identity(output))


def create_server(
    output: Path,
    port: int,
    build_id: str,
    quiet: bool = False,
) -> ThreadingHTTPServer:
    validate_port(port)
    return snapshot_server.create_snapshot_server(
        output,
        port,
        validate_build_id(build_id),
        host=LOOPBACK_HOST,
        handler_base=PilotRequestHandler,
        quiet=quiet,
    )


def _fetch_smoke_target(
    port: int,
    path: str,
    host_header: str | None = None,
    method: str = "GET",
) -> tuple[int, dict[str, str], bytes]:
    """Fetch one loopback target with a short startup retry window."""
    last_error: OSError | None = None
    for _ in range(20):
        connection = http.client.HTTPConnection(LOOPBACK_HOST, port, timeout=5)
        try:
            headers = {} if host_header is None else {"Host": host_header}
            connection.request(method, path, headers=headers)
            response = connection.getresponse()
            body = response.read()
            response_headers = {
                key.lower(): value for key, value in response.getheaders()
            }
            return response.status, response_headers, body
        except OSError as exc:
            last_error = exc
            time.sleep(0.02)
        finally:
            connection.close()
    raise ConnectionError(f"could not reach loopback pilot target {path}: {last_error}")


def _verify_smoke_headers(target_id: str, headers: dict[str, str]) -> None:
    for header, expected_value in SMOKE_REQUIRED_HEADERS.items():
        actual_value = headers.get(header)
        if actual_value != expected_value:
            raise ValueError(
                f"pilot smoke target {target_id} header {header!r} "
                f"must be {expected_value!r}, found {actual_value!r}"
            )


def smoke_served_output(output: Path, build_id: str, route: str = DEFAULT_ROUTE) -> dict[str, object]:
    """Serve and verify the exact packaged pilot without retaining any state."""
    verify_output(output)
    expected_build_id = validate_build_id(build_id)
    actual_build_id = pilot_build_identity(output)
    if actual_build_id != expected_build_id:
        raise ValueError(
            "verified build package does not match the expected Pilot build ID"
        )
    server = create_server(output, 0, expected_build_id, quiet=True)
    actual_host = str(server.server_address[0])
    actual_port = int(server.server_address[1])
    if actual_host != LOOPBACK_HOST:
        server.server_close()
        raise ValueError(f"pilot smoke server escaped loopback: {actual_host}")

    thread = threading.Thread(
        target=server.serve_forever,
        kwargs={"poll_interval": 0.01},
        daemon=True,
    )
    thread.start()
    verified_targets: list[str] = []
    head_verified = False
    foreign_host_methods_rejected: list[str] = []
    try:
        for target_id, path_template, marker in SMOKE_TARGETS:
            path = path_template.format(build_id=expected_build_id, route_id=route)
            status, headers, body = _fetch_smoke_target(actual_port, path)
            if status != 200:
                raise ValueError(
                    f"pilot smoke target {target_id} returned HTTP {status}"
                )
            _verify_smoke_headers(target_id, headers)
            if marker not in body:
                raise ValueError(
                    f"pilot smoke target {target_id} is missing its packaged marker"
                )
            if target_id == "manifest":
                served_build_id = hashlib.sha256(body).hexdigest()
                if served_build_id != expected_build_id:
                    raise ValueError(
                        "served build manifest does not match the expected Pilot build ID"
                    )
            verified_targets.append(target_id)

        head_status, head_headers, head_body = _fetch_smoke_target(
            actual_port,
            "/",
            method="HEAD",
        )
        if head_status != 200:
            raise ValueError(
                f"pilot smoke trusted HEAD request returned HTTP {head_status}"
            )
        _verify_smoke_headers("trusted-head", head_headers)
        if head_body:
            raise ValueError("pilot smoke trusted HEAD request returned a response body")
        head_verified = True

        for method in ("GET", "HEAD"):
            foreign_status, foreign_headers, foreign_body = _fetch_smoke_target(
                actual_port,
                "/",
                host_header="attacker.example",
                method=method,
            )
            if foreign_status != 421:
                raise ValueError(
                    f"pilot smoke foreign Host {method} request must return HTTP 421, "
                    f"found {foreign_status}"
                )
            _verify_smoke_headers(f"foreign-host-{method.lower()}", foreign_headers)
            if b"<title>Principia Product Alpha</title>" in foreign_body:
                raise ValueError(
                    f"pilot smoke foreign Host {method} request exposed the learner page"
                )
            foreign_host_methods_rejected.append(method)
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()

    return {
        "contract": "principia-product-alpha-pilot-smoke/0.1",
        "decision": "pilot-smoke-passed",
        "host": LOOPBACK_HOST,
        "build_id": expected_build_id,
        "target_count": len(verified_targets),
        "targets": verified_targets,
        "headers_verified": sorted(SMOKE_REQUIRED_HEADERS),
        "head_verified": head_verified,
        "foreign_host_rejected": foreign_host_methods_rejected == ["GET", "HEAD"],
        "foreign_host_methods_rejected": foreign_host_methods_rejected,
        "session_data_stored": False,
    }


def serve(output: Path, port: int, open_browser: bool, quiet: bool, route: str = DEFAULT_ROUTE) -> None:
    run_builder("build", output, route)
    verify_output(output)
    build_id = pilot_build_identity(output)
    try:
        server = create_server(output, port, build_id, quiet=quiet)
    except (OSError, ValueError) as exc:
        raise SystemExit(
            f"Could not bind the local pilot server to {LOOPBACK_HOST}:{port}: {exc}"
        ) from exc
    actual_port = int(server.server_address[1])
    urls = pilot_urls(actual_port, build_id)
    print("Principia Product Alpha pilot is ready.")
    print(f"Pilot build ID:       {build_id}")
    print(f"Learner route:        {urls['learner']}")
    print(f"Facilitator recorder: {urls['facilitator']}")
    print(f"Pilot Lab:            {urls['pilot_lab']}")
    print("Cohort rule: every exported session carries this pilot build ID.")
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
    parser.add_argument(
        "command",
        nargs="?",
        choices=("serve", "check", "smoke"),
        default="serve",
        help=(
            "serve the local pilot, verify its deterministic build, or smoke-test "
            "the real loopback HTTP path"
        ),
    )
    parser.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="loopback port; use 0 to select an available local port",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT, help="static build directory"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        dest="open_browser",
        help="open the learner, recorder, and Pilot Lab in local browser tabs",
    )
    parser.add_argument("--quiet", action="store_true", help="suppress HTTP request logs")
    parser.add_argument(
        "--route",
        default=DEFAULT_ROUTE,
        choices=SUPPORTED_ROUTES,
        help="learner route to package and serve",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        validate_port(args.port)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc
    output = args.output.resolve()
    if args.command in {"check", "smoke"}:
        run_builder("check", output, args.route)
        with tempfile.TemporaryDirectory() as directory:
            check_output = Path(directory)
            run_builder("build", check_output, args.route)
            verify_output(check_output)
            build_id = pilot_build_identity(check_output)
            urls = pilot_urls(0, build_id)
            if args.command == "smoke":
                report = smoke_served_output(check_output, build_id, args.route)
        if args.command == "check":
            print(
                "Product Alpha pilot launcher check passed: "
                f"host={LOOPBACK_HOST}, required_assets={len(REQUIRED_OUTPUTS)}, "
                f"build_id={build_id}, "
                f"recorder_bound={urls['facilitator'].endswith(build_id)}, "
                f"pilot_lab_bound={urls['pilot_lab'].endswith(build_id)}"
            )
        else:
            rejected_methods = "+".join(report["foreign_host_methods_rejected"])
            print(
                "Product Alpha pilot smoke passed: "
                f"host={report['host']}, targets={report['target_count']}, "
                f"build_id={report['build_id']}, "
                f"head_verified={str(report['head_verified']).lower()}, "
                f"foreign_host_methods_rejected={rejected_methods}, "
                f"session_data_stored={str(report['session_data_stored']).lower()}"
            )
        return 0
    serve(output, args.port, args.open_browser, args.quiet, args.route)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())