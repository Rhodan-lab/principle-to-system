#!/usr/bin/env python3
"""Validate the non-live Principia–Atlas bridge candidate and exact-revision export."""
from __future__ import annotations

import copy
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from export_principia_atlas_dependents import build_export, render

ROOT = Path(__file__).resolve().parent.parent
CONTRACT_ROOT = ROOT / "contracts" / "principia-atlas" / "0.1"
INTEGRATION_ROOT = ROOT / "integration" / "principia-atlas"
MANIFEST_PATH = INTEGRATION_ROOT / "manifests" / "feedback-instability.fixture.json"
EXPORT_PATH = INTEGRATION_ROOT / "exports" / "feedback-instability.external-dependent.fixture.json"
INVALID_ROOT = INTEGRATION_ROOT / "fixtures" / "invalid"

EXPERIENCE_FILES = {
    "system-dossiers/refrigerator.md": "system-dossier",
    "failure-atlas/feedback-instability.md": "failure-pattern",
    "investigations/room-cooling.md": "investigation",
    "design-challenges/passive-cooler.md": "design-challenge",
}
TEMPLATE_FILES = (
    "templates/system-dossier.md",
    "templates/failure-pattern.md",
    "templates/investigation.md",
    "templates/design-challenge.md",
)
PEDAGOGICAL_STATUSES = {"draft", "reviewed", "complete", "blocked"}
RELEASE_STATUSES = {"draft", "candidate", "released", "withdrawn"}
ROLES = {"load-bearing", "supporting", "context"}
USES = {"definition", "evidence", "claim-boundary", "model", "model-boundary", "source-context", "synthesis-context"}
CHANGE_POLICIES = {"inspect", "revalidate", "block-release"}
ENTITY_TYPES = {"source", "evidence", "claim", "concept", "model", "question", "synthesis"}
PREFIX_TO_TYPE = {
    "src": "source",
    "evidence": "evidence",
    "claim": "claim",
    "concept": "concept",
    "model": "model",
    "question": "question",
    "synthesis": "synthesis",
}
ARTIFACT_ID_RE = re.compile(r"^principia:(system-dossier|failure-pattern|investigation|design-challenge):[a-z0-9][a-z0-9-]*$")
ATLAS_ID_RE = re.compile(r"^(src|evidence|claim|concept|model|question|synthesis):[a-z0-9][a-z0-9:-]*$")
FORBIDDEN_KEYS = {
    "required_atlas_status",
    "knowledge_status",
    "inherited_status",
    "auto_promote",
    "promote_principia",
    "atlas_checkout",
}
EXPECTED_REVISIONS = {
    "claim:en:model-oscillation-does-not-prove-real-system": 1,
    "model:en:delayed-correction-recurrence": 2,
    "concept:en:feedback": 1,
    "concept:en:oscillation": 1,
}
EXPECTED_POLICY = {
    "knowledge_status_inheritance": "prohibited",
    "pedagogical_status_inheritance": "prohibited",
    "release_status_inheritance": "prohibited",
    "atlas_status_authority": "Atlas",
    "principia_status_authority": "Principia",
}


@dataclass(frozen=True)
class Finding:
    code: str
    message: str


class Report:
    def __init__(self) -> None:
        self.findings: list[Finding] = []

    def add(self, code: str, message: str) -> None:
        self.findings.append(Finding(code, message))

    @property
    def codes(self) -> set[str]:
        return {finding.code for finding in self.findings}


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read {path.relative_to(ROOT)}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON in {path.relative_to(ROOT)}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)} must contain a JSON object")
    return value


def parse_scalar(value: str) -> object:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        return value[1:-1]
    if value.isdigit():
        return int(value)
    return value


def read_frontmatter(path: Path, report: Report) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        report.add("artifact-file", f"cannot read {path.relative_to(ROOT)}: {exc}")
        return {}
    if not text.startswith("---\n"):
        report.add("artifact-frontmatter", f"{path.relative_to(ROOT)}: missing frontmatter")
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        report.add("artifact-frontmatter", f"{path.relative_to(ROOT)}: unterminated frontmatter")
        return {}
    result: dict[str, object] = {}
    for raw in text[4:end].splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        result[key.strip()] = parse_scalar(value)
    return result


