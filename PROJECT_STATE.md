# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 9 Technology review implemented and validated on draft PR #10; independent review and merge remain pending.**

The repository remains a material-first educational foundation. Software is intentionally deferred until the scientific material, source system, synthesis layer, and release gates are mature.

## Phase progress

| Phase | Scope | Status |
| --- | --- | --- |
| 0 | Vision and educational philosophy | Complete |
| 1 | Core knowledge inventory | First-draft inventory complete |
| 2 | Repository audit and hardening | Complete |
| 3 | Applied-material foundation | Implemented and validated |
| 4 | Core metadata normalization | Merged and validated |
| 5 | Legacy source-ledger repair | Merged and validated |
| 6 | Foundations scientific review | Merged and validated through PR #8 |
| 7 | Physical-science review | Merged and validated through PR #8 |
| 8 | Life and Earth systems review | Merged and validated through PR #9 |
| 9 | Technology review | Implemented and validated on PR #10; awaiting merge |
| 10 | Synthesis reconciliation | Next after Phase 9 integration |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration topology

The original Phase 6 work entered an outdated feature branch after Phase 5 had already reached `main`. PR #8 corrected the topology by integrating the reviewed Phase 6 and Phase 7 layers into `main`. PR #9 then integrated Phase 8.

The current order is clean:

1. `main` contains reviewed Modules 01–16;
2. `agent/phase-9-technology-review` was created directly from the merged Phase 8 state;
3. PR #10 carries the focused Phase 9 review into `main`;
4. no phase workflow automatically merges pull requests.

## Repository inventory and status

### Core material

- 20 modules;
- 60 learner-facing files;
- 7 crosscutting concepts;
- 6 end-to-end pathways;
- 3 Mermaid knowledge maps;
- normalized central source ledger;
- reusable metadata, source, scientific-review, continuity, and audit validators.

On PR #10:

- Modules 01–05: **Reviewed**;
- Modules 06–12: **Reviewed**;
- Modules 13–16: **Reviewed**;
- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;
- no core module is Complete.

Reviewed means all three files for a module—`overview.md`, `technology.md`, and `explore.md`—passed the applicable focused scientific, editorial, source, metadata, equation, safety, security, privacy, and limitation checks. Reviewed does not mean independently certified, production-qualified, or release-ready.

### Applied-material layer

- shared learning contract in `experiences/`;
- 4 family standards;
- 4 reusable templates;
- 4 reviewed exemplars;
- normalized experience-source ledger;
- dedicated strict validator and GitHub Actions workflow.

## Completed foundations

### Phase 4 — Metadata

Phase 4 normalized all 60 learner files with canonical slugs, domains, prerequisites, connections, review fields, and deterministic checks. It entered `main` through PR #4.

### Phase 5 — Sources

Phase 5 recovered malformed historical rows, removed weak records only when inspected replacements existed, produced a 110-record baseline, and established deterministic source validation. It is merged into `main`.

### Phase 6 — Foundations Modules 01–05

The 15 Foundations files were reviewed for causal reasoning, measurement, uncertainty, modelling, probability, statistics, computation, numerical limits, reproducibility, and safe exploration. Six reviewed sources increased the ledger to 116 records.

### Phase 7 — Physical Science Modules 06–12

The 21 Physical Science files were reviewed for quantum foundations, chemistry, thermodynamics, mechanics, electromagnetism, waves, fluids, materials, equations, model boundaries, and learner safety. Five reviewed sources increased the ledger to **121 records**. Phases 6 and 7 entered `main` through PR #8.

### Phase 8 — Life and Earth Systems Modules 13–16

The 12 files were reviewed for cellular energetics, genetics, evolution, ecology, complex systems, Earth systems, climate, mathematical models, scale transitions, privacy, and safe exploration. Ten institutional sources increased the ledger to **131 records**. Phase 8 entered `main` through PR #9.

## Phase 9 result — Technology Modules 17–20

Phase 9 reviewed all 12 Technology files as one coordinated transaction and then applied a second deterministic scientific-quality pass.

### Module 17 — Materials Science and Manufacturing

- replaced broad material-class stereotypes with conditional structure–processing–property–performance relationships;
- corrected phase, strengthening, diffusion, Hall–Petch, lever-rule, fracture, fatigue, creep, and symbol definitions;
- added process qualification, traceable metrology, uncertainty, acceptance criteria, digital-thread provenance, and configuration control;
- qualified casting, forming, machining, additive, joining, efficiency, lifecycle, and defect claims;
- removed learner fracture, glowing-metal, quenching, machine, laser, powder, and chemical hazards.

### Module 18 — Semiconductors and Electronics

- corrected band, Fermi-level, carrier, hole, doping, junction, diode, BJT, MOSFET, threshold, built-in-potential, and compact-model explanations;
- aligned equations and symbol definitions and removed literal technology-node and transistor-count interpretations;
- reframed Moore's observation, performance, power, thermal behaviour, yield, reliability, packaging, architecture, fabrication, and metrology;
- replaced physical teardown, intentional thermal stress, and fabrication activities with simulation, documentation, telemetry, and institutional metrology.

### Module 19 — Software and AI Foundations

