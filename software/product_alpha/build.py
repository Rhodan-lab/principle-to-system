#!/usr/bin/env python3
"""Build the Principia Product Alpha static experience from canonical repository content."""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import route_identity

DEFAULT_ROUTE = "refrigerator"
STATIC_ASSETS = ("index.html", "model-adapters.js", "facilitator.html", "pilot-lab.html")
EVALUATION_ASSETS = (
    "evaluation/rubric.json",
    "evaluation/session-template.json",
)
PILOT_LAB_DUPLICATE_COUNTER_BUG = b"state.duplicates=+1;"
PILOT_LAB_DUPLICATE_COUNTER_FIX = b"state.duplicates+=1;"

FACILITATOR_TRANSFORMS = (
    (
        b'const q=s=>document.querySelector(s);let rubric=null,template=null,lastRecord=null;',
        b'const BUILD_ID_PATTERN=/^[0-9a-f]{64}$/,q=s=>document.querySelector(s);let rubric=null,template=null,lastRecord=null,pilotBuildId=new URLSearchParams(location.search).get("build_id")||"";',
        "facilitator build-id state",
    ),
    (
        b'return{session_id:q("#sessionId").value.trim(),',
        b'return{pilot_build_id:pilotBuildId,session_id:q("#sessionId").value.trim(),',
        "facilitator session build-id field",
    ),
    (
        b'function validate(value){const errors=[];if(!/^anonymous-[A-Za-z0-9-]+$/.test(value.session_id))',
        b'function validate(value){const errors=[];if(!BUILD_ID_PATTERN.test(value.pilot_build_id))errors.push("Pilot build ID is missing or invalid. Open the recorder from run_pilot.py.");if(!/^anonymous-[A-Za-z0-9-]+$/.test(value.session_id))',
        "facilitator build-id validation",
    ),
    (
        b'q("#sessionId").value=anonymousId();[q("#sessionId")',
        b'q("#sessionId").value=anonymousId();if(!BUILD_ID_PATTERN.test(pilotBuildId))setStatus("Pilot build ID is missing. Open this recorder from the launcher URL.","error");[q("#sessionId")',
        "facilitator missing-build warning",
    ),
)

PILOT_LAB_TRANSFORMS = (
    (
        b'"use strict";\nconst ROUTE_ID=',
        b'"use strict";\nconst BUILD_ID_PATTERN=/^[0-9a-f]{64}$/,EXPECTED_BUILD_ID=new URLSearchParams(location.search).get("build_id")||"";\nconst ROUTE_ID=',
        "Pilot Lab build-id state",
    ),
    (
        b',c=s=>document.querySelector(s);',
        b',q=s=>document.querySelector(s);',
        "Pilot Lab selector helper",
    ),
    (
        b'if(found.length)fail(`${label}: personal-data fields are not allowed: ${found.join(", ")}.`);if(session.route_id!==ROUTE_ID)fail(',
        b'if(found.length)fail(`${label}: personal-data fields are not allowed: ${found.join(", ")}.`);if(!BUILD_ID_PATTERN.test(session.pilot_build_id))fail(`${label}: pilot_build_id must be a 64-character lowercase SHA-256.`);if(EXPECTED_BUILD_ID&&session.pilot_build_id!==EXPECTED_BUILD_ID)fail(`${label}: pilot_build_id does not match the launcher build.`);if(session.route_id!==ROUTE_ID)fail(',
        "Pilot Lab build-id validation",
    ),
    (
        b'state.duplicates=0;const seen=new Set;for(const file of state.files)',
        b'state.duplicates=0;const seen=new Set;let cohortBuildId=EXPECTED_BUILD_ID||null;for(const file of state.files)',
        "Pilot Lab cohort build state",
    ),
    (
        b'session=validateSession(parsed,label);if(seen.has(session.session_id))',
        b'session=validateSession(parsed,label);if(cohortBuildId&&session.pilot_build_id!==cohortBuildId)fail(`${label}: pilot_build_id does not match the cohort build.`);cohortBuildId=session.pilot_build_id;if(seen.has(session.session_id))',
        "Pilot Lab mixed-build rejection",
    ),
    (
        b'const summary={contract:"principia-product-alpha-pilot-summary/0.2",route_id:ROUTE_ID,',
        b'const summary={contract:"principia-product-alpha-pilot-summary/0.3",pilot_build_id:sessions[0].pilot_build_id,route_id:ROUTE_ID,',
        "Pilot Lab summary build identity",
    ),
    (
        b'box.innerHTML=`<table><caption>Cohort aggregate metrics</caption><tbody><tr><th scope="row">Started</th>',
        b'box.innerHTML=`<table><caption>Cohort aggregate metrics</caption><tbody><tr><th scope="row">Build ID</th><td><code>${s.pilot_build_id.slice(0,12)}...</code></td></tr><tr><th scope="row">Started</th>',
        "Pilot Lab build-id display",
    ),
    (
        b'"- Evidence status: **"+s.evidence_status+"**","- Route: `"+s.route_id+"`",',
        b'"- Evidence status: **"+s.evidence_status+"**","- Pilot build ID: `"+s.pilot_build_id+"`","- Route: `"+s.route_id+"`",',
        "Pilot Lab Markdown build identity",
    ),
)


