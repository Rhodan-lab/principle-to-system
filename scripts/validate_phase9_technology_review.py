#!/usr/bin/env python3
"""Validate the focused Phase 9 review of Technology Modules 17–20."""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parent.parent
REVIEW_DATE = "2026-07-26"
FILENAMES = ("overview.md", "technology.md", "explore.md")
MODULES = {
    "17-materials-manufacturing": (["06-matter-quantum", "07-chemical-bonding", "12-fluids-materials"], ["18-semiconductors-electronics"]),
    "18-semiconductors-electronics": (["06-matter-quantum", "10-electricity-magnetism", "17-materials-manufacturing"], ["19-software-ai", "20-sensors-control-infrastructure"]),
    "19-software-ai": (["04-probability-statistics", "05-computation-algorithms", "18-semiconductors-electronics"], ["20-sensors-control-infrastructure"]),
    "20-sensors-control-infrastructure": (["10-electricity-magnetism", "11-waves-signals", "18-semiconductors-electronics", "19-software-ai"], []),
}
REQUIRED_HEADINGS = {
    "overview.md": (
        "central questions", "observable phenomena", "essential concepts", "mechanisms and causal chains",
        "important quantities", "mathematical models and equations", "definitions of symbols and units",
        "assumptions and approximations", "spatial and temporal scales", "common misconceptions",
        "connections to other modules", "sources",
    ),
    "technology.md": (
        "scientific principles used", "engineering problem", "main components", "how the components interact",
        "matter, energy, force, or information flow", "system architecture", "design constraints",
        "performance and efficiency", "reliability and failure modes", "safety principles",
        "environmental and lifecycle considerations", "connections to other technologies", "sources",
    ),
    "explore.md": (
        "observation prompts", "prediction questions", "worked reasoning examples", "thought experiments",
        "household and browser-based explorations", "model-building prompts", "self-explanation questions",
        "transfer questions", "suggested learning paths", "reasoning notes", "sources",
    ),
}
BANNED = (
    "Wikipedia.",
    "18-solid-mechanics",
    "19-thermodynamics",
    "19-computing-architecture",
    "bend it back and forth repeatedly at the same spot until it breaks",
    "heat a piece of high-carbon steel until it glows red",
    "open it up and identify the printed circuit board",
    "ping google.com",
    "try balancing a long stick",
    "capacity c approaches infinity",
    "chip will melt",
    "depletion region devoid of mobile charge carriers",
    "minimum gate voltage required to create a conducting channel",
    "simply by processing more examples",
    "no single point of control or failure",
    "exact angular position",
    "predicting future error",
    "without melting",
    "unprecedented geometric complexity",
    "automatically secure",
)
REQUIRED_MARKERS = {
    "technology/17-materials-manufacturing/overview.md": (
        "plane-strain mode-I fracture toughness", "empirical Hall–Petch relation", "chemical-potential gradients",
    ),
    "technology/17-materials-manufacturing/technology.md": (
        "process qualification", "Learners should not operate", "digital thread",
    ),
    "technology/17-materials-manufacturing/explore.md": (
        "do not heat or quench metal", "non-safety-critical", "Do not extrapolate",
    ),
    "technology/18-semiconductors-electronics/overview.md": (
        "Fermi level", "Threshold is not a hard on/off boundary", "built-in potential is not directly measured",
    ),
    "technology/18-semiconductors-electronics/technology.md": (
        "P_{dyn}=\\alpha C V^2 f", "node names", "Learners should use simulations",
    ),
    "technology/18-semiconductors-electronics/explore.md": (
        "Virtual teardown", "Thermal throttling or shutdown", "Semiconductor metrology",
    ),
    "technology/19-software-ai/overview.md": (
        "asymptotic limits", "TCP does not guarantee", "distribution shift",
    ),
    "technology/19-software-ai/technology.md": (
        "human oversight", "Write-ahead logging supports recovery only", "Accuracy on one test set is insufficient",
    ),
    "technology/19-software-ai/explore.md": (
        "Do not probe private systems", "fictional profile", "appeal process",
    ),
    "technology/20-sensors-control-infrastructure/overview.md": (
        "measure–condition–sample–estimate–decide–act–verify", "actuator saturation", "grid-forming or grid-following",
    ),
    "technology/20-sensors-control-infrastructure/technology.md": (
        "Synthetic inertia is not an automatic property", "Industrial control systems require cybersecurity", "fail-operational",
    ),
    "technology/20-sensors-control-infrastructure/explore.md": (
        "public safe distance", "anti-windup", "do not balance long objects",
    ),
}
URL_RE = re.compile(r"https?://[^\s)\]>]+")
HEADING_RE = re.compile(r"^##\s+(?:\d+\.\s*)?(.+?)\s*$", re.MULTILINE)
INDEX_RE = re.compile(r"^\|\s*(\d{2})\s*\|.*\|\s*(Draft|Reviewed|Complete|Blocked)\s*\|\s*$", re.I)


