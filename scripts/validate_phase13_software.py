#!/usr/bin/env python3
"""Validate the Phase 13 machine-governed software foundation."""

from __future__ import annotations

import ast
import json
import re
import sys
import tempfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from software.principia_site import (  # noqa: E402
    EXPERIENCE_ROOTS,
    SYNTHESIS_ROOTS,
    build_catalog,
    build_site,
    graph_payload,
    search_payload,
)


EXPECTED_COUNTS = {
    "documents": 92,
    "modules": 20,
    "synthesis": 16,
    "experiences": 16,
}
ALLOWED_IMPORT_ROOTS = {
    "__future__",
    "argparse",
    "ast",
    "dataclasses",
    "hashlib",
    "html",
    "http",
    "json",
    "pathlib",
    "re",
    "shutil",
    "sys",
    "tempfile",
    "typing",
    "unittest",
    "urllib",
}


class Result:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.notes: list[str] = []

    def error(self, message: str) -> None:
        self.errors.append(message)

    def note(self, message: str) -> None:
        self.notes.append(message)


def read_json(relative: str, result: Result) -> dict[str, object]:
    path = ROOT / relative
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.error(f"{relative}: cannot load JSON: {exc}")
        return {}
    if not isinstance(value, dict):
        result.error(f"{relative}: root must be an object")
        return {}
    return value


def validate_governance(result: Result) -> None:
    governance = read_json("release/phase-13-machine-governance.json", result)
    authority = governance.get("authority")
    transition = governance.get("transition")
    scope = governance.get("software_scope")
    promotion = governance.get("promotion_policy")
    gates = governance.get("machine_gates")
    if not all(isinstance(item, dict) for item in (authority, transition, scope, promotion)):
        result.error("Phase 13 governance sections are incomplete")
        return
    assert isinstance(authority, dict)
    assert isinstance(transition, dict)
    assert isinstance(scope, dict)
    assert isinstance(promotion, dict)
    if authority.get("mode") != "machine-only":
        result.error("Phase 13 authority mode must be machine-only")
    if authority.get("human_review_required") is not False:
        result.error("Phase 13 must not require a human-review gate")
    if authority.get("automatic_merge") is not False:
        result.error("machine governance must not silently merge pull requests")
    if authority.get("failure_behavior") != "block-progression":
        result.error("failed machine gates must block progression")
    if transition.get("from") != "candidate-hold" or transition.get("to") != "machine-gated-development":
        result.error("Phase 13 transition must move RC1 into machine-gated development")
    if transition.get("material_promotion") is not False:
        result.error("software continuation must not promote material status")
    if scope.get("network_fetch_during_build") is not False:
        result.error("the reference build must not fetch from the network")
    if scope.get("content_duplication") is not False:
        result.error("repository content must remain the source of truth")
    if scope.get("atlas_live_integration") is not False:
        result.error("Phase 13 must keep Atlas integration non-live")
    if promotion.get("core_status_change") != "none":
        result.error("Phase 13 must not change core pedagogical status")
    if promotion.get("experience_status_change") != "none":
        result.error("Phase 13 must not change experience pedagogical status")
    if promotion.get("atlas_status_inheritance") is not False:
        result.error("Atlas status inheritance must remain disabled")
    required_gates = {
        "phase-12-continuity",
        "strict-repository-validation",
        "frontmatter-and-content-ingestion",
        "html-escaping-and-link-safety",
        "catalog-count-consistency",
        "deterministic-build",
        "search-index-completeness",
        "dependency-graph-integrity",
        "unit-tests",
        "workflow-immutability",
    }
    if not isinstance(gates, list) or set(gates) != required_gates:
        result.error("Phase 13 machine-gate set is incomplete or unexpected")


