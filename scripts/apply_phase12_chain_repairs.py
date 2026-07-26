#!/usr/bin/env python3
"""Apply or check explicit principle-to-system chains required by Phase 12."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INSERT_BEFORE = "\n## 7. Design constraints\n"

CHAINS: dict[str, str] = {
    "science/10-electricity-magnetism/technology.md": """
### Explicit Principle-to-System Chain

```text
changing magnetic flux and the Lorentz force
→ induced voltage and force on charges or currents
→ windings, magnetic cores, insulation, and switching components
→ generators, transformers, motors, and power converters
→ measurement, protection, and control
→ interconnected electrical service within thermal, insulation, and stability limits
```
""",
    "science/15-ecosystems-complex-systems/technology.md": """
### Explicit Principle-to-System Chain

```text
microbial metabolism, mass conservation, and transport
→ transformation rates and stoichiometric balances
→ biofilms, plants, substrates, and controlled bioreactors
→ hydraulic, nutrient, and atmospheric compartments
→ sensing, residence-time control, maintenance, and backup barriers
→ treatment or life-support service within declared open-system limits
```
""",
    "technology/17-materials-manufacturing/technology.md": """
### Explicit Principle-to-System Chain

```text
bonding, phase behaviour, kinetics, transport, and mechanics
→ process windows and defect mechanisms
→ feedstock, tooling, energy source, fixture, and atmosphere
→ controlled transformation, sensing, and metrology
→ qualified manufacturing route with configuration control
→ traceable component population under performance and lifecycle constraints
```
""",
    "technology/19-software-ai/technology.md": """
### Explicit Principle-to-System Chain

```text
physical information states, algorithms, logic, and probability
→ instruction execution, data representation, and protocol semantics
→ operating-system, network, storage, and model components
→ authenticated interfaces and distributed service architecture
→ monitoring, governance, human authority, fallback, and recovery
→ bounded user-facing software or AI-enabled service
```
""",
    "technology/20-sensors-control-infrastructure/technology.md": """
### Explicit Principle-to-System Chain

```text
physical state and transduction
→ calibrated measurement and state estimation
→ constrained control decision with timing and uncertainty
→ power conversion and actuator response
→ independent protection, diagnostics, and operator authority
→ resilient physical service under declared disturbances and operating limits
```
""",
}


def normalized(text: str, relative: str) -> str:
    chain = CHAINS[relative].strip("\n")
    if "### Explicit Principle-to-System Chain" in text:
        return text
    if INSERT_BEFORE not in text:
        raise ValueError(f"{relative}: missing canonical Design constraints insertion point")
    return text.replace(INSERT_BEFORE, f"\n\n{chain}\n{INSERT_BEFORE}", 1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--write", action="store_true")
    group.add_argument("--check", action="store_true")
    args = parser.parse_args()

    errors: list[str] = []
    changes: list[tuple[Path, str]] = []
    for relative in CHAINS:
        path = ROOT / relative
        try:
            original = path.read_text(encoding="utf-8")
            fixed = normalized(original, relative)
        except (OSError, ValueError) as exc:
            errors.append(str(exc))
            continue
        if fixed != original:
            changes.append((path, fixed))
        if "### Explicit Principle-to-System Chain" not in fixed:
            errors.append(f"{relative}: explicit chain is missing")
        if "→" not in fixed:
            errors.append(f"{relative}: chain arrows are missing")

    if errors:
        print("Phase 12 chain-repair errors:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    if args.check and changes:
        print("Phase 12 chain repairs are not applied:", file=sys.stderr)
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}", file=sys.stderr)
        return 1

    if args.write:
        for path, fixed in changes:
            path.write_text(fixed, encoding="utf-8")

    if changes:
        print("Phase 12 chain repairs applied:")
        for path, _ in changes:
            print(f"- {path.relative_to(ROOT)}")
    else:
        print("Phase 12 chain repairs already applied.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
