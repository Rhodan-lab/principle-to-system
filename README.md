# Principle to System

**Learn how foundational science becomes technology.**

Principle to System is an open-source knowledge repository for curious independent learners. It explains how scientific understanding is built, and how that understanding is progressively transformed into the engineered systems that shape the modern world. Every learning module follows the same explanatory arc:

```text
observation
→ scientific concept
→ mechanism
→ mathematical model
→ engineered component
→ technological system
→ limitation and trade-off
```

This is not a textbook, an exam course, or an encyclopaedia of disconnected facts. It is a connected map of causal explanations: why phenomena happen, how they are modelled, and how engineers exploit them.

## Who this is for

Independent learners who want to understand *why* technology works, not merely *that* it works. No formal enrolment, prerequisites beyond curiosity, or assessment framework is assumed. The material uses clear international English and meaningful mathematics, with all symbols and units defined where they appear.

## How the content is organised

The repository contains 20 learning modules grouped into three content folders, plus synthesis layers that connect them.

| Folder | Contents |
| --- | --- |
| `foundations/` | Modules 01–05: reasoning, measurement, mathematics, probability, and computation — the tools of science |
| `science/` | Modules 06–16: the natural sciences, from quantum matter to planetary systems |
| `technology/` | Modules 17–20: materials, electronics, software, and engineered infrastructure |
| `concepts/` | Seven crosscutting concepts (patterns, cause and effect, scale, systems, energy and matter, structure and function, stability and change) |
| `pathways/` | Six end-to-end science-to-technology pathways (e.g. atoms → computers) |
| `maps/` | Three Mermaid knowledge maps with labelled dependency relationships |
| `sources/` | The central source ledger recording every reference used |
| `scripts/` | The repository validator |

Every module directory contains exactly three learner-facing files:

| File | Purpose |
| --- | --- |
| `overview.md` | Central questions, phenomena, concepts, mechanisms, quantities, mathematical models, assumptions, scales, misconceptions, connections, and sources |
| `technology.md` | How the module's science is engineered into components and systems, including explicit principle-to-system chains, constraints, failure modes, and trade-offs |
| `explore.md` | Safe observation prompts, prediction questions, worked reasoning examples, thought experiments, and self-directed learning paths |

## How to begin learning

1. Open [`INDEX.md`](INDEX.md) to see all modules, their prerequisites, and their status.
2. If you are new to scientific reasoning, start with [`foundations/01-scientific-reasoning/overview.md`](foundations/01-scientific-reasoning/overview.md).
3. If you want a goal-directed route, pick a pathway in [`pathways/`](pathways/) — for example [`pathways/atoms-to-computers.md`](pathways/atoms-to-computers.md) — and follow the module prerequisites it lists.
4. Use the maps in [`maps/`](maps/) to see how everything depends on everything else.

## How to navigate dependencies

Each module's YAML frontmatter lists its `prerequisites` and `connections`. The [`INDEX.md`](INDEX.md) table summarises these, and [`maps/complete-dependency-map.md`](maps/complete-dependency-map.md) shows the full labelled dependency graph. Prerequisites are recommendations for smooth understanding, not gates: every file defines the ideas it relies on well enough to be read on its own.

## How to contribute

See [`CONTRIBUTING.md`](CONTRIBUTING.md). In short: follow the structure defined in [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md), cite sources according to [`SOURCE_POLICY.md`](SOURCE_POLICY.md), run `python3 scripts/validate_repo.py` before submitting, and keep explanations causal, accurate, and free of padding.

## Licensing

This repository uses two licences, deliberately kept distinct:

- **Code and scripts** (everything in `scripts/` and `.github/`) are licensed under the [Apache License 2.0](LICENSE).
- **Original educational content** (all Markdown learning materials) is licensed under [Creative Commons Attribution 4.0 International (CC BY 4.0)](LICENSE-CONTENT).

When reusing content, attribute "Principle to System contributors" and link back to this repository. See [`CITATION.cff`](CITATION.cff) for citation metadata.

## Project status

The live status of every module, pathway, and validation run is tracked in [`PROJECT_STATE.md`](PROJECT_STATE.md), which is kept current so the project remains resumable at any time.