def validate_standard_library_only(result: Result) -> None:
    paths = [
        ROOT / "software/principia_site.py",
        ROOT / "software/tests/test_principia_site.py",
        ROOT / "scripts/validate_phase13_software.py",
    ]
    for path in paths:
        if not path.is_file():
            result.error(f"missing software source: {path.relative_to(ROOT)}")
            continue
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            result.error(f"{path.relative_to(ROOT)}: syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    module = alias.name
                    root = module.split(".", 1)[0]
                    if root not in ALLOWED_IMPORT_ROOTS and root != "software":
                        result.error(f"{path.relative_to(ROOT)} imports non-standard module {module}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                module = node.module
                root = module.split(".", 1)[0]
                if root not in ALLOWED_IMPORT_ROOTS and root != "software":
                    result.error(f"{path.relative_to(ROOT)} imports non-standard module {module}")


def validate_catalog(result: Result) -> None:
    try:
        catalog = build_catalog(ROOT)
    except Exception as exc:
        result.error(f"catalog build failed: {exc}")
        return
    synthesis = sum(len(catalog.collection(name)) for name in SYNTHESIS_ROOTS)
    experiences = sum(len(catalog.collection(name)) for name in EXPERIENCE_ROOTS)
    actual = {
        "documents": len(catalog.documents),
        "modules": len(catalog.modules),
        "synthesis": synthesis,
        "experiences": experiences,
    }
    if actual != EXPECTED_COUNTS:
        result.error(f"catalog counts differ: expected {EXPECTED_COUNTS}, found {actual}")
    slugs = [document.slug for document in catalog.documents]
    if len(slugs) != len(set(slugs)):
        result.error("generated catalog contains duplicate slugs")
    sources = [document.source_path for document in catalog.documents]
    if len(sources) != len(set(sources)):
        result.error("generated catalog contains duplicate source paths")
    for module_id, documents in catalog.modules.items():
        if {document.role for document in documents} != {"overview", "technology", "explore"}:
            result.error(f"{module_id}: module does not contain the three canonical views")
        if any(document.status != "reviewed" for document in documents):
            result.error(f"{module_id}: software layer changed or exposed a non-reviewed core view")
    search = search_payload(catalog)
    if len(search) != EXPECTED_COUNTS["documents"]:
        result.error("search index does not cover every catalog document")
    if any(not item.get("title") or not item.get("text") for item in search):
        result.error("search index contains an empty title or body")
    graph = graph_payload(catalog)
    nodes = graph.get("nodes")
    edges = graph.get("edges")
    if not isinstance(nodes, list) or len(nodes) != EXPECTED_COUNTS["modules"]:
        result.error("dependency graph does not contain all modules")
        return
    node_ids = {str(node.get("id")) for node in nodes if isinstance(node, dict)}
    if not isinstance(edges, list):
        result.error("dependency graph edges must be a list")
        return
    for edge in edges:
        if not isinstance(edge, dict):
            result.error("dependency graph contains a non-object edge")
            continue
        if str(edge.get("source")) not in node_ids or str(edge.get("target")) not in node_ids:
            result.error(f"dependency graph edge references an unknown node: {edge}")


def validate_experience_policy(result: Result) -> None:
    inventory = read_json("experiences/phase-11b-inventory.json", result)
    policy = inventory.get("status_policy")
    governance = inventory.get("governance")
    if not isinstance(policy, dict) or not isinstance(governance, dict):
        result.error("experience inventory policy is incomplete")
        return
    if policy.get("pedagogical_status") != "reviewed":
        result.error("experience pedagogical status changed")
    if policy.get("release_status") != "draft":
        result.error("Phase 13 must preserve draft experience release status")
    if policy.get("complete_allowed") is not False:
        result.error("Phase 13 must not mark experiences Complete")
    if governance.get("atlas_live_dependency") is not False:
        result.error("experience inventory unexpectedly enables live Atlas")


def validate_generated_links(output: Path, result: Result) -> None:
    pattern = re.compile(r'(?:href|src)="([^"]+)"')
    output_resolved = output.resolve()
    for page in sorted(output.rglob("*.html")):
        content = page.read_text(encoding="utf-8")
        for raw in pattern.findall(content):
            split = urlsplit(raw)
            if split.scheme or raw.startswith(("#", "mailto:")):
                continue
            clean = unquote(split.path)
            if not clean:
                continue
            target = (page.parent / clean).resolve()
            try:
                target.relative_to(output_resolved)
            except ValueError:
                result.error(f"{page.relative_to(output)}: generated link escapes output: {raw}")
                continue
            if not target.exists():
                result.error(f"{page.relative_to(output)}: generated link is broken: {raw}")


def validate_build(result: Result) -> None:
    with tempfile.TemporaryDirectory() as temporary:
        root = Path(temporary)
        first_dir = root / "first"
        second_dir = root / "second"
        try:
            first = build_site(ROOT, first_dir)
            second = build_site(ROOT, second_dir)
        except Exception as exc:
            result.error(f"static build failed: {exc}")
            return
        if first.get("counts") != EXPECTED_COUNTS:
            result.error(f"build manifest counts differ: {first.get('counts')}")
        if first.get("network_fetch") is not False:
            result.error("build manifest must declare network_fetch false")
        if first.get("build_id") != second.get("build_id"):
            result.error("successive builds have different content build IDs")
        if first.get("tree_digest") != second.get("tree_digest"):
            result.error("successive builds are not byte-for-byte deterministic")
        validate_generated_links(first_dir, result)
        for relative in (
            "index.html",
            "modules/index.html",
            "pathways/index.html",
            "experiences/index.html",
            "graph/index.html",
            "search/index.html",
            "api/catalog.json",
            "api/search-index.json",
            "api/graph.json",
            "api/build-manifest.json",
        ):
            if not (first_dir / relative).is_file():
                result.error(f"static build is missing {relative}")


def validate_assets(result: Result) -> None:
    css = ROOT / "software/assets/site.css"
    js = ROOT / "software/assets/site.js"
    if not css.is_file() or not js.is_file():
        result.error("software browser assets are missing")
        return
    css_text = css.read_text(encoding="utf-8").lower()
    js_text = js.read_text(encoding="utf-8").lower()
    if "@import" in css_text or "url(http" in css_text:
        result.error("CSS must not load remote assets")
    if "https://" in js_text or "http://" in js_text:
        result.error("browser JavaScript must not call remote services")
    for token in ("eval(", "innerhtml", "document.write"):
        if token in js_text:
            result.error(f"browser JavaScript contains forbidden DOM execution pattern: {token}")


def validate_workflow(result: Result) -> None:
    path = ROOT / ".github/workflows/validate-phase-13-software.yml"
    if not path.is_file():
        result.error("Phase 13 workflow is missing")
        return
    text = path.read_text(encoding="utf-8")
    if "contents: read" not in text:
        result.error("Phase 13 workflow must use contents: read")
    for token in ("contents: write", "git push", "git commit", "pull_request_target"):
        if token in text:
            result.error(f"Phase 13 workflow contains forbidden token: {token}")
    required = (
        "validate_phase12_release_candidate.py",
        "validate_repo.py --strict",
        "unittest discover -s software/tests",
        "validate_phase13_software.py",
        "principia_site.py build",
    )
    for token in required:
        if token not in text:
            result.error(f"Phase 13 workflow does not run required gate: {token}")


def run() -> int:
    result = Result()
    validate_governance(result)
    validate_standard_library_only(result)
    validate_catalog(result)
    validate_experience_policy(result)
    validate_assets(result)
    validate_workflow(result)
    validate_build(result)

    print("Phase 13 software foundation validation")
    print(f"Repository: {ROOT}")
    for note in result.notes:
        print(f"NOTE: {note}")
    if result.errors:
        print(f"ERROR: {len(result.errors)}")
        for error in result.errors:
            print(f"  - {error}")
        print("PHASE 13 VALIDATION FAILED")
        return 1
    print("Validated: machine-only governance, 92 documents, 20 modules, deterministic static build")
    print("PHASE 13 VALIDATION PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
