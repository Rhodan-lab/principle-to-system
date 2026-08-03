#!/usr/bin/env python3
"""Validate the Product Alpha 0.2 second-route decision without writing files."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
SELECTION_PATH = ROOT / "reports" / "product-alpha-0-2-route-selection.json"
REPORT_PATH = ROOT / "reports" / "product-alpha-0-2-route-selection.md"
CONTRACT_PATH = (
    ROOT
    / "software"
    / "product_alpha"
    / "route-contracts"
    / "distributed-information.json"
)
INVENTORY_PATH = ROOT / "experiences" / "phase-11b-inventory.json"
PRODUCT_STATE_PATH = ROOT / "PRODUCT_STATE.md"

EXPECTED_CRITERIA = {
    "architectural-contrast",
    "deterministic-model-fit",
    "safe-offline-execution",
    "canonical-completeness",
    "diagnostic-clarity",
    "redesign-richness",
    "accessibility-privacy-fit",
    "atlas-expansion-pressure",
}
EXPECTED_CANDIDATES = {
    "resilient-energy",
    "water-infrastructure",
    "distributed-information",
}
EXPECTED_STEPS = ("observe", "map", "model", "diagnose", "redesign")
EXPECTED_ACTION = "implement-distributed-information-model-adapter-and-route"
EXPECTED_SELECTED = "distributed-information"


class RouteSelectionError(ValueError):
    """Raised when route-selection authority is inconsistent."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RouteSelectionError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RouteSelectionError(f"cannot load {path.relative_to(ROOT)}: {exc}") from exc
    require(isinstance(value, dict), f"{path.relative_to(ROOT)} must contain an object")
    return value


def inventory_route(inventory: dict[str, Any], route_id: str) -> dict[str, Any]:
    routes = inventory.get("routes")
    require(isinstance(routes, list), "experience inventory routes must be a list")
    matches = [item for item in routes if isinstance(item, dict) and item.get("id") == route_id]
    require(len(matches) == 1, f"experience inventory must contain one route: {route_id}")
    return matches[0]


def validate_selection(selection: dict[str, Any]) -> tuple[dict[str, float], dict[str, Any]]:
    require(selection.get("schema_version") == 1, "selection schema_version must be 1")
    require(
        selection.get("contract") == "principia-product-alpha-route-selection/0.1",
        "selection contract is invalid",
    )
    require(selection.get("baseline_route") == "refrigerator", "baseline must be refrigerator")

    criteria = selection.get("criteria")
    require(isinstance(criteria, list), "criteria must be a list")
    require(len(criteria) == len(EXPECTED_CRITERIA), "selection must define eight criteria")
    weights: dict[str, float] = {}
    for item in criteria:
        require(isinstance(item, dict), "criterion must be an object")
        criterion_id = item.get("id")
        weight = item.get("weight")
        require(isinstance(criterion_id, str), "criterion id must be a string")
        require(isinstance(weight, (int, float)) and weight > 0, f"{criterion_id}: weight must be positive")
        require(item.get("description"), f"{criterion_id}: description is required")
        require(criterion_id not in weights, f"duplicate criterion: {criterion_id}")
        weights[criterion_id] = float(weight)
    require(set(weights) == EXPECTED_CRITERIA, "criterion ids do not match the required set")
    require(abs(sum(weights.values()) - 1.0) < 1e-9, "criterion weights must sum to 1")

    candidates = selection.get("candidates")
    require(isinstance(candidates, list), "candidates must be a list")
    require(
        {item.get("id") for item in candidates if isinstance(item, dict)} == EXPECTED_CANDIDATES,
        "candidate ids do not match the canonical alternatives",
    )
    by_id: dict[str, dict[str, Any]] = {}
    for candidate in candidates:
        require(isinstance(candidate, dict), "candidate must be an object")
        candidate_id = candidate.get("id")
        require(isinstance(candidate_id, str), "candidate id must be a string")
        scores = candidate.get("scores")
        require(isinstance(scores, dict), f"{candidate_id}: scores must be an object")
        require(set(scores) == EXPECTED_CRITERIA, f"{candidate_id}: score criteria are incomplete")
        for criterion_id, score in scores.items():
            require(
                isinstance(score, int) and 1 <= score <= 5,
                f"{candidate_id}/{criterion_id}: score must be an integer from 1 to 5",
            )
        recomputed = round(sum(scores[key] * weights[key] for key in weights), 2)
        require(
            candidate.get("weighted_score") == recomputed,
            f"{candidate_id}: weighted score must be {recomputed}",
        )
        artifacts = candidate.get("artifacts")
        require(isinstance(artifacts, list) and len(artifacts) == 4, f"{candidate_id}: four artifacts are required")
        for raw_path in artifacts:
            require(isinstance(raw_path, str), f"{candidate_id}: artifact path must be text")
            require((ROOT / raw_path).is_file(), f"{candidate_id}: missing artifact {raw_path}")
        require(candidate.get("judgment"), f"{candidate_id}: judgment is required")
        by_id[candidate_id] = candidate

    ordered = sorted(by_id.values(), key=lambda item: item["weighted_score"], reverse=True)
    require(
        ordered[0]["weighted_score"] > ordered[1]["weighted_score"],
        "route selection must have one highest-scoring candidate",
    )
    decision = selection.get("decision")
    require(isinstance(decision, dict), "decision must be an object")
    require(decision.get("selected_route") == EXPECTED_SELECTED, "selected route is invalid")
    require(decision.get("action") == EXPECTED_ACTION, "selected action is invalid")
    require(ordered[0]["id"] == EXPECTED_SELECTED, "selected route must have the highest score")
    require(decision.get("rationale"), "decision rationale is required")
    require(len(decision.get("next_deliverables", [])) >= 4, "next deliverables are incomplete")

    boundary = selection.get("claim_boundary")
    require(isinstance(boundary, dict), "selection claim boundary is required")
    non_claims = {str(item).lower() for item in boundary.get("does_not_establish", [])}
    for required in (
        "a runnable second route",
        "real web-service performance",
        "empirical learning effectiveness",
        "product-market fit",
        "public production readiness",
    ):
        require(required in non_claims, f"selection claim boundary is missing: {required}")

    return weights, by_id[EXPECTED_SELECTED]


