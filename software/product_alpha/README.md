# Principia Product Alpha 0.1

This package is the first learner-facing product slice built from the existing Principia material foundation. It deliberately replaces phase-count growth with a concrete user journey and an evidence workflow that can be run locally.

## Alpha route

The first route asks a learner to understand a domestic refrigerator through five steps:

1. observe surprising behavior;
2. map system boundaries and flows;
3. manipulate a minimum thermal model;
4. diagnose normal cycling versus abnormal short-cycling;
5. redesign under constraints.

Canonical Principia Markdown remains authoritative. The build extracts required sections from the existing system dossier, failure pattern, investigation, and design challenge. The route configuration contains interaction structure, prompts, a bounded model, and pinned Atlas references; it does not duplicate the canonical learning corpus.

## Run the pilot

From the repository root, use the loopback-only launcher:

```bash
python3 software/product_alpha/run_pilot.py --open
```

The launcher builds Product Alpha, binds only to `127.0.0.1`, derives and prints the exact 64-character Pilot build ID, and opens build-bound learner, recorder, and Pilot Lab URLs. Every recorder export carries that ID. The Pilot Lab rejects records from another build. The launcher stores no session data. Use `Ctrl+C` to stop it.

Useful options:

```bash
# Select any available local port
python3 software/product_alpha/run_pilot.py --port 0 --open

# Verify the deterministic build and print its build ID without starting a server
python3 software/product_alpha/run_pilot.py check
```

### Static inspection only

A bare `python3 -m http.server` launch does not create the supported build-bound recorder and Pilot Lab URLs. It may be used to inspect static output, but it must not be used to collect pilot evidence. Use `run_pilot.py` for every real learner session.

## Pilot Lab

`pilot-lab.html` closes the operational gap between exporting individual sessions and reviewing a cohort. It runs entirely in the current browser tab and can:

- read one or many local JSONL files;
- validate every record against the Product Alpha session contract;
- require a valid `pilot_build_id` on every session;
- reject records that do not match the launcher build;
- reject mixed-build cohorts, malformed records, personal-data fields, and duplicate session labels;
- show accepted and rejected records without uploading them;
- calculate completion, duration, rubric averages, confusion counts, and voluntary continuation;
- mark cohorts below five valid sessions as incomplete;
- surface the documented revision triggers;
- export build-bound aggregate Markdown and JSON;
- export a combined validated JSONL file for private local use.

Refreshing the tab clears the Pilot Lab workspace. Aggregate exports omit facilitator notes. The validated JSONL export still contains raw anonymous records and must remain private.

## Verified command-line summary

Use the full Pilot build ID printed by `run_pilot.py` to independently verify the combined cohort before producing a command-line report:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --format markdown
```

The command rejects malformed expected IDs, mixed-build records, and a uniform cohort whose embedded ID does not match the recorded launcher build. On success it emits the existing deterministic `principia-product-alpha-pilot-summary/0.3` report.

`evaluation/summarize.py` remains the lower-level uniform-cohort summarizer. It validates embedded session IDs and rejects mixed builds, but it does not compare them with an independently recorded launcher ID. Use `verify_cohort.py` for the supported pilot verification path.

A tool-generated status never authorizes a second route, public release, SaaS expansion, or a learning-effectiveness claim.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 software/product_alpha/run_pilot.py check
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

The validation checks deterministic output, canonical-source extraction, five-step route completeness, exact-revision Atlas references, absence of external runtime dependencies, anonymous record boundaries, duplicate rejection, route-order integrity, build-ID binding, expected-build verification, evidence-status logic, revision signals, Pilot Lab packaging, and loopback-only serving.

## Learner pilot

Use [`PILOT.md`](PILOT.md) with 5–8 real learners who did not author or review the route. The protocol defines the session procedure, 0–2 rubric, anonymous records, recommended confusion tags, and evidence-based revision thresholds.

## Boundaries

- no account or cloud dependency;
- no analytics;
- no external network request;
- no repository mutation;
- no live Atlas call;
- no inherited Atlas or Principia status;
- learner notes remain only in the current browser tab;
- recorder and Pilot Lab state remain only in the current browser tab;
- raw pilot records remain local, anonymous, private, and facilitator-controlled;
- the launcher binds only to `127.0.0.1` and stores no session data;
- the thermal model supports reasoning and is not repair or safety guidance;
- aggregate evidence remains descriptive and requires human review.
