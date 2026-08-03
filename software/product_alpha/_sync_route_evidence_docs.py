#!/usr/bin/env python3
"""Synchronize supporting Product Alpha docs after distributed evidence-chain verification."""
from pathlib import Path


def replace_once(path: Path, old: str, new: str, label: str) -> None:
    text = path.read_text(encoding="utf-8")
    count = text.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected one anchor, found {count}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


replace_once(
    Path("README.md"),
    "The former milestone `make-facilitator-and-evidence-records-route-aware` is complete. The next concrete verification task is `prove-distributed-information-evidence-chain-end-to-end`: add one deterministic synthetic integration fixture that exercises preparation, intake, review, decision, receipt, handoff, and verification without pretending the fixture is real learner evidence.",
    "The milestones `make-facilitator-and-evidence-records-route-aware` and `prove-distributed-information-evidence-chain-end-to-end` are complete. A deterministic synthetic fixture now verifies distributed-information preparation, intake, review, decision, receipt, handoff, route-specific filenames, privacy redaction, and route-drift rejection. The fixture is test data, not real learner evidence. Further work is defect-driven; no third route, Atlas expansion, or public deployment is authorized without a concrete requirement.",
    "root Product Alpha completion state",
)

replace_once(
    Path("software/product_alpha/README.md"),
    """## Current verification boundary

Route identity is now bound through learner packaging, the facilitator recorder, Pilot Lab, summaries, workspace intake, and workspace launch. Existing refrigerator records remain valid.

The remaining test gap is a full distributed-information fixture through the unchanged private review, decision, receipt, and handoff chain. Lower-level route tests already cover package identity, rubric identity, session validation, mixed-route rejection, summary identity, route-specific workspace paths, and route-bound launch.

The next concrete milestone is:

```text
prove-distributed-information-evidence-chain-end-to-end
```

This means adding a deterministic synthetic integration fixture. It does not mean inventing real learner evidence.
""",
    """## Verified evidence boundary

Route identity is bound through learner packaging, the facilitator recorder, Pilot Lab, summaries, workspace intake, review, human-decision records, receipts, handoff candidates, and workspace launch. Existing refrigerator records remain valid.

A deterministic synthetic distributed-information fixture exercises the private chain from workspace preparation through assembly, review, decision, receipt, handoff, and verification. It proves route-specific filenames, `distributed-information-v1` propagation, canonical distributed confusion tags, privacy redaction, and fail-closed route-drift handling.

The fixture is test data only. It is not real learner evidence and does not support a learning-effectiveness claim. No known route-identity, rubric-binding, or distributed evidence-chain defect remains open; further work must respond to a concrete usability, accessibility, privacy, security, determinism, operator-safety, canonical-content, or provenance finding.
""",
    "package verification boundary",
)

replace_once(
    Path("software/product_alpha/PILOT.md"),
    "The next repository verification is one deterministic synthetic distributed-information fixture through preparation, assembly, review, decision, receipt, handoff, and verification. That fixture is test data only and must not be represented as real learner evidence.",
    "A deterministic synthetic distributed-information fixture now verifies preparation, assembly, review, decision, receipt, handoff, verification, route-specific filenames, privacy redaction, and route-drift rejection. That fixture is test data only and must not be represented as real learner evidence.",
    "optional pilot verification state",
)
