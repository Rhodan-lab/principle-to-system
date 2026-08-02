---
title: "Product Alpha 0.1 learner pilot"
slug: product-alpha-0-1-learner-pilot
domain: experience
experience_type: pilot-protocol
status: draft
artifact_revision: 8
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
- Use one exact prepared route build and the same facilitator prompts for every session.
- Do not collect names, email addresses, school details, birth dates, usernames, or other identifying information.
- Use a unique anonymous session label such as `anonymous-001`.

## Materials and preparation

1. Prepare a new private cohort workspace outside the repository:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

2. Do not begin participant sessions unless preparation reports `pilot-preparation-passed`.
3. Start Product Alpha through the prepared workspace:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

4. Do not proceed unless the launcher reports that the deterministic build exactly matches `workspace.json`.
5. Keep the learner route, build-bound recorder, and build-bound Pilot Lab available in separate tabs.
6. Keep this protocol visible separately from the product interfaces.
7. Export one anonymous JSONL record from the recorder after each session.
8. Review free-text notes for anonymity before placing each export in `incoming-sessions/`.
9. Keep the entire workspace private and facilitator-controlled.
10. Do not modify appliances or ask learners to perform physical repair work.

Preparation builds and smokes the exact product on `127.0.0.1`, verifies the learner page, recorder, Pilot Lab, route payload, build manifest, no-store headers, and security headers, and only then creates an empty workspace bound to the verified Pilot build ID. The long-running launcher rebuilds Product Alpha and fails closed if that build differs. These tools do not upload records, use browser persistence, create accounts, or call Atlas.

## Pilot build identity

The Pilot build ID is the SHA-256 of the exact deterministic `build-manifest.json` bytes. It binds the learner route, recorder, Pilot Lab, evaluation assets, route payload, and file hashes.

Use one workspace and one build ID for the complete cohort. When the product changes, start a new workspace rather than combining records from different builds.

Lower-level checks remain available:

```bash
python3 software/product_alpha/run_pilot.py check
python3 software/product_alpha/run_pilot.py smoke
python3 software/product_alpha/launch_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

A successful smoke or binding check establishes technical consistency only. It does not establish learning effectiveness, publication readiness, or permission to add another route.

## Current-stage check

At any point, verify the strongest completed workspace stage and the next valid action without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/refrigerator-cohort
```

The status command recognizes:

```text
prepared
→ collecting
→ ready-to-assemble
→ intake-verified
→ review-ready-for-decision
→ decision-verified
→ handoff-verified
```

It rejects partial or out-of-order intake, review, decision, and handoff artifacts.

## Facilitator protocol

### 1. Opening

Say:

> This is a prototype of a learning experience. I am testing the product, not you. Please say what you expect, what confuses you, and what evidence changes your mind.

Do not teach the answer before the learner attempts each step.

### 2. Observe

Ask why a refrigerator switches on and off rather than running continuously.

Record whether the learner distinguishes controlled cycling from random behavior. Score the explanation after the route presents the relevant mechanism, not prior knowledge.

### 3. Map

Ask the learner to identify the system boundary, one important store, and at least two flows.

Watch for treating electricity as the thing being cooled or “cold” as a substance entering the cabinet.

### 4. Model

Ask the learner to change one model control, predict the direction of the temperature response, and then explain the result.

Record whether the learner treats the model as a reasoning aid rather than a guaranteed description of every refrigerator.

### 5. Diagnose

Present the short-cycling challenge without hints. Ask what observation would distinguish normal hysteresis from an abnormal condition.

Record the selected answer, stated mechanism, and confusion between oscillation, instability, and operational failure.

### 6. Evidence boundary

Open the Atlas evidence panel and ask:

> What does this exact revision support, and what does it not prove about a physical refrigerator?

Record whether the learner notices revision, review status, limitations, and the difference between a model-derived claim and a real-system conclusion.

### 7. Redesign

Ask the learner to choose one redesign under a stated constraint and explain both its benefit and trade-off.

Do not reward a feature list without a mechanism or trade-off.

### 8. Close

Ask:

> Would you voluntarily continue to another system route now?

Record `true`, `false`, or `null` when unanswered. Then ask what single change would most improve the route.

## Scoring rubric

Use `evaluation/rubric.json`. Each learning measure is scored from 0–2:

- `0`: missing, contradicted, or copied without explanation;
- `1`: partly correct but incomplete, fragile, or poorly bounded;
- `2`: mechanistic, appropriately bounded, and transferable.

Score the learner’s final explanation for each measure. Use confusion tags for interface or concept problems that numeric scores hide.

## Session record

Use the build-bound `facilitator.html` URL printed by the launcher to record the ordered route prefix, duration, five rubric scores, confusion tags, voluntary continuation, and anonymous product observations.

