#!/usr/bin/env python3
"""Dependency-free static reference site for the Principia repository."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import re
import shutil
from dataclasses import dataclass
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path, PurePosixPath
from typing import Callable, Iterable
from urllib.parse import quote, urlsplit

MODULE_ROOTS = ("foundations", "science", "technology")
SYNTHESIS_ROOTS = ("pathways", "concepts", "maps")
EXPERIENCE_ROOTS = ("system-dossiers", "failure-atlas", "investigations", "design-challenges")
MODULE_FILES = ("overview.md", "technology.md", "explore.md")
BUILD_MARKER = ".principia-build"
SAFE_SCHEMES = {"http", "https", "mailto"}


@dataclass(frozen=True)
class Document:
    source_path: str
    collection: str
    title: str
    slug: str
    status: str
    module_id: str | None
    role: str
    prerequisites: tuple[str, ...]
    connections: tuple[str, ...]
    body: str
    headings: tuple[str, ...]

    @property
    def output_path(self) -> str:
        return f"documents/{quote(self.slug, safe='')}.html"

    @property
    def searchable_text(self) -> str:
        plain = re.sub(r"[#*_>`~|$\\[\](){}]", " ", self.body)
        return re.sub(r"\s+", " ", plain).strip()


@dataclass(frozen=True)
class Catalog:
    documents: tuple[Document, ...]
    build_id: str

    @property
    def modules(self) -> dict[str, tuple[Document, ...]]:
        grouped: dict[str, list[Document]] = {}
        for document in self.documents:
            if document.module_id:
                grouped.setdefault(document.module_id, []).append(document)
        role_order = {"overview": 0, "technology": 1, "explore": 2}
        return {
            key: tuple(sorted(value, key=lambda item: (role_order.get(item.role, 9), item.slug)))
            for key, value in sorted(grouped.items())
        }

    def collection(self, name: str) -> tuple[Document, ...]:
        return tuple(item for item in self.documents if item.collection == name)


def strip_quotes(value: str) -> str:
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def parse_value(raw: str) -> object:
    value = raw.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        return [] if not inner else [strip_quotes(part.strip()) for part in inner.split(",") if part.strip()]
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    if value.lower() == "null":
        return None
    if re.fullmatch(r"-?\d+", value):
        return int(value)
    return strip_quotes(value)


def parse_frontmatter(text: str) -> tuple[dict[str, object], str]:
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end < 0:
        raise ValueError("unterminated YAML frontmatter")
    data: dict[str, object] = {}
    for number, line in enumerate(text[4:end].splitlines(), start=2):
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if ":" not in stripped:
            raise ValueError(f"malformed frontmatter line {number}")
        key, value = stripped.split(":", 1)
        data[key.strip()] = parse_value(value)
    return data, text[end + 5 :]


def first_heading(body: str) -> str | None:
    match = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
    return match.group(1).strip() if match else None


def extract_headings(body: str) -> tuple[str, ...]:
    return tuple(
        re.sub(r"[`*_]", "", match.group(1)).strip()
        for match in re.finditer(r"^#{1,6}\s+(.+?)\s*$", body, re.MULTILINE)
    )


def load_document(path: Path, root: Path, collection: str, module_id: str | None, role: str) -> Document:
    frontmatter, body = parse_frontmatter(path.read_text(encoding="utf-8"))
    title = str(frontmatter.get("title") or first_heading(body) or path.stem.replace("-", " ").title())
    slug = str(frontmatter.get("slug") or path.relative_to(root).with_suffix("").as_posix().replace("/", "-"))
    prerequisites_raw = frontmatter.get("prerequisites", [])
    connections_raw = frontmatter.get("connections", [])
    prerequisites = tuple(str(item) for item in prerequisites_raw) if isinstance(prerequisites_raw, list) else ()
    connections = tuple(str(item) for item in connections_raw) if isinstance(connections_raw, list) else ()
    return Document(
        source_path=path.relative_to(root).as_posix(),
        collection=collection,
        title=title,
        slug=slug,
        status=str(frontmatter.get("status", "draft")),
        module_id=module_id,
        role=role,
        prerequisites=prerequisites,
        connections=connections,
        body=body,
        headings=extract_headings(body),
    )


def discover_documents(root: Path) -> tuple[Document, ...]:
    documents: list[Document] = []
    for collection in MODULE_ROOTS:
        base = root / collection
        if not base.is_dir():
            continue
        for module_dir in sorted(item for item in base.iterdir() if item.is_dir()):
            for filename in MODULE_FILES:
                path = module_dir / filename
                if path.is_file():
                    documents.append(load_document(path, root, collection, module_dir.name, path.stem))
    role_names = {
        "pathways": "pathway",
        "concepts": "concept",
        "maps": "map",
        "system-dossiers": "system-dossier",
        "failure-atlas": "failure-pattern",
        "investigations": "investigation",
        "design-challenges": "design-challenge",
    }
    for collection in SYNTHESIS_ROOTS + EXPERIENCE_ROOTS:
        base = root / collection
        if not base.is_dir():
            continue
        for path in sorted(base.glob("*.md")):
            if path.name.lower() == "readme.md":
                continue
            documents.append(load_document(path, root, collection, None, role_names[collection]))
    return tuple(sorted(documents, key=lambda item: (item.collection, item.module_id or "", item.role, item.slug)))


def calculate_build_id(root: Path, documents: Iterable[Document]) -> str:
    digest = hashlib.sha256()
    for document in documents:
        digest.update(document.source_path.encode())
        digest.update(b"\0")
        digest.update((root / document.source_path).read_bytes())
        digest.update(b"\0")
    for relative in (
        "release/phase-12-release-candidate.json",
        "release/phase-13-machine-governance.json",
        "experiences/phase-11b-inventory.json",
        "synthesis/phase-10-canonical-graph.json",
    ):
        path = root / relative
        if path.is_file():
            digest.update(relative.encode())
            digest.update(b"\0")
            digest.update(path.read_bytes())
    return digest.hexdigest()


def build_catalog(root: Path) -> Catalog:
    documents = discover_documents(root)
    return Catalog(documents, calculate_build_id(root, documents))


def safe_href(raw: str) -> str | None:
    href = raw.strip()
    if not href or href.lower().startswith(("javascript:", "data:", "vbscript:")):
        return None
    split = urlsplit(href)
    if split.scheme and split.scheme.lower() not in SAFE_SCHEMES:
        return None
    return href


def inline_markup(text: str, resolver: Callable[[str], str | None]) -> str:
    placeholders: list[str] = []

    def stash(fragment: str) -> str:
        token = f"@@PRINCIPIA{len(placeholders)}@@"
        placeholders.append(fragment)
        return token

    text = re.sub(
        r"`([^`\n]+)`",
        lambda match: stash(f"<code>{html.escape(match.group(1))}</code>"),
        text,
    )

    def replace_link(match: re.Match[str]) -> str:
        label = html.escape(match.group(1).strip() or "link")
        resolved = resolver(match.group(2).strip())
        href = safe_href(resolved) if resolved else None
        if href is None:
            return label
        external = urlsplit(href).scheme in SAFE_SCHEMES
        rel = ' rel="noopener noreferrer"' if external else ""
        return stash(f'<a href="{html.escape(href, quote=True)}"{rel}>{label}</a>')

    text = re.sub(r"\[([^\]]*)\]\(([^)]+)\)", replace_link, text)
    rendered = html.escape(text)
    rendered = re.sub(r"\*\*([^*\n]+)\*\*", r"<strong>\1</strong>", rendered)
    rendered = re.sub(r"(?<!\*)\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", rendered)
    rendered = re.sub(r"~~([^~\n]+)~~", r"<del>\1</del>", rendered)
    for index, fragment in enumerate(placeholders):
        rendered = rendered.replace(f"@@PRINCIPIA{index}@@", fragment)
    return rendered


def is_table_separator(line: str) -> bool:
    cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def render_table(lines: list[str], resolver: Callable[[str], str | None]) -> str:
    rows = [[cell.strip() for cell in line.strip().strip("|").split("|")] for line in lines]
    header = rows[0]
    body = rows[2:] if len(lines) > 1 and is_table_separator(lines[1]) else rows[1:]
    parts = ['<div class="table-wrap"><table><thead><tr>']
    parts.extend(f"<th>{inline_markup(cell, resolver)}</th>" for cell in header)
    parts.append("</tr></thead><tbody>")
    for row in body:
        parts.append("<tr>")
        parts.extend(f"<td>{inline_markup(cell, resolver)}</td>" for cell in row)
        parts.append("</tr>")
    parts.append("</tbody></table></div>")
    return "".join(parts)


def render_markdown(body: str, resolver: Callable[[str], str | None]) -> str:
    lines = body.splitlines()
    output: list[str] = []
    paragraph: list[str] = []
    list_kind: str | None = None
    code_lines: list[str] = []
    code_language = ""
    math_lines: list[str] = []
    in_code = False
    in_math = False
    index = 0

    def flush_paragraph() -> None:
        if not paragraph:
            return
        text = " ".join(item.strip() for item in paragraph).strip()
        paragraph.clear()
        if text:
            output.append(f"<p>{inline_markup(text, resolver)}</p>")

    def close_list() -> None:
        nonlocal list_kind
        if list_kind:
            output.append(f"</{list_kind}>")
            list_kind = None

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()

        if in_code:
            if stripped.startswith("```"):
                joined = "\n".join(html.escape(item) for item in code_lines)
                output.append(
                    f'<pre><code class="language-{html.escape(code_language, quote=True)}">{joined}</code></pre>'
                )
                in_code = False
                code_language = ""
                code_lines.clear()
            else:
                code_lines.append(line)
            index += 1
            continue

        if in_math:
            if stripped == "$$":
                joined = "\n".join(html.escape(item) for item in math_lines)
                output.append(f'<pre class="math">{joined}</pre>')
                in_math = False
                math_lines.clear()
            else:
                math_lines.append(line)
            index += 1
            continue

        if stripped.startswith("```"):
            flush_paragraph()
            close_list()
            in_code = True
            code_language = stripped[3:].strip()
            index += 1
            continue

        if stripped == "$$":
            flush_paragraph()
            close_list()
            in_math = True
            index += 1
            continue

        if "|" in line and index + 1 < len(lines) and is_table_separator(lines[index + 1]):
            flush_paragraph()
            close_list()
            table_lines = [line, lines[index + 1]]
            index += 2
            while index < len(lines) and lines[index].strip() and "|" in lines[index]:
                table_lines.append(lines[index])
                index += 1
            output.append(render_table(table_lines, resolver))
            continue

        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line)
        if heading:
            flush_paragraph()
            close_list()
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline_markup(heading.group(2), resolver)}</h{level}>")
            index += 1
            continue

        unordered = re.match(r"^\s*[-*]\s+(.+)$", line)
        ordered = re.match(r"^\s*\d+[.)]\s+(.+)$", line)
        if unordered or ordered:
            flush_paragraph()
            requested = "ul" if unordered else "ol"
            if list_kind != requested:
                close_list()
                output.append(f"<{requested}>")
                list_kind = requested
            item = (unordered or ordered).group(1)
            output.append(f"<li>{inline_markup(item, resolver)}</li>")
            index += 1
            continue

        if stripped.startswith(">"):
            flush_paragraph()
            close_list()
            output.append(
                f"<blockquote>{inline_markup(stripped.lstrip('>').strip(), resolver)}</blockquote>"
            )
            index += 1
            continue

        if not stripped:
            flush_paragraph()
            close_list()
            index += 1
            continue

        paragraph.append(line)
        index += 1

    flush_paragraph()
    close_list()
    if in_code:
        joined = "\n".join(html.escape(item) for item in code_lines)
        output.append(
            f'<pre><code class="language-{html.escape(code_language, quote=True)}">{joined}</code></pre>'
        )
    if in_math:
        output.append(f'<pre class="math">{" ".join(html.escape(item) for item in math_lines)}</pre>')
    return "\n".join(output)


def relative_prefix(page_path: str) -> str:
    return "../" * max(0, len(PurePosixPath(page_path).parts) - 1)


def page_shell(page_path: str, title: str, main: str, body_attrs: str = "") -> str:
    prefix = relative_prefix(page_path)
    nav_items = (
        ("Home", "index.html"),
        ("Modules", "modules/index.html"),
        ("Pathways", "pathways/index.html"),
        ("Experiences", "experiences/index.html"),
        ("Graph", "graph/index.html"),
        ("Search", "search/index.html"),
    )
    navigation = "".join(
        f'<a href="{prefix}{target}">{label}</a>' for label, target in nav_items
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Principia — principles to systems">
  <title>{html.escape(title)} · Principia</title>
  <link rel="stylesheet" href="{prefix}assets/site.css">
  <script defer src="{prefix}assets/site.js"></script>
</head>
<body {body_attrs}>
  <a class="skip-link" href="#main">Skip to content</a>
  <header class="site-header">
    <a class="brand" href="{prefix}index.html">Principia</a>
    <nav aria-label="Primary">{navigation}</nav>
  </header>
  <main id="main">{main}</main>
  <footer><p>Generated deterministically from repository Markdown and JSON.</p></footer>
</body>
</html>
"""


