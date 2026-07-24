#!/usr/bin/env python3
"""
Principle to System — Repository Validator

Checks:
  - Required files exist
  - Required module sections present
  - YAML frontmatter validity
  - Duplicate slugs
  - Relative internal links resolve
  - Missing source entries
  - Malformed Markdown links
  - Incomplete status markers
"""

import os
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

REPO_ROOT = Path(__file__).resolve().parent.parent

REQUIRED_TOP_FILES = [
    "README.md",
    "INDEX.md",
    "PROJECT_STATE.md",
    "CONTENT_GUIDE.md",
    "SOURCE_POLICY.md",
    "CONTRIBUTING.md",
    "CITATION.cff",
    "LICENSE",
    "LICENSE-CONTENT",
]

MODULE_DIRS = [
    "foundations/01-scientific-reasoning",
    "foundations/02-measurement-uncertainty",
    "foundations/03-mathematical-models",
    "foundations/04-probability-statistics",
    "foundations/05-computation-algorithms",
    "science/06-matter-quantum",
    "science/07-chemical-bonding",
    "science/08-energy-thermodynamics",
    "science/09-motion-forces",
    "science/10-electricity-magnetism",
    "science/11-waves-signals",
    "science/12-fluids-materials",
    "science/13-cells-bioenergetics",
    "science/14-dna-evolution",
    "science/15-ecosystems-complex-systems",
    "science/16-earth-planetary",
    "technology/17-materials-manufacturing",
    "technology/18-semiconductors-electronics",
    "technology/19-software-ai",
    "technology/20-sensors-control-infrastructure",
]

MODULE_FILES = ["overview.md", "technology.md", "explore.md"]

OVERVIEW_SECTIONS = [
    "central questions",
    "observable phenomena",
    "essential concepts",
    "mechanisms",
    "quantities",
    "mathematical models",
    "symbols",
    "assumptions",
    "scales",
    "misconceptions",
    "connections",
    "sources",
]

TECHNOLOGY_SECTIONS = [
    "scientific principles",
    "engineering problem",
    "components",
    "interact",
    "flow",
    "architecture",
    "constraints",
    "performance",
    "reliability",
    "safety",
    "environmental",
    "connections",
    "sources",
]

EXPLORE_SECTIONS = [
    "observation",
    "prediction",
    "worked",
    "thought experiment",
    "household",
    "model-building",
    "self-explanation",
    "transfer",
    "learning path",
    "reasoning",
]

VALID_STATUSES = {"draft", "reviewed", "complete", "blocked"}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

errors = []
warnings = []


def error(msg: str):
    errors.append(msg)


def warn(msg: str):
    warnings.append(msg)


