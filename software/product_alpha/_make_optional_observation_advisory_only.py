#!/usr/bin/env python3
"""Make optional Product Alpha observation artifacts advisory-only."""
from __future__ import annotations

import re
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def regex_once(path: Path, pattern: str, replacement: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.S)
    if count != 1:
        raise SystemExit(f"{label}: expected one regex match, found {count}")
    path.write_text(updated, encoding="utf-8")


review = Path("software/product_alpha/evaluation/prepare_review.py")
replace_once(
    review,
    'CONTRACT = "principia-product-alpha-pilot-review-packet/0.1"',
    'CONTRACT = "principia-product-alpha-pilot-review-packet/0.2"',
    "review contract bump",
)
replace_once(
    review,
    '''ALLOWED_PRIMARY_ACTIONS = (
    "revise-current-route",
    "repeat-current-route-pilot",
    "hold-current-route",
    "advance-to-next-product-planning-review",
)''',
    '''ALLOWED_PRIMARY_ACTIONS = (
    "record-observation-context",
    "revise-current-route",
    "repeat-current-route-pilot",
    "hold-current-route",
)''',
    "advisory action set",
)
replace_once(
    review,
    '''        "review": {
            "status": "human-review-required",
            "planning_review_eligible": packet_summary["evidence_status"]
            == "ready-for-human-review",
            "allowed_primary_actions": list(ALLOWED_PRIMARY_ACTIONS),''',
    '''        "review": {
            "status": "optional-advisory-review",
            "planning_review_eligible": False,
            "advisory_only": True,
            "roadmap_gate": False,
            "decision_authority": False,
            "allowed_primary_actions": list(ALLOWED_PRIMARY_ACTIONS),''',
    "review advisory contract",
)
replace_once(
    review,
    '            "automatic_product_decision": False,\n            "automatic_repository_mutation": False,',
    '            "advisory_only": True,\n            "roadmap_gate": False,\n            "decision_authority": False,\n            "automatic_product_decision": False,\n            "automatic_repository_mutation": False,',
    "review advisory boundaries",
)
replace_once(review, '"# Product Alpha Pilot Human Review",', '"# Product Alpha Optional Observation Review",', "review title")
regex_once(
    review,
    r'''        \(\n            f"- Valid sessions: \{summary\['sessions'\]\} / minimum "\n            f"\{summary\['minimum_cohort_size'\]\}"\n        \),''',
    '        f"- Valid observations: {summary[\'sessions\']} (no minimum count)",',
    "review observation count",
)
replace_once(
    review,
    '''        "> The hashes bind this worksheet to one verified local cohort. Raw session "
        "records, facilitator notes, and facilitator-authored custom tag text are not "
        "included and must remain private.",''',
    '''        "> The hashes bind this advisory worksheet to one verified local observation set. "
        "Raw session records, facilitator notes, and facilitator-authored custom tag text "
        "are not included and must remain private. This worksheet has no roadmap authority.",''',
    "review advisory note",
)
replace_once(
    review,
    '''        lines.append(
            "- No automatic revision trigger was detected. Human review is still required."
        )''',
    '''        lines.append(
            "- No automatic product signal was detected. Optional advisory review may still add context."
        )''',
    "review no-signal wording",
)
replace_once(review, '            "## Human decision",', '            "## Advisory interpretation",', "review advisory heading")
replace_once(
    review,
    '''            "Select exactly one primary action after reviewing the aggregate and the "
            "private facilitator notes:",''',
    '''            "Select exactly one advisory interpretation after reviewing the aggregate and "
            "the private facilitator notes. It cannot authorize or block roadmap work:",''',
    "review advisory instruction",
)
replace_once(
    review,
    '''            "- [ ] `revise-current-route`",
            "- [ ] `repeat-current-route-pilot`",
            "- [ ] `hold-current-route`",
            "- [ ] `advance-to-next-product-planning-review`",''',
    '''            "- [ ] `record-observation-context`",
            "- [ ] `revise-current-route`",
            "- [ ] `repeat-current-route-pilot`",
            "- [ ] `hold-current-route`",''',
    "review advisory checklist",
)
replace_once(
    review,
    '''            "Completing this worksheet does not automatically modify the repository, "
            "authorize a second route, establish release readiness, prove learning "
            "effectiveness, or establish product-market fit. Any product change requires "
            "a separate reviewed repository change.",''',
    '''            "Completing this worksheet records advisory context only. It cannot authorize "
            "or block roadmap work, modify the repository, authorize a second route, establish "
            "release readiness, prove learning effectiveness, or establish product-market fit. "
            "The internal multi-perspective review remains the product decision authority.",''',
    "review decision boundary",
)
replace_once(review, '    print("Product Alpha human-review packet created.")', '    print("Product Alpha optional-advisory packet created.")', "review CLI packet wording")
replace_once(review, '    print("Decision: human-review-required")', '    print("Decision: optional-advisory-review")', "review CLI decision wording")