def link_between(current_page: str, target_page: str) -> str:
    current_parts = PurePosixPath(current_page).parent.parts
    target_parts = PurePosixPath(target_page).parts
    common = 0
    for left, right in zip(current_parts, target_parts):
        if left != right:
            break
        common += 1
    parts = [".."] * (len(current_parts) - common) + list(target_parts[common:])
    return "/".join(parts)


def document_resolver(
    root: Path,
    document: Document,
    current_page: str,
    source_to_output: dict[str, str],
) -> Callable[[str], str | None]:
    source_parent = PurePosixPath(document.source_path).parent

    def resolve(raw_href: str) -> str | None:
        href = raw_href.strip()
        split = urlsplit(href)
        if split.scheme or href.startswith("#"):
            return href
        path_part, marker, fragment = href.partition("#")
        candidate = document.source_path if not path_part else (source_parent / path_part).as_posix()
        normalized = str(PurePosixPath(candidate))
        target_output = source_to_output.get(normalized)
        if target_output:
            resolved = link_between(current_page, target_output)
            return f"{resolved}#{fragment}" if marker and fragment else resolved
        if (root / normalized).exists():
            return None
        return None

    return resolve


def status_badge(status: str) -> str:
    safe = re.sub(r"[^a-z0-9-]", "-", status.lower())
    return f'<span class="badge badge-{safe}">{html.escape(status.title())}</span>'


