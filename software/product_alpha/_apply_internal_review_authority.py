#!/usr/bin/env python3
"""Apply the Product Alpha internal-review authority update once."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


readme = ROOT / "README.md"
replace_once(
    readme,
    "> **Current program:** **Product Alpha 0.1 — evidence integrity recovery.** The active milestone is completion of a verifiable real learner pilot of the refrigerator route, not another numbered governance phase. See [`PRODUCT_STATE.md`](PRODUCT_STATE.md) for the current decision state. The detailed Phase 0–50 ledger remains in [`PROJECT_STATE.md`](PROJECT_STATE.md) as validated project history.",
    "> **Current program:** **Product Alpha 0.2 — second-route planning and reusable route architecture.** Product Alpha 0.1 passed the deterministic internal multi-perspective review; external participant observation is optional research rather than a roadmap gate. See [`PRODUCT_STATE.md`](PRODUCT_STATE.md) and [`reports/product-alpha-0-1-multi-perspective-review.md`](reports/product-alpha-0-1-multi-perspective-review.md). The detailed Phase 0–50 ledger remains in [`PROJECT_STATE.md`](PROJECT_STATE.md) as validated project history.",
    "root current program",
)
start = readme.read_text(encoding="utf-8")
old_section_start = "### Next evidence gate\n"
old_section_end = "## Principia and Atlas\n"
if start.count(old_section_start) != 1 or start.count(old_section_end) != 1:
    raise SystemExit("root decision section anchors changed")
before, rest = start.split(old_section_start, 1)
_, after = rest.split(old_section_end, 1)
new_section = """### Current internal decision gate

Product Alpha 0.1 has passed an eight-perspective internal review covering product strategy, pedagogy, scientific integrity, UX and accessibility, privacy and security, operational reliability, evidence and provenance, and maintainability and governance.

Validate the decision authority without writing:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

The current action is `advance-to-next-product-planning-review`: keep refrigerator stable, select a second system route, and use it to prove reusable architecture. Optional field-observation tooling remains available but is not required for roadmap progress.

The review does not establish empirical learning effectiveness, retention, transfer, engagement outcomes, product-market fit, or public production readiness.

## Principia and Atlas
"""
readme.write_text(before + new_section + after, encoding="utf-8")
replace_once(
    readme,
    "Live Atlas integration remains disabled. Product Alpha is pilot-ready as software, not a public learning-effectiveness claim and not a production SaaS release.",
    "Live Atlas integration remains disabled. Product Alpha is internally validated as a local alpha and authorized for second-route planning, not a public learning-effectiveness claim or production SaaS release.",
    "root release boundary",
)

product_readme = ROOT / "software" / "product_alpha" / "README.md"
replace_once(
    product_readme,
    "This package is the first learner-facing product slice built from the existing Principia material foundation. It replaces phase-count growth with a concrete refrigerator journey and a private, verifiable pilot workflow that can run locally without accounts, analytics, cloud storage, or external runtime calls.",
    "This package is the first learner-facing product slice built from the existing Principia material foundation. It replaces phase-count growth with a concrete refrigerator journey, deterministic internal review, and optional local field-evaluation tools that require no accounts, analytics, cloud storage, or external runtime calls.",
    "product README introduction",
)
replace_once(
    product_readme,
    "## Supported pilot path\n\nPrepare a new private destination outside the repository before the first participant session:",
    "## Optional field-evaluation path\n\nThis path is retained for optional external observation or future research. It is not required for route planning, implementation, or repository progress.\n\nPrepare a new private destination outside the repository before any optional observation session:",
    "product README optional field path",
)
text = product_readme.read_text(encoding="utf-8")
old_start = "## Learner pilot\n"
old_end = "## Boundaries\n"
if text.count(old_start) != 1 or text.count(old_end) != 1:
    raise SystemExit("product README review anchors changed")
before, rest = text.split(old_start, 1)
_, after = rest.split(old_end, 1)
new = """## Internal multi-perspective review

The active product authority is the deterministic eight-perspective review:

- `reports/product-alpha-0-1-multi-perspective-review.json`
- `reports/product-alpha-0-1-multi-perspective-review.md`

Run the read-only validator:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

The current decision is `advance-to-next-product-planning-review`. Product Alpha 0.1 is the stable refrigerator baseline; the next task is selecting and implementing a second route to test architectural reuse.

Internal review supports claims about product coherence, scientific boundaries, accessibility contracts, privacy, security, deterministic operation, provenance, and maintainability. It does not establish empirical learning effectiveness, retention, transfer, engagement outcomes, product-market fit, or public production readiness.

## Optional field observation

[`PILOT.md`](PILOT.md) documents an optional local observation workflow. It has no minimum cohort requirement and does not authorize or block roadmap progress. Any records remain private, repository-external, and non-authoritative unless a future decision explicitly adopts them.