record = Path("software/product_alpha/evaluation/record_decision.py")
replace_once(
    record,
    '''    planning_eligible = review.get("planning_review_eligible")
    if not isinstance(planning_eligible, bool):
        raise ValueError("review packet planning_review_eligible must be boolean")''',
    '''    planning_eligible = review.get("planning_review_eligible")
    if planning_eligible is not False:
        raise ValueError("optional review must not be planning-review eligible")
    for key, expected in (
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if review.get(key) is not expected:
            raise ValueError(f"optional review field {key!r} is invalid")''',
    "decision review advisory validation",
)
replace_once(
    record,
    '        "planning_review_eligible": planning_eligible,',
    '        "planning_review_eligible": planning_eligible,\n        "advisory_only": True,\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "decision readiness advisory fields",
)
regex_once(
    record,
    r'''    planning_action_selected = action == "advance-to-next-product-planning-review"\n    if planning_action_selected and readiness\["planning_review_eligible"\] is not True:\n        raise ValueError\(\n            "advance-to-next-product-planning-review requires ready-for-human-review evidence"\n        \)''',
    '    planning_action_selected = False',
    "remove optional planning action",
)
replace_once(
    record,
    '        "evidence_status": readiness["evidence_status"],\n        "sessions": readiness["sessions"],',
    '        "evidence_status": readiness["evidence_status"],\n        "sessions": readiness["sessions"],\n        "observation_mode": "optional-descriptive",\n        "advisory_only": True,\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "decision top-level advisory fields",
)
replace_once(
    record,
    '            "status": "recorded",\n            "primary_action": action,',
    '            "status": "recorded",\n            "primary_action": action,\n            "advisory_only": True,\n            "roadmap_gate": False,\n            "decision_authority": False,',
    "human decision advisory fields",
)
replace_once(
    record,
    '            "human_supplied_decision": True,\n            "automatic_product_decision": False,',
    '            "human_supplied_decision": True,\n            "advisory_only": True,\n            "roadmap_gate": False,\n            "decision_authority": False,\n            "automatic_product_decision": False,',
    "decision advisory boundaries",
)
replace_once(record, '            "# Product Alpha Human Decision Record",', '            "# Product Alpha Optional Observation Advisory Record",', "decision markdown title")
replace_once(record, '            "## Human decision",', '            "## Human advisory interpretation",', "decision markdown heading")
replace_once(
    record,
    '''            "This record captures a human product action only. It does not automatically "
            "modify the repository, create a planning review, authorize a second route or "
            "public release, prove learning effectiveness, or establish product-market fit.",''',
    '''            "This record captures an optional advisory interpretation only. It cannot "
            "authorize or block roadmap work, create a planning review, modify the repository, "
            "authorize a second route or public release, prove learning effectiveness, or "
            "establish product-market fit. Internal multi-perspective review remains authoritative.",''',
    "decision markdown boundary",
)
replace_once(
    record,
    '        "primary_action": decision["primary_action"],\n        "decision_json": str(json_path),',
    '        "primary_action": decision["primary_action"],\n        "advisory_only": True,\n        "roadmap_gate": False,\n        "decision_authority": False,\n        "decision_json": str(json_path),',
    "receipt advisory fields",
)

