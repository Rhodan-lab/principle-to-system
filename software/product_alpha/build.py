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

try:
    from software.product_alpha import route_identity
except ModuleNotFoundError:
    import route_identity

DEFAULT_ROUTE = "refrigerator"
STATIC_ASSETS = ("index.html", "model-adapters.js", "facilitator.html", "pilot-lab.html")
EVALUATION_ASSETS = (
    "evaluation/rubric.json",
    "evaluation/session-template.json",
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
    required = {"id", "title", "sources", "steps", "model", "evaluation", "atlas_references"}
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
    evaluation = config.get("evaluation")
    if not isinstance(evaluation, dict):
        raise ValueError("Product Alpha route evaluation config is required")
    rubric_path = evaluation.get("rubric")
    if (
        not isinstance(rubric_path, str)
        or not rubric_path.startswith("software/product_alpha/evaluation/")
        or not (root / rubric_path).is_file()
    ):
        raise ValueError("Product Alpha route rubric path is invalid")
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


def prepare_static_asset(relative_path: str, data: bytes, route: str = DEFAULT_ROUTE) -> bytes:
    """Apply route packaging and reject ambiguous asset states."""
    evidence_route = route_identity.evidence_route_id(route)
    if relative_path == "evaluation/rubric.json":
        rubric = json.loads(data.decode("utf-8"))
        if rubric.get("route_id") != evidence_route:
            raise ValueError(
                f"rubric route_id must be {evidence_route!r} for route {route!r}"
            )
        return data
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
    return data


def copy_static_files(root: Path, output: Path, route: str = DEFAULT_ROUTE) -> list[dict[str, str]]:
    assets = root / "software" / "product_alpha"
    config = load_config(root, route)
    rubric_source = root / config["evaluation"]["rubric"]
    copied: list[dict[str, str]] = []
    for relative_path in (*STATIC_ASSETS, *EVALUATION_ASSETS):
        source = (
            rubric_source
            if relative_path == "evaluation/rubric.json"
            else assets / relative_path
        )
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
