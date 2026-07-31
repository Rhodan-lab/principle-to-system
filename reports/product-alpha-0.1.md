# Principia Product Alpha 0.1

## Decision

Active development moves from recursive offline authorization envelopes to a learner-facing product slice.

## Product hypothesis

Principia is most distinctive when a learner starts with a real system, observes surprising behavior, forms a causal model, diagnoses failure, and redesigns under constraints. Atlas should appear as a trust and provenance layer inside that journey rather than as a second product the learner must understand first.

## Implemented slice

The first alpha route uses the existing refrigerator route:

```text
observe
→ map boundary and flows
→ manipulate a thermal model
→ diagnose cycling behavior
→ redesign under constraints
```

The implementation includes:

- a responsive static learner interface;
- five-step journey navigation;
- content extraction from four canonical Principia artifacts;
- a dependency-free interactive thermal model;
- a diagnosis challenge distinguishing bounded oscillation from instability;
- a browser-tab-only learner explanation field;
- exact-revision, read-only Atlas evidence presentation;
- deterministic build output and unit tests.

## Authority boundary

The alpha does not create accounts, analytics, network dependencies, repository writes, live Atlas synchronization, status inheritance, or automated publication. These are product-scope limits, not a new recursive governance phase.

## Next evidence

The next decision should be based on use of this route by real learners. Measure completion, explanation quality, misconception patterns, and voluntary continuation before adding another system route or production infrastructure.