handoff = Path("software/product_alpha/evaluation/prepare_handoff.py")
replace_once(
    handoff,
    '''    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")''',
    '''    review = packet.get("review")
    if not isinstance(review, dict):
        raise ValueError("review packet review must be an object")
    for key, expected in (
        ("planning_review_eligible", False),
        ("advisory_only", True),
        ("roadmap_gate", False),
        ("decision_authority", False),
    ):
        if review.get(key) is not expected:
            raise ValueError(f"review packet advisory field {key!r} is invalid")
    boundaries = packet.get("boundaries")
    if not isinstance(boundaries, dict):
        raise ValueError("review packet boundaries must be an object")''',
    "handoff review advisory validation",
)
replace_once(
    handoff,
    '        "planning_review_action_selected": decision[\n            "planning_review_action_selected"\n        ],',
    '        "planning_review_action_selected": decision[\n            "planning_review_action_selected"\n        ],\n        "advisory_only": True,\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "handoff candidate advisory fields",
)
replace_once(
    handoff,
    '            "human_decision_verified": True,\n            "raw_session_records_included": False,',
    '            "human_decision_verified": True,\n            "advisory_only": True,\n            "roadmap_gate": False,\n            "decision_authority": False,\n            "raw_session_records_included": False,',
    "handoff advisory boundaries",
)
replace_once(handoff, '        f"- Valid sessions: {candidate[\'sessions\']}",', '        f"- Valid observations: {candidate[\'sessions\']}",', "handoff observation count")
replace_once(handoff, '        f"- Verified human action: `{candidate[\'primary_action\']}`",', '        f"- Verified advisory action: `{candidate[\'primary_action\']}`",', "handoff advisory action wording")
replace_once(
    handoff,
    '''        "> This candidate is de-identified output for a separate human-reviewed "
        "repository change. It is not an authorization, publication action, or proof "
        "of learning effectiveness.",''',
    '''        "> This candidate is de-identified advisory context for the internal "
        "multi-perspective review. It is not roadmap authority, a repository-change "
        "authorization, a publication action, or proof of learning effectiveness.",''',
    "handoff advisory note",
)

status = Path("software/product_alpha/evaluation/workspace_status.py")
replace_once(status, '            "stage": "review-ready-for-decision",', '            "stage": "review-ready-for-advisory",', "workspace advisory review stage")
replace_once(status, '            "next_action": "record-human-decision",', '            "next_action": "record-optional-advisory",', "workspace advisory next action")
regex_once(
    status,
    r'''    follow_up = \{\n        "revise-current-route": "prepare-bounded-route-revision",\n        "repeat-current-route-pilot": "prepare-new-private-cohort",\n        "hold-current-route": "hold-until-recorded-checkpoint",\n        "advance-to-next-product-planning-review": "prepare-separate-planning-review",\n    \}\.get\(action, "review-recorded-human-action"\)''',
    '    follow_up = "return-to-internal-multi-perspective-review"',
    "workspace advisory follow-up",
)
replace_once(status, '            "stage": "decision-verified",', '            "stage": "advisory-verified",', "workspace advisory verified stage")
replace_once(status, '            "next_action": "prepare-deidentified-repository-handoff",', '            "next_action": "prepare-deidentified-advisory-handoff",', "workspace advisory handoff action")
replace_once(status, '        "stage": "handoff-verified",', '        "stage": "advisory-handoff-verified",', "workspace advisory handoff stage")

workspace = Path("software/product_alpha/evaluation/prepare_workspace.py")
replace_once(
    workspace,
    '''6. Check that the unchanged review packet is ready for a separate human decision record:''',
    '''6. Check that the unchanged optional review packet is ready for a separate advisory record:''',
    "workspace advisory check wording",
)
replace_once(
    workspace,
    '''7. After reviewing the aggregate and private facilitator notes, record exactly one human action:''',
    '''7. After reviewing the aggregate and private facilitator notes, record exactly one advisory interpretation:''',
    "workspace advisory record wording",
)
replace_once(
    workspace,
    '''Allowed primary actions are `revise-current-route`, `repeat-current-route-pilot`, `hold-current-route`, and `advance-to-next-product-planning-review`. The last action is rejected unless the cohort reached `ready-for-human-review` status.''',
    '''Allowed advisory actions are `record-observation-context`, `revise-current-route`, `repeat-current-route-pilot`, and `hold-current-route`. None authorizes or blocks roadmap work; the internal multi-perspective review remains the only product authority.''',
    "workspace advisory action documentation",
)
replace_once(
    workspace,
    '''The handoff JSON and Markdown contain the verified human action, de-identified aggregate metrics, revision signals, and evidence hashes.''',
    '''The handoff JSON and Markdown contain the verified advisory action, de-identified aggregate metrics, revision signals, and evidence hashes.''',
    "workspace advisory handoff wording",
)

