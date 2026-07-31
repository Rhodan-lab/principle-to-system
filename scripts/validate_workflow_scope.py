#!/usr/bin/env python3
"""Validate deterministic GitHub Actions ownership and Product Alpha path scope."""

from __future__ import annotations

import json

from apply_ci_product_alpha_scope import ScopeError, validate_policy


def main() -> None:
    try:
        summary = validate_policy()
    except (OSError, ValueError, ScopeError) as exc:
        raise SystemExit(f"workflow scope validation failed: {exc}") from exc
    print("Workflow scope validation passed")
    print(json.dumps(summary, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
