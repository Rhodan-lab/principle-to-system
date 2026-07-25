# Project State

> Last updated: 2026-07-26

## Current phase

**Phase 9 Technology review implemented on `agent/phase-9-technology-review`; coordinated validation and pull-request integration remain pending.**

The repository remains a material-first educational foundation. Software is intentionally deferred until the scientific material, sources, review workflow, synthesis, and release gates are mature.

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
| 9 | Technology review | Implemented on Phase 9 branch; coordinated validation pending |
| 10 | Synthesis reconciliation | Next after Phase 9 integration |
| 11 | Controlled material expansion | Seed exemplars complete |
| 12 | Release candidate | Not started |
| 13 | Optional software layer | Deferred |

## Integration history

The original Phase 6 work was merged into an outdated feature branch after Phase 5 had already entered `main`. PR #8 corrected that topology by integrating the reviewed Phase 6 and Phase 7 layers into `main`.

PR #9 then integrated the Phase 8 Life and Earth Systems review into `main`.

Current branch order is clean:

1. `main` contains reviewed Modules 01–16;
2. `agent/phase-9-technology-review` was created directly from the merged Phase 8 state;
3. Phase 9 will enter `main` through its own focused pull request;
4. no phase workflow automatically merges pull requests.

## Content inventory and status

### Core layer

- 20 modules and 60 learner-facing files;
- 7 crosscutting concepts;
- 6 end-to-end pathways;
- 3 Mermaid knowledge maps;
- normalized central source ledger;
- reusable metadata, source, scientific-review, and continuity validators.

On the Phase 9 branch after the coordinated transaction:

- Modules 01–05: **Reviewed**;
- Modules 06–12: **Reviewed**;
- Modules 13–16: **Reviewed**;
- Modules 17–20: **Reviewed**;
- Modules 01–20: **Reviewed**;
- no core module is Complete.

A module is Reviewed only when its `overview.md`, `technology.md`, and `explore.md` files all complete the same focused scientific and editorial review. Reviewed does not mean independently certified, production-qualified, or release-ready.

### Applied-material layer

- shared learning contract in `experiences/`;
- 4 family standards;
- 4 reusable templates;
- 4 reviewed exemplars;
- normalized experience-source ledger;
- dedicated strict validator and GitHub Actions workflow.

## Phase 4 result — Metadata foundation

Phase 4 normalized all 60 original learner files:

- unique canonical slugs by file role;
- consistent module identifiers and subject domains;
- canonical prerequisites and connections;
- removal of self-references and unknown legacy identifiers;
- deterministic normalization and audit artifacts;
- focused idempotence validation.

Phase 4 was merged through PR #4.

## Phase 5 result — Source foundation

Phase 5:

- recovered 109 logical records from malformed source rows;
- normalized one eight-column row per source;
- removed weak or invalid records only when inspected replacements were supplied;
- produced a 110-record baseline;
- established source coverage for every core module;
- added deterministic source-repair tools and a read-only CI gate.

Phase 5 is merged into `main`.

## Phase 6 result — Foundations Modules 01–05

Phase 6 reviewed all 15 Foundations files. Major corrections covered:

- causal identification, p-values, confidence intervals, reproducibility, and replicability;
- measurement terminology, covariance propagation, traceability, and dynamic measurement;
- calibration, validation, identifiability, linearisation, scaling, and extrapolation limits;
- finite-sample inference, calibration, sampling bias, and decision thresholds;
- conditioning, stability, consistency, convergence, numerical error, verification, and validation;
- safe and age-appropriate exploration activities.

Phase 6 added six source records, producing a 116-record ledger.

## Phase 7 result — Physical Science Modules 06–12

Phase 7 reviewed all 21 Physical Science files. Major corrections covered:

- quantum states, uncertainty, measurement, vacuum language, MRI, STM, and tunnelling;
- bonding, activities, standard states, catalytic cycles, electrochemistry, and rate models;
- temperature, entropy, heat, work, free energy, radiation, Carnot scope, and exergy;
- momentum, invariant mass, rotation, specific impulse, safety factors, and arithmetic;
- revised-SI electromagnetic constants, Ohmic limits, impedance, induction, and circuits;
- Fourier analysis, sampling, interference, guided modes, bandwidth, and data rate;
- Bernoulli assumptions, lift, non-Newtonian flow, tensor mechanics, fracture, fatigue, and anisotropy;
- removal of unsafe batteries, sealed heating, fragile resonance, traffic, cutting, fracture, and weapon-based activities.

Phase 7 added five source records, producing a **121-record** ledger. Phases 6 and 7 entered `main` through PR #8.

## Phase 8 result — Life and Earth Systems Modules 13–16

Phase 8 reviewed all 12 learner-facing files.

### Cells and Bioenergetics

- corrected ATP coupling, enzymes, membrane transport, respiration, photosynthesis, and ATP-yield explanations;
- added electrochemical activity, sign, direction, and model limits;
- removed unsafe pressure, hot-water, tasting, and real-poison activities.

### DNA and Evolution

- corrected replication fidelity, gene-expression scope, replication machinery, mutation, selection, Hardy–Weinberg notation, fitness, and PCR limits;
- replaced sensitive family-trait, alcohol-extraction, and antibiotic-exposure prompts;
- clarified synonymous-substitution effects and canonical links.

### Ecosystems and Complex Systems

- removed fixed trophic-transfer, carrying-capacity, modularity, wetland-performance, and reliability claims;
- corrected network roles, Lotka–Volterra, logistic-map, and causal-loop interpretations;
- reframed regenerative systems around leakage, accumulation, ageing, and backup;
- replaced standing-water contact and sealed-organism activities.