pilot = Path("software/product_alpha/PILOT.md")
replace_once(
    pilot,
    '''Observations may inform a later decision, but they do not automatically authorize, block, or mutate repository work.''',
    '''Observations may inform internal review, but their review, decision, receipt, and handoff artifacts are advisory-only. They cannot select `advance-to-next-product-planning-review`, authorize, block, or mutate repository work.''',
    "optional protocol advisory boundary",
)

product_state = Path("PRODUCT_STATE.md")
replace_once(
    product_state,
    '''Recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain optional research capability. They are not required for roadmap progress. The runtime has no participant-count threshold: any non-empty valid observation set may be summarized or assembled, and compatibility status fields never authorize or block the roadmap.''',
    '''Recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain optional research capability. They are not required for roadmap progress. The runtime has no participant-count threshold: any non-empty valid observation set may be summarized or assembled. Every downstream artifact is advisory-only, cannot select `advance-to-next-product-planning-review`, and must return to the internal multi-perspective review; compatibility status fields never authorize or block the roadmap.''',
    "product state advisory boundary",
)

review_test = Path("software/tests/test_product_alpha_review_packet.py")
replace_once(review_test, '"principia-product-alpha-pilot-review-packet/0.1",', '"principia-product-alpha-pilot-review-packet/0.2",', "review test contract")
replace_once(
    review_test,
    '''        self.assertTrue(first["review"]["planning_review_eligible"])
        self.assertEqual(first["review"]["status"], "human-review-required")''',
    '''        self.assertFalse(first["review"]["planning_review_eligible"])
        self.assertEqual(first["review"]["status"], "optional-advisory-review")
        self.assertTrue(first["review"]["advisory_only"])
        self.assertFalse(first["review"]["roadmap_gate"])
        self.assertFalse(first["review"]["decision_authority"])''',
    "review test advisory fields",
)
replace_once(
    review_test,
    '''        self.assertTrue(packet["review"]["planning_review_eligible"])
        self.assertEqual(packet["review"]["status"], "human-review-required")''',
    '''        self.assertFalse(packet["review"]["planning_review_eligible"])
        self.assertEqual(packet["review"]["status"], "optional-advisory-review")''',
    "small review advisory status",
)
replace_once(review_test, '        self.assertIn("# Product Alpha Pilot Human Review", markdown)', '        self.assertIn("# Product Alpha Optional Observation Review", markdown)', "review markdown title test")
replace_once(
    review_test,
    '''        self.assertIn("revise-current-route", markdown)
        self.assertIn("advance-to-next-product-planning-review", markdown)''',
    '''        self.assertIn("record-observation-context", markdown)
        self.assertIn("revise-current-route", markdown)
        self.assertNotIn("advance-to-next-product-planning-review", markdown)''',
    "review markdown action test",
)
replace_once(review_test, '        self.assertIn("Product Alpha human-review packet created.", result.stdout)\n        self.assertIn("Decision: human-review-required", result.stdout)', '        self.assertIn("Product Alpha optional-advisory packet created.", result.stdout)\n        self.assertIn("Decision: optional-advisory-review", result.stdout)', "review CLI advisory output test")

human_test = Path("software/tests/test_product_alpha_human_decision.py")
replace_once(
    human_test,
    '''            self.assertIn(
                "This record captures a human product action only.",
                decision_markdown.read_text(encoding="utf-8"),
            )''',
    '''            self.assertIn(
                "optional advisory interpretation only",
                decision_markdown.read_text(encoding="utf-8"),
            )
            self.assertTrue(record["advisory_only"])
            self.assertFalse(record["roadmap_gate"])
            self.assertFalse(record["decision_authority"])''',
    "human decision advisory assertions",
)
regex_once(
    human_test,
    r'''    def test_optional_small_set_does_not_block_recording_a_planning_action\(self\) -> None:.*?    def test_rejects_modified_review_markdown''',
    '''    def test_optional_observation_rejects_planning_advance(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory), count=2)
            with self.assertRaisesRegex(ValueError, "unsupported primary action"):
                record_decision.record_workspace_decision(
                    workspace,
                    "advance-to-next-product-planning-review",
                    "facilitator-reviewer",
                    "2026-08-02",
                    "Optional observations cannot authorize a planning review action.",
                    "Return to the internal multi-perspective review.",
                )

    def test_optional_observation_records_advisory_context(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory), count=1)
            report = record_decision.record_workspace_decision(
                workspace,
                "record-observation-context",
                "facilitator-reviewer",
                "2026-08-02",
                "The optional observation adds context without becoming roadmap authority.",
                "Return to the internal multi-perspective review.",
            )
            decision = json.loads(Path(str(report["decision_json"])).read_text(encoding="utf-8"))
            self.assertFalse(decision["human_decision"]["planning_review_action_selected"])
            self.assertTrue(decision["human_decision"]["advisory_only"])
            self.assertFalse(decision["human_decision"]["decision_authority"])

    def test_rejects_modified_review_markdown''',
    "human advisory tests",
)
replace_once(
    human_test,
    '''            self.assertTrue(report["planning_review_eligible"])
            self.assertFalse(report["decision_outputs_exist"])''',
    '''            self.assertFalse(report["planning_review_eligible"])
            self.assertTrue(report["advisory_only"])
            self.assertFalse(report["decision_authority"])
            self.assertFalse(report["decision_outputs_exist"])''',
    "decision check advisory test",
)

