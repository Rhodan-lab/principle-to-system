#!/usr/bin/env python3
"""Remove participant-count gating from optional Product Alpha observation tools."""
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


# Python summary contract: no minimum, no incomplete signal, explicit non-authority.
summary = Path("software/product_alpha/evaluation/summarize.py")
replace_once(
    summary,
    "MIN_COHORT_SIZE = 5",
    "MIN_COHORT_SIZE = 0  # compatibility sentinel: optional observation has no minimum",
    "summary no-minimum sentinel",
)
regex_once(
    summary,
    r'''    if summary\["sessions"\] < MIN_COHORT_SIZE:\n        signals\.append\(\n            \{\n                "code": "cohort-incomplete",\n                "message": \(\n                    f"Only \{summary\['sessions'\]\} valid sessions are present; "\n                    f"the documented minimum is \{MIN_COHORT_SIZE\}\."\n                \),\n            \}\n        \)\n''',
    "",
    "remove threshold revision signal",
)
replace_once(
    summary,
    '"contract": "principia-product-alpha-pilot-summary/0.3",',
    '"contract": "principia-product-alpha-pilot-summary/0.4",',
    "summary contract bump",
)
replace_once(
    summary,
    '        "minimum_cohort_size": MIN_COHORT_SIZE,\n        "cohort_complete": len(sessions) >= MIN_COHORT_SIZE,',
    '        "minimum_cohort_size": MIN_COHORT_SIZE,\n        "cohort_complete": True,\n        "observation_mode": "optional-descriptive",\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "summary compatibility and authority fields",
)
regex_once(
    summary,
    r'''    summary\["evidence_status"\] = \(\n        "incomplete"\n        if not summary\["cohort_complete"\]\n        else "ready-for-human-review"\n    \)''',
    '    summary["evidence_status"] = "ready-for-human-review"',
    "summary non-gated evidence status",
)
regex_once(
    summary,
    r'''        \(\n            f"- Valid sessions: \{summary\['sessions'\]\} / minimum "\n            f"\{summary\['minimum_cohort_size'\]\}"\n        \),''',
    '        f"- Valid observations: {summary[\'sessions\']} (no minimum count)",',
    "summary markdown no minimum",
)
replace_once(
    summary,
    '            "- No automatic revision trigger was detected. "\n            "Human review is still required."',
    '            "- No automatic product signal was detected. Optional review may still add context."',
    "summary no-signal wording",
)
replace_once(
    summary,
    '                "Use these aggregates to choose one primary product action. "\n                "Do not commit raw session records or identifiable notes. "\n                "A tool-generated status never authorizes a second route, public "\n                "release, SaaS expansion, or a learning-effectiveness claim."',
    '                "These optional aggregates may inform a product discussion, but they "\n                "never authorize or block roadmap progress. Do not commit raw session "\n                "records or identifiable notes. A tool-generated status never authorizes "\n                "a second route, public release, SaaS expansion, or a learning-effectiveness claim."',
    "summary decision boundary",
)

