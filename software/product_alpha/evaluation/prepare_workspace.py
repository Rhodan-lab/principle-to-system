#!/usr/bin/env python3
"""Create a private, build-bound Product Alpha cohort workspace outside the repo."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
import sys
from pathlib import Path
from typing import Sequence

PRODUCT_ALPHA_ROOT = Path(__file__).resolve().parents[1]
if str(PRODUCT_ALPHA_ROOT) not in sys.path:
    sys.path.insert(0, str(PRODUCT_ALPHA_ROOT))
import route_identity

CONTRACT = "principia-product-alpha-pilot-workspace/0.1"
ROUTE_ID = route_identity.DEFAULT_EVIDENCE_ROUTE
BUILD_ID_PATTERN = re.compile(r"^[0-9a-f]{64}$")
REPO_ROOT = Path(__file__).resolve().parents[3]


def validate_build_id(value: str) -> str:
    """Return a valid lowercase SHA-256 build ID or raise ValueError."""
    if not BUILD_ID_PATTERN.fullmatch(value):
        raise ValueError(
            "pilot build ID must be a 64-character lowercase SHA-256"
        )
    return value


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def _manifest(build_id: str, route_id: str) -> dict[str, object]:
    validated_route = route_identity.validate_evidence_route_id(route_id)
    route_slug = route_identity.software_route_id(validated_route)
    return {
        "contract": CONTRACT,
        "pilot_build_id": build_id,
        "route_id": validated_route,
        "privacy_boundaries": {
            "participant_names_allowed": False,
            "raw_sessions_committed_to_repository": False,
            "repository_output_allowed": False,
        },
        "paths": {
            "incoming_sessions": "incoming-sessions",
            "combined_jsonl": "verified/anonymous-sessions.jsonl",
            "intake_manifest": "verified/intake-manifest.json",
            "review_output_prefix": f"review/{route_slug}-review",
        },
    }


def _readme(workspace: Path, build_id: str, route_id: str) -> str:
    quote = shlex.quote
    route_slug = route_identity.software_route_id(route_id)
    workspace_arg = quote(str(workspace))
    handoff_arg = quote(
        str(workspace / "handoff" / f"{route_slug}-product-change")
    )
    return f"""# Principia Product Alpha private cohort workspace

This folder is outside the repository. Keep raw anonymous session records here and do not commit them.

- Route: `{route_id}`
- Expected pilot build ID: `{build_id}`
- Participant names, email addresses, account identifiers, and contact details are not allowed.

## Launch the bound pilot

Start the long-running loopback product through the workspace binding:

```bash
python3 software/product_alpha/launch_workspace.py \\
  --workspace {workspace_arg} \\
  --open
```

The launcher rebuilds Product Alpha, reads this `workspace.json`, and refuses to open a server unless the current deterministic build exactly matches `{build_id}`. This removes manual build-ID comparison from the supported cohort path. It stores no session data and does not modify the workspace manifest.

## Check the current stage

At any point, verify the workspace and print the next valid action without writing:

```bash
python3 software/product_alpha/evaluation/workspace_status.py \\
  --workspace {workspace_arg}
```

The status command recognizes prepared, collecting, ready-to-assemble, intake-verified, review-ready-for-decision, decision-verified, and handoff-verified stages. It validates every artifact required by the current stage, rejects partial or out-of-order evidence, and returns a machine-readable next action and command. It never creates, edits, or removes workspace files.

## Folder use

1. Place individual anonymous recorder exports (`.jsonl` or `.json`) in `incoming-sessions/`.

2. During collection, validate the current files without sealing the cohort:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py check \\
  --workspace {workspace_arg}
```

The check command fully validates every current export, rejects malformed, mixed-build, duplicate, personal-data-bearing, symlinked, or unsupported records, predicts the exact combined JSONL and source-record hashes, reports the valid session count and cohort status, and writes nothing. It is safe to repeat after each new session.

3. After collection is intentionally closed and the documented minimum has been reached, assemble the immutable cohort intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \\
  --workspace {workspace_arg}
```

Normal assembly refuses fewer than five valid sessions so a facilitator cannot accidentally lock an incomplete cohort while collection is still active. If the pilot must close early because recruitment or execution stopped, make that decision explicit:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \\
  --workspace {workspace_arg} \\
  --allow-incomplete
```

Assembly validates every file again, sorts accepted records by anonymous session ID, and writes `verified/anonymous-sessions.jsonl` plus `verified/intake-manifest.json`. The intake manifest hashes every raw export, the source-record set, and the combined JSONL. Source files are not changed. Existing verified outputs are never overwritten. `--allow-incomplete` records an intentional early closure; it does not make the evidence complete or eligible for planning advance.

4. Check the complete workspace evidence chain without writing review outputs:

```bash
python3 software/product_alpha/evaluation/review_workspace.py check \\
  --workspace {workspace_arg}
```

5. Create the private, de-identified human-review packet:

```bash
python3 software/product_alpha/evaluation/review_workspace.py \\
  --workspace {workspace_arg}
