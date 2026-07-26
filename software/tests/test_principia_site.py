from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from software.principia_site import (
    EXPERIENCE_ROOTS,
    SYNTHESIS_ROOTS,
    build_catalog,
    build_site,
    inline_markup,
    prepare_output,
    search_payload,
)


ROOT = Path(__file__).resolve().parents[2]


class PrincipiaCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = build_catalog(ROOT)

    def test_repository_scope_is_complete(self) -> None:
        self.assertEqual(len(self.catalog.modules), 20)
        self.assertEqual(len(self.catalog.documents), 92)
        synthesis = sum(len(self.catalog.collection(name)) for name in SYNTHESIS_ROOTS)
        experiences = sum(len(self.catalog.collection(name)) for name in EXPERIENCE_ROOTS)
        self.assertEqual(synthesis, 16)
        self.assertEqual(experiences, 16)

    def test_module_views_are_complete_and_reviewed(self) -> None:
        for module_id, documents in self.catalog.modules.items():
            self.assertEqual({document.role for document in documents}, {"overview", "technology", "explore"}, module_id)
            self.assertTrue(all(document.status == "reviewed" for document in documents), module_id)

    def test_search_index_covers_every_document(self) -> None:
        records = search_payload(self.catalog)
        self.assertEqual(len(records), len(self.catalog.documents))
        self.assertEqual(len({record["slug"] for record in records}), len(records))
        self.assertTrue(all(record["title"] and record["text"] for record in records))

    def test_inline_renderer_escapes_html_and_rejects_script_links(self) -> None:
        rendered = inline_markup(
            '<script>alert(1)</script> [unsafe](javascript:alert(2)) **safe**',
            lambda target: target,
        )
        self.assertNotIn("<script>", rendered)
        self.assertNotIn("javascript:", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertIn("<strong>safe</strong>", rendered)


class PrincipiaBuildTests(unittest.TestCase):
    def test_build_outputs_catalog_graph_search_and_pages(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "site"
            manifest = build_site(ROOT, output)
            self.assertEqual(manifest["counts"], {
                "documents": 92,
                "modules": 20,
                "synthesis": 16,
                "experiences": 16,
            })
            for relative in (
                "index.html",
                "modules/index.html",
                "pathways/index.html",
                "experiences/index.html",
                "graph/index.html",
                "search/index.html",
                "api/catalog.json",
                "api/search-index.json",
                "api/graph.json",
                "api/build-manifest.json",
            ):
                self.assertTrue((output / relative).is_file(), relative)
            catalog = json.loads((output / "api/catalog.json").read_text(encoding="utf-8"))
            self.assertEqual(catalog["build_id"], manifest["build_id"])

    def test_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            first = build_site(ROOT, base / "first")
            second = build_site(ROOT, base / "second")
            self.assertEqual(first["build_id"], second["build_id"])
            self.assertEqual(first["tree_digest"], second["tree_digest"])

    def test_output_cleanup_requires_build_marker(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "protected"
            output.mkdir()
            (output / "keep.txt").write_text("do not delete", encoding="utf-8")
            with self.assertRaises(RuntimeError):
                prepare_output(output)
            self.assertTrue((output / "keep.txt").is_file())


if __name__ == "__main__":
    unittest.main()