# Browser Pilot Lab mirrors the same non-gated summary semantics.
pilot_lab = Path("software/product_alpha/pilot-lab.html")
replace_once(
    pilot_lab,
    'const ROUTE_ID="refrigerator-v1",MIN_COHORT_SIZE=5,STEPS=',
    'const ROUTE_ID="refrigerator-v1",MIN_COHORT_SIZE=0,STEPS=',
    "Pilot Lab no-minimum sentinel",
)
regex_once(
    pilot_lab,
    r'''if\(summary\.sessions<MIN_COHORT_SIZE\)signals\.push\(\{code:"cohort-incomplete",message:`Only \$\{summary\.sessions\} valid sessions are present; the documented minimum is \$\{MIN_COHORT_SIZE\}\.`,?\}\);''',
    "",
    "Pilot Lab remove threshold signal",
)
replace_once(
    pilot_lab,
    'contract:"principia-product-alpha-pilot-summary/0.3"',
    'contract:"principia-product-alpha-pilot-summary/0.4"',
    "Pilot Lab summary contract bump",
)
replace_once(
    pilot_lab,
    'minimum_cohort_size:MIN_COHORT_SIZE,cohort_complete:sessions.length>=MIN_COHORT_SIZE,started',
    'minimum_cohort_size:MIN_COHORT_SIZE,cohort_complete:true,observation_mode:"optional-descriptive",roadmap_gate:false,decision_authority:false,started',
    "Pilot Lab authority fields",
)
replace_once(
    pilot_lab,
    'summary.evidence_status=summary.cohort_complete?"ready-for-human-review":"incomplete"',
    'summary.evidence_status="ready-for-human-review"',
    "Pilot Lab non-gated evidence status",
)
replace_once(
    pilot_lab,
    'status.className="status incomplete";status.textContent=`Evidence gate incomplete: 0 of ${MIN_COHORT_SIZE} valid sessions.`;',
    'status.className="status incomplete";status.textContent="Optional observation set is empty. Add valid records only when external observation is useful.";',
    "Pilot Lab empty status",
)
regex_once(
    pilot_lab,
    r'''status\.className=`status \$\{s\.cohort_complete\?"review":"incomplete"\}`;status\.textContent=s\.cohort_complete\?`Cohort minimum reached: \$\{s\.sessions\} valid sessions\. Human evidence review is required\.`:`Evidence gate incomplete: \$\{s\.sessions\} of \$\{MIN_COHORT_SIZE\} valid sessions\.`;''',
    'status.className="status review";status.textContent=`Optional descriptive observation: ${s.sessions} valid record${s.sessions===1?"":"s"}. No minimum count; this does not gate roadmap progress.`;',
    "Pilot Lab descriptive status",
)
replace_once(
    pilot_lab,
    '"- Valid sessions: "+s.sessions+" / minimum "+s.minimum_cohort_size,',
    '"- Valid observations: "+s.sessions+" (no minimum count)",',
    "Pilot Lab markdown no minimum",
)
replace_once(
    pilot_lab,
    "else lines.push(\"- No automatic revision trigger was detected. Human review is still required.\");",
    "else lines.push(\"- No automatic product signal was detected. Optional review may still add context.\");",
    "Pilot Lab no-signal wording",
)
replace_once(
    pilot_lab,
    '"Use these aggregates to choose one primary product action. Do not commit raw session records or identifiable notes. A tool-generated status never authorizes a second route, public release, SaaS expansion, or a learning-effectiveness claim.",""',
    '"These optional aggregates may inform a product discussion, but they never authorize or block roadmap progress. Do not commit raw session records or identifiable notes. A tool-generated status never authorizes a second route, public release, SaaS expansion, or a learning-effectiveness claim.",""',
    "Pilot Lab decision boundary",
)

# Workspace intake accepts any non-empty valid observation set without an override.
assembly = Path("software/product_alpha/evaluation/assemble_workspace.py")
regex_once(
    assembly,
    r'''    complete = bool\(plan\.summary\["cohort_complete"\]\)\n    if not complete and not allow_incomplete:\n        raise ValueError\(\n            f"cohort has \{len\(plan\.sessions\)\} valid sessions; "\n            f"the documented minimum is \{pilot_summary\.MIN_COHORT_SIZE\}\. "\n            "Run the check command while collecting, or pass --allow-incomplete "\n            "only when intentionally closing the cohort early\."\n        \)\n''',
    '    complete = bool(plan.summary["cohort_complete"])\n',
    "remove assembly threshold gate",
)
replace_once(
    assembly,
    '        "incomplete_assembly_authorized": not complete and allow_incomplete,',
    '        "incomplete_assembly_authorized": False,\n        "observation_mode": "optional-descriptive",\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "assembly non-authority fields",
)
replace_once(
    assembly,
    '        "human_review_required": True,\n    }\n\n\ndef assemble_workspace',
    '        "human_review_required": True,\n        "observation_mode": "optional-descriptive",\n        "roadmap_gate": False,\n        "decision_authority": False,\n    }\n\n\ndef assemble_workspace',
    "preflight non-authority fields",
)
replace_once(
    assembly,
    '        help="intentionally seal fewer than the documented minimum sessions",',
    '        help="deprecated compatibility flag; optional observation has no minimum",',
    "assembly compatibility flag help",
)

