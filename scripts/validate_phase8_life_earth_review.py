#!/usr/bin/env python3
"""Validate the focused Phase 8 review of Modules 13–16."""
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
    "13-cells-bioenergetics": (["07-chemical-bonding", "08-energy-thermodynamics"], ["14-dna-evolution", "15-ecosystems-complex-systems"]),
    "14-dna-evolution": (["07-chemical-bonding", "13-cells-bioenergetics"], ["15-ecosystems-complex-systems"]),
    "15-ecosystems-complex-systems": (["04-probability-statistics", "13-cells-bioenergetics", "14-dna-evolution"], ["16-earth-planetary"]),
    "16-earth-planetary": (["08-energy-thermodynamics", "09-motion-forces", "12-fluids-materials", "15-ecosystems-complex-systems"], []),
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
    "Wikipedia contributors",
    "cyanide",
    "rubbing alcohol",
    "stretch a balloon over the mouth of the bottle",
    "hermetically sealed glass jar",
    "10% rule",
    "exact duplication of their genetic material",
    "DNA polymerase III then",
    "primary driver of **plate tectonics**",
    "transparent to shortwave radiation",
    "over 3,800 active floats",
    ">90% removal of BOD",
    "70-90% removal of nitrogen",
    "sustain human life indefinitely",
    "14-genetics-molecular-biology",
    "15-physiology-systems",
    "15-ecology-systems",
    "16-climate-earth-systems",
    "18-agricultural-engineering",
    "22-environmental-control-systems",
)
REQUIRED_MARKERS = {
    "science/13-cells-bioenergetics/overview.md": (
        "compound kinetic parameter", "model-dependent accounting quantity", "activity ratio",
    ),
    "science/13-cells-bioenergetics/explore.md": (
        "without naming or handling any real inhibitor", "loosely covered cup", "not automatically a direct affinity",
    ),
    "science/14-dna-evolution/overview.md": (
        "bacterial polymerase names are not universal", "coding or non-coding RNA", "chosen non-negative scale",
    ),
    "science/14-dna-evolution/explore.md": (
        "synonymous substitution", "anonymised or fictional pedigree", "Replication-fidelity model",
    ),
    "science/15-ecosystems-complex-systems/overview.md": (
        "transfer efficiency varying", "neutrally stable closed orbits", "dimensionless control parameter",
    ),
    "science/15-ecosystems-complex-systems/technology.md": (
        "site-specific evidence", "indefinite closure is not assumed", "reliability must be demonstrated",
    ),
    "science/16-earth-planetary/overview.md": (
        "top of the atmosphere", "not a direct prediction of surface temperature", "no single mechanism explains every plate",
    ),
    "science/16-earth-planetary/technology.md": (
        "Forecast and projection uncertainty", "architecture- and solver-dependent", "changing international array",
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
            path = ROOT / "science" / module / filename
            rel = path.relative_to(ROOT).as_posix()
            if not path.exists():
                result.errors.append(f"{rel}: missing")
                continue
            text = path.read_text(encoding="utf-8")
            fm, body = parse_frontmatter(text, rel, result)
            expected = {
                "slug": expected_slug(module, filename),
                "module": f"Module {module[:2]}",
                "domain": "science",
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

            source_match = re.search(r"^##\s+(?:\d+\.\s*)?Sources\s*$", body, re.I | re.M)
            if not source_match:
                result.errors.append(f"{rel}: source section missing")
            else:
                direct = {normalize_url(url) for url in URL_RE.findall(body[source_match.end():])}
                if len(direct) < 4:
                    result.errors.append(f"{rel}: only {len(direct)} direct source URLs; minimum is 4")
                for url in sorted(direct - locators):
                    result.errors.append(f"{rel}: source absent from ledger: {url}")

            lower = text.lower()
            for phrase in BANNED:
                if phrase.lower() in lower:
                    result.errors.append(f"{rel}: prohibited legacy or unsafe text: {phrase}")
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
    for number in [f"{value:02d}" for value in range(1, 17)]:
        if statuses.get(number) != "reviewed":
            result.errors.append(f"INDEX.md: Module {number} must be Reviewed")
    for number in ("17", "18", "19", "20"):
        if statuses.get(number) != "draft":
            result.errors.append(f"INDEX.md: Module {number} must remain Draft")


def check_artifacts(result: Result) -> None:
    required = (
        ROOT / "sources" / "phase-8-reviewed-sources.json",
        ROOT / "scripts" / "apply_phase8_review_sources.py",
        ROOT / "scripts" / "apply_phase8_life_earth_review.py",
        ROOT / "reports" / "phase-8-life-earth-review.md",
        ROOT / "reports" / "phase-8-life-earth-sources.json",
    )
    for path in required:
        if not path.exists():
            result.errors.append(f"{path.relative_to(ROOT)}: missing")

    source_report = ROOT / "reports" / "phase-8-life-earth-sources.json"
    if source_report.exists():
        try:
            report = json.loads(source_report.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            result.errors.append(f"phase-8 source report invalid JSON: {exc}")
        else:
            if report.get("errors"):
                result.errors.append(f"phase-8 source report contains errors: {report['errors']}")
            if report.get("ledger_records_after") != 131:
                result.errors.append(
                    f"phase-8 source report ledger_records_after={report.get('ledger_records_after')!r}, expected 131"
                )

    state_path = ROOT / "PROJECT_STATE.md"
    state = state_path.read_text(encoding="utf-8") if state_path.exists() else ""
    for marker in (
        "Phase 8 Life and Earth Systems review implemented",
        "Modules 13–16: **Reviewed**",
        "Modules 17–20: **Draft**",
        "**131 records**",
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
        print("Phase 8 warnings:")
        for warning in result.warnings:
            print(f"- {warning}")
    if result.errors:
        print("Phase 8 review errors:", file=sys.stderr)
        for error in result.errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print(f"Phase 8 review passed: 4 modules, 12 reviewed files, {len(locators)} source locators.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
