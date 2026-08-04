#!/usr/bin/env python3
"""Verify and run an extracted Principia & Atlas release."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import webbrowser
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath

CONTRACT = "principia-atlas-release/0.1"
PRODUCT = "Principia & Atlas"
MANIFEST_NAME = "RELEASE-MANIFEST.json"
SHA256 = re.compile(r"^[0-9a-f]{64}$")
MAX_FILE_BYTES = 64 * 1024 * 1024
MAX_TOTAL_BYTES = 512 * 1024 * 1024
MAX_FILES = 4096
HOST = "127.0.0.1"


def canonical_json(value):
    return (
        json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
        + "\n"
    ).encode("utf-8")


def sha256(raw):
    return hashlib.sha256(raw).hexdigest()


def strict_object(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key: " + key)
        output[key] = value
    return output


def decode(raw):
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=strict_object,
            parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)),
        )
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ValueError("release manifest is not strict UTF-8 JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("release manifest must be an object")
    return value


def safe_relative(path):
    if not path or "\\" in path or path.startswith("/"):
        raise ValueError("unsafe release path: " + repr(path))
    candidate = PurePosixPath(path)
    if (
        any(part in {"", ".", ".."} for part in candidate.parts)
        or candidate.as_posix() != path
    ):
        raise ValueError("unsafe release path: " + repr(path))
    return candidate


def verify(root):
    root = Path(os.path.abspath(os.fspath(root)))
    manifest_path = root / MANIFEST_NAME
    if (
        manifest_path.is_symlink()
        or not manifest_path.is_file()
        or manifest_path.stat().st_size > 1024 * 1024
    ):
        raise ValueError("release manifest is missing or invalid")
    manifest = decode(manifest_path.read_bytes())
    if manifest.get("contract") != CONTRACT or manifest.get("product") != PRODUCT:
        raise ValueError("release manifest contract is invalid")
    release_id = manifest.get("release_id")
    unsigned = dict(manifest)
    unsigned.pop("release_id", None)
    if (
        not isinstance(release_id, str)
        or not SHA256.fullmatch(release_id)
        or sha256(canonical_json(unsigned)) != release_id
    ):
        raise ValueError("release manifest seal is invalid")
    payload = manifest.get("payload")
    if not isinstance(payload, dict) or not isinstance(payload.get("files"), dict):
        raise ValueError("release payload manifest is invalid")
    expected = payload["files"]
    actual = {}
    total = 0
    for path in sorted(root.rglob("*")):
        if path == manifest_path:
            continue
        if path.is_symlink():
            raise ValueError("release contains a symlink: " + str(path))
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("release contains a non-regular entry: " + str(path))
        relative = path.relative_to(root).as_posix()
        safe_relative(relative)
        size = path.stat().st_size
        if size > MAX_FILE_BYTES:
            raise ValueError("release file exceeds resource limit: " + relative)
        raw = path.read_bytes()
        total += len(raw)
        if len(actual) + 1 > MAX_FILES or total > MAX_TOTAL_BYTES:
            raise ValueError("release exceeds resource limits")
        actual[relative] = {"sha256": sha256(raw), "size": len(raw)}
    if actual != expected:
        raise ValueError("release payload does not match its manifest")
    if payload.get("file_count") != len(actual) or payload.get("total_bytes") != total:
        raise ValueError("release payload counters are invalid")
    product = root / "product"
    if not (product / "index.html").is_file():
        raise ValueError("release product entry point is missing")
    print(
        "Verified Principia & Atlas release "
        + str(manifest.get("version"))
        + " ("
        + release_id
        + ")"
    )
    return manifest


class Handler(SimpleHTTPRequestHandler):
    quiet = False

    def log_message(self, format, *args):
        if not self.quiet:
            super().log_message(format, *args)

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "no-referrer")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        super().end_headers()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("verify", "run"))
    parser.add_argument("--port", type=int, default=8787)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parent
    verify(root)
    if args.command == "verify":
        return 0
    if args.port < 0 or args.port > 65535:
        raise ValueError("port must be between 0 and 65535")
    product = root / "product"
    Handler.quiet = args.quiet
    handler = lambda *values, **kwargs: Handler(
        *values,
        directory=str(product),
        **kwargs,
    )
    server = ThreadingHTTPServer((HOST, args.port), handler)
    port = int(server.server_address[1])
    home = f"http://{HOST}:{port}/"
    print("Principia & Atlas: " + home)
    print("Learn: " + home + "principia/index.html")
    print("Research: " + home + "atlas/index.html")
    if args.open:
        webbrowser.open(home)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