def expected_artifact_id(experience_type: str, slug: str) -> str | None:
    prefix = f"{experience_type}-"
    if not slug.startswith(prefix) or len(slug) <= len(prefix):
        return None
    return f"principia:{experience_type}:{slug[len(prefix):]}"


def find_forbidden_keys(value: object, path: str = "$") -> list[str]:
    found: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key in FORBIDDEN_KEYS:
                found.append(f"{path}.{key}")
            found.extend(find_forbidden_keys(child, f"{path}.{key}"))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            found.extend(find_forbidden_keys(child, f"{path}[{index}]"))
    return found


def validate_seed_artifacts(report: Report) -> dict[str, dict[str, object]]:
    parsed: dict[str, dict[str, object]] = {}
    for relative, expected_type in EXPERIENCE_FILES.items():
        path = ROOT / relative
        frontmatter = read_frontmatter(path, report)
        parsed[relative] = frontmatter
        if frontmatter.get("experience_type") != expected_type:
            report.add("artifact-type", f"{relative}: expected experience_type {expected_type}")
        revision = frontmatter.get("artifact_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
            report.add("artifact-revision", f"{relative}: artifact_revision must be a positive integer")
        if frontmatter.get("release_status") not in RELEASE_STATUSES:
            report.add("release-status", f"{relative}: invalid release_status")
        if frontmatter.get("status") not in PEDAGOGICAL_STATUSES:
            report.add("pedagogical-status", f"{relative}: invalid pedagogical status")
        slug = frontmatter.get("slug")
        if not isinstance(slug, str) or expected_artifact_id(expected_type, slug) is None:
            report.add("artifact-id", f"{relative}: slug cannot produce a stable Principia artifact ID")

    for relative in TEMPLATE_FILES:
        path = ROOT / relative
        try:
            text = path.read_text(encoding="utf-8")
        except OSError as exc:
            report.add("template-file", f"cannot read {relative}: {exc}")
            continue
        for marker in ("artifact_revision:", "release_status:", "status` records pedagogical maturity", "Neither inherits Atlas knowledge status"):
            if marker not in text:
                report.add("template-contract", f"{relative}: missing marker {marker!r}")
    return parsed


def validate_material_boundary(report: Report) -> None:
    feedback = (ROOT / "failure-atlas" / "feedback-instability.md").read_text(encoding="utf-8").lower()
    refrigerator = (ROOT / "system-dossiers" / "refrigerator.md").read_text(encoding="utf-8").lower()
    for marker in (
        "oscillation is a pattern of repeated change",
        "does not by itself establish instability",
        "exactly periodic with period 6",
        "it is also bounded",
        "does not demonstrate that the orbit is unstable",
    ):
        if marker not in feedback:
            report.add("oscillation-boundary", f"failure-atlas/feedback-instability.md missing marker {marker!r}")
    for marker in (
        "not automatically evidence of instability",
        "the resulting bounded temperature cycle is intentional",
        "a repeated cycle is not automatically unstable",
        "abnormal short-cycling",
    ):
        if marker not in refrigerator:
            report.add("oscillation-boundary", f"system-dossiers/refrigerator.md missing marker {marker!r}")


def validate_manifest(manifest: dict[str, Any], artifacts: dict[str, dict[str, object]] | None = None) -> Report:
    report = Report()
    if manifest.get("contract") != "principia-atlas-bridge/0.1":
        report.add("contract", "contract must be principia-atlas-bridge/0.1")
    bridge_id = manifest.get("id")
    if not isinstance(bridge_id, str) or not bridge_id.startswith("bridge:"):
        report.add("bridge-id", "id must be a namespaced bridge identifier")
    if manifest.get("mode") != "bridge-candidate" or manifest.get("live") is not False:
        report.add("live-dependency", "candidate requires mode=bridge-candidate and live=false")

    for location in find_forbidden_keys(manifest):
        report.add("status-policy", f"forbidden cross-repository authority field at {location}")

    principia = manifest.get("principia")
    if not isinstance(principia, dict):
        report.add("principia-object", "principia must be an object")
        principia = {}
    if principia.get("repository") != "Rhodan-lab/principle-to-system":
        report.add("principia-repository", "principia.repository must identify this repository")
    artifact_id = principia.get("artifact_id")
    if not isinstance(artifact_id, str) or not ARTIFACT_ID_RE.fullmatch(artifact_id):
        report.add("artifact-id", "principia.artifact_id is invalid")
    artifact_path = principia.get("path")
    if not isinstance(artifact_path, str):
        report.add("artifact-path", "principia.path must be a repository-relative string")
    else:
        resolved = (ROOT / artifact_path).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            report.add("artifact-path", "principia.path escapes the repository")
        if not resolved.is_file():
            report.add("artifact-path", f"principia.path does not exist: {artifact_path}")
    revision = principia.get("artifact_revision")
    if not isinstance(revision, int) or isinstance(revision, bool) or revision < 1:
        report.add("artifact-revision", "principia.artifact_revision must be a positive integer")
    if principia.get("pedagogical_status_field") != "status":
        report.add("pedagogical-status", "pedagogical_status_field must remain status")
    if principia.get("pedagogical_status") not in PEDAGOGICAL_STATUSES:
        report.add("pedagogical-status", "principia.pedagogical_status is invalid")
    if principia.get("release_status") not in RELEASE_STATUSES:
        report.add("release-status", "principia.release_status is invalid")

    if artifacts is not None and isinstance(artifact_path, str) and artifact_path in artifacts:
        frontmatter = artifacts[artifact_path]
        for manifest_key, frontmatter_key, code in (
            ("artifact_revision", "artifact_revision", "artifact-revision"),
            ("pedagogical_status", "status", "pedagogical-status"),
            ("release_status", "release_status", "release-status"),
        ):
            if principia.get(manifest_key) != frontmatter.get(frontmatter_key):
                report.add(code, f"manifest {manifest_key} does not match {artifact_path} frontmatter")
        experience_type = frontmatter.get("experience_type")
        slug = frontmatter.get("slug")
        if isinstance(experience_type, str) and isinstance(slug, str):
            expected = expected_artifact_id(experience_type, slug)
            if artifact_id != expected:
                report.add("artifact-id", f"artifact_id must be {expected!r} for {artifact_path}")

    atlas = manifest.get("atlas")
    if not isinstance(atlas, dict):
        report.add("atlas-object", "atlas must be an object")
        atlas = {}
    if atlas.get("repository") != "Rhodan-lab/Atlas":
        report.add("atlas-repository", "atlas.repository must be Rhodan-lab/Atlas")
    if atlas.get("content_contract") != "atlas-content/0.1":
        report.add("atlas-contract", "atlas.content_contract must be atlas-content/0.1")
    dependencies = atlas.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        report.add("dependencies", "atlas.dependencies must be a non-empty list")
        dependencies = []
    seen_ids: set[str] = set()
    actual_revisions: dict[str, int] = {}
    for index, dependency in enumerate(dependencies):
        prefix = f"atlas.dependencies[{index}]"
        if not isinstance(dependency, dict):
            report.add("dependency", f"{prefix} must be an object")
            continue
        entity_id = dependency.get("id")
        dep_revision = dependency.get("revision")
        entity_type = dependency.get("entity_type")
        if not isinstance(entity_id, str) or not ATLAS_ID_RE.fullmatch(entity_id):
            report.add("dependency-id", f"{prefix}.id is invalid")
        if not isinstance(dep_revision, int) or isinstance(dep_revision, bool) or dep_revision < 1:
            report.add("dependency-revision", f"{prefix}.revision must be a positive exact integer")
        if entity_type not in ENTITY_TYPES:
            report.add("dependency-type", f"{prefix}.entity_type is invalid")
        if isinstance(entity_id, str) and ":" in entity_id:
            expected_type = PREFIX_TO_TYPE.get(entity_id.split(":", 1)[0])
            if expected_type is not None and entity_type != expected_type:
                report.add("dependency-type", f"{prefix}.entity_type must match ID prefix {expected_type}")
        if dependency.get("role") not in ROLES:
            report.add("dependency-role", f"{prefix}.role is invalid")
        if dependency.get("use") not in USES:
            report.add("dependency-use", f"{prefix}.use is invalid")
        if dependency.get("change_policy") not in CHANGE_POLICIES:
            report.add("change-policy", f"{prefix}.change_policy is invalid")
        if isinstance(entity_id, str):
            if entity_id in seen_ids:
                report.add("duplicate-dependency", f"duplicate Atlas dependency {entity_id}")
            seen_ids.add(entity_id)
            if isinstance(dep_revision, int) and not isinstance(dep_revision, bool):
                actual_revisions[entity_id] = dep_revision
    if actual_revisions != EXPECTED_REVISIONS:
        report.add("dependency-revision", f"candidate exact revisions differ: {actual_revisions}")

    if manifest.get("status_policy") != EXPECTED_POLICY:
        report.add("status-policy", "status_policy must preserve separate Atlas and Principia authority")

    export_policy = manifest.get("export")
    if not isinstance(export_policy, dict):
        report.add("export-policy", "export must be an object")
    else:
        if export_policy.get("schema") != "principia-atlas-external-dependent/0.2":
            report.add("export-policy", "export.schema must be principia-atlas-external-dependent/0.2")
        if export_policy.get("kind") != "principia-artifact":
            report.add("export-policy", "export.kind must be principia-artifact")
        if export_policy.get("role") not in ROLES:
            report.add("export-policy", "export.role is invalid")
        if export_policy.get("exact_revisions") is not True:
            report.add("export-policy", "export.exact_revisions must be true")
    return report


def merge_patch(base: object, patch: object) -> object:
    if not isinstance(patch, dict):
        return copy.deepcopy(patch)
    result = copy.deepcopy(base) if isinstance(base, dict) else {}
    assert isinstance(result, dict)
    for key, value in patch.items():
        if value is None:
            result.pop(key, None)
        elif isinstance(value, dict):
            result[key] = merge_patch(result.get(key), value)
        else:
            result[key] = copy.deepcopy(value)
    return result


def validate_invalid_fixtures(report: Report, artifacts: dict[str, dict[str, object]]) -> None:
    fixtures = sorted(INVALID_ROOT.glob("*.json"))
    if len(fixtures) < 3:
        report.add("invalid-fixtures", "at least three invalid bridge fixtures are required")
    for path in fixtures:
        try:
            fixture = load_json(path)
        except ValueError as exc:
            report.add("invalid-fixture-json", str(exc))
            continue
        if fixture.get("contract") != "principia-atlas-invalid-fixture/0.1":
            report.add("invalid-fixture-contract", f"{path.relative_to(ROOT)}: invalid fixture contract")
            continue
        base_ref = fixture.get("base_manifest")
        expected = fixture.get("expected_error_codes")
        patch = fixture.get("patch")
        if not isinstance(base_ref, str) or not isinstance(expected, list) or not isinstance(patch, dict):
            report.add("invalid-fixture-shape", f"{path.relative_to(ROOT)}: malformed invalid fixture")
            continue
        try:
            base = load_json(ROOT / base_ref)
        except ValueError as exc:
            report.add("invalid-fixture-base", str(exc))
            continue
        candidate = merge_patch(base, patch)
        if not isinstance(candidate, dict):
            report.add("invalid-fixture-shape", f"{path.relative_to(ROOT)}: patch did not produce an object")
            continue
        candidate_report = validate_manifest(candidate, artifacts)
        expected_codes = {str(item) for item in expected}
        if not candidate_report.findings:
            report.add("invalid-fixture-pass", f"{path.relative_to(ROOT)} unexpectedly passed")
        missing = expected_codes - candidate_report.codes
        if missing:
            report.add("invalid-fixture-diagnostic", f"{path.relative_to(ROOT)} missing expected error codes: {sorted(missing)}")


def validate_contract_artifacts(report: Report) -> None:
    required = (
        CONTRACT_ROOT / "README.md",
        CONTRACT_ROOT / "bridge-manifest.schema.json",
        MANIFEST_PATH,
        EXPORT_PATH,
        ROOT / "scripts" / "export_principia_atlas_dependents.py",
        Path(__file__),
    )
    for path in required:
        if not path.is_file():
            report.add("required-file", f"missing {path.relative_to(ROOT)}")
    try:
        schema = load_json(CONTRACT_ROOT / "bridge-manifest.schema.json")
    except ValueError as exc:
        report.add("schema-json", str(exc))
    else:
        if schema.get("title") != "Principia–Atlas Bridge Manifest 0.1":
            report.add("schema-title", "bridge schema title is incorrect")
        serialized = json.dumps(schema, ensure_ascii=False)
        for marker in (
            "principia-atlas-bridge/0.1",
            "compatibility-fixture",
            "bridge-candidate",
            "principia-atlas-external-dependent/0.2",
            "exact_revisions",
            "knowledge_status_inheritance",
        ):
            if marker not in serialized:
                report.add("schema-contract", f"bridge schema missing marker {marker!r}")
    try:
        contract_text = (CONTRACT_ROOT / "README.md").read_text(encoding="utf-8")
    except OSError as exc:
        report.add("contract-doc", f"cannot read contract README: {exc}")
    else:
        for marker in (
            "No status crosses the boundary automatically",
            "mode: bridge-candidate",
            "live: false",
            "depends_on_exact",
            "Atlas Phase 2 importer",
            "No live cross-repository call",
        ):
            if marker not in contract_text:
                report.add("contract-doc", f"contract README missing marker {marker!r}")


def validate_export(report: Report, manifest: dict[str, Any]) -> None:
    try:
        expected_text = render(build_export(manifest))
        actual_text = EXPORT_PATH.read_text(encoding="utf-8")
    except (ValueError, OSError) as exc:
        report.add("export", str(exc))
        return
    if actual_text != expected_text:
        report.add("export-stale", "stored Atlas external-dependent export is stale")
    try:
        export_value = json.loads(actual_text)
    except json.JSONDecodeError as exc:
        report.add("export-json", f"invalid export JSON: {exc}")
        return
    if not isinstance(export_value, dict):
        report.add("export-json", "export root must be an object")
        return
    if export_value.get("contract") != "principia-atlas-external-dependent/0.2":
        report.add("export-contract", "candidate export contract is incorrect")
    if export_value.get("bridge_mode") != "bridge-candidate" or export_value.get("live") is not False:
        report.add("export-live", "candidate export must remain bridge-candidate and non-live")
    exact = export_value.get("depends_on_exact")
    if not isinstance(exact, list):
        report.add("export-revisions", "candidate export lacks depends_on_exact")
    else:
        actual = {
            item.get("id"): item.get("revision")
            for item in exact
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        }
        if actual != EXPECTED_REVISIONS:
            report.add("export-revisions", f"candidate export exact revisions differ: {actual}")
    forbidden = {"status", "pedagogical_status", "release_status", "knowledge_status"} & set(export_value)
    if forbidden:
        report.add("export-authority", f"Atlas export leaks Principia status fields: {sorted(forbidden)}")


def main() -> int:
    report = Report()
    artifacts = validate_seed_artifacts(report)
    validate_material_boundary(report)
    validate_contract_artifacts(report)
    try:
        manifest = load_json(MANIFEST_PATH)
    except ValueError as exc:
        report.add("manifest-json", str(exc))
        manifest = {}
    manifest_report = validate_manifest(manifest, artifacts)
    report.findings.extend(manifest_report.findings)
    if manifest:
        validate_export(report, manifest)
    validate_invalid_fixtures(report, artifacts)

    if report.findings:
        print("Principia–Atlas bridge candidate validation failed:", file=sys.stderr)
        for finding in report.findings:
            print(f"- [{finding.code}] {finding.message}", file=sys.stderr)
        return 1
    print(
        "Principia–Atlas bridge candidate passed: delayed-correction model@2, other dependencies unchanged, "
        "separate status authority, exact-revision export, non-live importer boundary, and negative fixtures."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
