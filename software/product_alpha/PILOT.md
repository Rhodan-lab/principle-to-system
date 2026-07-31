# Product Alpha 0.1 learner pilot

This protocol tests whether the refrigerator route helps a learner explain a system, reason with a bounded model, distinguish normal cycling from failure, use evidence cautiously, and propose a defensible redesign.

The pilot is an evidence-gathering activity, not a release gate and not a test of the learner. Record product problems rather than blaming participants.

## Cohort and session

- Start with 5–8 learners who have not contributed to the route.
- Run one learner per session where possible.
- Reserve 25–35 minutes.
- Use the same route build and facilitator prompts for every session.
- Do not collect names, email addresses, school details, birth dates, usernames, or other identifying information.
- Assign an anonymous session label such as `anonymous-001`.

## Materials

1. Build and serve Product Alpha locally.
2. Copy `evaluation/session-template.json` once per learner into a private local JSONL file.
3. Keep the facilitator protocol visible separately from the learner interface.
4. Do not modify appliances or ask learners to perform physical repair work.

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

Store one compact JSON object per line. Begin from `evaluation/session-template.json` and keep records anonymous.

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

## Summarize

```bash
python3 software/product_alpha/evaluation/summarize.py \
  --input path/to/anonymous-sessions.jsonl \
  --format markdown
```

The summarizer validates route order, score ranges, anonymous-data boundaries, and produces completion, duration, score, confusion, and voluntary-continuation summaries.

## Decision rule

Do not add a second route merely because the first route runs without errors. Review the pilot evidence first.

Prioritize revision when:

- the same confusion tag appears in at least two sessions;
- fewer than half of started sessions reach redesign;
- average mechanism, diagnosis, or evidence-boundary score is below 1.25;
- learners manipulate controls without being able to predict direction;
- learners repeatedly treat Atlas status as proof that a physical conclusion is true;
- learners finish but do not voluntarily continue.

A small pilot cannot establish general learning effectiveness. It can reveal obvious interaction failures, recurring misconceptions, and whether the product deserves a larger evaluation.