# Workspace status no longer has a collecting-until-threshold stage.
status = Path("software/product_alpha/evaluation/workspace_status.py")
replace_once(
    status,
    '        "human_review_required": True,',
    '        "human_review_required": True,\n        "observation_mode": "optional-descriptive",\n        "roadmap_gate": False,\n        "decision_authority": False,',
    "workspace status non-authority fields",
)
regex_once(
    status,
    r'''        complete = preflight\["cohort_complete"\] is True\n        if complete:\n            return \{\n                \*\*report,\n                "stage": "ready-to-assemble",\n                "sessions": preflight\["sessions"\],\n                "minimum_cohort_size": preflight\["minimum_cohort_size"\],\n                "cohort_complete": True,\n                "evidence_status": preflight\["evidence_status"\],\n                "predicted_combined_sha256": preflight\[\n                    "predicted_combined_sha256"\n                \],\n                "source_records_sha256": preflight\["source_records_sha256"\],\n                "next_action": "assemble-immutable-intake",\n                "next_command": _workspace_command\(\n                    "assemble_workspace\.py",\n                    root,\n                \),\n                "validation_command": _workspace_command\(\n                    "assemble_workspace\.py",\n                    root,\n                    "check",\n                \),\n            \}\n        return \{\n            \*\*report,\n            "stage": "collecting",\n            "sessions": preflight\["sessions"\],\n            "minimum_cohort_size": preflight\["minimum_cohort_size"\],\n            "cohort_complete": False,\n            "evidence_status": preflight\["evidence_status"\],\n            "predicted_combined_sha256": preflight\["predicted_combined_sha256"\],\n            "source_records_sha256": preflight\["source_records_sha256"\],\n            "next_action": "collect-more-session-records",\n            "next_command": _launch_command\(root\),\n            "validation_command": _workspace_command\(\n                "assemble_workspace\.py",\n                root,\n                "check",\n            \),\n        \}''',
    '''        return {
            **report,
            "stage": "ready-to-assemble",
            "sessions": preflight["sessions"],
            "minimum_cohort_size": preflight["minimum_cohort_size"],
            "cohort_complete": True,
            "evidence_status": preflight["evidence_status"],
            "predicted_combined_sha256": preflight["predicted_combined_sha256"],
            "source_records_sha256": preflight["source_records_sha256"],
            "next_action": "assemble-immutable-intake",
            "next_command": _workspace_command("assemble_workspace.py", root),
            "validation_command": _workspace_command(
                "assemble_workspace.py",
                root,
                "check",
            ),
        }''',
    "workspace status remove threshold stage",
)

# Generated workspace instructions align with the actual no-minimum runtime.
prepare_workspace = Path("software/product_alpha/evaluation/prepare_workspace.py")
regex_once(
    prepare_workspace,
    r'''2\. During collection, validate the current files without sealing the cohort:\n\n```bash\npython3 software/product_alpha/evaluation/assemble_workspace\.py check \\\\\n  --workspace \{workspace_arg\}\n```\n\nThe check command fully validates every current export, rejects malformed, mixed-build, duplicate, personal-data-bearing, symlinked, or unsupported records, predicts the exact combined JSONL and source-record hashes, reports the valid session count and cohort status, and writes nothing\. It is safe to repeat after each new session\.\n\n3\. After collection is intentionally closed and the documented minimum has been reached, assemble the immutable cohort intake:\n\n```bash\npython3 software/product_alpha/evaluation/assemble_workspace\.py \\\\\n  --workspace \{workspace_arg\}\n```\n\nNormal assembly refuses fewer than five valid sessions so a facilitator cannot accidentally lock an incomplete cohort while collection is still active\. If the pilot must close early because recruitment or execution stopped, make that decision explicit:\n\n```bash\npython3 software/product_alpha/evaluation/assemble_workspace\.py \\\\\n  --workspace \{workspace_arg\} \\\\\n  --allow-incomplete\n```\n\nAssembly validates every file again, sorts accepted records by anonymous session ID, and writes `verified/anonymous-sessions\.jsonl` plus `verified/intake-manifest\.json`\. The intake manifest hashes every raw export, the source-record set, and the combined JSONL\. Source files are not changed\. Existing verified outputs are never overwritten\. `--allow-incomplete` records an intentional early closure; it does not make the evidence complete or eligible for planning advance\.''',
    '''2. While the optional observation set is open, validate the current files without writing verified outputs:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \\
  --workspace {workspace_arg}
```

The check command fully validates every current export, rejects malformed, mixed-build, duplicate, personal-data-bearing, symlinked, or unsupported records, predicts the exact combined JSONL and source-record hashes, reports the valid observation count, and writes nothing. It is safe to repeat after each new record.

3. Whenever the project intentionally closes a non-empty optional observation set, assemble the immutable intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \\
  --workspace {workspace_arg}
```

There is no minimum observation count and no incomplete-cohort override. Assembly validates every file again, sorts accepted records by anonymous session ID, and writes `verified/anonymous-sessions.jsonl` plus `verified/intake-manifest.json`. The intake manifest hashes every raw export, the source-record set, and the combined JSONL. Source files are not changed and existing verified outputs are never overwritten. Assembly records optional descriptive evidence only; it never authorizes or blocks roadmap progress.''',
    "generated workspace no-minimum instructions",
)
replace_once(
    prepare_workspace,
    'Do not treat an empty directory, an incomplete cohort, an intake manifest, a review packet, a decision record, a decision receipt, a repository handoff candidate, or this workspace manifest as proof of learning effectiveness. Human judgment remains required, and no generated artifact by itself authorizes a second route or public release.',
    'Do not treat an empty directory, an optional observation set, an intake manifest, a review packet, a decision record, a decision receipt, a repository handoff candidate, or this workspace manifest as proof of learning effectiveness. No generated artifact authorizes or blocks roadmap progress, a second route, or public release.',
    "generated workspace claim boundary",
)

