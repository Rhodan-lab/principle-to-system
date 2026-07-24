# Project State

> Last updated: 2026-07-24

## Current phase

**Complete.** All mandatory deliverables are committed to GitHub. The repository is fully functional and resumable.

## Completed modules

All 20 modules (60 core files):

1. Scientific reasoning, causality, and explanation
2. Measurement, units, error, and uncertainty
3. Mathematical models, quantities, vectors, and scale
4. Probability, statistics, and data interpretation
5. Computation, algorithms, numerical methods, and simulation
6. Matter, atoms, electron behaviour, and quantum foundations
7. Chemical bonding, molecular interactions, and reactions
8. Energy, heat, entropy, and thermodynamics
9. Motion, forces, momentum, rotation, and gravitation
10. Electricity, magnetism, fields, and circuits
11. Oscillations, waves, sound, optics, and signals
12. Fluids, material properties, and structural behaviour
13. Cells, membranes, enzymes, metabolism, and bioenergetics
14. DNA, gene expression, inheritance, and evolution
15. Ecosystems, feedback, networks, and complex systems
16. Earth, atmosphere, oceans, climate, and planetary systems
17. Materials science, fabrication, and manufacturing
18. Semiconductors, electronics, and computer hardware
19. Software, information, networks, and AI foundations
20. Sensors, control, automation, robotics, energy, and infrastructure

## Modules in progress

None.

## Completed pathways

All 6 pathways:

1. Atoms to computers
2. Fields to electric power
3. Waves to global communication
4. Chemistry to materials and batteries
5. Biology to biotechnology
6. Data to AI and automation

## Crosscutting concepts

All 7 complete:

1. Patterns
2. Cause and effect
3. Scale, proportion, and quantity
4. Systems and models
5. Energy and matter
6. Structure and function
7. Stability and change

## Knowledge maps

All 3 complete:

1. Foundations map
2. Science-to-technology map
3. Complete dependency map

## Source-ledger status

97 entries recorded across all 20 modules.

## Validation status

`scripts/validate_repo.py` passes with 0 errors, 0 warnings.

## Unresolved problems

- `.github/workflows/validate.yml` could not be pushed due to GitHub App permissions (workflows scope). The file exists locally and can be added manually by the repository owner or via the GitHub web interface.

## Next highest-priority action

If continuing development:
1. Add the GitHub Actions workflow file via the GitHub web UI (paste contents of `.github/workflows/validate.yml` from local).
2. Expand source ledger entries with additional high-quality references.
3. Review module content for scientific accuracy and cross-link completeness.
4. Consider adding worked numerical examples to `explore.md` files.

## Continuation instructions

Clone the repository, read this file, and continue from the next highest-priority action above. All standards are defined in `CONTENT_GUIDE.md` and `SOURCE_POLICY.md`. Run `python3 scripts/validate_repo.py` to verify structural integrity before committing.