@dataclass
class Result:
    errors: list[str]
    warnings: list[str]


def normalize_url(raw: str) -> str:
    raw = raw.rstrip(".,;:")
    parts = urlsplit(raw)
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower(), parts.netloc.lower(), path, parts.query, ""))


def parse_frontmatter(text: str, rel: str, result: Result) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        result.errors.append(f"{rel}: missing frontmatter")
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        result.errors.append(f"{rel}: unterminated frontmatter")
        return {}, text
    data: dict[str, object] = {}
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            result.errors.append(f"{rel}: malformed frontmatter line: {line}")
            continue
        key, value = line.split(":", 1)
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            data[key.strip()] = [item.strip().strip("\"'") for item in value[1:-1].split(",") if item.strip()]
        else:
            data[key.strip()] = value.strip("\"'")
    return data, text[end + 5 :]


def ledger_urls(result: Result) -> set[str]:
    path = ROOT / "sources" / "source-ledger.md"
    locators: set[str] = set()
    started = False
    for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if line.startswith("| Title |"):
            started = True
            continue
        if not started or not line.startswith("|") or re.match(r"^\|\s*-", line):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) != 8:
            result.errors.append(f"sources/source-ledger.md:{line_no}: expected 8 columns")
            continue
        if cells[3].startswith(("http://", "https://")):
            locators.add(normalize_url(cells[3]))
    return locators


def expected_slug(module: str, filename: str) -> str:
    return module if filename == "overview.md" else f"{module}-{filename.removesuffix('.md')}"


def check_files(result: Result, locators: set[str]) -> None:
    seen_slugs: set[str] = set()
    for module, (prerequisites, connections) in MODULES.items():
        for filename in FILENAMES:
            path = ROOT / "technology" / module / filename
            rel = path.relative_to(ROOT).as_posix()
            if not path.exists():
                result.errors.append(f"{rel}: missing")
                continue
            text = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text, rel, result)
            expected = {
                "slug": expected_slug(module, filename),
                "module": f"Module {module[:2]}",
                "domain": "technology",
                "status": "reviewed",
                "last_reviewed": REVIEW_DATE,
                "content_license": "CC-BY-4.0",
            }
            for key, value in expected.items():
                if fm.get(key) != value:
                    result.errors.append(f"{rel}: {key}={fm.get(key)!r}, expected {value!r}")
            if fm.get("prerequisites") != prerequisites:
                result.errors.append(f"{rel}: prerequisites={fm.get('prerequisites')!r}, expected {prerequisites!r}")
            if fm.get("connections") != connections:
                result.errors.append(f"{rel}: connections={fm.get('connections')!r}, expected {connections!r}")
            slug = str(fm.get("slug", ""))
            if slug in seen_slugs:
                result.errors.append(f"{rel}: duplicate slug {slug}")
            seen_slugs.add(slug)

            headings = {re.sub(r"[`*_]", "", match.group(1)).strip().lower() for match in HEADING_RE.finditer(body)}
            for required in REQUIRED_HEADINGS[filename]:
                if not any(required in heading for heading in headings):
                    result.errors.append(f"{rel}: missing heading containing '{required}'")
            if "Phase 9 review boundaries and validity limits" not in body:
                result.errors.append(f"{rel}: Phase 9 validity-limit section missing")

            source_match = re.search(r"^##\s+(?:\d+\.\s*)?Sources\s*$", body, re.I | re.M)
            if not source_match:
                result.errors.append(f"{rel}: source section missing")
            else:
                direct = {normalize_url(url) for url in URL_RE.findall(body[source_match.end():])}
                if len(direct) < 6:
                    result.errors.append(f"{rel}: only {len(direct)} direct source URLs; minimum is 6")
                for url in sorted(direct - locators):
                    result.errors.append(f"{rel}: source absent from ledger: {url}")

            lower = text.lower()
            for phrase in BANNED:
                if phrase.lower() in lower:
                    result.errors.append(f"{rel}: prohibited legacy, unsafe, or weak text: {phrase}")
            for marker in REQUIRED_MARKERS.get(rel, ()):
                if marker.lower() not in lower:
                    result.errors.append(f"{rel}: required reviewed marker missing: {marker}")
            if filename == "explore.md" and len(body.split()) < 500:
                result.warnings.append(f"{rel}: exploration is unusually short")