# Active docs make the compatibility semantics explicit.
pilot_doc = Path("software/product_alpha/PILOT.md")
replace_once(
    pilot_doc,
    "Validate current exports without sealing the cohort:",
    "Validate current exports without closing the optional observation set:",
    "pilot protocol collection wording",
)
replace_once(
    pilot_doc,
    "If the project deliberately closes an observation set, it may use the existing assembly, review, decision, receipt, and handoff commands documented in the generated workspace README. Those tools retain privacy, non-overwrite, hash-binding, route-binding, and repository-external guarantees.",
    "If the project deliberately closes any non-empty observation set, it may use the existing assembly, review, decision, receipt, and handoff commands documented in the generated workspace README. There is no minimum count and no incomplete-set override. The compatibility fields `minimum_cohort_size: 0` and `cohort_complete: true` mean only that the optional set can be reviewed; they are never roadmap authority. Those tools retain privacy, non-overwrite, hash-binding, route-binding, and repository-external guarantees.",
    "pilot protocol compatibility semantics",
)

product_state = Path("PRODUCT_STATE.md")
replace_once(
    product_state,
    "Recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain optional research capability. They are not required for roadmap progress.",
    "Recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain optional research capability. They are not required for roadmap progress. The runtime has no participant-count threshold: any non-empty valid observation set may be summarized or assembled, and compatibility status fields never authorize or block the roadmap.",
    "product state no-threshold authority",
)

# Regression tests: summary semantics.
evaluation_test = Path("software/tests/test_product_alpha_evaluation.py")
regex_once(
    evaluation_test,
    r'''    def test_summary_is_deterministic_and_marks_incomplete_cohort\(self\):.*?    def test_load_rejects_personal_data_fields''',
    '''    def test_summary_is_deterministic_and_has_no_observation_threshold(self):
        sessions = [
            session("anonymous-001", MODULE.STEPS, confusion_tags=["model-controls"]),
            session(
                "anonymous-002",
                MODULE.STEPS[:3],
                duration_minutes=20,
                voluntary_continue=False,
                confusion_tags=["model-controls", "evidence-status"],
            ),
        ]
        summary = MODULE.summarize(sessions)
        first = MODULE.render_markdown(summary)
        second = MODULE.render_markdown(MODULE.summarize(sessions))
        self.assertEqual(first, second)
        self.assertEqual(summary["contract"], "principia-product-alpha-pilot-summary/0.4")
        self.assertEqual(summary["pilot_build_id"], BUILD_ID)
        self.assertEqual(summary["evidence_status"], "ready-for-human-review")
        self.assertTrue(summary["cohort_complete"])
        self.assertEqual(summary["minimum_cohort_size"], 0)
        self.assertEqual(summary["observation_mode"], "optional-descriptive")
        self.assertFalse(summary["roadmap_gate"])
        self.assertFalse(summary["decision_authority"])
        self.assertIn(f"Pilot build ID: `{BUILD_ID}`", first)
        self.assertIn("Valid observations: 2 (no minimum count)", first)
        self.assertIn("Completion rate: 50.0%", first)
        self.assertIn("`model-controls`: 2", first)
        self.assertNotIn("`cohort-incomplete`", first)
        self.assertIn("`recurring-confusion:model-controls`", first)

    def test_single_observation_is_ready_for_optional_review(self):
        summary = MODULE.summarize([session("anonymous-001", MODULE.STEPS)])
        self.assertTrue(summary["cohort_complete"])
        self.assertEqual(summary["minimum_cohort_size"], 0)
        self.assertEqual(summary["evidence_status"], "ready-for-human-review")
        self.assertFalse(
            any(signal["code"] == "cohort-incomplete" for signal in summary["revision_signals"])
        )

    def test_load_rejects_personal_data_fields''',
    "evaluation tests no threshold",
)