```

The workspace review command verifies this manifest, the exact build and route, every raw source hash, the intake manifest hash, the combined JSONL hash, session count, summary contract, and evidence status before writing `review/{route_slug}-review.json` and `review/{route_slug}-review.md`. It refuses changed evidence and never overwrites an existing review packet.

6. Check that the unchanged review packet is ready for a separate human decision record:

```bash
python3 software/product_alpha/evaluation/record_decision.py check \\
  --workspace {workspace_arg}
```

7. After reviewing the aggregate and private facilitator notes, record exactly one human action:

```bash
python3 software/product_alpha/evaluation/record_decision.py \\
  --workspace {workspace_arg} \\
  --action <allowed-primary-action> \\
  --reviewer "<role-or-initials>" \\
  --review-date YYYY-MM-DD \\
  --rationale "<de-identified rationale>" \\
  --next-checkpoint "<next checkpoint>"
```

Allowed primary actions are `revise-current-route`, `repeat-current-route-pilot`, `hold-current-route`, and `advance-to-next-product-planning-review`. The last action is rejected unless the cohort reached `ready-for-human-review` status. The command verifies the untouched review JSON/Markdown pair and the complete workspace evidence chain before writing `review/{route_slug}-review-decision.json`, `review/{route_slug}-review-decision.md`, and `review/{route_slug}-review-decision-receipt.json`. The receipt seals both decision-file hashes together with the review, intake, combined-cohort, and source-record bindings. It never edits the review packet, never overwrites a decision artifact, and never modifies the repository.

8. Verify the finished decision artifact trio against the unchanged workspace evidence:

```bash
python3 software/product_alpha/evaluation/record_decision.py verify \\
  --workspace {workspace_arg}
```

Verification rechecks every earlier evidence binding, canonical decision JSON, rendered decision Markdown, and receipt hash without writing. The receipt provides local tamper evidence for accidental or partial edits; it is not a digital signature, timestamp authority, or proof of authorship.

9. Prepare a de-identified candidate for a separate repository change. Check first without writing:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py check \\
  --workspace {workspace_arg} \\
  --output-prefix {handoff_arg}
```

Create the private candidate pair:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py \\
  --workspace {workspace_arg} \\
  --output-prefix {handoff_arg}
```

Then verify it against the unchanged decision and evidence chain:

```bash
python3 software/product_alpha/evaluation/prepare_handoff.py verify \\
  --workspace {workspace_arg} \\
  --output-prefix {handoff_arg}
```

The handoff JSON and Markdown contain the verified human action, de-identified aggregate metrics, revision signals, and evidence hashes. They exclude raw sessions, session identifiers, facilitator notes, custom confusion-tag text, reviewer identity, review date, private rationale, checkpoint text, and local workspace paths. The pair remains outside the repository. It does not authorize or perform a repository change; a human must inspect it and create a separate normal pull request.

Keep participant identities out of reviewer, rationale, and checkpoint text. A reviewer role or initials are sufficient.

`verify_cohort.py` and `prepare_review.py` remain lower-level tools. The workspace-bound commands are the supported end-to-end path because they prove that review, decision, and handoff artifacts still match the earlier intake and unchanged raw exports.

Do not treat an empty directory, an incomplete cohort, an intake manifest, a review packet, a decision record, a decision receipt, a repository handoff candidate, or this workspace manifest as proof of learning effectiveness. Human judgment remains required, and no generated artifact by itself authorizes a second route or public release.
"""


def prepare_workspace(
    workspace: Path,
    build_id: str,
    *,
    repo_root: Path = REPO_ROOT,
    route_id: str = ROUTE_ID,
) -> dict[str, object]:
    """Create one empty private workspace and return its manifest."""
    expected_build_id = validate_build_id(build_id)
    destination = workspace.expanduser().resolve(strict=False)
    repository = repo_root.resolve(strict=False)

    if _is_within(destination, repository):
        raise ValueError("workspace must be outside the repository")
    if destination.exists():
        raise FileExistsError(f"workspace already exists: {destination}")

    manifest = _manifest(expected_build_id, route_id)
    try:
        (destination / "incoming-sessions").mkdir(parents=True, exist_ok=False)
        (destination / "verified").mkdir()
        (destination / "review").mkdir()
        (destination / "workspace.json").write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        (destination / "README.md").write_text(
            _readme(destination, expected_build_id, route_id),
            encoding="utf-8",
        )
    except Exception:
        if destination.exists():
            shutil.rmtree(destination)
        raise
    return manifest


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--workspace",
        type=Path,
        required=True,
        help="new private workspace directory outside this repository",
    )
    parser.add_argument(
        "--expect-build-id",
        required=True,
        help="full 64-character Pilot build ID printed by run_pilot.py",
    )
    parser.add_argument(
        "--route",
        default=route_identity.DEFAULT_SOFTWARE_ROUTE,
        choices=route_identity.SUPPORTED_SOFTWARE_ROUTES,
        help="packaged learner route bound to this workspace",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = prepare_workspace(
            args.workspace,
            args.expect_build_id,
            route_id=route_identity.evidence_route_id(args.route),
        )
    except (OSError, ValueError) as exc:
        raise SystemExit(f"workspace creation failed: {exc}") from exc

    print(
        json.dumps(
            {
                "contract": manifest["contract"],
                "decision": "private-workspace-created",
                "pilot_build_id": manifest["pilot_build_id"],
                "workspace": str(args.workspace.expanduser().resolve(strict=False)),
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