@dataclass(frozen=True)
class SourceDocument:
    path: str
    title: str
    metadata: dict[str, str]
    sections: dict[str, str]


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated Markdown frontmatter")
    raw = text[4:end]
    body = text[end + 5 :]
    metadata: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        metadata[key.strip()] = value.strip().strip('"')
    return metadata, body


def parse_sections(body: str) -> tuple[str, dict[str, str]]:
    title = ""
    sections: dict[str, list[str]] = {"intro": []}
    current = "intro"
    for line in body.splitlines():
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            continue
        if line.startswith("## "):
            current = line[3:].strip()
            sections.setdefault(current, [])
            continue
        sections.setdefault(current, []).append(line)
    cleaned = {
        key: "\n".join(value).strip()
        for key, value in sections.items()
        if "\n".join(value).strip()
    }
    return title, cleaned


def load_document(root: Path, relative_path: str) -> SourceDocument:
    path = root / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"missing canonical source: {relative_path}")
    metadata, body = split_frontmatter(path.read_text(encoding="utf-8"))
    title, sections = parse_sections(body)
    if not title:
        title = metadata.get("title", Path(relative_path).stem)
    return SourceDocument(relative_path, title, metadata, sections)


def section(document: SourceDocument, name: str) -> str:
    try:
        return document.sections[name]
    except KeyError as exc:
        raise ValueError(f"{document.path} is missing required section: {name}") from exc


def canonical_json(data: Any) -> bytes:
    return (
        json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
    ).encode("utf-8")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_config(root: Path, route: str) -> dict[str, Any]:
    config_path = root / "software" / "product_alpha" / "routes" / f"{route}.json"
    if not config_path.is_file():
        raise FileNotFoundError(f"missing route config: {config_path.relative_to(root)}")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    required = {"id", "title", "sources", "steps", "model", "atlas_references"}
    missing = sorted(required - config.keys())
    if missing:
        raise ValueError(f"route config missing fields: {', '.join(missing)}")
    if len(config["steps"]) != 5:
        raise ValueError("Product Alpha routes must contain exactly five learner steps")
    model = config["model"]
    if model.get("adapter") not in {"thermal-cabinet-v1", "queue-delay-fluid-v1"}:
        raise ValueError("Product Alpha route model adapter is unsupported")
    if not isinstance(model.get("parameters"), list) or not model["parameters"]:
        raise ValueError("Product Alpha route model parameters are required")
    return config


def build_route(root: Path, route: str) -> dict[str, Any]:
    config = load_config(root, route)
    documents = {
        name: load_document(root, path) for name, path in config["sources"].items()
    }
    dossier, failure = documents["system"], documents["failure"]
    investigation, design = documents["investigation"], documents["design"]
    content = {
        "observe": {
            "heading": "Observe the system",
            "body": section(dossier, "1. Observable system"),
            "prompt": config["steps"][0]["prompt"],
        },
        "map": {
            "heading": "Map boundaries and flows",
            "body": "\n\n".join(
                [
                    section(dossier, "2. System boundary and environment"),
                    section(dossier, "3. Inputs, outputs, stores, and flows"),
                    section(dossier, "6. Interaction architecture"),
                ]
            ),
            "prompt": config["steps"][1]["prompt"],
        },
        "model": {
            "heading": "Test the smallest useful model",
            "body": section(dossier, "7. Quantitative model"),
            "prompt": config["steps"][2]["prompt"],
        },
        "diagnose": {
            "heading": "Diagnose a failure",
            "body": "\n\n".join(
                [
                    section(failure, config["failure_section"]),
                    section(dossier, "9. Failure modes"),
                ]
            ),
            "prompt": config["steps"][3]["prompt"],
            "challenge": config["challenge"],
        },
        "redesign": {
            "heading": "Redesign under constraints",
            "body": "\n\n".join(
                [
                    section(investigation, config["investigation_section"]),
                    section(design, config["design_section"]),
                ]
            ),
            "prompt": config["steps"][4]["prompt"],
        },
    }
    return {
        "contract": "principia-product-alpha-route/0.1",
        "route_id": config["id"],
        "title": config["title"],
        "subtitle": config["subtitle"],
        "release_state": "alpha",
        "canonical_sources": [
            {
                "role": role,
                "path": doc.path,
                "title": doc.title,
                "artifact_revision": doc.metadata.get("artifact_revision"),
                "status": doc.metadata.get("status"),
                "release_status": doc.metadata.get("release_status"),
            }
            for role, doc in documents.items()
        ],
        "learner_steps": content,
        "model": config["model"],
        "atlas": {
            "mode": "exact-revision-advisory",
            "live": False,
            "status_inheritance": "prohibited",
            "references": config["atlas_references"],
        },
        "product_boundaries": {
            "accounts": False,
            "analytics": False,
            "repository_mutation": False,
            "external_network_required": False,
            "browser_notes_persisted": False,
        },
    }


