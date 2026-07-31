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

Open `http://127.0.0.1:8000`.

## Validation

```bash
python3 software/product_alpha/build.py check
python3 -m unittest discover -s software/tests -p 'test_product_alpha.py' -v
```

The validation checks deterministic output, canonical-source extraction, five-step route completeness, exact-revision Atlas references, and the absence of external runtime dependencies.

## Boundaries

- no account or cloud dependency;
- no analytics;
- no external network request;
- no repository mutation;
- no live Atlas call;
- no inherited Atlas or Principia status;
- learner notes remain only in the current browser tab;
- the thermal model supports reasoning and is not repair or safety guidance.