### Earth and Planetary Systems

- corrected plate-driving mechanisms, overturning circulation, effective radiative forcing, greenhouse physics, energy-balance limits, and projection uncertainty;
- removed unstable observing-system and computing claims;
- replaced stove heating, permanent-marker, and operational terraforming activities.

Phase 8 added ten institutional source records, producing a **131-record** ledger. Phase 8 entered `main` through PR #9.

## Phase 9 result — Technology Modules 17–20

Phase 9 reviews all 12 Technology files as one coordinated transaction.

### Module 17 — Materials Science and Manufacturing

- qualifies material-class, phase, strengthening, diffusion, fracture, fatigue, and Hall–Petch claims;
- adds process qualification, traceable metrology, uncertainty, acceptance criteria, and digital-thread controls;
- corrects additive, casting, forming, machining, joining, efficiency, and lifecycle boundaries;
- removes learner fracture, glowing-metal, quenching, machine, laser, powder, and chemical hazards.

### Module 18 — Semiconductors and Electronics

- corrects band, Fermi-level, carrier, doping, junction, diode, BJT, MOSFET, threshold, and compact-model explanations;
- reframes Moore's observation, node names, scaling, performance, power, thermal, packaging, yield, and metrology;
- replaces physical teardown and fabrication activities with simulations, documentation, telemetry, and institutional metrology resources.

### Module 19 — Software and AI Foundations

- limits compression, channel-capacity, TCP, networking, optimisation, and machine-learning claims to their specifications and assumptions;
- adds distribution shift, calibration, subgroup performance, robustness, privacy, security, misuse, monitoring, human oversight, appeal, and incident response;
- replaces third-party network probing and sensitive-profile observation with authorised, fictional, or own-device explorations.

### Module 20 — Sensors, Control, and Infrastructure

- replaces anthropomorphic control descriptions with measurement, estimation, decision, actuation, verification, and protection layers;
- corrects PID, state-space, power, delay, sampling, saturation, inverter, resilience, and failure claims;
- adds industrial-control cybersecurity, defence in depth, safe-state and fail-operational analysis, human authority, and recovery testing;
- removes unsafe infrastructure proximity and long-object balancing activities.

Phase 9 declares twelve authoritative source additions:

- NIST, NIOSH, and OSHA manufacturing and safety records;
- NIST semiconductor metrology records;
- NIST AI risk-management records and IETF RFC 9293;
- NIST cyber-physical and industrial-control guidance plus the U.S. Department of Energy Grid Modernization Initiative.

The coordinated source transition is **131 → 143 records**. The Phase 9 branch therefore contains **143 records** after application.

Artifacts:

- `reports/phase-9-technology-review.md`;
- `reports/phase-9-technology-sources.json`;
- `sources/phase-9-reviewed-sources.json`;
- `scripts/apply_phase9_review_sources.py`;
- `scripts/apply_phase9_technology_review.py`;
- `scripts/validate_phase8_continuity_phase9.py`;
- `scripts/validate_phase9_technology_review.py`;
- `.github/workflows/validate-phase-9-technology.yml` after write automation is removed.

## Status meanings

- **Draft** — content exists but has not completed focused review.
- **Reviewed** — claims, sources, structure, safety, security, privacy, metadata, equations, links, assumptions, and limitations received focused review.
- **Complete** — reviewed content passes the applicable repository-wide release gate with no unresolved findings.
- **Blocked** — progress depends on a recorded unresolved issue.

Reviewed does not mean independently certified or release-ready.

## Validation

### Metadata and source foundation

```bash
python3 scripts/normalize_module_metadata.py
python3 scripts/normalize_source_ledger.py --check --strict
python3 scripts/apply_verified_source_baseline.py --check
```

### Earlier-phase continuity

```bash
python3 scripts/apply_foundations_review_sources.py --check
python3 scripts/validate_foundations_continuity_phase8.py --allow-downstream-reviewed
python3 scripts/apply_phase7_review_sources.py --check
python3 scripts/finalize_phase7_review.py --check
python3 scripts/apply_phase8_review_sources.py --check
python3 scripts/finalize_phase8_review.py --check
python3 scripts/validate_phase8_continuity_phase9.py
```

### Phase 9 review

```bash
python3 scripts/apply_phase9_review_sources.py --check
python3 scripts/apply_phase9_technology_review.py --check
python3 scripts/validate_phase9_technology_review.py
python3 scripts/validate_repo.py
```

The Phase 9 gate checks:

- all 12 expected Technology files and Reviewed metadata;
- canonical slugs, prerequisites, domains, connections, and all 20 INDEX statuses;
- direct source-to-ledger matching and the preserved 131→143 source transition;
- materials, semiconductor, software, AI, control, and infrastructure model boundaries;
- measurement, qualification, cybersecurity, privacy, human oversight, and lifecycle claims;
- removal of stale identifiers and unsafe or operational exploration instructions;
- continuity of reviewed Modules 01–16;
- deterministic idempotence and review-record consistency;
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

1. Complete coordinated Phase 9 validation and open its focused pull request.
2. Obtain independent review before merging Phase 9.
3. Complete Phase 10 synthesis reconciliation.
4. Pass repository-wide strict release validation.
5. Expand applied materials only from stable reviewed patterns.
6. Consider software only after the material system is mature.

## Continuation instructions

Read `README.md`, `CONTENT_GUIDE.md`, `SOURCE_POLICY.md`, `AUDIT.md`, this file, and the relevant phase reports. Keep metadata repair, source repair, scientific review, synthesis, expansion, and software implementation in separate focused pull requests. Never promote content solely because a file exists or a structural check passes.