product_test = Path("software/tests/test_product_alpha.py")
replace_once(
    product_test,
    '        self.assertIn("cohort-incomplete", asset)',
    '        self.assertNotIn("cohort-incomplete", asset)\n        self.assertIn("no minimum count", asset)',
    "static Pilot Lab no-threshold test",
)

# Workspace intake regression tests.
intake_test = Path("software/tests/test_product_alpha_workspace_intake.py")
replace_once(
    intake_test,
    '            self.assertEqual(report["minimum_cohort_size"], 5)',
    '            self.assertEqual(report["minimum_cohort_size"], 0)',
    "intake preflight minimum sentinel",
)
replace_once(
    intake_test,
    '            self.assertFalse(first["cohort_complete"])\n            self.assertTrue(first["incomplete_assembly_requires_override"])',
    '            self.assertTrue(first["cohort_complete"])\n            self.assertFalse(first["incomplete_assembly_requires_override"])\n            self.assertTrue(first["ready_for_default_assembly"])',
    "repeated preflight no threshold",
)
regex_once(
    intake_test,
    r'''    def test_default_assembly_blocks_incomplete_cohort_without_writing\(self\) -> None:.*?    def test_preflight_reports_existing_verified_outputs''',
    '''    def test_default_assembly_accepts_any_nonempty_valid_observation_set(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 1)

            report = assemble_workspace.assemble_workspace(workspace)

            self.assertEqual(report["sessions"], 1)
            self.assertEqual(report["minimum_cohort_size"], 0)
            self.assertTrue(report["cohort_complete"])
            self.assertFalse(report["incomplete_assembly_authorized"])
            self.assertEqual(report["observation_mode"], "optional-descriptive")
            self.assertFalse(report["roadmap_gate"])
            self.assertTrue(
                (workspace / "verified" / "anonymous-sessions.jsonl").exists()
            )

    def test_allow_incomplete_flag_is_a_compatibility_noop(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)

            report = assemble_workspace.assemble_workspace(
                workspace,
                allow_incomplete=True,
            )

            self.assertEqual(report["sessions"], 2)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["evidence_status"], "ready-for-human-review")
            self.assertFalse(report["incomplete_assembly_authorized"])

    def test_preflight_reports_existing_verified_outputs''',
    "intake assembly tests no threshold",
)
regex_once(
    intake_test,
    r'''    def test_cli_requires_explicit_incomplete_override\(self\) -> None:.*?\n\n\nif __name__ == "__main__":''',
    '''    def test_cli_assembles_single_observation_without_override(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 1)

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--workspace",
                    str(workspace),
                ],
                cwd=REPO_ROOT,
                check=True,
                capture_output=True,
                text=True,
            )
            report = json.loads(completed.stdout)
            self.assertEqual(report["sessions"], 1)
            self.assertTrue(report["cohort_complete"])
            self.assertFalse(report["incomplete_assembly_authorized"])


if __name__ == "__main__":''',
    "intake CLI no threshold",
)