def validate_contract(
    contract: dict[str, Any], inventory: dict[str, Any], selected: dict[str, Any]
) -> None:
    require(contract.get("schema_version") == 1, "route contract schema_version must be 1")
    require(
        contract.get("contract") == "principia-product-alpha-route-candidate/0.1",
        "route candidate contract is invalid",
    )
    require(contract.get("id") == EXPECTED_SELECTED, "route contract id is invalid")
    require(contract.get("status") == "selected-for-implementation", "route contract status is invalid")
    require(contract.get("baseline_route") == "refrigerator", "route contract baseline is invalid")

    canonical_sources = contract.get("canonical_sources")
    require(isinstance(canonical_sources, dict), "canonical_sources must be an object")
    require(set(canonical_sources) == {"system", "failure", "investigation", "design"}, "route roles are incomplete")
    contract_paths = []
    for role, source in canonical_sources.items():
        require(isinstance(source, dict), f"{role}: source must be an object")
        path = source.get("path")
        slug = source.get("slug")
        require(isinstance(path, str) and (ROOT / path).is_file(), f"{role}: source path is invalid")
        require(isinstance(slug, str) and slug, f"{role}: source slug is required")
        text = (ROOT / path).read_text(encoding="utf-8")
        require(f"slug: {slug}" in text, f"{role}: source slug does not match canonical file")
        require("status: reviewed" in text, f"{role}: canonical source must be reviewed")
        require(source.get("artifact_revision") == 1, f"{role}: artifact revision must be 1")
        contract_paths.append(path)

    inventory_selected = inventory_route(inventory, EXPECTED_SELECTED)
    inventory_artifacts = inventory_selected.get("artifacts")
    require(isinstance(inventory_artifacts, list), "selected inventory artifacts must be a list")
    inventory_paths = {
        item.get("path") for item in inventory_artifacts if isinstance(item, dict)
    }
    require(set(contract_paths) == inventory_paths, "route contract sources must match the canonical inventory")
    require(set(contract_paths) == set(selected["artifacts"]), "route contract and scorecard sources differ")

    steps = contract.get("learner_steps")
    require(isinstance(steps, list), "learner_steps must be a list")
    require(tuple(item.get("id") for item in steps if isinstance(item, dict)) == EXPECTED_STEPS, "five learner steps are required in order")
    require(all(item.get("prompt") for item in steps), "every learner step needs a prompt")

    adapter = contract.get("model_adapter")
    require(isinstance(adapter, dict), "model_adapter must be an object")
    require(adapter.get("id") == "queue-delay-fluid-v1", "queue adapter id is invalid")
    require(adapter.get("kind") == "deterministic-queue", "queue adapter kind is invalid")
    parameters = adapter.get("parameters")
    require(isinstance(parameters, list) and len(parameters) == 5, "queue adapter must define five parameters")
    parameter_ids = {item.get("id") for item in parameters if isinstance(item, dict)}
    require(
        parameter_ids
        == {
            "external_arrival_rate_rps",
            "service_rate_rps",
            "retry_fraction",
            "queue_capacity_requests",
            "observation_seconds",
        },
        "queue adapter parameters are incomplete",
    )
    require(len(adapter.get("outputs", [])) >= 6, "queue adapter outputs are incomplete")
    require(len(adapter.get("limitations", [])) >= 3, "queue adapter limitations are incomplete")

    challenge = contract.get("diagnosis_challenge")
    require(isinstance(challenge, dict), "diagnosis challenge is required")
    options = challenge.get("options")
    require(isinstance(options, list) and len(options) == 4, "diagnosis challenge must have four options")
    require(challenge.get("correct_index") == 1, "diagnosis correct index is invalid")
    require(challenge.get("explanation"), "diagnosis explanation is required")

    safety = contract.get("safety_boundaries")
    require(isinstance(safety, dict), "safety boundaries are required")
    for key in ("synthetic_only", "no_live_traffic", "no_real_accounts", "no_personal_data"):
        require(safety.get(key) is True, f"safety boundary must require {key}")

    atlas = contract.get("atlas")
    require(isinstance(atlas, dict), "Atlas decision is required")
    require(atlas.get("live") is False, "live Atlas access must remain disabled")
    require(atlas.get("status_inheritance") == "prohibited", "Atlas status inheritance must be prohibited")
    require(atlas.get("expansion_required") is False, "route selection must not force Atlas expansion")

    requirements = "\n".join(str(item).lower() for item in contract.get("reusable_shell_requirements", []))
    for operation in ("validate", "run", "summarize", "describe-chart"):
        require(operation in requirements, f"reusable shell requirements must include {operation}")
    require("refrigerator" in requirements, "reusable shell requirements must preserve refrigerator")
    require(len(contract.get("acceptance_criteria", [])) >= 7, "route acceptance criteria are incomplete")