## Boundaries
"""
product_readme.write_text(before + new + after, encoding="utf-8")

pilot = ROOT / "software" / "product_alpha" / "PILOT.md"
pilot.write_text("""---
title: "Product Alpha 0.1 optional field observation"
slug: product-alpha-0-1-optional-field-observation
domain: experience
experience_type: optional-observation-protocol
status: optional
artifact_revision: 9
release_status: draft
prerequisites: [system-dossier-refrigerator]
connections: [product-alpha-internal-multi-perspective-review]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Product Alpha 0.1 optional field observation

This protocol is retained as an optional research capability. It is not a roadmap gate, release prerequisite, or decision authority.

The active decision authority is the internal multi-perspective review:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

## When to use this protocol

Use it only when the project deliberately wants external observation of interaction problems, misconceptions, or workflow friction. There is no minimum participant count and no requirement to run it before planning or implementing another route.

Observations may inform a later decision, but they do not automatically authorize, block, or mutate repository work.

## Safety and privacy boundaries

- Do not collect names, contact details, school details, account identifiers, birth dates, or other identifying information.
- Use anonymous session labels.
- Keep all records outside the repository.
- Keep the workspace local and facilitator-controlled.
- Do not modify appliances or ask anyone to perform physical repair work.
- Review free text before export.
- Treat the recorder as a convenience boundary rather than a guarantee of anonymity.

## Optional preparation

Prepare a repository-external workspace:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-observation
```

Preparation runs the deterministic build and loopback smoke gate before creating the empty workspace.

Launch the exact prepared build:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-observation \
  --open
```

The launcher fails closed on build drift and stores no session data.

## Observation prompts

When external observation is intentionally used, focus on product behavior rather than scoring people:

1. Can the person identify the system boundary and important flows?
2. Do they predict a model direction before running it?
3. Can they distinguish model output from a universal physical claim?
4. Can they distinguish controlled cycling from an abnormal failure condition?
5. Do they understand what the pinned evidence revision supports and does not prove?
6. Can they state a redesign benefit and trade-off?
7. Which interface step creates avoidable friction or ambiguity?

Do not teach the answer before the first attempt. Record product problems without blaming the participant.

## Optional local evidence chain

The existing tools remain available:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/refrigerator-observation