def write_text(output: Path, relative: str, content: str) -> None:
    target = output / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8", newline="\n")


def prepare_output(output: Path) -> None:
    if output.exists():
        marker = output / BUILD_MARKER
        if any(output.iterdir()) and not marker.is_file():
            raise RuntimeError(
                f"refusing to clean non-empty output directory without {BUILD_MARKER}: {output}"
            )
        shutil.rmtree(output)
    output.mkdir(parents=True)
    (output / BUILD_MARKER).write_text("generated by Principia\n", encoding="utf-8")


def copy_assets(root: Path, output: Path) -> None:
    for name in ("site.css", "site.js"):
        source = root / "software/assets" / name
        if not source.is_file():
            raise FileNotFoundError(source)
        target = output / "assets" / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def build_home(catalog: Catalog) -> str:
    synthesis = sum(len(catalog.collection(name)) for name in SYNTHESIS_ROOTS)
    experiences = sum(len(catalog.collection(name)) for name in EXPERIENCE_ROOTS)
    cards = (
        ("Core modules", str(len(catalog.modules)), "modules/index.html"),
        ("Synthesis documents", str(synthesis), "pathways/index.html"),
        ("Applied experiences", str(experiences), "experiences/index.html"),
        ("Build identity", catalog.build_id[:12], "api/build-manifest.json"),
    )
    metrics = "".join(
        f'<a class="metric-card" href="{href}"><strong>{html.escape(value)}</strong>'
        f"<span>{html.escape(label)}</span></a>"
        for label, value, href in cards
    )
    main = f"""
<section class="hero">
  <p class="eyebrow">Principle → mechanism → model → component → system</p>
  <h1>Explore how scientific principles become engineered systems.</h1>
  <p>The site is generated directly from the repository. Edit Markdown, rebuild, and navigation, search, catalog data, and dependency views update together.</p>
</section>
<section class="metric-grid" aria-label="Catalog summary">{metrics}</section>
<section>
  <h2>Start with a route</h2>
  <div class="feature-grid">
    <a class="feature" href="modules/index.html"><h3>Core modules</h3><p>Foundations, science, and technology in prerequisite order.</p></a>
    <a class="feature" href="pathways/index.html"><h3>Pathways</h3><p>Follow complete principle-to-system transformations.</p></a>
    <a class="feature" href="experiences/index.html"><h3>Applied experiences</h3><p>System dossiers, failure patterns, investigations, and design challenges.</p></a>
    <a class="feature" href="graph/index.html"><h3>Dependency graph</h3><p>Inspect prerequisites and cross-module connections.</p></a>
  </div>
</section>
"""
    return page_shell("index.html", "Home", main)