- limited compression, channel-capacity, TCP, optimisation, and machine-learning claims to their specifications and assumptions;
- distinguished theorem limits, finite implementations, application semantics, trust boundaries, and failure models;
- added task validity, uncertainty, calibration, subgroup performance, distribution shift, robustness, privacy, security, misuse, monitoring, provenance, human oversight, appeal, rollback, and incident response;
- corrected information-theory and optimisation symbols and removed unstable size, latency, training-duration, and architecture claims;
- replaced third-party network probing and sensitive-profile observation with authorised, fictional, or own-device explorations.

### Module 20 — Sensors, Control, and Infrastructure

- replaced anthropomorphic control descriptions with measure–condition–sample–estimate–decide–act–verify;
- corrected PID, state-space, complex-power, sampling, delay, estimation, saturation, inverter, protection, resilience, reliability, and symbol definitions;
- added independent protection, fail-safe and fail-operational analysis, common-cause failure, human authority, industrial-control cybersecurity, defence in depth, and recovery testing;
- qualified grid balance, smart-inverter, synthetic-inertia, communication, storage, and service claims;
- removed unsafe infrastructure proximity, operational-system experimentation, and long-object balancing activities.

## Phase 9 sources

Phase 9 added twelve inspected authoritative records:

- NIST additive manufacturing, semiconductor metrology, AI risk management, cyber-physical systems, and industrial-control guidance;
- NIOSH metal-powder additive-manufacturing safety;
- OSHA machine-guarding requirements;
- IETF RFC 9293 for TCP;
- U.S. Department of Energy Grid Modernization Initiative.

The preserved source transition is **131 → 143 records**. The Phase 9 branch contains **143 records**, twelve additions, and zero source-report errors.

## Phase 9 validation artifacts

- `reports/phase-9-technology-review.md`;
- `reports/phase-9-technology-sources.json`;
- `sources/phase-9-reviewed-sources.json`;
- `scripts/apply_phase9_review_sources.py`;
- `scripts/apply_phase9_technology_review.py`;
- `scripts/finalize_phase9_review.py`;
- `scripts/normalize_phase9_transformer_literals.py`;
- `scripts/normalize_phase9_finalizer.py`;
- `scripts/validate_foundations_continuity_phase9.py`;
- `scripts/validate_phase8_continuity_phase9.py`;
- `scripts/validate_phase9_technology_review.py`;
- `scripts/validate_phase9_audit.py`;
- `.github/workflows/validate-phase-9-technology.yml`.

The temporary write-capable Phase 9 workflow is removed after material generation. Permanent CI is read-only.

## Status meanings

- **Draft** — content exists but has not completed focused review.
- **Reviewed** — claims, sources, structure, safety, security, privacy, metadata, equations, links, assumptions, and limitations received focused review.
- **Complete** — reviewed content passes repository-wide synthesis and release gates with no unresolved findings.
- **Blocked** — progress depends on a recorded unresolved issue.

No core module is Complete.

## Validation commands

### Metadata and sources

```bash
python3 scripts/normalize_module_metadata.py
python3 scripts/normalize_source_ledger.py --check --strict
python3 scripts/apply_verified_source_baseline.py --check
```

### Earlier-phase continuity

```bash
python3 scripts/apply_foundations_review_sources.py --check
python3 scripts/validate_foundations_continuity_phase9.py --allow-downstream-reviewed
python3 scripts/apply_phase7_review_sources.py --check
python3 scripts/finalize_phase7_review.py --check
python3 scripts/apply_phase8_review_sources.py --check
python3 scripts/finalize_phase8_review.py --check
python3 scripts/validate_phase8_continuity_phase9.py
```

### Phase 9

```bash
python3 scripts/normalize_phase9_transformer_literals.py --check
python3 scripts/normalize_phase9_finalizer.py --check
python3 scripts/apply_phase9_review_sources.py --check
python3 scripts/finalize_phase9_review.py --check
python3 scripts/validate_phase9_technology_review.py
python3 scripts/validate_phase9_audit.py
python3 scripts/validate_repo.py
```

The permanent gate checks:

- all 12 expected Technology files and Reviewed metadata;
- canonical slugs, prerequisites, domains, connections, and all 20 INDEX statuses;
- direct source-to-ledger matching and the preserved 131→143 transition;
- materials, semiconductor, software, AI, control, and infrastructure model boundaries;
- equations, symbols, units, measurement, qualification, lifecycle, cybersecurity, privacy, and human oversight;
- removal of stale identifiers and unsafe or operational exploration instructions;
- continuity of reviewed Modules 01–16;
- deterministic idempotence of both review layers;
- review-record and project-state consistency;
- no core module marked Complete.

## Next phase — Phase 10 Synthesis reconciliation

Phase 10 must reconcile:

1. pathways and prerequisite sequences;
2. crosscutting concepts;
3. Mermaid knowledge maps;
4. terminology, symbols, equations, and units;
5. source and status references;
6. cross-module transfer and technology links;
7. contradictions, duplication, gaps, and release blockers.

## Remaining core work

1. Obtain independent review and merge PR #10 when explicitly approved.
2. Complete Phase 10 synthesis reconciliation.
3. Pass repository-wide strict release validation.
4. Expand applied materials only from stable reviewed patterns.
5. Consider software only after the material system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the relevant phase reports. Keep scientific review, synthesis, expansion, and software implementation in separate focused pull requests. Never promote content solely because a file exists or a structural check passes.
