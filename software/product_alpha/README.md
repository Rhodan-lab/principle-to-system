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

Then launch the long-running product through the prepared workspace:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

The workspace launcher rebuilds Product Alpha and refuses to open a server unless the current deterministic build exactly matches the Pilot build ID recorded in `workspace.json`. Only after that binding succeeds does it serve the learner route, recorder, and Pilot Lab on `127.0.0.1`. Every recorder export carries that ID. The launcher stores no session data and does not modify the workspace. Use `Ctrl+C` to stop it.

Useful lower-level options:

```bash
# Verify the workspace/build binding without opening a server
python3 software/product_alpha/launch_workspace.py check \
  --workspace /private/path/refrigerator-cohort

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

A bare `python3 -m http.server` launch does not create the supported build-bound recorder and Pilot Lab URLs or enforce the workspace/build binding. It may be used to inspect static output, but it must not be used to collect pilot evidence. Use the supported preparation and workspace-launch commands for every real learner session.

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

The three evidence directories begin empty. The workspace manifest uses contract `principia-product-alpha-pilot-workspace/0.1` and records the exact Pilot build ID, route ID, intended combined JSONL path, intake-manifest path, review-packet prefix, and privacy boundaries. The generated README contains build-bound launch, intake, verification, review, and human-decision commands with shell-safe paths.

Do not treat the workspace, empty directories, intake manifest, review packet, decision record, or workspace manifest as learner evidence. Do not place participant names, contact details, school details, account identifiers, or other identifying information in the workspace.

## Deterministic workspace intake

After each facilitator-reviewed recorder export has been placed in `incoming-sessions/`, assemble the private cohort without manually editing JSONL:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

The command accepts individual `.jsonl` or `.json` exports containing one session object each. It validates the existing Product Alpha session contract, workspace route, exact build ID, and privacy boundaries; rejects personal-data fields, malformed records, duplicate anonymous session IDs, symlinks, unsupported files, and mixed-build evidence; then sorts accepted sessions by anonymous session ID and writes:

```text
verified/anonymous-sessions.jsonl
verified/intake-manifest.json
```

The intake manifest records SHA-256 hashes for every raw export and the exact combined JSONL. The command does not rename, move, or modify raw source files, and it refuses to overwrite either verified output. Validation completes before any output is written, so invalid intake leaves the verified directory unchanged. The reported cohort status is descriptive only; human review remains required.

## Workspace-bound review

Before creating review files, verify that the private evidence still matches the earlier intake:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

The command independently checks:

- the repository-external workspace and strict privacy boundaries;
- the exact route and Pilot build ID;
- every raw incoming export against its recorded SHA-256;
- the intake-manifest contract and SHA-256;
- the combined JSONL path and SHA-256;
- session count, summary contract, and evidence status.

It fails before writing review outputs if a raw export, the combined cohort, or the intake metadata changed after assembly.

Create the private, de-identified human-review packet with the same workspace binding:

```bash
python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

The command writes `review/refrigerator-review.json` and `review/refrigerator-review.md`. The packet embeds the verified aggregate summary and binds it to the exact private combined input, intake manifest, and source-record hash set. It excludes raw session records, facilitator notes, and custom confusion-tag text; leaves the product decision pending for a human reviewer; refuses repository output; and refuses to overwrite an existing packet.

`verify_cohort.py` and `prepare_review.py` remain lower-level tools. The workspace-bound command is the supported review path because it proves the packet still matches the earlier intake and unchanged raw exports.

## Immutable human decision record

Do not complete or edit the generated review packet. First verify that its JSON and Markdown files remain the untouched generated pair and still match the workspace evidence:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \
  --workspace /private/path/refrigerator-cohort
```

After reviewing the aggregate together with the private facilitator notes, record exactly one primary action:

```bash
python3 software/product_alpha/evaluation/record_decision.py \
  --workspace /private/path/refrigerator-cohort \
  --action revise-current-route \
  --reviewer "facilitator-reviewer" \
  --review-date YYYY-MM-DD \
  --rationale "De-identified rationale for the selected action." \
  --next-checkpoint "The next bounded product checkpoint."
```

Allowed primary actions are:

- `revise-current-route`;
- `repeat-current-route-pilot`;
- `hold-current-route`;
- `advance-to-next-product-planning-review`.

The recorder rejects the fourth action unless the cohort reached `ready-for-human-review`. It writes `review/refrigerator-review-decision.json` and `review/refrigerator-review-decision.md`, binding the human-supplied action, reviewer label, date, rationale, and checkpoint to the untouched review JSON/Markdown hashes and the verified intake, combined cohort, and source-record hashes. It refuses to overwrite an existing decision record and does not edit the review packet or repository.

Keep participant identities out of reviewer, rationale, and checkpoint text. A role label or initials are sufficient. Selecting `advance-to-next-product-planning-review` records that human choice only; a separate planning review must still be created and reviewed. No recorded action authorizes a second route, public release, SaaS expansion, a learning-effectiveness claim, or a product-market-fit claim.

## Pilot Lab

`pilot-lab.html` runs entirely in the current browser tab and can:

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

Refreshing the tab clears the Pilot Lab workspace. Aggregate exports omit facilitator notes. The validated JSONL export still contains raw anonymous records and must remain private. The command-line workspace intake, review, and decision path remains the authoritative private evidence chain.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 software/product_alpha/run_pilot.py check
python3 software/product_alpha/run_pilot.py smoke
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

The validation checks deterministic output, canonical-source extraction, five-step route completeness, exact-revision Atlas references, absence of external runtime dependencies, anonymous record boundaries, duplicate rejection, route-order integrity, workspace/build binding, expected-build verification, evidence-status logic, revision signals, review-packet hashing and de-identification, repository-output refusal, private-workspace creation, deterministic workspace intake and source hashing, post-intake tamper rejection, untouched review-pair verification, immutable decision recording, incomplete-cohort planning-advance rejection, decision-output overwrite refusal, smoke-before-workspace ordering, Pilot Lab packaging, loopback-only serving, served resource markers, manifest identity, and no-store/security headers.

## Learner pilot

Use [`PILOT.md`](PILOT.md) with 5–8 real learners who did not author or review the route. The protocol defines the session procedure, 0–2 rubric, anonymous records, recommended confusion tags, evidence-based revision thresholds, and final human-decision step.

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
- private workspaces, review packets, and decision records must remain outside the repository until a separate human-reviewed product change is prepared;
- the launchers and smoke gate bind only to `127.0.0.1` and store no session data;
- the preparation command creates no placeholder evidence;
- workspace intake preserves raw exports and refuses verified-output overwrite;
- workspace review rejects changed raw exports, changed combined evidence, and relaxed human-review boundaries;
- human-decision recording rejects edited review packets, incomplete-cohort planning advance, and output overwrite;
- the thermal model supports reasoning and is not repair or safety guidance;
- aggregate evidence remains descriptive and every product action remains human-supplied.
