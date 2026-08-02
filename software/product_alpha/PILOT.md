---
title: "Product Alpha 0.1 learner pilot"
slug: product-alpha-0-1-learner-pilot
domain: experience
experience_type: pilot-protocol
status: draft
artifact_revision: 7
release_status: draft
prerequisites: [system-dossier-refrigerator]
connections: [investigation-room-cooling, design-challenge-passive-cooler]
last_reviewed: 2026-08-02
content_license: CC-BY-4.0
---

# Product Alpha 0.1 learner pilot

This protocol tests whether the refrigerator route helps a learner explain a system, reason with a bounded model, distinguish normal cycling from failure, use evidence cautiously, and propose a defensible redesign.

The pilot is an evidence-gathering activity, not a release gate and not a test of the learner. Record product problems rather than blaming participants.

## Cohort and session

- Start with 5–8 learners who have not contributed to the route.
- Run one learner per session where possible.
- Reserve 25–35 minutes.
- Use the same route build and facilitator prompts for every session.
- Do not collect names, email addresses, school details, birth dates, usernames, or other identifying information.
- Use a unique anonymous session label such as `anonymous-001`.

## Materials

1. Prepare a new private cohort workspace outside the repository:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

2. Do not begin any participant session unless preparation reports `pilot-preparation-passed`.
3. Start Product Alpha through the prepared workspace:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

4. Do not proceed unless the launcher reports that the current deterministic build exactly matches `workspace.json`.
5. Keep the learner route, build-bound recorder, and build-bound Pilot Lab available in separate tabs.
6. Keep this protocol visible separately from the product interfaces.
7. Export one anonymous JSONL record from the recorder after each session.
8. Review the free-text notes for anonymity before placing each export in `incoming-sessions/`.
9. Keep the entire workspace private and facilitator-controlled.
10. Do not modify appliances or ask learners to perform physical repair work.

Preparation performs the deterministic build check, packages a fresh temporary build, starts the exact product on an OS-selected `127.0.0.1` port, verifies the learner page, recorder, Pilot Lab, route payload, exact build manifest, and required no-store/security headers, then creates an empty workspace bound to the verified Pilot build ID. The long-running workspace launcher rebuilds Product Alpha and refuses to open a server if its build ID differs from that workspace. None of these tools uploads records, uses browser storage, creates accounts, or calls Atlas.

## Pilot build identity

The launcher derives the Pilot build ID from the exact bytes of the deterministic `build-manifest.json`. The ID binds the packaged learner route, recorder, Pilot Lab, evaluation assets, route payload, and their hashes.

Use one prepared workspace and one Pilot build ID for every session in a cohort. A lower-level ephemeral loopback smoke check remains available as:

```bash
python3 software/product_alpha/run_pilot.py smoke
```

A file-only deterministic check remains available as:

```bash
python3 software/product_alpha/run_pilot.py check
```

The supported real-cohort path is `prepare_pilot.py` followed by `launch_workspace.py`. If the current build changes, the workspace launcher fails closed. Start a separate workspace and cohort rather than combining records from different builds.

A preparation or smoke pass establishes only that the packaged local product path is internally consistent and reachable. Exact workspace/build agreement establishes build consistency only. Neither establishes learning effectiveness, publication readiness, or permission to add another route.

## Facilitator protocol

### 1. Opening

Say:

> This is a prototype of a learning experience. I am testing the product, not you. Please say what you expect, what confuses you, and what evidence changes your mind.

Do not teach the answer before the learner attempts each step.

### 2. Observe

Ask the learner to predict why a refrigerator switches on and off rather than running continuously.

Record whether the learner distinguishes controlled cycling from random behavior. Do not score prior knowledge; score the explanation after the route presents the relevant mechanism.

### 3. Map

Ask the learner to identify the system boundary, one important store, and at least two flows.

Watch for boundary confusion, especially treating electricity as the thing being cooled or treating “cold” as a substance entering the cabinet.

### 4. Model

Ask the learner to change one model control, predict the direction of the temperature response, and then explain the result.

Record whether the learner treats the model as a reasoning aid or as a guaranteed description of every refrigerator.

### 5. Diagnose

Present the short-cycling challenge without giving hints. Ask what observation would distinguish normal hysteresis from an abnormal condition.

Record the selected answer, the mechanism stated, and any confusion between oscillation, instability, and operational failure.

### 6. Evidence boundary

Open the Atlas evidence panel and ask:

> What does this exact revision support, and what does it not prove about a physical refrigerator?

Record whether the learner notices revision, review status, limitations, and the difference between a model-derived claim and a real-system conclusion.

### 7. Redesign

Ask the learner to choose one redesign under a stated constraint and explain both its benefit and trade-off.

Do not reward a list of features without a mechanism or trade-off.

### 8. Close

Ask:

> Would you voluntarily continue to another system route now?

Record `true`, `false`, or `null` when unanswered. Then ask what single change would most improve the route.

## Scoring rubric

Use `evaluation/rubric.json`. Each learning measure is scored from 0–2:

