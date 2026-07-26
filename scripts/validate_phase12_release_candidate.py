#!/usr/bin/env python3
"""Validate the Principia Phase 12 material release candidate without writing files."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import unquote

ROOT = Path(__file__).resolve().parent.parent
RC_PATH = ROOT / "release" / "phase-12-release-candidate.json"
TERMS_PATH = ROOT / "release" / "phase-12-terminology.json"
EQUATIONS_PATH = ROOT / "release" / "phase-12-equation-contracts.json"
IMPACT_PATH = ROOT / "release" / "phase-12-revision-impact.json"
PILOT_PATH = ROOT / "release" / "phase-12-pilot-readiness.json"
GRAPH_PATH = ROOT / "synthesis" / "phase-10-canonical-graph.json"
EXPERIENCE_PATH = ROOT / "experiences" / "phase-11b-inventory.json"
BRIDGE_PATH = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validate-phase-12-release-candidate.yml"
REPORT_PATH = ROOT / "reports" / "phase-12-release-candidate.md"

FRONT_RE = re.compile(r"\A---\n(.*?)\n---\n", re.S)
LINK_RE = re.compile(r"\[([^\]]*)\]\(([^)]+)\)")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.M)

REQUIRED_TERMS = {
    "reviewed",
    "complete",
    "release_status",
    "artifact_revision",
    "exact revision",
    "model",
    "cause",
    "energy",
    "power",
    "efficiency",
    "resilience",
    "uncertainty",
    "availability",
    "non-live compatibility fixture",
}

EQUATION_MARKERS: dict[str, tuple[str, ...]] = {
    "little-law": ("Little", "\\lambda", "W"),
    "queue-backlog-balance": ("\\lambda", "\\mu", "B"),
    "pv-power": ("P_{pv}", "\\eta_{pv}"),
    "battery-energy-balance": ("\\eta_c", "\\eta_d"),
    "water-storage-balance": ("Q_{in}", "Q_{out}"),
    "rainwater-storage-balance": ("S_{k+1}", "S_{max}"),
    "sensor-affine-error": ("a(t)", "b(t)", "\\epsilon"),
    "filter-resistance": ("\\Delta p", "resistance"),
    "first-order-cooling": ("T_{env}", "\\tau"),
    "refrigerator-cop": ("COP_R",),
}


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]

    def error(self, message: str) -> None:
        self.errors.append(message)

    def warning(self, message: str) -> None:
        self.warnings.append(message)


def load_json(path: Path, result: Result) -> dict[str, object]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result.error(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return {}
    if not isinstance(data, dict):
        result.error(f"{path.relative_to(ROOT)}: root must be an object")
        return {}
    return data


def parse_frontmatter(path: Path, result: Result) -> tuple[dict[str, str], str]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        result.error(f"{path.relative_to(ROOT)}: cannot read: {exc}")
        return {}, ""
    match = FRONT_RE.match(text)
    if not match:
        result.error(f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}, text
    values: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip().strip('"\'')
    return values, text[match.end():]


def module_file_paths(graph: dict[str, object], result: Result) -> list[Path]:
    modules = graph.get("modules")
    if not isinstance(modules, dict) or len(modules) != 20:
        result.error("synthesis graph must contain exactly 20 modules")
        return []
    paths: list[Path] = []
    for module_id in modules:
        number = int(str(module_id)[:2])
        family = "foundations" if number <= 5 else "science" if number <= 16 else "technology"
        for filename in ("overview.md", "technology.md", "explore.md"):
            paths.append(ROOT / family / str(module_id) / filename)
    return paths


def synthesis_paths(graph: dict[str, object], result: Result) -> list[Path]:
    paths: list[Path] = []
    for key, expected in (("pathways", 6), ("concepts", 7), ("maps", 3)):
        values = graph.get(key)
        if not isinstance(values, list) or len(values) != expected:
            result.error(f"synthesis graph `{key}` must contain {expected} paths")
            continue
        paths.extend(ROOT / str(value) for value in values)
    return paths


def experience_paths(inventory: dict[str, object], result: Result) -> list[Path]:
    counts = inventory.get("counts")
    if not isinstance(counts, dict) or counts.get("artifacts") != 16 or counts.get("routes") != 4:
        result.error("Phase 11B inventory must declare 4 routes and 16 artifacts")
    routes = inventory.get("routes")
    if not isinstance(routes, list) or len(routes) != 4:
        result.error("Phase 11B inventory must contain exactly 4 routes")
        return []
    paths: list[Path] = []
    slugs: set[str] = set()
    types: dict[str, int] = {}
    for route in routes:
        if not isinstance(route, dict):
            result.error("experience route must be an object")
            continue
        artifacts = route.get("artifacts")
        if not isinstance(artifacts, list) or len(artifacts) != 4:
            result.error(f"experience route {route.get('id')} must contain four artifacts")
            continue
        route_types: set[str] = set()
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                result.error("experience artifact inventory entry must be an object")
                continue
            rel = artifact.get("path")
            slug = artifact.get("slug")
            artifact_type = artifact.get("type")
            if not all(isinstance(value, str) and value for value in (rel, slug, artifact_type)):
                result.error(f"experience route {route.get('id')} contains an incomplete artifact entry")
                continue
            if slug in slugs:
                result.error(f"duplicate experience slug: {slug}")
            slugs.add(slug)
            route_types.add(artifact_type)
            types[artifact_type] = types.get(artifact_type, 0) + 1
            paths.append(ROOT / rel)
        if route_types != {"system-dossier", "failure-pattern", "investigation", "design-challenge"}:
            result.error(f"experience route {route.get('id')} must contain all four artifact families")
    if len(paths) != 16 or len(set(paths)) != 16:
        result.error("experience inventory must contain 16 unique paths")
    for artifact_type in ("system-dossier", "failure-pattern", "investigation", "design-challenge"):
        if types.get(artifact_type) != 4:
            result.error(f"experience inventory must contain four {artifact_type} artifacts")
    return paths


def check_statuses(module_paths: list[Path], synthesis: list[Path], experiences: list[Path], result: Result) -> None:
    for path in module_paths:
        if not path.is_file():
            result.error(f"missing core file: {path.relative_to(ROOT)}")
            continue
        fm, _ = parse_frontmatter(path, result)
        if fm.get("status") != "reviewed":
            result.error(f"{path.relative_to(ROOT)}: core status must remain reviewed")
    for path in synthesis:
        if not path.is_file():
            result.error(f"missing synthesis file: {path.relative_to(ROOT)}")
            continue
        fm, _ = parse_frontmatter(path, result)
        if fm.get("status") != "reviewed":
            result.error(f"{path.relative_to(ROOT)}: synthesis status must remain reviewed")
    for path in experiences:
        if not path.is_file():
            result.error(f"missing experience file: {path.relative_to(ROOT)}")
            continue
        fm, _ = parse_frontmatter(path, result)
        if fm.get("status") != "reviewed":
            result.error(f"{path.relative_to(ROOT)}: experience status must remain reviewed")
        if fm.get("artifact_revision") != "1":
            result.error(f"{path.relative_to(ROOT)}: RC1 expects artifact_revision 1")
        if fm.get("release_status") != "draft":
            result.error(f"{path.relative_to(ROOT)}: release_status must remain draft")


def count_ledger(path: Path, result: Result) -> int:
    count = 0
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        result.error(f"{path.relative_to(ROOT)}: cannot read ledger: {exc}")
        return 0
    for line in lines:
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            continue
        if cells[0].lower() in {"module", "title", "---"}:
            continue
        if all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        count += 1
    return count


def check_links(path: Path, text: str, result: Result) -> None:
    for label, target in LINK_RE.findall(text):
        if label.strip().lower() in {"here", "click here", "link"}:
            result.error(f"{path.relative_to(ROOT)}: non-descriptive link label `{label}`")
        target = unquote(target.split("#", 1)[0].strip())
        if not target or target.startswith(("http://", "https://", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            result.error(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            result.error(f"{path.relative_to(ROOT)}: broken local link: {target}")


def check_accessibility(path: Path, result: Result) -> None:
    fm, body = parse_frontmatter(path, result)
    if not body:
        return
    headings = [(len(prefix), title.strip()) for prefix, title in HEADING_RE.findall(body)]
    if not headings or headings[0][0] != 1:
        result.error(f"{path.relative_to(ROOT)}: document must begin with a level-1 heading after frontmatter")
    if sum(1 for level, _ in headings if level == 1) != 1:
        result.error(f"{path.relative_to(ROOT)}: document must contain exactly one level-1 heading")
    previous = 0
    for level, title in headings:
        if not title:
            result.error(f"{path.relative_to(ROOT)}: empty heading")
        if previous and level > previous + 1:
            result.error(f"{path.relative_to(ROOT)}: heading level jumps from H{previous} to H{level}")
        previous = level
    for alt, _ in IMAGE_RE.findall(body):
        if not alt.strip():
            result.error(f"{path.relative_to(ROOT)}: image is missing alternative text")
    if body.count("```") % 2:
        result.error(f"{path.relative_to(ROOT)}: unbalanced fenced code block")
    if body.count("$$") % 2:
        result.error(f"{path.relative_to(ROOT)}: unbalanced display-math delimiter")
    check_links(path, body, result)
    if fm.get("domain") == "experience" and fm.get("experience_type") not in {"index", None}:
        if "Sources and module links" not in body:
            result.error(f"{path.relative_to(ROOT)}: experience must end with sources and module links")


def check_release_contract(rc: dict[str, object], result: Result) -> None:
    if rc.get("schema") != "principia-release-candidate/0.1":
        result.error("release candidate uses the wrong schema")
    if rc.get("candidate_id") != "principia-material-foundation-rc1":
        result.error("release candidate id must be principia-material-foundation-rc1")
    scope = rc.get("scope")
    expected_scope = {
        "core_modules": 20,
        "core_files": 60,
        "pathways": 6,
        "crosscutting_concepts": 7,
        "knowledge_maps": 3,
        "synthesis_files": 16,
        "experience_routes": 4,
        "experience_artifacts": 16,
        "system_dossiers": 4,
        "failure_patterns": 4,
        "investigations": 4,
        "design_challenges": 4,
        "core_source_records": 143,
        "experience_source_records": 28,
        "bridge_fixtures": 1,
    }
    if not isinstance(scope, dict):
        result.error("release candidate scope must be an object")
    else:
        for key, expected in expected_scope.items():
            if scope.get(key) != expected:
                result.error(f"release candidate scope `{key}` must equal {expected}")
    policy = rc.get("status_policy")
    expected_policy = {
        "core_pedagogical_status": "reviewed",
        "synthesis_pedagogical_status": "reviewed",
        "experience_pedagogical_status": "reviewed",
        "experience_artifact_revision": 1,
        "experience_release_status": "draft",
        "repository_release_state": "candidate-hold",
        "complete_allowed": False,
        "released_allowed": False,
        "automatic_promotion": False,
        "atlas_status_inheritance": False,
        "principia_status_export": False,
    }
    if not isinstance(policy, dict):
        result.error("release candidate status policy must be an object")
    else:
        for key, expected in expected_policy.items():
            if policy.get(key) != expected:
                result.error(f"release status policy `{key}` must equal {expected!r}")
    decision = rc.get("decision")
    if not isinstance(decision, dict):
        result.error("release candidate decision must be an object")
    else:
        if decision.get("release_decision") != "hold":
            result.error("RC1 release decision must remain hold")
        if decision.get("bounded_pilot_readiness") != "conditional":
            result.error("RC1 bounded pilot readiness must remain conditional")
        if decision.get("live_atlas_integration") is not False:
            result.error("RC1 must not activate live Atlas integration")
    human_gates = rc.get("human_authority_gates")
    if not isinstance(human_gates, list) or len(human_gates) < 7:
        result.error("RC1 must preserve at least seven explicit human authority gates")
    contracts = rc.get("contracts")
    if not isinstance(contracts, dict):
        result.error("RC1 contracts section is missing")
    else:
        for rel in contracts.values():
            if not isinstance(rel, str) or not (ROOT / rel).is_file():
                result.error(f"RC1 contract path is missing: {rel}")


def check_terminology(terms: dict[str, object], documents: list[Path], result: Result) -> None:
    entries = terms.get("terms")
    if not isinstance(entries, list):
        result.error("terminology registry must contain a terms list")
        return
    names = {entry.get("term") for entry in entries if isinstance(entry, dict)}
    if names != REQUIRED_TERMS:
        result.error(f"terminology registry does not match the required term set: {sorted(names)}")
    shortcuts = terms.get("forbidden_shortcuts")
    if not isinstance(shortcuts, list) or len(shortcuts) < 8:
        result.error("terminology registry must declare the forbidden shortcuts")
        return
    negation_markers = (
        "does not",
        "do not",
        "must not",
        "cannot",
        "not establish",
        "not imply",
        "not automatically",
        "misconception",
        "myth",
        "forbidden",
    )
    for path in documents:
        if not path.is_file():
            continue
        scan = path.read_text(encoding="utf-8").lower()
        for phrase in shortcuts:
            if not isinstance(phrase, str):
                continue
            target = phrase.lower()
            start = 0
            while True:
                position = scan.find(target, start)
                if position < 0:
                    break
                context = scan[max(0, position - 120) : position + len(target) + 220]
                if not any(marker in context for marker in negation_markers):
                    result.error(
                        f"{path.relative_to(ROOT)}: contains affirmative forbidden semantic shortcut: {phrase}"
                    )
                start = position + len(target)


def check_equations(equations: dict[str, object], result: Result) -> None:
    contracts = equations.get("contracts")
    if not isinstance(contracts, list) or len(contracts) != 10:
        result.error("equation registry must contain exactly ten contracts")
        return
    seen: set[str] = set()
    for contract in contracts:
        if not isinstance(contract, dict):
            result.error("equation contract must be an object")
            continue
        contract_id = contract.get("id")
        if not isinstance(contract_id, str) or contract_id not in EQUATION_MARKERS:
            result.error(f"unknown equation contract id: {contract_id}")
            continue
        if contract_id in seen:
            result.error(f"duplicate equation contract id: {contract_id}")
        seen.add(contract_id)
        artifacts = contract.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            result.error(f"equation contract {contract_id} has no artifacts")
            continue
        for rel in artifacts:
            path = ROOT / str(rel)
            if not path.is_file():
                result.error(f"equation contract {contract_id}: missing artifact {rel}")
                continue
            text = path.read_text(encoding="utf-8")
            if "$$" not in text:
                result.error(f"equation contract {contract_id}: {rel} has no display equation")
            for marker in EQUATION_MARKERS[contract_id]:
                if marker not in text:
                    result.error(f"equation contract {contract_id}: {rel} missing marker {marker}")
            lower = text.lower()
            if not any(word in lower for word in ("model", "limit", "assumption", "boundary", "approximation", "interpretation")):
                result.error(f"equation contract {contract_id}: {rel} lacks model-boundary language")
    if seen != set(EQUATION_MARKERS):
        result.error("equation registry does not cover the canonical ten contracts")


def check_revision_impact(impact: dict[str, object], bridge: dict[str, object], result: Result) -> None:
    principia = bridge.get("principia")
    atlas = bridge.get("atlas")
    if not isinstance(principia, dict) or not isinstance(atlas, dict):
        result.error("bridge fixture is missing Principia or Atlas sections")
        return
    if bridge.get("mode") != "compatibility-fixture" or bridge.get("live") is not False:
        result.error("bridge fixture must remain non-live")
    dependencies = atlas.get("dependencies")
    if not isinstance(dependencies, list):
        result.error("bridge fixture Atlas dependencies must be a list")
        return
    dep_map = {
        dep.get("id"): dep
        for dep in dependencies
        if isinstance(dep, dict) and isinstance(dep.get("id"), str)
    }
    scenarios = impact.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 5:
        result.error("revision-impact contract must contain exactly five scenarios")
        return
    for scenario in scenarios:
        if not isinstance(scenario, dict):
            result.error("revision-impact scenario must be an object")
            continue
        if scenario.get("expected_release_status") != "draft":
            result.error(f"revision-impact scenario {scenario.get('id')} must preserve draft release status")
        if scenario.get("automatic_pedagogical_change") is not False:
            result.error(f"revision-impact scenario {scenario.get('id')} must forbid automatic pedagogical change")
        entity = scenario.get("atlas_entity")
        if entity is None:
            if scenario.get("id") != "principia-meaning-changed" or scenario.get("to_revision") != 2:
                result.error("Principia meaning-change scenario must increment revision from 1 to 2")
            continue
        dep = dep_map.get(entity)
        if not isinstance(dep, dict):
            result.error(f"revision-impact scenario references unknown fixture dependency: {entity}")
            continue
        if scenario.get("from_revision") != dep.get("revision"):
            result.error(f"revision-impact scenario {scenario.get('id')} starts from the wrong revision")
        if scenario.get("change_policy") != dep.get("change_policy"):
            result.error(f"revision-impact scenario {scenario.get('id')} does not preserve fixture change policy")
        if scenario.get("atlas_event") == "retracted" and "block-release" not in str(scenario.get("expected_principia_action")):
            result.error("load-bearing retraction must block release")
    forbidden = impact.get("forbidden_outcomes")
    if not isinstance(forbidden, list) or "automatic-release" not in forbidden or "copy-atlas-status" not in forbidden:
        result.error("revision-impact contract must forbid automatic release and status copying")


def check_pilot(pilot: dict[str, object], result: Result) -> None:
    scope = pilot.get("scope")
    principia = pilot.get("principia_readiness")
    atlas = pilot.get("atlas_readiness")
    state = pilot.get("integration_state")
    if not all(isinstance(value, dict) for value in (scope, principia, atlas, state)):
        result.error("pilot readiness record is incomplete")
        return
    assert isinstance(scope, dict) and isinstance(principia, dict) and isinstance(atlas, dict) and isinstance(state, dict)
    if scope.get("principia_artifact_revision") != 1:
        result.error("pilot must reference Principia artifact revision 1")
    for key in ("exact_revision_identity", "status_separation", "deterministic_export", "revision_impact_scenarios"):
        if principia.get(key) is not True:
            result.error(f"pilot Principia readiness `{key}` must be true")
    if principia.get("human_release_approval") is not False:
        result.error("pilot must record that human release approval is absent")
    for key in ("repository_changed_by_phase_12", "direct_integration_freeze_exited", "external_dependent_accepted", "live_pilot_approval"):
        if atlas.get(key) is not False:
            result.error(f"pilot Atlas readiness `{key}` must remain false")
    if state.get("mode") != "compatibility-fixture" or state.get("live") is not False or state.get("decision") != "hold":
        result.error("pilot integration state must remain compatibility-fixture, non-live, and hold")
    tests = pilot.get("required_end_to_end_tests")
    if not isinstance(tests, list) or len(tests) < 8:
        result.error("pilot readiness must preserve the eight end-to-end test classes")


def check_project_records(result: Result) -> None:
    required = (
        ROOT / "release" / "README.md",
        RC_PATH,
        TERMS_PATH,
        EQUATIONS_PATH,
        IMPACT_PATH,
        PILOT_PATH,
        REPORT_PATH,
        WORKFLOW_PATH,
        Path(__file__),
    )
    for path in required:
        if not path.is_file():
            result.error(f"missing Phase 12 artifact: {path.relative_to(ROOT)}")
    state = (ROOT / "PROJECT_STATE.md").read_text(encoding="utf-8")
    for marker in (
        "Phase 12 — Release Candidate",
        "principia-material-foundation-rc1",
        "release decision remains **Hold**",
        "4 complete routes",
        "16 Reviewed artifacts",
        "143 records",
        "28 records",
        "live: false",
        "Phase 13",
    ):
        if marker not in state:
            result.error(f"PROJECT_STATE.md: missing Phase 12 marker: {marker}")
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    for marker in ("Phase 12", "release/phase-12-release-candidate.json", "candidate-hold"):
        if marker not in readme:
            result.error(f"README.md: missing Phase 12 marker: {marker}")
    if WORKFLOW_PATH.is_file():
        workflow = WORKFLOW_PATH.read_text(encoding="utf-8")
        forbidden = (
            "contents" + ": write",
            "git " + "push",
            "git " + "commit",
            "pull_request" + "_target",
            "Rhodan-lab/" + "Atlas",
        )
        if "contents: read" not in workflow:
            result.error("Phase 12 workflow must declare contents: read")
        for token in forbidden:
            if token in workflow:
                result.error(f"Phase 12 workflow contains forbidden write or live-integration token: {token}")


def main() -> int:
    result = Result([], [])
    rc = load_json(RC_PATH, result)
    graph = load_json(GRAPH_PATH, result)
    inventory = load_json(EXPERIENCE_PATH, result)
    terms = load_json(TERMS_PATH, result)
    equations = load_json(EQUATIONS_PATH, result)
    impact = load_json(IMPACT_PATH, result)
    pilot = load_json(PILOT_PATH, result)
    bridge = load_json(BRIDGE_PATH, result)

    module_paths = module_file_paths(graph, result)
    synth_paths = synthesis_paths(graph, result)
    exp_paths = experience_paths(inventory, result)
    check_statuses(module_paths, synth_paths, exp_paths, result)

    core_count = count_ledger(ROOT / "sources" / "source-ledger.md", result)
    experience_count = count_ledger(ROOT / "sources" / "experience-source-ledger.md", result)
    if core_count != 143:
        result.error(f"core source ledger must contain 143 records, found {core_count}")
    if experience_count != 28:
        result.error(f"experience source ledger must contain 28 records, found {experience_count}")

    documents = module_paths + synth_paths + exp_paths
    for path in documents:
        if path.is_file():
            check_accessibility(path, result)

    check_release_contract(rc, result)
    check_terminology(terms, documents, result)
    check_equations(equations, result)
    check_revision_impact(impact, bridge, result)
    check_pilot(pilot, result)
    check_project_records(result)

    if len(module_paths) != 60:
        result.error(f"release candidate must resolve 60 core files, found {len(module_paths)}")
    if len(synth_paths) != 16:
        result.error(f"release candidate must resolve 16 synthesis files, found {len(synth_paths)}")
    if len(exp_paths) != 16:
        result.error(f"release candidate must resolve 16 experience files, found {len(exp_paths)}")

    if result.warnings:
        print("Phase 12 warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 12 release-candidate errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(
        "Phase 12 RC1 passed: 60 reviewed core files, 16 reviewed synthesis files, "
        "16 reviewed draft-release experiences, 143 core sources, 28 experience sources, "
        "candidate hold, and non-live Principia–Atlas readiness."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