def validate_documents(selection: dict[str, Any], selected: dict[str, Any]) -> None:
    report = REPORT_PATH.read_text(encoding="utf-8")
    state = PRODUCT_STATE_PATH.read_text(encoding="utf-8")
    lowered_report = report.lower()
    lowered_state = state.lower()
    command = "software/product_alpha/evaluation/validate_route_selection.py check"
    for text, label in ((lowered_report, "route report"), (lowered_state, "product state")):
        require(EXPECTED_SELECTED in text, f"{label} must name the selected route")
        require(EXPECTED_ACTION in text, f"{label} must name the selected action")
        require("a runnable second route" in text, f"{label} must preserve the runnable-route claim boundary")
    require(command in report, "route report must expose the validator command")
    require(command in state, "product state must expose the validator command")
    require("4.95" in report, "route report must record the selected weighted score")
    require(str(selected["weighted_score"]) in report, "route report score does not match JSON")


def validate() -> dict[str, Any]:
    selection = load_json(SELECTION_PATH)
    contract = load_json(CONTRACT_PATH)
    inventory = load_json(INVENTORY_PATH)
    _, selected = validate_selection(selection)
    validate_contract(contract, inventory, selected)
    validate_documents(selection, selected)
    return selection


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check",))
    parser.parse_args()
    selection = validate()
    selected_id = selection["decision"]["selected_route"]
    selected = next(item for item in selection["candidates"] if item["id"] == selected_id)
    print(f"route-selection-passed: {selected_id} ({selected['weighted_score']:.2f})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
