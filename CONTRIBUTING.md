# Contributing to Principle to System

Thank you for helping independent learners understand how foundational science becomes technology. Contributions of corrections, clarifications, better examples, stronger sources, and improved cross-links are all welcome.

## Before you start

1. Read [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md) — it defines the module structure, required sections, frontmatter, and editorial standard.
2. Read [`SOURCE_POLICY.md`](SOURCE_POLICY.md) — it defines which sources are acceptable and how they must be recorded.
3. Check [`PROJECT_STATE.md`](PROJECT_STATE.md) and open issues to avoid duplicating work in progress.

## Making a contribution

1. Fork the repository and create a branch with a descriptive name (e.g. `fix/thermo-entropy-units`).
2. Make your changes, keeping each pull request focused on one module or one concern.
3. Add any new sources to [`sources/source-ledger.md`](sources/source-ledger.md).
4. Run the validator locally:

   ```bash
   python3 scripts/validate_repo.py
   ```

5. Update the `last_reviewed` date and, if appropriate, the `status` field in the frontmatter of files you changed.
6. Open a pull request describing what you changed and why, citing sources for any factual changes.

## What we look for in review

- Scientific accuracy, with claims traceable to credible sources.
- Causal explanation rather than description or summary.
- Correct equations, symbols, and SI units.
- Working relative links and consistent terminology.
- No padding, no exam-style framing, no unsafe activity suggestions.

## Commit message style

Use concise, descriptive messages with a conventional prefix, for example:

```text
content: complete energy and thermodynamics module
fix: correct induction model and references
docs: clarify source policy
chore: update validator
```

## Licensing of contributions

By contributing, you agree that code and scripts you submit are licensed under the [Apache License 2.0](LICENSE) and original educational content under [CC BY 4.0](LICENSE-CONTENT).