- `0`: missing, contradicted, or copied without explanation;
- `1`: partly correct but incomplete, fragile, or poorly bounded;
- `2`: mechanistic, appropriately bounded, and transferable.

Score the learner's final explanation for each measure. Use confusion tags to capture interface or concept problems that a numeric score would hide.

## Session record

Use the build-bound `facilitator.html` URL printed by the workspace launcher to record the ordered route prefix, duration, five rubric scores, confusion tags, voluntary continuation, and anonymous product observations. The recorder prevents export until its local validation passes and applies basic checks for common identity or contact-information patterns.

The recorder is a convenience boundary, not a guarantee that free-text notes are anonymous. The facilitator remains responsible for reviewing notes before export. Every session label must begin with `anonymous-` and must be unique within the cohort.

Suggested confusion tags:

- `navigation`
- `reading-density`
- `system-boundary`
- `energy-versus-cold`
- `model-controls`
- `model-to-world-transfer`
- `cycling-versus-failure`
- `oscillation-versus-instability`
- `evidence-status`
- `revision-meaning`
- `redesign-tradeoff`

Add a new tag only when the existing set cannot describe the observation.

## Cohort preview with Pilot Lab

1. Open the build-bound Pilot Lab URL printed by the workspace launcher.
2. Select or drop the exported JSONL files.
3. Review rejected records and duplicate session labels.
4. Confirm that every session belongs to the same workspace-bound Pilot build ID.
5. Confirm that at least five valid unique sessions are present before treating the cohort as complete.
6. Review the aggregate metrics and every revision signal.
7. Export aggregate Markdown or JSON only when useful for private comparison.
8. Keep any combined JSONL export private; it still contains raw anonymous session records and facilitator notes.
9. Refresh the page after the preview to clear the in-memory workspace.

The Pilot Lab aggregate intentionally omits facilitator notes. It is a browser-local preview and does not edit the repository or create the authoritative command-line evidence chain.

## Deterministic workspace intake

After all facilitator-reviewed exports are present in `incoming-sessions/`, assemble the immutable cohort intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

The command independently validates every raw export, exact route and build identity, anonymous labels, score ranges, route order, personal-data fields, duplicate session IDs, and workspace privacy boundaries. It sorts accepted records by anonymous session ID and writes:

```text
verified/anonymous-sessions.jsonl
verified/intake-manifest.json
```

The intake manifest hashes every raw source and the exact combined JSONL. Raw exports are not modified, and verified outputs are never overwritten.

## Workspace-bound review packet

Check the entire evidence chain without writing review files:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

The command rescans every raw export and verifies the intake-manifest hash, source-record hash set, combined JSONL hash, session count, summary contract, evidence status, route, build, and privacy boundaries. It rejects post-intake changes.

Create the immutable private review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

The command writes `review/refrigerator-review.json` and `review/refrigerator-review.md`. The packet contains the de-identified aggregate, revision signals, allowed actions, and evidence hashes. It excludes raw session records, facilitator notes, and custom confusion-tag text. It refuses repository output and overwrite.

Do not edit either review file. Review the generated aggregate together with the separate private facilitator notes.

## Human decision record

Verify that the review JSON/Markdown pair remains untouched and still matches the complete workspace evidence chain:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \
  --workspace /private/path/refrigerator-cohort
```

Record exactly one human-supplied primary action:

```bash
python3 software/product_alpha/evaluation/record_decision.py \
  --workspace /private/path/refrigerator-cohort \
  --action <allowed-primary-action> \
  --reviewer "<role-or-initials>" \
  --review-date YYYY-MM-DD \
  --rationale "<de-identified rationale>" \
  --next-checkpoint "<next checkpoint>"
```

Allowed actions are:

- `revise-current-route`;
- `repeat-current-route-pilot`;
- `hold-current-route`;
- `advance-to-next-product-planning-review`.

The fourth action is rejected unless the cohort status is `ready-for-human-review`. The command writes `review/refrigerator-review-decision.json` and `review/refrigerator-review-decision.md`, binds them to the untouched review packet and workspace evidence hashes, refuses overwrite, and does not modify the repository.

Keep participant identities out of reviewer, rationale, and checkpoint text. A reviewer role or initials are sufficient. Selecting the fourth action records only the human choice to proceed toward a separate planning review. It does not create that review or authorize a second route.

## Decision rule

Do not add a second route merely because the interface runs without errors, because preparation succeeds, or because the five-session minimum is reached. Review the evidence first and record one primary action.

Prioritize revision when:

- the same confusion tag appears in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate controls without being able to predict direction;
- learners repeatedly treat Atlas status as proof that a physical conclusion is true;
- learners finish but do not voluntarily continue.

A small pilot cannot establish general learning effectiveness. It can reveal obvious interaction failures, recurring misconceptions, and whether the product deserves a larger evaluation. The Pilot Lab and command-line summary surface descriptive signals; a human reviewer still chooses the product action. Neither the review packet nor the decision record automatically modifies the repository, creates a planning review, authorizes public release, establishes product-market fit, permits a learning-effectiveness claim, or authorizes a second route.
