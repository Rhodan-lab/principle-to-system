# Principia Product Alpha 0.1

This package is the first learner-facing product slice built from the existing Principia material foundation. It replaces phase-count growth with a concrete refrigerator journey and a private, verifiable pilot workflow that can run locally without accounts, analytics, cloud storage, or external runtime calls.

## Alpha route

The first route asks a learner to understand a domestic refrigerator through five steps:

1. observe surprising behavior;
2. map system boundaries and flows;
3. manipulate a minimum thermal model;
4. diagnose normal cycling versus abnormal short-cycling;
5. redesign under constraints.

Canonical Principia Markdown remains authoritative. The build extracts required sections from the existing system dossier, failure pattern, investigation, and design challenge. The route configuration contains interaction structure, prompts, a bounded model, and pinned Atlas references; it does not duplicate the canonical learning corpus.

## Supported pilot path

Prepare a new private destination outside the repository before the first participant session:

```bash
python3 software/product_alpha/prepare_pilot.py \
  --workspace /private/path/refrigerator-cohort
```

Preparation performs a deterministic build check, packages a fresh temporary build, starts the exact product on an OS-selected `127.0.0.1` port, fetches the learner page, build-bound recorder, build-bound Pilot Lab, route payload, and exact build manifest, verifies no-store and security response headers, and confirms that the served manifest bytes match the 64-character Pilot build ID. The workspace is created only after that smoke gate succeeds.

A successful command reports:

```text
pilot-preparation-passed
```

It stores no session data and creates no placeholder evidence. Smoke failure leaves no workspace. Repository-local or existing destinations are rejected without overwrite.

Launch every participant session through the prepared workspace:

```bash
python3 software/product_alpha/launch_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --open
```

The launcher rebuilds Product Alpha and fails closed unless the current deterministic build exactly matches `workspace.json`. Only then does it serve the learner route, recorder, and Pilot Lab on `127.0.0.1`. Every recorder export carries that exact build ID. The launcher stores no session data and does not modify the workspace.

Useful lower-level options remain available:

```bash
# Verify workspace/build binding without serving
python3 software/product_alpha/launch_workspace.py check \
  --workspace /private/path/refrigerator-cohort

# Verify deterministic files and build identity
python3 software/product_alpha/run_pilot.py check

# Exercise the complete ephemeral loopback HTTP path
python3 software/product_alpha/run_pilot.py smoke

# Create an empty workspace from an already recorded build ID
python3 software/product_alpha/evaluation/prepare_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --expect-build-id <64-character-pilot-build-id>
```

A bare `python3 -m http.server` launch is static inspection only. It does not create the supported build-bound recorder and Pilot Lab URLs or enforce workspace/build identity, so it must not collect pilot evidence.

## Private cohort workspace

Preparation creates:

```text
refrigerator-cohort/
├── README.md
├── workspace.json
├── incoming-sessions/
├── verified/
└── review/
```

The evidence directories begin empty. The generated README includes shell-safe commands for the complete path through handoff verification.

At any time, verify the strongest completed stage and print the next valid action without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \
  --workspace /private/path/refrigerator-cohort
```

Recognized stages are:

```text
prepared
→ collecting
→ ready-to-assemble
→ intake-verified
→ review-ready-for-decision
→ decision-verified
→ handoff-verified
```

The status command verifies every artifact required by the current stage and rejects partial or out-of-order intake, review, decision, or handoff artifacts.

Do not treat the workspace, empty directories, intake manifest, review packet, decision record, receipt, handoff candidate, or workspace manifest as learner evidence. Do not place participant names, contact details, school details, account identifiers, or other identifying information in the workspace.

## Collection and non-writing preflight

After each facilitator-reviewed recorder export is placed in `incoming-sessions/`, validate all current files without sealing the cohort:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

Preflight accepts individual `.jsonl` or `.json` exports containing one session object each. It validates the session contract, route, exact build ID, privacy boundaries, source file types, anonymous labels, route order, score ranges, duplicate IDs, and personal-data fields. It predicts the exact combined JSONL and source-record hashes, reports the valid session count and evidence status, and writes nothing. It is safe to repeat after every new session.

## Immutable cohort intake

After collection is deliberately closed and at least five valid sessions are present, create the immutable intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

Normal assembly refuses fewer than five sessions before writing. When recruitment or execution intentionally stops early, close the incomplete cohort explicitly:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \
  --workspace /private/path/refrigerator-cohort \
  --allow-incomplete
```

The override records deliberate early closure; it does not make the evidence complete or planning-review eligible.

Assembly revalidates every source, sorts sessions by anonymous ID, and exclusively writes:

```text
verified/anonymous-sessions.jsonl
verified/intake-manifest.json
```

The intake manifest records every raw-source SHA-256, the source-record-set SHA-256, and the exact combined JSONL SHA-256. Raw files are not renamed, moved, or modified. Existing verified outputs are never overwritten.

