from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from export_principia_atlas_dependents import build_export  # noqa: E402

MANIFEST = ROOT / "integration" / "principia-atlas" / "manifests" / "feedback-instability.fixture.json"
EXPORT = ROOT / "integration" / "principia-atlas" / "exports" / "feedback-instability.external-dependent.fixture.json"
EXPECTED_REVISIONS = {
    "claim:en:model-oscillation-does-not-prove-real-system": 1,
    "model:en:delayed-correction-recurrence": 2,
    "concept:en:feedback": 1,
    "concept:en:oscillation": 1,
}


class BridgeCandidateTests(unittest.TestCase):
    def load(self, path: Path) -> dict[str, object]:
        value = json.loads(path.read_text(encoding="utf-8"))
        self.assertIsInstance(value, dict)
        return value

    def test_candidate_is_non_live_and_exact_revision_pinned(self) -> None:
        manifest = self.load(MANIFEST)
        self.assertEqual(manifest["mode"], "bridge-candidate")
        self.assertIs(manifest["live"], False)
        atlas = manifest["atlas"]
        self.assertIsInstance(atlas, dict)
        dependencies = atlas["dependencies"]
        actual = {item["id"]: item["revision"] for item in dependencies}
        self.assertEqual(actual, EXPECTED_REVISIONS)

    def test_status_authority_remains_separate(self) -> None:
        manifest = self.load(MANIFEST)
        policy = manifest["status_policy"]
        self.assertEqual(policy["knowledge_status_inheritance"], "prohibited")
        self.assertEqual(policy["pedagogical_status_inheritance"], "prohibited")
        self.assertEqual(policy["release_status_inheritance"], "prohibited")
        principia = manifest["principia"]
        self.assertEqual(principia["pedagogical_status"], "reviewed")
        self.assertEqual(principia["release_status"], "draft")
        self.assertEqual(principia["artifact_revision"], 1)

    def test_committed_export_matches_deterministic_builder(self) -> None:
        manifest = self.load(MANIFEST)
        committed = self.load(EXPORT)
        self.assertEqual(committed, build_export(manifest))
        self.assertEqual(committed["contract"], "principia-atlas-external-dependent/0.2")
        self.assertEqual(committed["bridge_mode"], "bridge-candidate")
        self.assertIs(committed["live"], False)
        exact = {item["id"]: item["revision"] for item in committed["depends_on_exact"]}
        self.assertEqual(exact, EXPECTED_REVISIONS)
        for forbidden in ("status", "pedagogical_status", "release_status", "knowledge_status"):
            self.assertNotIn(forbidden, committed)

    def test_revision_impact_records_adoption_without_status_promotion(self) -> None:
        impact = self.load(ROOT / "release" / "phase-12-revision-impact.json")
        accepted = impact["accepted_changes"]
        self.assertEqual(len(accepted), 1)
        adoption = accepted[0]
        self.assertEqual(adoption["atlas_entity"], "model:en:delayed-correction-recurrence")
        self.assertEqual((adoption["from_revision"], adoption["to_revision"]), (1, 2))
        self.assertIs(adoption["principia_meaning_changed"], False)
        self.assertEqual(adoption["principia_artifact_revision_after"], 1)
        self.assertEqual(adoption["principia_pedagogical_status_after"], "reviewed")
        self.assertEqual(adoption["principia_release_status_after"], "draft")

    def test_materials_separate_oscillation_from_instability(self) -> None:
        feedback = (ROOT / "failure-atlas" / "feedback-instability.md").read_text(encoding="utf-8").lower()
        refrigerator = (ROOT / "system-dossiers" / "refrigerator.md").read_text(encoding="utf-8").lower()
        self.assertIn("does not by itself establish instability", feedback)
        self.assertIn("exactly periodic with period 6", feedback)
        self.assertIn("it is also bounded", feedback)
        self.assertIn("the resulting bounded temperature cycle is intentional", refrigerator)
        self.assertIn("a repeated cycle is not automatically unstable", refrigerator)
        self.assertIn("abnormal short-cycling", refrigerator)

    def test_pilot_record_targets_phase_2_importer_without_live_calls(self) -> None:
        pilot = self.load(ROOT / "release" / "phase-12-pilot-readiness.json")
        state = pilot["integration_state"]
        self.assertEqual(state["mode"], "bridge-candidate")
        self.assertIs(state["live"], False)
        self.assertEqual(state["decision"], "candidate-ready")
        self.assertIs(pilot["principia_readiness"]["phase_2_importer_candidate"], True)
        self.assertIs(pilot["atlas_readiness"]["repository_changed_by_bridge_candidate"], False)


if __name__ == "__main__":
    unittest.main()