def _replace_once(data: bytes, old: bytes, new: bytes, label: str) -> bytes:
    old_count = data.count(old)
    new_count = data.count(new)
    if old_count == 1 and new_count == 0:
        return data.replace(old, new, 1)
    if old_count == 0 and new_count == 1:
        return data
    raise ValueError(f"{label} must contain exactly one canonical state")


def prepare_static_asset(relative_path: str, data: bytes, route: str = DEFAULT_ROUTE) -> bytes:
    """Apply bounded packaging repairs and reject ambiguous asset states."""
    evidence_route = route_identity.evidence_route_id(route)
    if relative_path == "index.html":
        marker = b'<meta name="principia-route" content="refrigerator">'
        replacement = f'<meta name="principia-route" content="{route}">'.encode("utf-8")
        if data.count(marker) != 1:
            raise ValueError("learner route marker must occur exactly once")
        return data.replace(marker, replacement, 1)
    if relative_path == "evaluation/session-template.json":
        template = json.loads(data.decode("utf-8"))
        supported = template.get("supported_route_ids")
        if supported != list(route_identity.SUPPORTED_EVIDENCE_ROUTES):
            raise ValueError("session template supported_route_ids do not match route identity authority")
        template["route_id"] = evidence_route
        return json.dumps(template, indent=2, ensure_ascii=False).encode("utf-8") + b"\n"
    if relative_path == "facilitator.html":
        for old, new, label in FACILITATOR_TRANSFORMS:
            data = _replace_once(data, old, new, label)
        return data
    if relative_path != "pilot-lab.html":
        return data

    default_route_marker = b'const ROUTE_ID="refrigerator-v1"'
    if data.count(default_route_marker) != 1:
        raise ValueError("Pilot Lab route identity must occur exactly once")
    if evidence_route != route_identity.DEFAULT_EVIDENCE_ROUTE:
        data = data.replace(
            default_route_marker,
            f'const ROUTE_ID="{evidence_route}"'.encode("utf-8"),
            1,
        )
    data = _replace_once(
        data,
        PILOT_LAB_DUPLICATE_COUNTER_BUG,
        PILOT_LAB_DUPLICATE_COUNTER_FIX,
        "Pilot Lab duplicate counter",
    )
    for old, new, label in PILOT_LAB_TRANSFORMS:
        data = _replace_once(data, old, new, label)
    return data


def copy_static_files(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> list[dict[str, str]]:
    assets = root / "software" / "product_alpha"
    copied: list[dict[str, str]] = []
    for relative_path in (*STATIC_ASSETS, *EVALUATION_ASSETS):
        source = assets / relative_path
        if not source.is_file():
            raise FileNotFoundError(
                f"missing Product Alpha asset: {source.relative_to(root)}"
            )
        destination = output / relative_path
        destination.parent.mkdir(parents=True, exist_ok=True)
        data = prepare_static_asset(relative_path, source.read_bytes(), route)
        destination.write_bytes(data)
        copied.append({"path": relative_path, "sha256": sha256(data)})
    return copied


def build(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> dict[str, Any]:
    if output.exists():
        shutil.rmtree(output)
    (output / "data").mkdir(parents=True)
    route_payload = build_route(root, route)
    route_bytes = canonical_json(route_payload)
    (output / "data" / f"{route}.json").write_bytes(route_bytes)
    files = copy_static_files(root, output, route)
    files.append({"path": f"data/{route}.json", "sha256": sha256(route_bytes)})
    files.sort(key=lambda item: item["path"])
    manifest = {
        "contract": "principia-product-alpha-build/0.1",
        "route_id": route,
        "file_count": len(files),
        "files": files,
        "deterministic": True,
    }
    (output / "build-manifest.json").write_bytes(canonical_json(manifest))
    return manifest


def check_determinism(root: Path, route: str) -> None:
    with tempfile.TemporaryDirectory() as first_dir, tempfile.TemporaryDirectory() as second_dir:
        first, second = Path(first_dir), Path(second_dir)
        build(root, first, route)
        build(root, second, route)
        first_files = sorted(
            path.relative_to(first) for path in first.rglob("*") if path.is_file()
        )
        second_files = sorted(
            path.relative_to(second) for path in second.rglob("*") if path.is_file()
        )
        if first_files != second_files:
            raise SystemExit("Product Alpha build file sets differ")
        for relative in first_files:
            if (first / relative).read_bytes() != (second / relative).read_bytes():
                raise SystemExit(
                    f"Product Alpha build is not deterministic: {relative}"
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("build", "check"))
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[2]
    )
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--route", default=DEFAULT_ROUTE)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = args.root.resolve()
    if args.command == "check":
        check_determinism(root, args.route)
        print(f"Product Alpha deterministic build passed: route={args.route}")
        return 0
    output = (
        args.output or root / "software" / "product_alpha" / "dist"
    ).resolve()
    manifest = build(root, output, args.route)
    print(
        f"Built Product Alpha route {args.route}: "
        f"{manifest['file_count']} files -> {output}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