## Workspace-bound review

Verify that the intake and raw sources remain unchanged:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \
  --workspace /private/path/refrigerator-cohort
```

The command independently checks the repository-external workspace, privacy boundaries, exact route and build, every incoming source hash, intake-manifest hash, combined JSONL hash, session count, summary contract, and evidence status.

Create the immutable private review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py \
  --workspace /private/path/refrigerator-cohort
```

It writes:

```text
review/refrigerator-review.json
review/refrigerator-review.md
```

The packet contains the verified de-identified aggregate and decision options. It excludes raw session records, facilitator notes, and facilitator-authored custom confusion-tag text; refuses repository output and overwrite; and leaves the product decision pending for a human.

`verify_cohort.py` and `prepare_review.py` remain lower-level tools. The workspace-bound command is authoritative because it proves that the review still matches the immutable intake and unchanged raw exports.

## Sealed human decision

Do not edit the review packet. Verify readiness first:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \
  --workspace /private/path/refrigerator-cohort
```

After reviewing the aggregate together with the separate private facilitator notes, record exactly one human action:

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

The fourth action is rejected unless the cohort reached `ready-for-human-review`. Recording writes an exclusive artifact trio:

```text
review/refrigerator-review-decision.json
review/refrigerator-review-decision.md
review/refrigerator-review-decision-receipt.json
```

The receipt seals the decision JSON and Markdown hashes together with the review, intake, combined-cohort, and source-record bindings. Recording never edits the review packet, overwrites a decision artifact, or modifies the repository.

Verify the completed decision and every earlier evidence binding without writing:

```bash
python3 software/product_alpha/evaluation/record_decision.py verify \
  --workspace /private/path/refrigerator-cohort
```

The receipt provides local tamper evidence. It is not a digital signature, trusted timestamp, external notarization, or proof of authorship.

Keep participant identities out of reviewer, rationale, and checkpoint text. A role label or initials are sufficient. A recorded planning-review action starts a separate planning review only; it does not authorize a second route, public release, SaaS expansion, a learning-effectiveness claim, or product-market fit.

## De-identified repository handoff

After decision verification, check a repository-external handoff candidate without writing:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py check \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

Create the candidate pair:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

Verify it against the unchanged decision and evidence chain:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py verify \
  --workspace /private/path/refrigerator-cohort \
  --output-prefix /private/path/refrigerator-cohort/handoff/refrigerator-product-change
```

The handoff JSON and Markdown contain only an allowlisted de-identified aggregate, the verified human action, revision signals, and evidence hashes. They exclude raw sessions, anonymous session identifiers, facilitator notes, custom confusion-tag text, reviewer identity, review date, private rationale, checkpoint text, and local workspace paths.

Handoff outputs must remain outside the repository and are non-overwriting. They do not authorize or perform a repository change. A human must inspect the candidate and create a separate normal pull request.

## Pilot Lab

`pilot-lab.html` runs entirely in the current browser tab and can:

- read one or many local JSONL files;
- add batches without silently discarding earlier files;
- explicitly replace or clear the in-memory file set;
- validate records against the Product Alpha session contract and launcher build;
- reject mixed-build cohorts, malformed records, personal-data fields, duplicate labels, and repeated files;
- calculate completion, duration, rubric averages, confusion counts, and voluntary continuation;
- mark cohorts below five valid sessions as incomplete;
- surface documented revision triggers;
- export aggregate Markdown and JSON;
- export combined validated JSONL for private local use.

Refreshing clears Pilot Lab state. Aggregate exports omit facilitator notes. A validated JSONL export still contains private raw anonymous records. The command-line workspace chain is the authoritative evidence path.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 software/product_alpha/run_pilot.py check
python3 software/product_alpha/run_pilot.py smoke
node --test software/tests/test_product_alpha*.mjs
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

CI covers deterministic output, canonical extraction, route completeness, exact-revision Atlas references, browser-state boundaries, recorder capture locking, Pilot Lab batch handling, loopback-only serving, workspace/build binding, intake preflight and assembly, source hashing, tamper rejection, review de-identification, sealed decision creation and verification, handoff privacy and rollback, stage reporting, repository-output refusal, and clean-repository behavior.

## Learner pilot

Use [`PILOT.md`](PILOT.md) with 5–8 real learners who did not author or review the route. The protocol defines the session procedure, 0–2 rubric, anonymous records, confusion tags, evidence-based revision thresholds, private review, sealed decision, and de-identified handoff.

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
- private workspaces, review packets, decisions, receipts, and handoff candidates remain outside the repository;
- launchers and smoke validation bind only to `127.0.0.1` and store no session data;
- preparation creates no placeholder evidence;
- incomplete intake requires explicit authorization and stays incomplete;
- review, decision, and handoff verification reject changed earlier evidence;
- the thermal model supports reasoning and is not repair or safety guidance;
- aggregate evidence remains descriptive and every product action remains human-supplied.
