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

## Prepare and run the pilot

Before the first participant session for a cohort, run the integrated pilot preparation command with a new private destination outside the repository:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

This command performs the deterministic build check, packages a fresh temporary build, starts the exact product on an OS-selected `127.0.0.1` port, and fetches the learner page, build-bound recorder, build-bound Pilot Lab, route payload, and exact build manifest. It verifies the no-store and security response headers and confirms that the served manifest bytes match the 64-character Pilot build ID. Only after that smoke gate passes does it create the empty private cohort workspace bound to the same ID.

A successful command reports:

```text
pilot-preparation-passed
```

It stores no session data and creates no placeholder evidence. If smoke verification fails, no workspace is created. If the destination is inside the repository or already exists, preparation fails without overwriting it.

Then start the long-running loopback-only launcher:

```bash
python3 software/product_alpha/run_pilot.py --open
```

Confirm that the launcher prints the same Pilot build ID recorded in the new workspace. The launcher builds Product Alpha, binds only to `127.0.0.1`, and opens build-bound learner, recorder, and Pilot Lab URLs. Every recorder export carries that ID. The Pilot Lab rejects records from another build. The launcher stores no session data. Use `Ctrl+C` to stop it.

Useful lower-level options:

```bash
# Select any available local port for the long-running pilot
python3 software/product_alpha/run_pilot.py --port 0 --open

# Verify deterministic files and build identity without exercising HTTP
python3 software/product_alpha/run_pilot.py check

# Exercise the complete ephemeral loopback HTTP path without creating a workspace
python3 software/product_alpha/run_pilot.py smoke

# Create an empty workspace from an already recorded build ID
python3 software/product_alpha/evaluation/prepare_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --expect-build-id <64-character-pilot-build-id>
```

### Static inspection only

A bare `python3 -m http.server` launch does not create the supported build-bound recorder and Pilot Lab URLs or the pilot smoke guarantees. It may be used to inspect static output, but it must not be used to collect pilot evidence. Use the supported preparation and launcher commands for every real learner session.

## Private cohort workspace

The integrated preparation command creates:

```text
refrigerator-cohort/
├── README.md
├── workspace.json
├── incoming-sessions/
├── verified/
└── review/
```

The three evidence directories begin empty. The workspace manifest uses contract `principia-product-alpha-pilot-workspace/0.1` and records the exact Pilot build ID, route ID, intended combined JSONL path, review-packet prefix, and privacy boundaries. The generated README contains build-bound verification and review commands with shell-safe paths.

Do not treat the workspace, empty directories, or manifest as learner evidence. Do not place participant names, contact details, school details, account identifiers, or other identifying information in the workspace.

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

Use the full Pilot build ID recorded in `workspace.json` and printed by `run_pilot.py` to independently verify the combined cohort before producing a command-line report:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --format markdown
```

The command rejects malformed expected IDs, mixed-build records, and a uniform cohort whose embedded ID does not match the recorded launcher build. On success it emits the existing deterministic `principia-product-alpha-pilot-summary/0.3` report.

`evaluation/summarize.py` remains the lower-level uniform-cohort summarizer. It validates embedded session IDs and rejects mixed builds, but it does not compare them with an independently recorded launcher ID. Use `verify_cohort.py` for the supported pilot verification path.

## Human-review packet

After command-line verification, create the de-identified decision packet in the private facilitator-controlled cohort folder:

```bash
python3 software/product_alpha/evaluation/prepare_review.py \
  --input path/to/anonymous-sessions.jsonl \
  --expect-build-id <64-character-pilot-build-id> \
  --output-prefix /private/cohort-folder/refrigerator-review
```

The command writes matching `.json` and `.md` files. The packet embeds the verified aggregate summary, hashes the exact private JSONL input and canonical summary, excludes raw session records and facilitator notes, and leaves the product decision pending for a human reviewer. It refuses output paths inside the repository and refuses to overwrite an existing packet.

The Markdown worksheet permits one bounded primary action:

- revise the current route;
- repeat the current-route pilot;
- hold the current route;
- advance to a separate next-product planning review.

Advancing to planning review does not itself authorize a second route. A tool-generated status or completed worksheet never authorizes public release, SaaS expansion, a learning-effectiveness claim, or product-market-fit claim.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 software/product_alpha/run_pilot.py check
python3 software/product_alpha/run_pilot.py smoke
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

The validation checks deterministic output, canonical-source extraction, five-step route completeness, exact-revision Atlas references, absence of external runtime dependencies, anonymous record boundaries, duplicate rejection, route-order integrity, build-ID binding, expected-build verification, evidence-status logic, revision signals, review-packet hashing and de-identification, repository-output refusal, private-workspace creation, smoke-before-workspace ordering, Pilot Lab packaging, loopback-only serving, served resource markers, manifest identity, and no-store/security headers.

## Learner pilot

Use [`PILOT.md`](PILOT.md) with 5–8 real learners who did not author or review the route. The protocol defines the session procedure, 0–2 rubric, anonymous records, recommended confusion tags, evidence-based revision thresholds, and the final human-review step.

## Boundaries

- no account or cloud dependency;
- no analytics;
- no external network request;
- no automatic repository mutation;
- no live Atlas call;
- no inherited Atlas or Principia status;
- learner notes remain only in the current browser tab;
- recorder and Pilot Lab state remain only in the current browser tab;
- raw pilot records remain local, anonymous, private, and facilitator-controlled;
- private workspaces and review packets must remain outside the repository until a separate human-reviewed product change is prepared;
- the launcher and smoke gate bind only to `127.0.0.1` and store no session data;
- the preparation command creates no placeholder evidence;
- the thermal model supports reasoning and is not repair or safety guidance;
- aggregate evidence remains descriptive and requires human review.