def extract_frontmatter(filepath: Path):
    """Extract YAML frontmatter as raw text and return (frontmatter_dict, content)."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except Exception as e:
        error(f"Cannot read {filepath}: {e}")
        return None, ""

    if not text.startswith("---"):
        return None, text

    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, text

    fm_text = parts[1].strip()
    content = parts[2]

    # Simple YAML parser (no external deps)
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if ":" in line:
            key, _, value = line.partition(":")
            fm[key.strip()] = value.strip().strip('"').strip("'")

    return fm, content


def check_sections(filepath: Path, content: str, required_keywords: list, file_type: str):
    """Check that content contains headings or text matching required section keywords."""
    content_lower = content.lower()
    for keyword in required_keywords:
        if keyword.lower() not in content_lower:
            warn(f"{filepath.relative_to(REPO_ROOT)}: missing expected section keyword '{keyword}' in {file_type}")


def find_md_links(content: str):
    """Find all Markdown links [text](url) and return list of (text, url)."""
    return re.findall(r'\[([^\]]*)\]\(([^)]+)\)', content)


# ---------------------------------------------------------------------------
# Checks
# ---------------------------------------------------------------------------

def check_required_files():
    """Check that all required top-level files exist."""
    for fname in REQUIRED_TOP_FILES:
        if not (REPO_ROOT / fname).exists():
            error(f"Missing required file: {fname}")


def check_module_files():
    """Check that all 60 module files exist."""
    for mdir in MODULE_DIRS:
        for mfile in MODULE_FILES:
            fpath = REPO_ROOT / mdir / mfile
            if not fpath.exists():
                error(f"Missing module file: {mdir}/{mfile}")


def check_frontmatter_and_slugs():
    """Check YAML frontmatter validity and detect duplicate slugs."""
    slugs = {}
    md_files = list(REPO_ROOT.rglob("*.md"))

    for fpath in md_files:
        # Skip non-content files
        rel = fpath.relative_to(REPO_ROOT)
        parts = rel.parts
        if parts[0] in (".github", "scripts"):
            continue
        if fpath.name in ("README.md", "INDEX.md", "PROJECT_STATE.md",
                          "CONTENT_GUIDE.md", "SOURCE_POLICY.md",
                          "CONTRIBUTING.md", "source-ledger.md"):
            continue

        fm, content = extract_frontmatter(fpath)
        if fm is None:
            warn(f"{rel}: no YAML frontmatter found")
            continue

        # Check required fields
        for field in ("title", "slug", "status"):
            if field not in fm or not fm[field]:
                warn(f"{rel}: frontmatter missing '{field}'")

        # Check status value
        status = fm.get("status", "")
        if status and status not in VALID_STATUSES:
            error(f"{rel}: invalid status '{status}' (allowed: {VALID_STATUSES})")

        # Check duplicate slugs
        slug = fm.get("slug", "")
        if slug:
            if slug in slugs:
                error(f"{rel}: duplicate slug '{slug}' (also in {slugs[slug]})")
            else:
                slugs[slug] = str(rel)


def check_module_sections():
    """Check that module files contain expected section keywords."""
    for mdir in MODULE_DIRS:
        overview = REPO_ROOT / mdir / "overview.md"
        tech = REPO_ROOT / mdir / "technology.md"
        explore = REPO_ROOT / mdir / "explore.md"

        if overview.exists():
            _, content = extract_frontmatter(overview)
            check_sections(overview, content, OVERVIEW_SECTIONS, "overview.md")

        if tech.exists():
            _, content = extract_frontmatter(tech)
            check_sections(tech, content, TECHNOLOGY_SECTIONS, "technology.md")

        if explore.exists():
            _, content = extract_frontmatter(explore)
            check_sections(explore, content, EXPLORE_SECTIONS, "explore.md")


def check_internal_links():
    """Check that relative Markdown links resolve to existing files."""
    md_files = list(REPO_ROOT.rglob("*.md"))

    for fpath in md_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        links = find_md_links(content)
        for text, url in links:
            # Skip external links
            if url.startswith("http://") or url.startswith("https://"):
                continue
            # Skip anchors
            if url.startswith("#"):
                continue

            # Resolve relative path
            target = (fpath.parent / url.split("#")[0]).resolve()
            if not target.exists():
                warn(f"{fpath.relative_to(REPO_ROOT)}: broken link [{text}]({url})")


def check_source_ledger():
    """Check that source ledger exists and has entries."""
    ledger = REPO_ROOT / "sources" / "source-ledger.md"
    if not ledger.exists():
        error("Missing sources/source-ledger.md")
        return

    content = ledger.read_text(encoding="utf-8")
    # Count table rows (lines starting with |, excluding header and separator)
    rows = [l for l in content.split("\n") if l.startswith("|") and "---" not in l and "Title" not in l]
    if len(rows) < 20:
        warn(f"Source ledger has only {len(rows)} entries (expected ≥20 for 20 modules)")


def check_malformed_links():
    """Check for common Markdown link syntax errors."""
    md_files = list(REPO_ROOT.rglob("*.md"))
    # Pattern for malformed links: [text]( ) or [text](  missing closing paren
    malformed_pattern = re.compile(r'\[[^\]]*\]\([^)]*$', re.MULTILINE)

    for fpath in md_files:
        try:
            content = fpath.read_text(encoding="utf-8")
        except Exception:
            continue

        for i, line in enumerate(content.split("\n"), 1):
            if malformed_pattern.search(line):
                # Check if it's actually malformed (not just a long line)
                open_brackets = line.count("[")
                close_parens = line.count(")")
                open_parens = line.count("(")
                if open_parens > close_parens:
                    warn(f"{fpath.relative_to(REPO_ROOT)}:{i}: possibly malformed link")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    print(f"Validating repository at: {REPO_ROOT}\n")

    check_required_files()
    check_module_files()
    check_frontmatter_and_slugs()
    check_module_sections()
    check_internal_links()
    check_source_ledger()
    check_malformed_links()

    # Report
    if warnings:
        print(f"⚠  {len(warnings)} warning(s):")
        for w in warnings:
            print(f"   {w}")
        print()

    if errors:
        print(f"✗  {len(errors)} error(s):")
        for e in errors:
            print(f"   {e}")
        print()
        print("VALIDATION FAILED")
        sys.exit(1)
    else:
        print(f"✓  Validation passed ({len(warnings)} warnings, 0 errors)")
        sys.exit(0)


if __name__ == "__main__":
    main()
