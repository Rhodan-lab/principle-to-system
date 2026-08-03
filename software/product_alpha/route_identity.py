#!/usr/bin/env python3
"""Canonical software-route and evidence-route identities for Product Alpha."""
from __future__ import annotations

SOFTWARE_TO_EVIDENCE_ROUTE = {
    "refrigerator": "refrigerator-v1",
    "distributed-information": "distributed-information-v1",
}
EVIDENCE_TO_SOFTWARE_ROUTE = {
    evidence: software for software, evidence in SOFTWARE_TO_EVIDENCE_ROUTE.items()
}
DEFAULT_SOFTWARE_ROUTE = "refrigerator"
DEFAULT_EVIDENCE_ROUTE = SOFTWARE_TO_EVIDENCE_ROUTE[DEFAULT_SOFTWARE_ROUTE]
SUPPORTED_SOFTWARE_ROUTES = tuple(SOFTWARE_TO_EVIDENCE_ROUTE)
SUPPORTED_EVIDENCE_ROUTES = tuple(EVIDENCE_TO_SOFTWARE_ROUTE)


def evidence_route_id(software_route: str) -> str:
    """Return the evidence identity for one supported packaged route."""
    try:
        return SOFTWARE_TO_EVIDENCE_ROUTE[software_route]
    except KeyError as exc:
        allowed = ", ".join(SUPPORTED_SOFTWARE_ROUTES)
        raise ValueError(
            f"unsupported Product Alpha software route {software_route!r}; expected one of: {allowed}"
        ) from exc


def software_route_id(evidence_route: str) -> str:
    """Return the packaged route name for one supported evidence identity."""
    try:
        return EVIDENCE_TO_SOFTWARE_ROUTE[evidence_route]
    except KeyError as exc:
        allowed = ", ".join(SUPPORTED_EVIDENCE_ROUTES)
        raise ValueError(
            f"unsupported Product Alpha evidence route {evidence_route!r}; expected one of: {allowed}"
        ) from exc


def validate_evidence_route_id(value: object) -> str:
    """Return a supported evidence route ID or raise ValueError."""
    if not isinstance(value, str):
        raise ValueError("route_id must be text")
    software_route_id(value)
    return value
