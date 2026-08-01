---
title: "Product Alpha 0.1 learner pilot"
slug: product-alpha-0-1-learner-pilot
domain: experience
experience_type: pilot-protocol
status: draft
artifact_revision: 5
release_status: draft
prerequisites: [system-dossier-refrigerator]
connections: [investigation-room-cooling, design-challenge-passive-cooler]
last_reviewed: 2026-08-01
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

1. Run the pilot-day gate with `python3 software/product_alpha/run_pilot.py smoke`.
2. Do not begin any participant session unless the smoke command reports `pilot smoke passed`.
3. Record the full 64-character Pilot build ID printed by the smoke command in the private cohort folder.
4. Start Product Alpha with `python3 software/product_alpha/run_pilot.py --open`.
5. Confirm that the long-running launcher prints the same Pilot build ID recorded from the smoke command.
6. Keep the learner route, build-bound recorder, and build-bound Pilot Lab available in separate tabs.
7. Keep this protocol visible separately from the product interfaces.
8. Export one anonymous JSONL record from the recorder after each session.
9. Store exported records in a private local folder controlled by the facilitator.
10. Do not modify appliances or ask learners to perform physical repair work.

The smoke command starts an ephemeral loopback server, verifies the packaged learner page, recorder, Pilot Lab, route payload, exact manifest, and required no-store/security headers, then shuts down. The long-running recorder performs browser-side contract checks and downloads one compact JSON object. The Pilot Lab reads selected files locally, rejects malformed or duplicate records, and produces aggregate previews. None of these tools uploads records, uses browser storage, creates accounts, or calls Atlas.

## Pilot build identity

The launcher derives the Pilot build ID from the exact bytes of the deterministic `build-manifest.json`. The ID binds the packaged learner route, recorder, Pilot Lab, evaluation assets, route payload, and their hashes.

Use one Pilot build ID for every session in a cohort. Before the first session, run:

```bash
python3 software/product_alpha/run_pilot.py smoke
```

The smoke gate performs the deterministic build check and verifies the actual loopback HTTP path. A lower-level file-only check remains available as:

```bash
python3 software/product_alpha/run_pilot.py check
```

Keep the full smoke build ID with the private local cohort records. Confirm that the long-running launcher prints the same ID before every session. If the ID changes, do not combine the new sessions with the earlier cohort; start a separate cohort or explicitly repeat the earlier sessions on the new build.

A smoke pass establishes only that the packaged local product path is internally consistent and reachable. Matching build IDs establish build consistency only. Neither establishes learning effectiveness, publication readiness, or permission to add another route.

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

Use the build-bound `facilitator.html` URL printed by the launcher to record the ordered route prefix, duration, five rubric scores, confusion tags, voluntary continuation, and anonymous product observations. The recorder prevents export until its local validation passes and applies basic checks for common identity or contact-information patterns.

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

## Cohort review with Pilot Lab

1. Open the build-bound Pilot Lab URL printed by the loopback launcher.
2. Select or drop the exported JSONL files.
3. Review rejected records and duplicate session labels.
4. Confirm that every session belongs to the same recorded Pilot build ID.
5. Confirm that at least five valid unique sessions are present before treating the cohort as complete.
6. Review the aggregate metrics and every revision signal.
7. Export the aggregate Markdown or JSON for de-identified review.
8. Keep the validated combined JSONL export private; it still contains raw anonymous session records and facilitator notes.
9. Refresh the page after the review to clear the in-memory workspace.

The Pilot Lab aggregate intentionally omits facilitator notes. It does not edit the repository or update the official report automatically.

## Independent command-line verification

Combine the exported JSONL lines into one local file, one compact JSON object per line, then verify the cohort against the independently recorded smoke/launcher build ID:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --format markdown
```

The verifier independently validates route order, score ranges, anonymous labels, personal-data fields, duplicate session IDs, mixed-build rejection, and exact agreement with the expected launcher build. It then produces completion, duration, score, confusion, continuation, evidence-status, and revision-signal summaries.

`evaluation/summarize.py` remains the lower-level uniform-cohort summarizer. It does not compare a cohort with an independently recorded launcher ID and is not the supported final verification command.

## Decision rule

Do not add a second route merely because the interface runs without errors, because the smoke gate passes, or because the five-session minimum is reached. Review the evidence first.

Prioritize revision when:

- the same confusion tag appears in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate controls without being able to predict direction;
- learners repeatedly treat Atlas status as proof that a physical conclusion is true;
- learners finish but do not voluntarily continue.

A small pilot cannot establish general learning effectiveness. It can reveal obvious interaction failures, recurring misconceptions, and whether the product deserves a larger evaluation. The Pilot Lab surfaces these triggers; a human reviewer still chooses the product action.
