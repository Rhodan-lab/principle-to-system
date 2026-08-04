#!/usr/bin/env python3
"""Build, verify, and run Principia & Atlas from two source checkouts."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import uuid
import webbrowser
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator, Mapping, Sequence

try:
    from software.principia_atlas import suite
    from software.product_alpha import build as principia_build
except ModuleNotFoundError:
    REPO_BOOTSTRAP = Path(__file__).resolve().parents[2]
    sys.path.insert(0, str(REPO_BOOTSTRAP))
    from software.principia_atlas import suite
    from software.product_alpha import build as principia_build

CONTRACT = "principia-atlas-orchestration-receipt/0.1"
PRODUCT = "Principia & Atlas"
PRINCIPIA_REPOSITORY = "Rhodan-lab/principle-to-system"
ATLAS_REPOSITORY = "Rhodan-lab/Atlas"
ATLAS_MODULE = "tools.phase4_workspace.package_product_input"
ATLAS_REPORT_NAME = "workspace-shell-build-report.json"
RECEIPT_SUFFIX = ".build-receipt.json"
MAX_RECEIPT_BYTES = 1024 * 1024
GIT_OBJECT_ID = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")

PRINCIPIA_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ATLAS_REPO = PRINCIPIA_ROOT.parent / "Atlas"
DEFAULT_OUTPUT = PRINCIPIA_ROOT / "software" / "principia_atlas" / "dist"


def canonical_json(value: object) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _absolute(path: Path) -> Path:
    return Path(os.path.abspath(os.fspath(path.expanduser())))


def _run(
    command: Sequence[str],
    *,
    cwd: Path,
    capture: bool = False,
) -> str:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        list(command),
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
        env=env,
    )
    return completed.stdout.strip() if capture else ""


def _checkout(path: Path, label: str, required: Sequence[str]) -> Path:
    raw = _absolute(path)
    if raw.is_symlink():
        raise ValueError(f"{label} checkout must not be a symlink")
    try:
        root = raw.resolve(strict=True)
    except FileNotFoundError as exc:
        raise ValueError(f"{label} checkout does not exist: {raw}") from exc
    if not root.is_dir():
        raise ValueError(f"{label} checkout must be a directory")
    for relative in required:
        if not (root / relative).is_file():
            raise ValueError(f"{label} checkout is missing {relative}")
    return root


def git_state(
    root: Path,
    repository: str,
    *,
    allow_dirty: bool,
    expected_commit: str | None = None,
) -> dict[str, object]:
    top = Path(
        _run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            cwd=root,
            capture=True,
        )
    ).resolve()
    if top != root:
        raise ValueError(f"{repository} checkout root does not match its Git root")
    commit = _run(
        ["git", "-C", str(root), "rev-parse", "--verify", "HEAD"],
        cwd=root,
        capture=True,
    )
    if not GIT_OBJECT_ID.fullmatch(commit):
        raise ValueError(f"{repository} HEAD is not a full Git object ID")
    if expected_commit is not None and commit != expected_commit:
        raise ValueError(f"{repository} checkout is {commit}, expected {expected_commit}")
    dirty = bool(
        _run(
            [
                "git",
                "-C",
                str(root),
                "status",
                "--porcelain",
                "--untracked-files=no",
            ],
            cwd=root,
            capture=True,
        )
    )
    if dirty and not allow_dirty:
        raise ValueError(
            f"{repository} checkout has tracked changes; use --allow-dirty only for development"
        )
    return {"repository": repository, "commit": commit, "clean": not dirty}


def _source_roots(principia_root: Path, atlas_repo: Path) -> tuple[Path, Path]:
    principia = _checkout(
        principia_root,
        "Principia",
        ("software/product_alpha/build.py", "software/principia_atlas/suite.py"),
    )
    atlas = _checkout(
        atlas_repo,
        "Atlas",
        (
            "tools/phase4_workspace/package_product_input.py",
            "apps/workspace-shell/index.html",
        ),
    )
    return principia, atlas


def _validate_output(output: Path, roots: Sequence[Path]) -> Path:
    target = _absolute(output)
    if not target.name:
        raise ValueError("product output must have a final path component")
    for root in roots:
        if target == root or target in root.parents:
            raise ValueError("product output must not replace a source checkout")
    if target.is_symlink():
        raise ValueError("product output must not be a symlink")
    if target.exists() and not target.is_dir():
        raise ValueError("product output must be a directory")
    return target


def _atlas(atlas_root: Path, *arguments: str) -> None:
    _run([sys.executable, "-m", ATLAS_MODULE, *arguments], cwd=atlas_root)


def check_source_determinism(
    principia_root: Path,
    atlas_root: Path,
    route: str,
) -> None:
    _atlas(atlas_root, "check")
    principia_build.check_determinism(principia_root, route)


def build_source_packages(
    principia_root: Path,
    atlas_root: Path,
    route: str,
    work_root: Path,
) -> tuple[Path, Path, Path]:
    principia_package = work_root / "principia-package"
    atlas_package = work_root / "atlas-package"
    _atlas(atlas_root, "build", "--output", str(atlas_package))
    _atlas(atlas_root, "verify", "--package", str(atlas_package))
    principia_build.build(principia_root, principia_package, route)
    report = atlas_package / ATLAS_REPORT_NAME
    if not report.is_file():
        raise ValueError("Atlas packager did not produce its build report")
    return principia_package, atlas_package, report


def _source_states(
    principia_root: Path,
    atlas_root: Path,
    *,
    allow_dirty: bool,
    expected_principia_commit: str | None,
    expected_atlas_commit: str | None,
) -> tuple[dict[str, object], dict[str, object]]:
    return (
        git_state(
            principia_root,
            PRINCIPIA_REPOSITORY,
            allow_dirty=allow_dirty,
            expected_commit=expected_principia_commit,
        ),
        git_state(
            atlas_root,
            ATLAS_REPOSITORY,
            allow_dirty=allow_dirty,
            expected_commit=expected_atlas_commit,
        ),
    )


def _same_sources(
    before: tuple[dict[str, object], dict[str, object]],
    after: tuple[dict[str, object], dict[str, object]],
) -> None:
    if before != after:
        raise ValueError("source checkout state changed during product assembly")


def make_receipt(
    manifest: Mapping[str, Any],
    principia_state: Mapping[str, object],
    atlas_state: Mapping[str, object],
) -> dict[str, object]:
    unsigned: dict[str, object] = {
        "contract": CONTRACT,
        "product": PRODUCT,
        "bundle_id": manifest["bundle_id"],
        "route_id": manifest["principia"]["route_id"],
        "sources": {
            "principia": dict(principia_state),
            "atlas": dict(atlas_state),
        },
        "artifacts": {
            "principia_build_id": manifest["principia"]["build_id"],
            "atlas_shell_build_digest": manifest["atlas"]["shell_build_digest"],
            "atlas_report_digest": manifest["atlas"]["report_digest"],
            "atlas_workspace": manifest["atlas"]["workspace"],
        },
        "boundaries": {
            "authorities_separate": True,
            "status_inheritance": "prohibited",
            "live_cross_repository_dependency": False,
            "external_network_required": False,
            "repository_mutation": False,
        },
    }
    receipt = dict(unsigned)
    receipt["receipt_id"] = sha256(canonical_json(unsigned))
    return receipt


def receipt_path(output: Path) -> Path:
    return output.with_name(output.name + RECEIPT_SUFFIX)


def _atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(raw)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def verify_receipt(output: Path, path: Path | None = None) -> dict[str, object]:
    manifest, _ = suite.verify_bundle(output)
    target = path or receipt_path(output)
    raw = suite.read_regular(target, "orchestration receipt", MAX_RECEIPT_BYTES)
    receipt = suite.decode(raw, "orchestration receipt")
    if receipt.get("contract") != CONTRACT or receipt.get("product") != PRODUCT:
        raise ValueError("orchestration receipt contract is invalid")
    receipt_id = receipt.get("receipt_id")
    unsigned = dict(receipt)
    unsigned.pop("receipt_id", None)
    if (
        not isinstance(receipt_id, str)
        or not suite.SHA.fullmatch(receipt_id)
        or sha256(canonical_json(unsigned)) != receipt_id
    ):
        raise ValueError("orchestration receipt seal is invalid")
    expected_boundaries = {
        "authorities_separate": True,
        "status_inheritance": "prohibited",
        "live_cross_repository_dependency": False,
        "external_network_required": False,
        "repository_mutation": False,
    }
    expected_artifacts = {
        "principia_build_id": manifest["principia"]["build_id"],
        "atlas_shell_build_digest": manifest["atlas"]["shell_build_digest"],
        "atlas_report_digest": manifest["atlas"]["report_digest"],
        "atlas_workspace": manifest["atlas"]["workspace"],
    }
    if (
        receipt.get("bundle_id") != manifest["bundle_id"]
        or receipt.get("route_id") != manifest["principia"]["route_id"]
        or receipt.get("artifacts") != expected_artifacts
        or receipt.get("boundaries") != expected_boundaries
    ):
        raise ValueError("orchestration receipt does not match the product bundle")
    sources = receipt.get("sources")
    if not isinstance(sources, dict) or set(sources) != {"principia", "atlas"}:
        raise ValueError("orchestration receipt source identity is invalid")
    for name, repository in (
        ("principia", PRINCIPIA_REPOSITORY),
        ("atlas", ATLAS_REPOSITORY),
    ):
        state = sources.get(name)
        if (
            not isinstance(state, dict)
            or state.get("repository") != repository
            or not isinstance(state.get("clean"), bool)
            or not isinstance(state.get("commit"), str)
            or not GIT_OBJECT_ID.fullmatch(state["commit"])
        ):
            raise ValueError("orchestration receipt source identity is invalid")
    return receipt


def _publish_tree(stage: Path, output: Path) -> None:
    if not stage.is_dir() or stage.is_symlink():
        raise ValueError("staged product must be a regular directory")
    if output.is_symlink():
        raise ValueError("product output must not be a symlink")
    backup = output.parent / f".{output.name}.backup-{uuid.uuid4().hex}"
    had_output = output.exists()
    if had_output:
        if not output.is_dir():
            raise ValueError("product output must be a directory")
        output.replace(backup)
    try:
        stage.replace(output)
    except BaseException:
        if had_output and backup.exists() and not output.exists():
            backup.replace(output)
        raise
    else:
        if backup.exists():
            shutil.rmtree(backup, ignore_errors=True)


@contextmanager
def build_lock(output: Path) -> Iterator[None]:
    output.parent.mkdir(parents=True, exist_ok=True)
    lock = output.parent / f".{output.name}.build.lock"
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    try:
        fd = os.open(lock, flags, 0o600)
    except FileExistsError as exc:
        raise ValueError(f"another product build owns {lock}") from exc
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(f"pid={os.getpid()}\n")
            stream.flush()
            os.fsync(stream.fileno())
        yield
    finally:
        try:
            lock.unlink()
        except FileNotFoundError:
            pass


def build_product(
    *,
    principia_root: Path,
    atlas_repo: Path,
    route: str,
    output: Path,
    allow_dirty: bool = False,
    expected_principia_commit: str | None = None,
    expected_atlas_commit: str | None = None,
) -> tuple[dict[str, Any], dict[str, object]]:
    principia, atlas = _source_roots(principia_root, atlas_repo)
    target = _validate_output(output, (principia, atlas))
    before = _source_states(
        principia,
        atlas,
        allow_dirty=allow_dirty,
        expected_principia_commit=expected_principia_commit,
        expected_atlas_commit=expected_atlas_commit,
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    with build_lock(target):
        check_source_determinism(principia, atlas, route)
        with tempfile.TemporaryDirectory(
            prefix=f".{target.name}.staging-", dir=target.parent
        ) as temporary:
            work = Path(temporary)
            principia_package, atlas_package, atlas_report = build_source_packages(
                principia, atlas, route, work
            )
            staged_bundle = work / "bundle"
            manifest = suite.build_bundle(
                principia_package, atlas_package, atlas_report, staged_bundle
            )
            suite.verify_bundle(staged_bundle)
            suite.smoke(staged_bundle)
            after = _source_states(
                principia,
                atlas,
                allow_dirty=allow_dirty,
                expected_principia_commit=expected_principia_commit,
                expected_atlas_commit=expected_atlas_commit,
            )
            _same_sources(before, after)
            receipt = make_receipt(manifest, before[0], before[1])
            _publish_tree(staged_bundle, target)
        _atomic_write(receipt_path(target), canonical_json(receipt))
        verify_receipt(target)
    return manifest, receipt


def check_integration(
    *,
    principia_root: Path,
    atlas_repo: Path,
    route: str,
    allow_dirty: bool = False,
    expected_principia_commit: str | None = None,
    expected_atlas_commit: str | None = None,
) -> str:
    principia, atlas = _source_roots(principia_root, atlas_repo)
    before = _source_states(
        principia,
        atlas,
        allow_dirty=allow_dirty,
        expected_principia_commit=expected_principia_commit,
        expected_atlas_commit=expected_atlas_commit,
    )
    check_source_determinism(principia, atlas, route)
    products: list[tuple[dict[str, Any], dict[str, bytes]]] = []
    with tempfile.TemporaryDirectory() as first, tempfile.TemporaryDirectory() as second:
        for root_name in (first, second):
            work = Path(root_name)
            principia_package, atlas_package, atlas_report = build_source_packages(
                principia, atlas, route, work
            )
            bundle = work / "bundle"
            suite.build_bundle(
                principia_package, atlas_package, atlas_report, bundle
            )
            manifest, snapshot = suite.verify_bundle(bundle)
            suite.smoke(bundle)
            products.append((manifest, snapshot))
    if products[0] != products[1]:
        raise ValueError("end-to-end Principia & Atlas assembly is not deterministic")
    after = _source_states(
        principia,
        atlas,
        allow_dirty=allow_dirty,
        expected_principia_commit=expected_principia_commit,
        expected_atlas_commit=expected_atlas_commit,
    )
    _same_sources(before, after)
    return products[0][0]["bundle_id"]


def verify_product(output: Path) -> tuple[dict[str, Any], dict[str, object]]:
    target = _absolute(output)
    manifest, _ = suite.verify_bundle(target)
    suite.smoke(target)
    receipt = verify_receipt(target)
    return manifest, receipt


def serve_product(
    output: Path,
    *,
    port: int,
    open_browser: bool,
    quiet: bool,
) -> None:
    manifest, _ = verify_product(output)
    server = suite.create_server(_absolute(output), port, quiet)
    actual_port = int(server.server_address[1])
    home = f"http://{suite.HOST}:{actual_port}/"
    build_id = manifest["principia"]["build_id"]
    print(f"Principia & Atlas: {home}")
    print(f"Learn: {home}principia/index.html")
    print(f"Research: {home}atlas/index.html")
    print(f"Recorder: {home}principia/facilitator.html?build_id={build_id}")
    print(f"Pilot Lab: {home}principia/pilot-lab.html?build_id={build_id}")
    if open_browser:
        webbrowser.open(home)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "check", "verify", "run"))
    parser.add_argument("--principia-root", type=Path, default=PRINCIPIA_ROOT)
    parser.add_argument("--atlas-repo", type=Path, default=DEFAULT_ATLAS_REPO)
    parser.add_argument("--route", default=principia_build.DEFAULT_ROUTE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--expected-principia-commit")
    parser.add_argument("--expected-atlas-commit")
    parser.add_argument("--allow-dirty", action="store_true")
    parser.add_argument("--port", type=int, default=suite.DEFAULT_PORT)
    parser.add_argument("--open", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "check":
        bundle_id = check_integration(
            principia_root=args.principia_root,
            atlas_repo=args.atlas_repo,
            route=args.route,
            allow_dirty=args.allow_dirty,
            expected_principia_commit=args.expected_principia_commit,
            expected_atlas_commit=args.expected_atlas_commit,
        )
        print(f"Principia & Atlas end-to-end check passed: {bundle_id}")
        return 0
    if args.command == "verify":
        manifest, receipt = verify_product(args.output)
        print(
            "Verified Principia & Atlas product "
            f"{manifest['bundle_id']} with receipt {receipt['receipt_id']}"
        )
        return 0
    manifest, receipt = build_product(
        principia_root=args.principia_root,
        atlas_repo=args.atlas_repo,
        route=args.route,
        output=args.output,
        allow_dirty=args.allow_dirty,
        expected_principia_commit=args.expected_principia_commit,
        expected_atlas_commit=args.expected_atlas_commit,
    )
    print(
        f"Built Principia & Atlas product {manifest['bundle_id']} -> "
        f"{_absolute(args.output)}"
    )
    print(f"Build receipt: {receipt_path(_absolute(args.output))}")
    print(f"Receipt ID: {receipt['receipt_id']}")
    if args.command == "run":
        serve_product(
            args.output,
            port=args.port,
            open_browser=args.open,
            quiet=args.quiet,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