def build_document_page(
    root: Path,
    document: Document,
    source_to_output: dict[str, str],
) -> str:
    resolver = document_resolver(root, document, document.output_path, source_to_output)
    rendered = render_markdown(document.body, resolver)
    metadata = [
        f"<dt>Status</dt><dd>{status_badge(document.status)}</dd>",
        f"<dt>Collection</dt><dd>{html.escape(document.collection)}</dd>",
        f"<dt>Role</dt><dd>{html.escape(document.role)}</dd>",
        f"<dt>Source</dt><dd><code>{html.escape(document.source_path)}</code></dd>",
    ]
    if document.module_id:
        metadata.append(f"<dt>Module</dt><dd>{html.escape(document.module_id)}</dd>")
    main = f"""
<article class="document">
  <header class="document-header">
    <p class="eyebrow">{html.escape(document.collection)}</p>
    <h1>{html.escape(document.title)}</h1>
    <dl class="metadata">{''.join(metadata)}</dl>
  </header>
  <div class="prose">{rendered}</div>
</article>
"""
    return page_shell(document.output_path, document.title, main)


def build_modules_index(catalog: Catalog) -> str:
    cards = []
    for module_id, documents in catalog.modules.items():
        overview = next((item for item in documents if item.role == "overview"), documents[0])
        prerequisites = ", ".join(overview.prerequisites) or "None"
        cards.append(
            f'<a class="catalog-card" href="{quote(module_id, safe="")}.html">'
            f'<p class="eyebrow">{html.escape(overview.collection)}</p>'
            f"<h2>{html.escape(overview.title)}</h2>"
            f"<p><code>{html.escape(module_id)}</code></p>"
            f"<p>Prerequisites: {html.escape(prerequisites)}</p>"
            f"{status_badge(overview.status)}</a>"
        )
    main = (
        '<header class="page-heading"><h1>Core modules</h1>'
        "<p>Each module exposes overview, technology, and exploration views from one source directory.</p></header>"
        f'<section class="catalog-grid">{"".join(cards)}</section>'
    )
    return page_shell("modules/index.html", "Modules", main)