status_test = Path("software/tests/test_product_alpha_workspace_status.py")
replace_once(
    status_test,
    '    assemble_workspace.assemble_workspace(\n        workspace,\n        allow_incomplete=count < 5,\n    )',
    '    assemble_workspace.assemble_workspace(workspace)',
    "workspace status assembly helper",
)
regex_once(
    status_test,
    r'''    def test_reports_collecting_without_sealing\(self\) -> None:.*?    def test_reports_complete_collection_ready_to_assemble''',
    '''    def test_reports_any_valid_observation_set_ready_to_assemble(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = create_workspace(Path(directory))
            write_sessions(workspace, 2)
            report = workspace_status.inspect_workspace(workspace)

            self.assertEqual(report["stage"], "ready-to-assemble")
            self.assertEqual(report["sessions"], 2)
            self.assertTrue(report["cohort_complete"])
            self.assertEqual(report["minimum_cohort_size"], 0)
            self.assertEqual(report["next_action"], "assemble-immutable-intake")
            self.assertRegex(str(report["predicted_combined_sha256"]), r"^[0-9a-f]{64}$")
            self.assertEqual(list((workspace / "verified").iterdir()), [])

    def test_reports_complete_collection_ready_to_assemble''',
    "workspace status no collecting threshold",
)

review_test = Path("software/tests/test_product_alpha_review_packet.py")
regex_once(
    review_test,
    r'''    def test_incomplete_cohort_stays_pending_and_not_planning_eligible\(self\) -> None:.*?    def test_expected_build_mismatch_is_rejected''',
    '''    def test_small_optional_set_remains_reviewable_without_a_gate(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            input_path = Path(directory) / "sessions.jsonl"
            write_sessions(input_path, count=2)
            packet = review_packet.build_review_packet(input_path, BUILD_ID)

        summary = packet["aggregate_summary"]
        self.assertEqual(summary["evidence_status"], "ready-for-human-review")
        self.assertEqual(summary["minimum_cohort_size"], 0)
        self.assertTrue(summary["cohort_complete"])
        self.assertFalse(any(signal["code"] == "cohort-incomplete" for signal in summary["revision_signals"]))
        self.assertTrue(packet["review"]["planning_review_eligible"])
        self.assertEqual(packet["review"]["status"], "human-review-required")

    def test_expected_build_mismatch_is_rejected''',
    "review packet no threshold",
)

human_test = Path("software/tests/test_product_alpha_human_decision.py")
replace_once(
    human_test,
    '    assemble_workspace.assemble_workspace(\n        workspace,\n        allow_incomplete=count < 5,\n    )',
    '    assemble_workspace.assemble_workspace(workspace)',
    "human decision workspace helper",
)
regex_once(
    human_test,
    r'''    def test_blocks_planning_advance_for_incomplete_cohort\(self\) -> None:.*?    def test_rejects_modified_review_markdown''',
    '''    def test_optional_small_set_does_not_block_recording_a_planning_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            workspace = reviewed_workspace(Path(directory), count=2)

            report = record_decision.record_workspace_decision(
                workspace,
                "advance-to-next-product-planning-review",
                "facilitator-reviewer",
                "2026-08-02",
                "Optional observations were reviewed without treating their count as a gate.",
                "Use the internal multi-perspective authority for the actual roadmap decision.",
            )

            self.assertTrue(report["planning_review_action_selected"])
            decision = json.loads(Path(str(report["decision_json"])).read_text(encoding="utf-8"))
            self.assertFalse(decision["boundaries"]["automatic_repository_mutation"])
            self.assertFalse(decision["boundaries"]["second_route_authorized"])

    def test_rejects_modified_review_markdown''',
    "human decision no threshold",
)

# Final bounded scan for reintroduced active participant-count gates.
for path in (
    summary,
    pilot_lab,
    assembly,
    status,
    prepare_workspace,
    pilot_doc,
    product_state,
):
    text = path.read_text(encoding="utf-8")
    forbidden = (
        "cohort-incomplete",
        "the documented minimum is",
        "Evidence gate incomplete",
        "fewer than five valid sessions",
        "documented minimum has been reached",
    )
    found = [phrase for phrase in forbidden if phrase in text]
    if found:
        raise SystemExit(f"{path}: obsolete threshold wording remains: {found}")
