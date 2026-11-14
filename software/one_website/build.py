#!/usr/bin/env python3
"""Build a read-only, single-origin Principia + Atlas static website.

Generated artifacts are disposable presentations of canonical Principia and Atlas
sources. The public static surface cannot write learner data or promote evidence.
"""
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
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from software.product_alpha import build as principia_build
from software.product_alpha import package_integrity
from software.principia_atlas import suite

HERE = Path(__file__).resolve().parent
CONTRACT = "principia-atlas-static-web/0.1"
MANIFEST = "site-manifest.json"
ATLAS_MODULE = "tools.phase4_workspace.package_product_input"
ATLAS_REPORT = "workspace-shell-build-report.json"
ROUTES = ("refrigerator", "distributed-information")
ATLAS_PIN = (HERE / "atlas-commit.txt").read_text(encoding="ascii").strip()
SHA = re.compile(r"^[0-9a-f]{40}$")
MAX_FILES = 48
MAX_ASSET = 16 * 1024 * 1024
MAX_TOTAL = 64 * 1024 * 1024

GLOBAL_NAV_STYLE = """
<style id="principia-atlas-navigation">
#pa-global-nav{position:fixed;z-index:2000;bottom:1rem;left:50%;transform:translateX(-50%);
display:flex;align-items:center;justify-content:center;gap:.3rem;max-width:calc(100vw - 1.25rem);
border:1px solid #c7cec8;border-radius:999px;box-shadow:0 12px 45px #17221d24;
padding:.35rem;background:#faf9f5f5;backdrop-filter:blur(18px);font:700 12px/1.25 system-ui,-apple-system,sans-serif}
#pa-global-nav a{display:inline-flex;align-items:center;justify-content:center;min-height:2.75rem;
padding:.55rem .9rem;border-radius:999px;white-space:nowrap;text-decoration:none;color:#34453b}
#pa-global-nav a[aria-current="page"]{background:#173d33;color:#fff}
#pa-global-nav a:focus-visible,.pa-global-skip:focus-visible{outline:3px solid #bd8129;outline-offset:2px}
.pa-global-skip{position:fixed;top:.5rem;left:.5rem;z-index:2500;transform:translateY(-160%);
padding:.6rem .9rem;border-radius:.6rem;background:#173d33;color:#fff;font:700 13px system-ui}
.pa-global-skip:focus{transform:none}
body{padding-bottom:5.75rem!important}
@media(max-width:570px){#pa-global-nav{bottom:.5rem;gap:0;padding:.25rem;border-radius:1rem}
#pa-global-nav a{padding:.5rem .55rem;font-size:11px;white-space:normal;text-align:center}}
@media(prefers-reduced-motion:reduce){#pa-global-nav{backdrop-filter:none}}
</style>
"""

NAV_ITEMS = (
    ("/", "Home", "home"),
    ("/learn/refrigerator/", "Refrigerator", "refrigerator"),
    ("/learn/distributed-information/", "Information", "distributed-information"),
    ("/research/", "Atlas research", "atlas"),
)


def canonical(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def git_head(repo: Path) -> str:
    done = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    )
    head = done.stdout.strip()
    if not SHA.fullmatch(head):
        raise ValueError("Git source must have a 40-character pinned commit")
    return head


