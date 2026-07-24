# Content Guide

This guide defines the structure, terminology, and editorial standard for all learning materials in Principle to System. Every contributor — human or AI — must follow it so the repository reads as one coherent work.

## The explanatory arc

Every module teaches along the same arc:

```text
observation
→ scientific concept
→ mechanism
→ mathematical model
→ engineered component
→ technological system
→ limitation and trade-off
```

Explanations must be causal ("X happens because Y"), not merely descriptive ("X is associated with Y"). State assumptions and system boundaries explicitly. Give scale (spatial, temporal, energetic) wherever it aids intuition. Identify what is conserved, what is approximated, and where the model breaks down.

## Module file structure

Each of the 20 modules lives in its own directory inside `foundations/`, `science/`, or `technology/`, named with a two-digit number and slug (for example `foundations/02-measurement-uncertainty/`). Each module contains exactly three learner-facing files.

### `overview.md` — required sections

1. The central questions
2. Observable phenomena
3. Essential concepts
4. Mechanisms and causal chains
5. Important quantities
6. Mathematical models and equations
7. Definitions of symbols and units
8. Assumptions and approximations
9. Spatial and temporal scales
10. Common misconceptions
11. Connections to other modules
12. Sources

Conceptual foundations and mathematical models are combined here; there is no separate `models.md`.

### `technology.md` — required sections

1. Scientific principles used
2. The engineering problem
3. Main components
4. How the components interact
5. Matter, energy, force, or information flow
6. System architecture
7. Design constraints
8. Performance and efficiency
9. Reliability and failure modes
10. Safety principles
11. Environmental and lifecycle considerations
12. Connections to other technologies
13. Sources

Each `technology.md` must show at least one explicit chain, for example:

```text
atomic structure
→ semiconductor behaviour
→ transistor
→ logic gate
→ processor
→ computer
```

Do not organise material around commercial brands.

### `explore.md` — required sections

1. Observation prompts
2. Prediction questions
3. Worked reasoning examples
4. Thought experiments
5. Household and browser-based explorations
6. Model-building prompts
7. Self-explanation questions
8. Transfer questions
9. Suggested learning paths
10. Reasoning notes

Exploration must be safe and free. Never include grades, deadlines, scores, classroom targets, competitive rankings, or motivational streaks. Never instruct readers to use fire, high voltage, hazardous chemicals, harmful biological material, pressure vessels, unsafe machinery, or uncontrolled radiation sources.

## YAML frontmatter

Every learner-facing Markdown file begins with:

```yaml
---
title:
slug:
module:
domain:
status:
prerequisites:
connections:
last_reviewed:
content_license: CC-BY-4.0
---
```

Allowed `status` values: `draft`, `reviewed`, `complete`, `blocked`. Do not add numerical confidence scores. Slugs must be unique across the repository.

## Editorial standard

Prioritise causal explanation, scientific accuracy, meaningful mathematical models, explicit assumptions, system boundaries, scale, conservation, limitations, cross-domain connections, and useful examples.

Avoid shallow summaries, repeated introductions, excessive historical detail, unsupported fun facts, childish language, exam-oriented writing, unnecessary jargon, paragraphs repeated across files, and padding to reach a word count. A file is complete when it explains its subject sufficiently, not when it reaches an arbitrary length.

Write mathematics in LaTeX-style notation inside Markdown (inline `$...$` or display `$$...$$`), and always define every symbol and its SI unit at first use.

## Cross-references

Use relative links between files (for example `../../science/08-energy-thermodynamics/overview.md`). Every module should link to the modules it depends on and the crosscutting concepts it exemplifies. Run `python3 scripts/validate_repo.py` to verify structure and links before committing.
