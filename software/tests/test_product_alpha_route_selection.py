from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SELECTION_PATH = REPO_ROOT / "reports" / "product-alpha-0-2-route-selection.json"
CONTRACT_PATH = (
    REPO_ROOT
    / "software"
    / "product_alpha"
    / "route-contracts"
    / "distributed-information.json"
)
INVENTORY_PATH = REPO_ROOT / "experiences" / "phase-11b-inventory.json"
VALIDATOR = (
    REPO_ROOT
    / "software"
    / "product_alpha"
    / "evaluation"
    / "validate_route_selection.py"
)
PRODUCT_STATE = REPO_ROOT / "PRODUCT_STATE.md"


class ProductAlphaRouteSelectionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.selection = json.loads(SELECTION_PATH.read_text(encoding="utf-8"))
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
        self.inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))

    def test_distributed_information_is_unique_highest_score(self) -> None:
        candidates = sorted(
            self.selection["candidates"],
            key=lambda item: item["weighted_score"],
            reverse=True,
        )
        self.assertEqual(candidates[0]["id"], "distributed-information")
        self.assertGreater(candidates[0]["weighted_score"], candidates[1]["weighted_score"])
        self.assertEqual(candidates[0]["weighted_score"], 4.95)
        self.assertEqual(
            self.selection["decision"]["action"],
            "implement-distributed-information-model-adapter-and-route",
        )

    def test_route_contract_matches_canonical_inventory(self) -> None:
        route = next(
            item
            for item in self.inventory["routes"]
            if item["id"] == "distributed-information"
        )
        inventory_paths = {item["path"] for item in route["artifacts"]}
        contract_paths = {
            item["path"] for item in self.contract["canonical_sources"].values()
        }
        self.assertEqual(contract_paths, inventory_paths)
        self.assertTrue(all((REPO_ROOT / path).is_file() for path in contract_paths))
        self.assertEqual(
            [item["id"] for item in self.contract["learner_steps"]],
            ["observe", "map", "model", "diagnose", "redesign"],
        )

    def test_contract_records_implemented_local_alpha(self) -> None:
        self.assertEqual(self.contract["status"], "implemented-local-alpha")
        implementation = self.contract["implementation"]
        self.assertEqual(
            implementation["route_path"],
            "software/product_alpha/routes/distributed-information.json",
        )
        self.assertEqual(
            implementation["adapter_asset"],
            "software/product_alpha/model-adapters.js",
        )
        self.assertEqual(implementation["default_route"], "refrigerator")
        self.assertEqual(implementation["adapter_id"], "queue-delay-fluid-v1")
        self.assertEqual(implementation["acceptance_status"], "pass")
        for key in ("route_path", "adapter_asset", "learner_shell", "builder", "launcher"):
            self.assertTrue((REPO_ROOT / implementation[key]).is_file())

    def test_contract_requires_reusable_model_adapter_and_safe_execution(self) -> None:
        adapter = self.contract["model_adapter"]
        self.assertEqual(adapter["id"], "queue-delay-fluid-v1")
        self.assertEqual(adapter["kind"], "deterministic-queue")
        self.assertEqual(len(adapter["parameters"]), 5)
        self.assertGreaterEqual(len(adapter["outputs"]), 6)
        safety = self.contract["safety_boundaries"]
        self.assertTrue(safety["synthetic_only"])
        self.assertTrue(safety["no_live_traffic"])
        self.assertTrue(safety["no_real_accounts"])
        self.assertTrue(safety["no_personal_data"])
        requirements = "\n".join(self.contract["reusable_shell_requirements"])
        for marker in ("validate", "run", "summarize", "describe-chart"):
            self.assertIn(marker, requirements)
        self.assertIn("refrigerator", requirements.lower())

    def test_product_state_records_route_aware_evidence_and_next_verification(self) -> None:
        state = PRODUCT_STATE.read_text(encoding="utf-8")
        for marker in (
            "distributed-information",
            "implemented-local-alpha",
            "two-route local alpha",
            "thermal-cabinet-v1",
            "queue-delay-fluid-v1",
            "distributed-information-v1",
            "route-bound local records",
            "make-facilitator-and-evidence-records-route-aware",
            "prove-distributed-information-evidence-chain-end-to-end",
        ):
            self.assertIn(marker, state)
        self.assertIn(
            "software/product_alpha/evaluation/validate_route_selection.py check",
            state,
        )
        self.assertIn("performance of a real distributed service", state.lower())
        self.assertIn("must not fabricate real learner evidence", state.lower())

    def test_validator_is_read_only_and_passes(self) -> None:
        tracked = {
            path: path.read_bytes()
            for path in (SELECTION_PATH, CONTRACT_PATH, PRODUCT_STATE)
        }
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "check"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn(
            "route-selection-passed: distributed-information (4.95); implementation=implemented-local-alpha",
            completed.stdout,
        )
        for path, content in tracked.items():
            self.assertEqual(path.read_bytes(), content)


if __name__ == "__main__":
    unittest.main()