def build_module_page(module_id: str, documents: tuple[Document, ...]) -> str:
    overview = next((item for item in documents if item.role == "overview"), documents[0])
    links = "".join(
        f'<a class="feature" href="../{document.output_path}">'
        f"<h2>{html.escape(document.role.title())}</h2>"
        f"<p>{html.escape(document.title)}</p>{status_badge(document.status)}</a>"
        for document in documents
    )
    prerequisites = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in overview.prerequisites)
    connections = "".join(f"<li><code>{html.escape(item)}</code></li>" for item in overview.connections)
    main = f"""
<header class="page-heading">
  <p class="eyebrow">{html.escape(overview.collection)}</p>
  <h1>{html.escape(overview.title)}</h1>
  <p><code>{html.escape(module_id)}</code></p>
</header>
<section class="feature-grid">{links}</section>
<section class="split">
  <div><h2>Prerequisites</h2><ul>{prerequisites or '<li>None</li>'}</ul></div>
  <div><h2>Connections</h2><ul>{connections or '<li>None declared</li>'}</ul></div>
</section>
"""
    return page_shell(f"modules/{quote(module_id, safe='')}.html", overview.title, main)


def collection_index(
    page_path: str,
    title: str,
    description: str,
    documents: Iterable[Document],
) -> str:
    cards = "".join(
        f'<a class="catalog-card" href="../{document.output_path}">'
        f'<p class="eyebrow">{html.escape(document.collection)}</p>'
        f"<h2>{html.escape(document.title)}</h2>"
        f"<p><code>{html.escape(document.source_path)}</code></p>"
        f"{status_badge(document.status)}</a>"
        for document in documents
    )
    main = (
        f'<header class="page-heading"><h1>{html.escape(title)}</h1>'
        f"<p>{html.escape(description)}</p></header>"
        f'<section class="catalog-grid">{cards}</section>'
    )
    return page_shell(page_path, title, main)


