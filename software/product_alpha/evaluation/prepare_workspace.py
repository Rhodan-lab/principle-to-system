#!/usr/bin/env python3
"""Create a private, build-bound Product Alpha cohort workspace outside the repo."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import shutil
from pathlib import Path
from typing import Sequence

CONTRACT = "principia-product-alpha-pilot-workspace/0.1"
ROUTE_ID = "refrigerator-v1"
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
    return {
        "contract": CONTRACT,
        "pilot_build_id": build_id,
        "route_id": route_id,
        "privacy_boundaries": {
            "participant_names_allowed": False,
            "raw_sessions_committed_to_repository": False,
            "repository_output_allowed": False,
        },
        "paths": {
            "incoming_sessions": "incoming-sessions",
            "combined_jsonl": "verified/anonymous-sessions.jsonl",
            "intake_manifest": "verified/intake-manifest.json",
            "review_output_prefix": "review/refrigerator-review",
        },
    }


def _readme(workspace: Path, build_id: str) -> str:
    combined = workspace / "verified" / "anonymous-sessions.jsonl"
    review_prefix = workspace / "review" / "refrigerator-review"
    quote = shlex.quote
    return f"""# Principia Product Alpha private cohort workspace

This folder is outside the repository. Keep raw anonymous session records here and do not commit them.

- Route: `{ROUTE_ID}`
- Expected pilot build ID: `{build_id}`
- Participant names, email addresses, account identifiers, and contact details are not allowed.

## Folder use

1. Place individual anonymous recorder exports (`.jsonl` or `.json`) in `incoming-sessions/`.
2. Validate and assemble the immutable cohort intake:

```bash
python3 software/product_alpha/evaluation/assemble_workspace.py \\
  --workspace {quote(str(workspace))}
```

This command validates every file, rejects malformed, mixed-build, duplicate, or personal-data-bearing records, sorts accepted records by anonymous session ID, and writes `verified/anonymous-sessions.jsonl` plus `verified/intake-manifest.json`. The intake manifest hashes every raw export and the combined JSONL. Source files are not changed. Existing verified outputs are never overwritten.

3. Verify the cohort against the launcher build:

```bash
python3 software/product_alpha/evaluation/verify_cohort.py \\
  --input {quote(str(combined))} \\
  --expect-build-id {build_id} \\
  --format markdown
```

4. Create the private, de-identified human-review packet:

```bash
python3 software/product_alpha/evaluation/prepare_review.py \\
  --input {quote(str(combined))} \\
  --expect-build-id {build_id} \\
  --output-prefix {quote(str(review_prefix))}
```

Do not treat an empty directory, an incomplete cohort, an intake manifest, or this workspace manifest as learner evidence. Human review remains required.
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
            _readme(destination, expected_build_id),
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
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        manifest = prepare_workspace(args.workspace, args.expect_build_id)
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
