# Contributing to Principle to System

Thank you for helping independent learners understand how foundational science becomes technology and how to reason about complete systems.

## Before you start

1. Read [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md).
2. Read [`SOURCE_POLICY.md`](SOURCE_POLICY.md).
3. Check [`PROJECT_STATE.md`](PROJECT_STATE.md) and [`AUDIT.md`](AUDIT.md).
4. Keep module-audit work separate from applied-material expansion.

## Core module contributions

1. Create a focused branch.
2. Keep the pull request limited to one module or one repository-wide concern.
3. Add verified sources to [`sources/source-ledger.md`](sources/source-ledger.md).
4. Run:

   ```bash
   python3 scripts/validate_repo.py
   ```

5. Update `last_reviewed` only when factual review occurred.
6. Do not advance status solely because a file exists or structural validation passes.

## Applied-material contributions

Choose one family and begin from its template:

| Family | Template |
| --- | --- |
| System dossier | [`templates/system-dossier.md`](templates/system-dossier.md) |
| Failure pattern | [`templates/failure-pattern.md`](templates/failure-pattern.md) |
| Investigation | [`templates/investigation.md`](templates/investigation.md) |
| Design challenge | [`templates/design-challenge.md`](templates/design-challenge.md) |

Then:

1. use `domain: experience` and the correct `experience_type`;
2. use canonical module, concept, and experience identifiers;
3. include a meaningful quantitative model with symbols, units, assumptions, and limits;
4. state system boundaries, uncertainty, failure modes, and trade-offs;
5. keep all physical activities optional, low-energy, and safe;
6. add directly inspected sources to [`sources/experience-source-ledger.md`](sources/experience-source-ledger.md), one source per eight-column row;
7. run:

   ```bash
   python3 scripts/validate_experiences.py --strict
   ```

GitHub Actions runs the same strict experience gate when relevant files change.

## What review looks for

- scientific accuracy and appropriate scope;
- claims traceable to credible sources;
- causal explanation rather than disconnected description;
- correct equations, symbols, units, and sign conventions;
- explicit assumptions, boundaries, scales, uncertainty, and validity limits;
- working links and canonical identifiers;
- substantive safety, reliability, lifecycle, and trade-off analysis;
- no padding, gamification, exam framing, or unsafe activity suggestions.

## Pull-request review record

Include:

```text
Files reviewed:
Claims corrected or added:
Equations and units checked:
Assumptions and limits added:
Sources opened and verified:
Safety reviewed:
Links and identifiers checked:
Remaining caveats:
Status transition:
```

## Commit messages

Use concise prefixes, for example:

```text
content: add battery system dossier
fix: correct feedback delay explanation
docs: clarify experience source policy
chore: extend experience validator
```

## Licensing

Code and scripts are licensed under [Apache License 2.0](LICENSE). Original educational content is licensed under [CC BY 4.0](LICENSE-CONTENT).