def graph_payload(catalog: Catalog) -> dict[str, object]:
    nodes: list[dict[str, object]] = []
    edges: list[dict[str, str]] = []
    module_ids = set(catalog.modules)
    for module_id, documents in catalog.modules.items():
        overview = next((item for item in documents if item.role == "overview"), documents[0])
        nodes.append(
            {
                "id": module_id,
                "title": overview.title,
                "domain": overview.collection,
                "status": overview.status,
                "url": f"../modules/{quote(module_id, safe='')}.html",
            }
        )
        for target in overview.prerequisites:
            if target in module_ids:
                edges.append({"source": target, "target": module_id, "type": "prerequisite"})
        for target in overview.connections:
            if target in module_ids and target != module_id:
                edges.append({"source": module_id, "target": target, "type": "connection"})
    seen: set[tuple[str, str, str]] = set()
    unique_edges = []
    for edge in edges:
        key = (edge["source"], edge["target"], edge["type"])
        if key not in seen:
            seen.add(key)
            unique_edges.append(edge)
    return {"nodes": nodes, "edges": unique_edges}


def build_graph_page(payload: dict[str, object]) -> str:
    nodes = payload["nodes"]
    edges = payload["edges"]
    assert isinstance(nodes, list) and isinstance(edges, list)
    node_list = "".join(
        f'<li><a href="../modules/{quote(str(node["id"]), safe="")}.html">'
        f'<code>{html.escape(str(node["id"]))}</code> — {html.escape(str(node["title"]))}</a></li>'
        for node in nodes
        if isinstance(node, dict)
    )
    edge_list = "".join(
        f"<li><code>{html.escape(str(edge['source']))}</code> → "
        f"<code>{html.escape(str(edge['target']))}</code> "
        f"({html.escape(str(edge['type']))})</li>"
        for edge in edges
        if isinstance(edge, dict)
    )
    main = f"""
<header class="page-heading">
  <h1>Dependency graph</h1>
  <p>The visual layer is progressively enhanced from the same accessible node and edge lists.</p>
</header>
<div id="graph-canvas" class="graph-canvas" role="img" aria-label="Interactive module dependency graph"></div>
<section class="split">
  <div><h2>Modules</h2><ul class="compact-list">{node_list}</ul></div>
  <div><h2>Relationships</h2><ul class="compact-list">{edge_list}</ul></div>
</section>
"""
    return page_shell(
        "graph/index.html",
        "Dependency graph",
        main,
        'data-graph-index="../api/graph.json"',
    )


def build_search_page() -> str:
    main = """
<header class="page-heading">
  <h1>Search the material foundation</h1>
  <p>Search titles, headings, identifiers, and document text. The index is generated locally.</p>
</header>
<label class="search-label" for="search-input">Search</label>
<input id="search-input" class="search-input" type="search" autocomplete="off" placeholder="Try: feedback, entropy, semiconductor, uncertainty">
<p id="search-summary" aria-live="polite"></p>
<ol id="search-results" class="search-results"></ol>
"""
    return page_shell(
        "search/index.html",
        "Search",
        main,
        'data-search-index="../api/search-index.json"',
    )


def search_payload(catalog: Catalog) -> list[dict[str, object]]:
    return [
        {
            "title": item.title,
            "slug": item.slug,
            "url": f"../{item.output_path}",
            "collection": item.collection,
            "module_id": item.module_id,
            "role": item.role,
            "status": item.status,
            "headings": list(item.headings),
            "text": item.searchable_text,
        }
        for item in catalog.documents
    ]