def safe_relative(value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("Site asset path is invalid")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(x in ("", ".", "..") for x in path.parts):
        raise ValueError("Site asset path is unsafe")
    return value


def add_navigation(raw: bytes, active: str) -> bytes:
    if active not in ("refrigerator", "distributed-information", "atlas"):
        raise ValueError("Unknown navigation route")
    source = raw.decode("utf-8")
    if source.count("</head>") != 1 or source.count("<body>") != 1:
        raise ValueError("Expected one head and one body in canonical viewer")
    links = []
    for url, label, key in NAV_ITEMS:
        current = ' aria-current="page"' if key == active else ""
        links.append(f'<a href="{url}"{current}>{label}</a>')
    skip_target = "#main-content" if active == "atlas" else "#heading"
    navigation = (
        f'<a class="pa-global-skip" href="{skip_target}">Skip to page content</a>'
        '<nav id="pa-global-nav" aria-label="Unified Principia and Atlas navigation">'
        + "".join(links) + "</nav>"
    )
    assets = '<link rel="stylesheet" href="/experience.css">'
    if active != "atlas":
        assets += '<script defer src="/experience.js"></script>'
    source = source.replace("</head>", GLOBAL_NAV_STYLE + assets + "</head>", 1)
    body_class = "pa-research" if active == "atlas" else "pa-learner"
    source = source.replace("<body>", f'<body class="{body_class}">' + navigation, 1)
    return source.encode("utf-8")


def write_asset(target: Path, relative: str, content: bytes, files: list[dict[str, object]]) -> None:
    safe_relative(relative)
    if len(content) > MAX_ASSET:
        raise ValueError(f"Site asset exceeds limit: {relative}")
    destination = target.joinpath(*PurePosixPath(relative).parts)
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        raise ValueError(f"Site asset collision: {relative}")
    destination.write_bytes(content)
    files.append({"path": relative, "bytes": len(content), "sha256": sha256(content)})


def expected_paths() -> set[str]:
    paths = {"index.html", "styles.css", "site.js", "experience.css", "experience.js", "robots.txt"}
    for route in ROUTES:
        paths.update((
            f"learn/{route}/index.html",
            f"learn/{route}/model-adapters.js",
            f"learn/{route}/data/{route}.json",
        ))
    paths.update(f"research/{p}" for p in suite.ATLAS_FILES)
    return paths


def verify(output: Path) -> dict[str, object]:
    if output.is_symlink() or not output.is_dir():
        raise ValueError("Static website must be a real directory")
    manifest_path = output / MANIFEST
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise ValueError("Site manifest missing or unsafe")
    raw = manifest_path.read_bytes()
    if len(raw) > 1024 * 1024:
        raise ValueError("Site manifest too large")
    def unique(pairs):
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("Duplicate manifest key")
            result[key] = value
        return result
    manifest = json.loads(raw.decode("utf-8"), object_pairs_hook=unique)
    if not isinstance(manifest, dict) or manifest.get("contract") != CONTRACT:
        raise ValueError("Site manifest contract mismatch")
    unsigned = dict(manifest)
    seal = unsigned.pop("build_id", None)
    if not isinstance(seal, str) or not re.fullmatch(r"[0-9a-f]{64}", seal) or sha256(canonical(unsigned)) != seal:
        raise ValueError("Site manifest seal mismatch")
    authority = manifest.get("authority")
    if authority != {
        "atlas_advisory_only": True, "authorities_separate": True,
        "canonical_mutation": False, "external_runtime_network": False,
        "human_verification_claimed": False, "live_sync": False,
        "repository_mutation": False, "status_inheritance": False,
    }:
        raise ValueError("Site authority contract invalid")
    if manifest.get("routes") != list(ROUTES):
        raise ValueError("Site route contract mismatch")
    records = manifest.get("files")
    if not isinstance(records, list) or len(records) > MAX_FILES:
        raise ValueError("Site file inventory invalid")
    declared = {}
    total = 0
    for record in records:
        if not isinstance(record, dict) or set(record) != {"path", "bytes", "sha256"}:
            raise ValueError("Site file identity malformed")
        rel = safe_relative(record["path"])
        size, digest = record["bytes"], record["sha256"]
        if rel in declared or rel == MANIFEST or not isinstance(size, int) or isinstance(size, bool) or size < 0 or size > MAX_ASSET:
            raise ValueError("Site file inventory duplicated or invalid")
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            raise ValueError("Site file digest invalid")
        declared[rel] = record
        total += size
    if set(declared) != expected_paths() or total > MAX_TOTAL:
        raise ValueError("Site asset set or byte budget mismatch")
    actual = set()
    for path in output.rglob("*"):
        if path.is_symlink():
            raise ValueError("Symlink not allowed in static website")
        if path.is_dir():
            continue
        if not path.is_file():
            raise ValueError("Non-file static artifact")
        actual.add(path.relative_to(output).as_posix())
    if actual != set(declared) | {MANIFEST}:
        raise ValueError("Static website contains missing or undeclared files")
    for rel, item in declared.items():
        payload = output.joinpath(*PurePosixPath(rel).parts).read_bytes()
        if len(payload) != item["bytes"] or sha256(payload) != item["sha256"]:
            raise ValueError(f"Static website asset changed: {rel}")
    for route in ROUTES:
        source = output / "learn" / route
        data = json.loads((source / "data" / f"{route}.json").read_text(encoding="utf-8"))
        if data.get("route_id") != route or data.get("atlas", {}).get("live") is not False:
            raise ValueError(f"Static learner route identity invalid: {route}")
        html = (source / "index.html").read_text(encoding="utf-8")
        if f'<meta name="principia-route" content="{route}">' not in html:
            raise ValueError("Packaged learner marker mismatch")
    research_html = (output / "research/index.html").read_text(encoding="utf-8")
    if 'aria-current="page">Atlas research</a>' not in research_html:
        raise ValueError("Research navigation missing")
    research_data = json.loads((output / "research/data/workspace-shell-data.json").read_text(encoding="utf-8"))
    if research_data.get("contract") != suite.ATLAS_SHELL or research_data.get("authority", {}).get("live_principia_dependency") is not False:
        raise ValueError("Atlas workspace data authority mismatch")
    return manifest


def prepare(principia_repo: Path, atlas_repo: Path, stage: Path) -> dict[str, object]:
    if not SHA.fullmatch(ATLAS_PIN):
        raise ValueError("Invalid Atlas source commit pin")
    if git_head(atlas_repo) != ATLAS_PIN:
        raise ValueError("Atlas checkout differs from audited atlas-commit.txt pin")
    principle_head = git_head(principia_repo)
    with tempfile.TemporaryDirectory(prefix="pa-web-packages-") as scratch:
        temp = Path(scratch)
        atlas_package = temp / "atlas"
        done = subprocess.run(
            [sys.executable, "-m", ATLAS_MODULE, "build", "--output", str(atlas_package)],
            cwd=atlas_repo, text=True, capture_output=True,
        )
        if done.returncode:
            raise RuntimeError(f"Atlas accepted workspace build failed:\n{done.stderr[-2500:]}")
        report = atlas_package / ATLAS_REPORT
        atlas_meta, atlas_files, _ = suite.load_atlas(atlas_package, report)
        files = []
        for route in ROUTES:
            package_root = temp / "principia" / route
            principia_build.build(principia_repo, package_root, route)
            metadata, raw_manifest, assets = package_integrity.load_verified_package(package_root)
            if metadata["route_id"] != route:
                raise ValueError("Principal route package identity mismatch")
            base = f"learn/{route}"
            for rel in ("index.html", "model-adapters.js", f"data/{route}.json"):
                payload = assets[rel]
                if rel == "index.html":
                    payload = add_navigation(payload, route)
                write_asset(stage, f"{base}/{rel}", payload, files)
            # No operational recorder, cohort exports, or local-only pilot endpoints
            # are published by the static export.
            if route == ROUTES[0]:
                build_ids = {}
            build_ids[route] = sha256(raw_manifest)
        for rel in suite.ATLAS_FILES:
            payload = atlas_files[rel]
            if rel == "index.html":
                payload = add_navigation(payload, "atlas")
            write_asset(stage, f"research/{rel}", payload, files)
        home = (HERE / "index.html").read_text(encoding="utf-8")
        for needle, value in {
            "__PRINCIPIA_COMMIT__": principle_head[:12],
            "__ATLAS_COMMIT__": ATLAS_PIN[:12],
            "__ATLAS_WORKSPACE__": str(atlas_meta["workspace"]["id"]),
            "__ATLAS_REVISION__": str(atlas_meta["workspace"]["revision"]),
        }.items():
            if home.count(needle) != 1:
                raise ValueError("Home template token missing or duplicated")
            home = home.replace(needle, value)
        write_asset(stage, "index.html", home.encode("utf-8"), files)
        for asset in ("styles.css", "site.js", "experience.css", "experience.js"):
            write_asset(stage, asset, (HERE / asset).read_bytes(), files)
        write_asset(stage, "robots.txt", b"User-agent: *\nDisallow: /\n", files)
        files.sort(key=lambda x: x["path"])
        unsigned = {
            "contract": CONTRACT,
            "product": "Principia & Atlas",
            "mode": "static-read-only-preview",
            "routes": list(ROUTES),
            "sources": {
                "principia": {"repository": "Rhodan-lab/principle-to-system", "commit": principle_head},
                "atlas": {"repository": "Rhodan-lab/Atlas", "commit": ATLAS_PIN},
            },
            "source_builds": {"principia": build_ids, "atlas": atlas_meta["shell_id"]},
            "atlas_workspace": atlas_meta["workspace"],
            "authority": {
                "atlas_advisory_only": True, "authorities_separate": True,
                "canonical_mutation": False, "external_runtime_network": False,
                "human_verification_claimed": False, "live_sync": False,
                "repository_mutation": False, "status_inheritance": False,
            },
            "files": files,
        }
        record = dict(unsigned, build_id=sha256(canonical(unsigned)))
        (stage / MANIFEST).write_bytes(canonical(record))
        verify(stage)
        return record


def build(principia_repo: Path, atlas_repo: Path, output: Path) -> dict[str, object]:
    principia_repo, atlas_repo = principia_repo.resolve(), atlas_repo.resolve()
    output = output.expanduser().resolve()
    if (
        output in (principia_repo, atlas_repo)
        or output in principia_repo.parents
        or output in atlas_repo.parents
        or atlas_repo in output.parents
        or (principia_repo in output.parents and output != principia_repo / "dist")
    ):
        raise ValueError("Output may not overwrite a source checkout")
    if output.is_symlink():
        raise ValueError("Output must not be a symlink")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".pa-web-build-", dir=output.parent) as staging:
        stage = Path(staging) / "site"
        stage.mkdir()
        result = prepare(principia_repo, atlas_repo, stage)
        backup = output.with_name(f".{output.name}.backup-{uuid.uuid4().hex}")
        existed = output.exists()
        if existed:
            if not output.is_dir():
                raise ValueError("Output is not a directory")
            output.rename(backup)
        try:
            stage.rename(output)
            verify(output)
        except BaseException:
            if output.exists():
                shutil.rmtree(output)
            if existed:
                backup.rename(output)
            raise
        if existed:
            shutil.rmtree(backup)
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("build", "verify", "check"))
    parser.add_argument("--atlas-repo", type=Path, default=ROOT.parent / "Atlas")
    parser.add_argument("--output", type=Path, default=ROOT / "dist")
    args = parser.parse_args()
    if args.command == "verify":
        result = verify(args.output.resolve())
    elif args.command == "build":
        result = build(ROOT, args.atlas_repo, args.output)
    else:
        with tempfile.TemporaryDirectory(prefix="pa-web-check-") as root:
            first, second = Path(root) / "first", Path(root) / "second"
            one = build(ROOT, args.atlas_repo, first)
            two = build(ROOT, args.atlas_repo, second)
            if one != two:
                raise ValueError("Two static builds differ")
            result = one
    print(f"Principia & Atlas static website: {args.command} passed; build={result['build_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