python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/refrigerator-observation
```

If the project deliberately closes an observation set, it may use the existing assembly, review, decision, and handoff commands. Those tools retain their privacy, non-overwrite, hash-binding, and repository-external guarantees.

They do not authorize another route, public release, SaaS infrastructure, empirical learning claims, or repository mutation.

## Claim boundary

Optional observation may reveal interaction failures or recurring confusion. It does not by itself establish:

- empirical learning effectiveness;
- retention;
- transfer;
- engagement outcomes;
- product-market fit;
- public production readiness.

The current roadmap proceeds from the internal review decision, whether or not this optional protocol is used.
""", encoding="utf-8")

pilot_summary = ROOT / "reports" / "product-alpha-0-1-pilot-summary.md"
pilot_summary.write_text("""---
title: "Product Alpha 0.1 optional field-evaluation status"
slug: product-alpha-0-1-optional-field-evaluation-status
domain: product
status: superseded
artifact_revision: 5
release_status: alpha
prerequisites: [product-alpha-refrigerator]
connections: [product-alpha-internal-multi-perspective-review]
last_reviewed: 2026-08-03
content_license: CC-BY-4.0
---

# Product Alpha 0.1 optional field-evaluation status

**Status:** superseded as active decision authority  
**Current authority:** `reports/product-alpha-0-1-multi-perspective-review.json`  
**Current decision:** `advance-to-next-product-planning-review`

## Authority change

External participant observation is no longer required for roadmap progress. The repository now uses a deterministic internal multi-perspective review across product strategy, pedagogy, scientific integrity, UX and accessibility, privacy and security, operational reliability, evidence and provenance, and maintainability and governance.

Validate the current authority:

```bash
python3 software/product_alpha/evaluation/validate_internal_review.py check
```

## Retained capability

The recorder, Pilot Lab, repository-external workspace, aggregation, review, decision, receipt, and handoff tools remain available for optional field observation or future research.

They are not required for:

- second-route planning;
- route implementation;
- internal product decisions;
- repository progress.

Any optional records remain local, private, repository-external, and non-authoritative unless a future decision explicitly adopts them.

## Claim boundary

The internal review may support claims about product coherence, deterministic operation, scientific boundaries, accessibility contracts, privacy, security, provenance, and maintainability.

It may not establish:

- empirical learning effectiveness;
- retention or transfer;
- engagement outcomes;
- product-market fit;
- public production readiness.

## Completion criteria

This authority transition is complete when:

- the eight-perspective JSON and Markdown review artifacts agree;
- the read-only validator passes;
- `PRODUCT_STATE.md` records the next-product planning decision;
- active README files no longer treat external participant observation as a gate;
- the optional observation protocol explicitly states that it does not authorize or block roadmap progress;
- focused Product Alpha CI passes;
- the change is separately reviewed and merged.
""", encoding="utf-8")

state_test = ROOT / "software" / "tests" / "test_product_alpha_state_authority.py"
state_test.write_text("""from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
PRODUCT_STATE = REPO_ROOT / "PRODUCT_STATE.md"
ROOT_README = REPO_ROOT / "README.md"
PRODUCT_README = REPO_ROOT / "software" / "product_alpha" / "README.md"
OPTIONAL_PROTOCOL = REPO_ROOT / "software" / "product_alpha" / "PILOT.md"
LEGACY_REPORT = REPO_ROOT / "reports" / "product-alpha-0-1-pilot-summary.md"
REVIEW_JSON = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.json"
REVIEW_MD = REPO_ROOT / "reports" / "product-alpha-0-1-multi-perspective-review.md"

ACTIVE_DOCUMENTS = (PRODUCT_STATE, ROOT_README, PRODUCT_README, REVIEW_MD)
FORBIDDEN_ACTIVE_GATES = (
    "5–8 real learner",
    "5-8 real learner",
    "run and complete the learner pilot",
    "until real cohort evidence exists",
    "real cohort execution and human review",
)


class ProductAlphaStateAuthorityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.review = json.loads(REVIEW_JSON.read_text(encoding="utf-8"))
        self.active = {path: path.read_text(encoding="utf-8") for path in ACTIVE_DOCUMENTS}
        self.optional_protocol = OPTIONAL_PROTOCOL.read_text(encoding="utf-8")
        self.legacy_report = LEGACY_REPORT.read_text(encoding="utf-8")

    def test_current_authority_is_internal_multi_perspective_review(self) -> None:
        product_state = self.active[PRODUCT_STATE]
        self.assertIn("last_reviewed: 2026-08-03", product_state)
        self.assertIn("internal multi-perspective review", product_state.lower())
        self.assertIn("advance-to-next-product-planning-review", product_state)
        self.assertEqual(
            self.review["decision"]["action"],
            "advance-to-next-product-planning-review",
        )
        self.assertEqual(len(self.review["perspectives"]), 8)

    def test_active_documents_remove_external_observation_as_gate(self) -> None:
        for path, text in self.active.items():
            lowered = text.lower()
            with self.subTest(path=path):
                for forbidden in FORBIDDEN_ACTIVE_GATES:
                    self.assertNotIn(forbidden.lower(), lowered)
                self.assertIn("empirical learning effectiveness", lowered)
                self.assertIn("product-market fit", lowered)

    def test_validator_command_is_visible(self) -> None:
        command = "software/product_alpha/evaluation/validate_internal_review.py check"
        for path in (PRODUCT_STATE, ROOT_README, PRODUCT_README, REVIEW_MD):
            with self.subTest(path=path):
                self.assertIn(command, self.active[path])

    def test_optional_protocol_is_not_authority(self) -> None:
        lowered = self.optional_protocol.lower()
        self.assertIn("optional research capability", lowered)
        self.assertIn("not a roadmap gate", lowered)
        self.assertIn("no minimum participant count", lowered)
        self.assertIn("does not authorize", lowered)
        self.assertIn("outside the repository", lowered)

    def test_legacy_report_is_superseded(self) -> None:
        lowered = self.legacy_report.lower()
        self.assertIn("status: superseded", lowered)
        self.assertIn("no longer required for roadmap progress", lowered)
        self.assertIn("advance-to-next-product-planning-review", lowered)
        self.assertIn("## completion criteria", lowered)

    def test_review_preserves_claim_boundaries_and_residual_risks(self) -> None:
        non_claims = {
            item.lower()
            for item in self.review["claim_boundary"]["does_not_establish"]
        }
        for required in (
            "empirical learning effectiveness",
            "retention",
            "transfer",
            "product-market fit",
            "public production readiness",
        ):
            self.assertIn(required, non_claims)
        for perspective in self.review["perspectives"]:
            self.assertTrue(perspective["residual_risk"])
            self.assertTrue(perspective["next_action"])
            self.assertGreaterEqual(len(perspective["evidence"]), 2)

    def test_obsolete_manual_flow_is_not_reintroduced(self) -> None:
        for text in (*self.active.values(), self.optional_protocol, self.legacy_report):
            self.assertNotIn("run_pilot.py --open", text)
            self.assertNotIn("verify_cohort.py \\\n  --input", text)
            self.assertNotIn("prepare_review.py \\\n  --input", text)


if __name__ == "__main__":
    unittest.main()
""", encoding="utf-8")