handoff_test = Path("software/tests/test_product_alpha_handoff.py")
replace_once(
    handoff_test,
    '''            self.assertEqual(first["evidence_status"], "ready-for-human-review")''',
    '''            self.assertEqual(first["evidence_status"], "ready-for-human-review")
            self.assertTrue(first["advisory_only"])
            self.assertFalse(first["roadmap_gate"])
            self.assertFalse(first["decision_authority"])
            self.assertFalse(first["planning_review_action_selected"])''',
    "handoff advisory candidate assertions",
)
replace_once(
    handoff_test,
    '''            self.assertFalse(boundaries["human_rationale_included"])''',
    '''            self.assertFalse(boundaries["human_rationale_included"])
            self.assertTrue(boundaries["advisory_only"])
            self.assertFalse(boundaries["decision_authority"])''',
    "handoff advisory boundary assertions",
)

status_test = Path("software/tests/test_product_alpha_workspace_status.py")
replace_once(status_test, '            self.assertEqual(report["stage"], "review-ready-for-decision")\n            self.assertTrue(report["planning_review_eligible"])\n            self.assertEqual(report["next_action"], "record-human-decision")', '            self.assertEqual(report["stage"], "review-ready-for-advisory")\n            self.assertFalse(report["planning_review_eligible"])\n            self.assertEqual(report["next_action"], "record-optional-advisory")', "workspace review advisory test")
replace_once(status_test, '            self.assertEqual(report["stage"], "decision-verified")', '            self.assertEqual(report["stage"], "advisory-verified")', "workspace decision stage test")
replace_once(status_test, '                "prepare-deidentified-repository-handoff",', '                "prepare-deidentified-advisory-handoff",', "workspace handoff action test")
replace_once(status_test, '                "prepare-bounded-route-revision",', '                "return-to-internal-multi-perspective-review",', "workspace post handoff test")
replace_once(status_test, '            self.assertEqual(report["stage"], "handoff-verified")', '            self.assertEqual(report["stage"], "advisory-handoff-verified")', "workspace final advisory stage test")
replace_once(status_test, '            self.assertEqual(report["next_action"], "prepare-bounded-route-revision")', '            self.assertEqual(report["next_action"], "return-to-internal-multi-perspective-review")', "workspace final advisory action test")
replace_once(status_test, '            self.assertEqual(report["stage"], "handoff-verified")\n            self.assertFalse(report["writes_performed"])', '            self.assertEqual(report["stage"], "advisory-handoff-verified")\n            self.assertFalse(report["writes_performed"])', "workspace CLI advisory stage test")

state_test = Path("software/tests/test_product_alpha_state_authority.py")
replace_once(
    state_test,
    '''        self.assertIn("no minimum participant count", lowered)
        self.assertTrue(''',
    '''        self.assertIn("no minimum participant count", lowered)
        self.assertIn("advisory-only", lowered)
        self.assertIn("cannot select `advance-to-next-product-planning-review`", lowered)
        self.assertTrue(''',
    "state authority advisory assertions",
)

for path in (review, record, handoff, status, workspace, pilot, product_state):
    text = path.read_text(encoding="utf-8")
    if path != product_state and "advance-to-next-product-planning-review" in text:
        raise SystemExit(f"{path}: optional planning advance remains")