def check_index(result: Result) -> None:
    statuses: dict[str, str] = {}
    for line in (ROOT / "INDEX.md").read_text(encoding="utf-8").splitlines():
        match = INDEX_RE.match(line)
        if match:
            number, status = match.groups()
            statuses[number] = status.lower()
    for number in [f"{value:02d}" for value in range(1, 21)]:
        if statuses.get(number) != "reviewed":
            result.errors.append(f"INDEX.md: Module {number} must be Reviewed")
    if any(status == "complete" for status in statuses.values()):
        result.errors.append("INDEX.md: no core module may be Complete before release validation")


def check_artifacts(result: Result) -> None:
    required = (
        ROOT / "sources" / "phase-9-reviewed-sources.json",
        ROOT / "scripts" / "apply_phase9_review_sources.py",
        ROOT / "scripts" / "apply_phase9_technology_review.py",
        ROOT / "scripts" / "validate_phase9_technology_review.py",
        ROOT / "reports" / "phase-9-technology-review.md",
        ROOT / "reports" / "phase-9-technology-sources.json",
    )
    for path in required:
        if not path.exists():
            result.errors.append(f"{path.relative_to(ROOT)}: missing")

    source_report = ROOT / "reports" / "phase-9-technology-sources.json"
    if source_report.exists():
        try:
            report = json.loads(source_report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result.errors.append(f"phase-9 source report invalid JSON: {exc}")
        else:
            if report.get("errors"):
                result.errors.append(f"phase-9 source report contains errors: {report['errors']}")
            if report.get("ledger_records_before") != 131 or report.get("ledger_records_after") != 143:
                result.errors.append("phase-9 source report must preserve the 131-to-143 transition")
            additions = report.get("records_added")
            if not isinstance(additions, list) or len(additions) != 12:
                result.errors.append("phase-9 source report must preserve twelve additions")

    state_path = ROOT / "PROJECT_STATE.md"
    state = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    for marker in (
        "Phase 9 Technology review implemented",
        "Modules 17–20: **Reviewed**",
        "Modules 01–20: **Reviewed**",
        "**143 records**",
        "Phase 10",
    ):
        if marker not in state:
            result.errors.append(f"PROJECT_STATE.md: missing marker: {marker}")


def main() -> int:
    result = Result([], [])
    locators = ledger_urls(result)
    check_files(result, locators)
    check_index(result)
    check_artifacts(result)

    if result.warnings:
        print("Phase 9 warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 9 review errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 9 review passed: 4 modules, 12 reviewed files, {len(locators)} source locators.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
