#!/usr/bin/env python3
"""Serve one verified Product Alpha build from an immutable in-memory snapshot."""

from __future__ import annotations

import hashlib
import io
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Type
from urllib.parse import unquote, urlsplit

try:
    from software.product_alpha import package_integrity
except ModuleNotFoundError:
    import package_integrity


def request_asset_path(target: str) -> str | None:
    """Map one safe request target to a manifest-bound package path."""
    decoded = unquote(urlsplit(target).path)
    if decoded == "/":
        return "index.html"
    if not decoded.startswith("/") or decoded.endswith("/"):
        return None
    relative = decoded[1:]
    path = PurePosixPath(relative)
    if (
        not relative
        or path.is_absolute()
        or relative != path.as_posix()
        or any(part in {"", ".", ".."} for part in path.parts)
        or "\\" in relative
    ):
        return None
    return relative


def create_snapshot_server(
    output: Path,
    port: int,
    expected_build_id: str,
    *,
    host: str,
    handler_base: Type[SimpleHTTPRequestHandler],
    quiet: bool = False,
) -> ThreadingHTTPServer:
    """Verify, snapshot, and serve one exact package without filesystem rereads."""
    if not package_integrity.SHA256_PATTERN.fullmatch(expected_build_id):
        raise ValueError("build ID must be a 64-character lowercase SHA-256")
    _, manifest_raw, package = package_integrity.load_verified_package(output)
    actual_build_id = hashlib.sha256(manifest_raw).hexdigest()
    if actual_build_id != expected_build_id:
        raise ValueError(
            "verified build package does not match the expected Pilot build ID"
        )

    class SnapshotHandler(handler_base):
        quiet_logs = quiet
        package_files = package

        def send_head(self) -> io.BytesIO | None:
            relative = request_asset_path(self.path)
            if relative is None or relative not in self.package_files:
                self.send_error(404, "Package asset not found")
                return None
            data = self.package_files[relative]
            stream = io.BytesIO(data)
            self.send_response(200)
            self.send_header("Content-Type", self.guess_type(relative))
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            return stream

    return ThreadingHTTPServer((host, port), SnapshotHandler)
