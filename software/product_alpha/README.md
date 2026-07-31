# Principia Product Alpha 0.1

This package is the first learner-facing product slice built from the existing Principia material foundation. It deliberately replaces phase-count growth with a concrete user journey.

## Alpha route

The first route asks a learner to understand a domestic refrigerator through five steps:

1. observe surprising behavior;
2. map system boundaries and flows;
3. manipulate a minimum thermal model;
4. diagnose normal cycling versus abnormal short-cycling;
5. redesign under constraints.

Canonical Principia Markdown remains authoritative. The build extracts required sections from the existing system dossier, failure pattern, investigation, and design challenge. The route configuration contains interaction structure, prompts, a bounded model, and pinned Atlas references; it does not duplicate the canonical learning corpus.

## Build

From the repository root:

```bash
python3 software/product_alpha/build.py build
python3 -m http.server 8000 --directory software/product_alpha/dist
```

Open the learner route at `http://127.0.0.1:8000`.

For a facilitated pilot, open the local recorder in a separate tab at:

```text
http://127.0.0.1:8000/facilitator.html
```

The recorder loads the committed rubric and session template from the same local build, validates an anonymous session record in the browser, and downloads one JSONL line. It does not submit data, create accounts, call Atlas, or write browser storage.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 -m unittest discover -s software/tests -p 'test_product_alpha*.py' -v
```

The validation checks deterministic output, canonical-source extraction, five-step route completeness, exact-revision Atlas references, the absence of external runtime dependencies, anonymous pilot-record boundaries, route-order integrity, deterministic evaluation summaries, and inclusion of the local facilitator recorder.

## Learner pilot

Use [`PILOT.md`](PILOT.md) before adding another route. It defines a 5–8 learner protocol, a 0–2 comprehension rubric, anonymous session records, recommended confusion tags, and evidence-based revision thresholds.

Use `facilitator.html` to export one anonymous `.jsonl` file per learner. Combine the compact JSON lines into one private local file, then summarize the cohort with:

```bash
python3 software/product_alpha/evaluation/summarize.py \
  --input path/to/anonymous-sessions.jsonl \
  --format markdown
```

The summarizer reports completion, duration, learning scores, recurring confusion, and voluntary continuation. It rejects known personal-data fields and malformed route progress. Facilitator notes must also remain anonymous.

## Boundaries

- no account or cloud dependency;
- no analytics;
- no external network request;
- no repository mutation;
- no live Atlas call;
- no inherited Atlas or Principia status;
- learner notes remain only in the current browser tab;
- pilot records remain local, anonymous, and facilitator-controlled;
- the recorder writes no browser storage and exports only on explicit facilitator action;
- the thermal model supports reasoning and is not repair or safety guidance.