def catalog_payload(catalog: Catalog) -> dict[str, object]:
    synthesis = sum(len(catalog.collection(name)) for name in SYNTHESIS_ROOTS)
    experiences = sum(len(catalog.collection(name)) for name in EXPERIENCE_ROOTS)
    return {
        "schema": "principia-content-catalog/0.1",
        "build_id": catalog.build_id,
        "counts": {
            "documents": len(catalog.documents),
            "modules": len(catalog.modules),
            "synthesis": synthesis,
            "experiences": experiences,
        },
        "documents": [
            {
                "source_path": item.source_path,
                "output_path": item.output_path,
                "collection": item.collection,
                "title": item.title,
                "slug": item.slug,
                "status": item.status,
                "module_id": item.module_id,
                "role": item.role,
                "prerequisites": list(item.prerequisites),
                "connections": list(item.connections),
            }
            for item in catalog.documents
        ],
    }


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = path.relative_to(root).as_posix()
        if relative == "api/build-manifest.json":
            continue
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def build_site(root: Path, output: Path) -> dict[str, object]:
    root = root.resolve()
    output = output.resolve()
    catalog = build_catalog(root)
    prepare_output(output)
    copy_assets(root, output)

    source_to_output = {item.source_path: item.output_path for item in catalog.documents}
    write_text(output, "index.html", build_home(catalog))
    write_text(output, "modules/index.html", build_modules_index(catalog))
    for module_id, documents in catalog.modules.items():
        write_text(
            output,
            f"modules/{quote(module_id, safe='')}.html",
            build_module_page(module_id, documents),
        )
    for document in catalog.documents:
        write_text(
            output,
            document.output_path,
            build_document_page(root, document, source_to_output),
        )

    synthesis_documents = tuple(
        item for collection in SYNTHESIS_ROOTS for item in catalog.collection(collection)
    )
    write_text(
        output,
        "pathways/index.html",
        collection_index(
            "pathways/index.html",
            "Pathways and synthesis",
            "Cross-module pathways, concepts, and maps.",
            synthesis_documents,
        ),
    )
    experience_documents = tuple(
        item for collection in EXPERIENCE_ROOTS for item in catalog.collection(collection)
    )
    write_text(
        output,
        "experiences/index.html",
        collection_index(
            "experiences/index.html",
            "Applied experiences",
            "System dossiers, failure patterns, investigations, and design challenges.",
            experience_documents,
        ),
    )

    graph = graph_payload(catalog)
    write_text(output, "graph/index.html", build_graph_page(graph))
    write_text(output, "search/index.html", build_search_page())
    payload = catalog_payload(catalog)
    write_text(
        output,
        "api/catalog.json",
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
    )
    write_text(
        output,
        "api/search-index.json",
        json.dumps(search_payload(catalog), indent=2, ensure_ascii=False) + "\n",
    )
    write_text(
        output,
        "api/graph.json",
        json.dumps(graph, indent=2, ensure_ascii=False) + "\n",
    )

    manifest: dict[str, object] = {
        "schema": "principia-static-build/0.1",
        "build_id": catalog.build_id,
        "generator": "software/principia_site.py",
        "network_fetch": False,
        "counts": payload["counts"],
    }
    manifest["tree_digest"] = tree_digest(output)
    write_text(
        output,
        "api/build-manifest.json",
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
    )
    return manifest


def serve(output: Path, host: str, port: int) -> None:
    output = output.resolve()
    if not (output / "index.html").is_file():
        raise FileNotFoundError(f"site has not been built: {output}")

    def handler(*args: object, **kwargs: object) -> SimpleHTTPRequestHandler:
        return SimpleHTTPRequestHandler(*args, directory=str(output), **kwargs)

    server = ThreadingHTTPServer((host, port), handler)
    print(f"Serving Principia at http://{host}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    subparsers = parser.add_subparsers(dest="command", required=True)

    build_parser = subparsers.add_parser("build", help="generate the static site")
    build_parser.add_argument("--output", type=Path, default=Path("software/dist"))

    inspect_parser = subparsers.add_parser("inspect", help="print catalog metadata")
    inspect_parser.add_argument("--pretty", action="store_true")

    serve_parser = subparsers.add_parser("serve", help="serve an existing build")
    serve_parser.add_argument("--output", type=Path, default=Path("software/dist"))
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)

    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.command == "build":
        manifest = build_site(root, args.output)
        print(json.dumps(manifest, indent=2, ensure_ascii=False))
        return 0
    if args.command == "inspect":
        payload = catalog_payload(build_catalog(root))
        print(json.dumps(payload, indent=2 if args.pretty else None, ensure_ascii=False))
        return 0
    if args.command == "serve":
        serve(args.output, args.host, args.port)
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