The recorder validates locally, blocks common identifying patterns, and locks the record after the first successful JSONL download or clipboard capture. Start the next session through the explicit next-session control, which generates a fresh anonymous label.

The recorder is a convenience boundary, not a guarantee that free text is anonymous. Review notes before export. Every label must begin with `anonymous-` and be unique within the cohort.

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

Add a custom tag only when the existing set cannot describe the observation. Custom text remains private and is collapsed to `other-custom-tag` in de-identified review and handoff outputs.

## Cohort preview with Pilot Lab

1. Open the build-bound Pilot Lab URL printed by the launcher.
2. Add exported JSONL files; additive loading preserves earlier batches.
3. Use explicit replace only when intentionally starting over.
4. Review rejected records, repeated files, and duplicate session labels.
5. Confirm that every session belongs to the same workspace-bound build ID.
6. Confirm that at least five valid unique sessions are present before treating the cohort as complete.
7. Review aggregate metrics and revision signals.
8. Keep combined JSONL exports private; they still contain raw anonymous records and facilitator notes.
9. Refresh after preview to clear the in-memory workspace.

Pilot Lab is a browser-local preview. It does not edit the repository or create the authoritative command-line evidence chain.

## Collection preflight

After every reviewed export is placed in `incoming-sessions/`, validate the current collection without sealing it:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

The command validates all current raw sources, route and build identity, labels, score ranges, route order, personal-data fields, file types, symlinks, and duplicates. It predicts the exact combined and source-record hashes, reports session count and evidence status, and writes nothing. Repeat it after each new session.

## Immutable workspace intake

After collection is deliberately closed and at least five valid sessions are present:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

Normal assembly blocks an incomplete cohort before writing. When recruitment or execution intentionally stops early, close it explicitly:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --allow-incomplete
```

The override does not make the cohort complete or planning-review eligible.

Assembly writes exclusively:

```text
verified/anonymous-sessions.jsonl
verified/intake-manifest.json
```

The manifest binds every source hash, the source-record-set hash, the exact combined JSONL, route, build, session count, and evidence status. Raw exports are not modified and verified outputs are never overwritten.

## Workspace-bound review packet

Check the complete evidence chain without writing review files:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

The command rescans every raw export and verifies intake, source-record, combined JSONL, summary, route, build, and privacy bindings.

Create the private de-identified review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

It writes:

```text
review/refrigerator-review.json
review/refrigerator-review.md
```

The packet contains the de-identified aggregate, revision signals, allowed actions, and evidence hashes. It excludes raw sessions, facilitator notes, and custom confusion-tag text. It refuses repository output and overwrite.

Do not edit either review file. Review the generated aggregate together with the separate private facilitator notes.

## Sealed human decision

Verify review readiness:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \
  --workspace /private/path/refrigerator-cohort
```

Record exactly one human-supplied action:

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

The fourth action requires `ready-for-human-review`. Recording creates:

```text
review/refrigerator-review-decision.json
review/refrigerator-review-decision.md
review/refrigerator-review-decision-receipt.json
```

The receipt seals both decision-file hashes and every earlier evidence binding. Recording refuses overwrite and does not modify the repository.

Verify the finished decision artifact trio and current evidence chain without writing:

```bash
python3 software/product_alpha/evaluation/record_decision.py verify \
  --workspace /private/path/refrigerator-cohort
```

The receipt is local tamper evidence, not a signature, trusted timestamp, notarization, or proof of authorship.

Keep participant identities out of reviewer, rationale, and checkpoint text. Selecting the fourth action records only a human choice to begin a separate planning review; it does not create or authorize another route.

## De-identified repository handoff

After decision verification, check the candidate without writing:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py check \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

Create the private candidate pair:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

Verify the pair against the unchanged decision and evidence chain:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py verify \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

The candidate includes an allowlisted de-identified aggregate, revision signals, verified human action, and evidence hashes. It excludes raw sessions, session IDs, facilitator notes, custom confusion text, reviewer identity, review date, private rationale, checkpoint text, and local paths.

The pair remains outside the repository and does not authorize or perform a repository change. A human must inspect it and create a separate normal pull request.

## Decision rule

Do not add another route because the interface runs, preparation succeeds, five sessions exist, or a handoff candidate was generated. Review the evidence and human action first.

Prioritize revision when:

- the same confusion tag appears in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate controls without predicting direction;
- learners treat Atlas status as proof of a physical conclusion;
- learners finish but do not voluntarily continue.

A small pilot cannot establish general learning effectiveness. It can reveal interaction failures, recurring misconceptions, and whether the product deserves larger evaluation. Pilot Lab, command-line summaries, review packets, decisions, receipts, and handoff candidates remain descriptive or human-supplied. None automatically modifies the repository, authorizes public release or another route, establishes product-market fit, or permits a learning-effectiveness claim.
