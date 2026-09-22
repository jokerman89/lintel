#!/usr/bin/env python3
# component: document-pdf-tests
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: owned synthetic data; existing pypdf reader; no browser or PDF raster action by tests
# last_intent_review: 2026-09-22
"""Separate source/preparation/reader tests from actual headless print observations."""
from __future__ import annotations

import argparse
from io import BytesIO
import importlib.util
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PREP = None
CHECK = None
OPTIONS = None


class Preparation(unittest.TestCase):
    def document(self):
        return '<!doctype html><html lang="sv"><head><title>Synthetic title</title></head><body><h1>Heading</h1><p>Reasoning &amp; limitation [S1].</p><table><tr><td>12.5 units</td></tr></table><pre>if ready:\n    acknowledge(item)</pre></body></html>'

    def test_complete_html_body_is_preserved(self):
        html = self.document()
        output, metadata = PREP.prepare_document(html, input_format="html")
        self.assertIn(html.split("</head>", 1)[1], output)
        self.assertIn('lang="sv"', output)
        self.assertFalse(metadata["rendered"])

    def test_a4_letter_orientation_and_background_options(self):
        for paper, label in (("a4", "A4"), ("letter", "letter")):
            for orientation in ("portrait", "landscape"):
                with self.subTest(paper=paper, orientation=orientation):
                    output, _ = PREP.prepare_document(self.document(), input_format="html",
                                                       paper=paper, orientation=orientation, no_background=True)
                    self.assertIn(f"size: {label} {orientation}", output)
                    self.assertIn("background:none!important", output)

    def test_header_footer_substitutions_are_css_text_not_html(self):
        output, _ = PREP.prepare_document(self.document(), input_format="html",
            header_footer={"header": '{{title}} </style><script>not code</script>',
                           "footer": "Page {{page}} of {{total}} | {{date}}"},
            date_text="2026-09-22")
        self.assertIn("counter(page)", output)
        self.assertIn("counter(pages)", output)
        self.assertIn("2026-09-22", output)
        self.assertIn("Synthetic title", output)
        self.assertNotIn("</style><script>", output)

    def test_unknown_header_keys_or_placeholders_refused(self):
        for value in ({"execute": "no"}, {"header": "{{unknown}}"}, {"footer": 12}):
            with self.subTest(value=value), self.assertRaises(PREP.PreparationError):
                PREP.prepare_document(self.document(), input_format="html", header_footer=value)

    def test_custom_size_requires_explicit_print_css(self):
        with self.assertRaises(PREP.PreparationError):
            PREP.prepare_document(self.document(), input_format="html", paper="custom")
        output, _ = PREP.prepare_document(self.document(), input_format="html", paper="custom",
                                          print_css="@page {size: 180mm 240mm}")
        self.assertIn("size: 180mm 240mm", output)
        self.assertNotIn("size: A4", output)

    def test_css_cannot_escape_style_element(self):
        with self.assertRaises(PREP.PreparationError):
            PREP.prepare_document(self.document(), input_format="html", print_css="</style><p>unexpected")

    def test_comment_head_marker_is_not_the_insertion_point(self):
        for separator in ("\r\n", "\r", "\x0b", "\u2028"):
            with self.subTest(separator=separator):
                html = self.document().replace("<head>", "<!-- </head>" + separator + "comment -->\n<head>")
                output, _ = PREP.prepare_document(html, input_format="html")
                self.assertTrue(output.index("</title>") < output.index('data-lintel-pdf="print"'))
                self.assertIn(html.split("</head>", 2)[-1], output)

    def test_duplicate_heads_stop_at_the_first_ambiguous_boundary(self):
        html = self.document().replace("</head>", "</head></head>" + "\n" * 4096)
        with self.assertRaisesRegex(PREP.PreparationError, "multiple closing heads"):
            PREP.prepare_document(html, input_format="html")

    def test_missing_converter_never_becomes_plain_text_success(self):
        with patch.dict(sys.modules, {"markdown_it": None}), self.assertRaisesRegex(PREP.PreparationError, "unavailable"):
            PREP.prepare_document("# source\n\n|a|b|\n|-|-|\n|1|2|", input_format="markdown")

    def test_empty_or_fragment_html_is_explicit_error(self):
        for html in ("", "<p>no explicit document head</p>"):
            with self.subTest(html=html), self.assertRaises(PREP.PreparationError):
                PREP.prepare_document(html, input_format="html")

    def test_read_only_bound_paths_and_existing_output_preserved(self):
        from context_safety import atomic_write, checked_root
        with tempfile.TemporaryDirectory() as name:
            root = checked_root(Path(name))
            atomic_write(root, "existing.html", b"owned original", check_expected=True)
            with self.assertRaises(ValueError):
                atomic_write(root, "existing.html", b"unexpected", expected=None, check_expected=True)
            self.assertEqual((root / "existing.html").read_bytes(), b"owned original")


class Reader(unittest.TestCase):
    def blank(self):
        from pypdf import PdfWriter
        out = BytesIO()
        writer = PdfWriter()
        writer.add_blank_page(width=612, height=792)
        writer.write(out)
        return out.getvalue()

    def test_blank_pdf_is_not_a_size_or_page_count_pass(self):
        result = CHECK.inspect_pdf(self.blank(), {"required_text": ["Real source required"]})
        self.assertEqual(result["status"], "fail")
        self.assertEqual(result["page_count"], 1)
        self.assertEqual(result["complete_visual_inspection"], "unverified")
        self.assertFalse(result["release_clearance"])

    def test_partial_pdf_does_not_pass(self):
        from pypdf.errors import PyPdfError
        with self.assertRaises(PyPdfError):
            CHECK.inspect_pdf(self.blank()[:40], {"required_text": ["source"]})

    def test_invalid_or_empty_expectations_refused(self):
        for expected in ({}, {"required_text": []}, {"required_text": ["x"], "min_pages": 0},
                         {"required_text": ["x"], "paper_points": [0, 200]}):
            with self.subTest(expected=expected), self.assertRaises(ValueError):
                CHECK.inspect_pdf(self.blank(), expected)

    def test_missing_required_raster_remains_blocked_in_p05(self):
        from review_contract import evaluate_controls
        control = {
            "id": "pdf-visual", "kind": "check", "requirement": "mandatory", "applicability": "applicable",
            "status": "unverified", "reason": "Complete PDF page inspection unavailable",
            "policy": {"source": "P12.md", "version": "c6462b4", "applicability": "Required visual inspection",
                       "jurisdiction": None, "actor": None, "effective_date": None},
            "evidence": ["print.json"], "observation": {}, "advisory_score": 100,
        }
        result = evaluate_controls([control], required_policy={
            "required": False, "status": "not_required", "source": None, "version": None,
            "applicability": "not_applicable",
        })
        self.assertTrue(result["blocked"])


class NativePdf(unittest.TestCase):
    def test_actual_print_retains_source_without_hiding_geometry_outcome(self):
        data = (OPTIONS.native_root / "long-technical-brief.pdf").read_bytes()
        expected = json.loads((OPTIONS.native_root / "pdf-expectations.json").read_text(encoding="utf-8"))
        result = CHECK.inspect_pdf(data, expected)
        self.assertEqual(result["source_text_status"], "pass", result["issues"])
        self.assertEqual(result["page_status"], "pass", result["issues"])
        outside = [origin for page in result["pages"] for origin in page["text_origins"]
                   if not origin["within_crop_box"]]
        if outside:
            self.assertEqual(result["text_origin_status"], "fail")
            self.assertEqual(result["status"], "fail")
            self.assertEqual(len([issue for issue in result["issues"] if issue["check"] == "text_origin"]), len(outside))
        self.assertGreaterEqual(result["page_count"], expected["min_pages"])
        self.assertEqual(result["complete_visual_inspection"], "unverified")

    def test_actual_print_negative_source_and_paper_expectations_fail(self):
        data = (OPTIONS.native_root / "long-technical-brief.pdf").read_bytes()
        for expected in ({"required_text": ["P12 ABSENT-SOURCE-SENTINEL"]},
                         {"required_text": ["Synthetic"], "paper_points": [100, 100]}):
            self.assertEqual(CHECK.inspect_pdf(data, expected)["status"], "fail")

    def test_actual_print_partial_file_is_not_success(self):
        from pypdf.errors import PyPdfError
        data = (OPTIONS.native_root / "long-technical-brief.pdf").read_bytes()
        with self.assertRaises(PyPdfError):
            CHECK.inspect_pdf(data[:80], {"required_text": ["Synthetic"]})


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    global OPTIONS, PREP, CHECK
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument("--native-root", type=Path)
    OPTIONS = parser.parse_args()
    OPTIONS.fixture_root.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="pdf-tests-", dir=OPTIONS.fixture_root.resolve()))
    roots = {name: root / name for name in ("home", "app", "localapp", "temp", "lintel", "target")}
    for path in roots.values():
        path.mkdir()
    env = {"PATH": os.pathsep.join((str(Path(sys.executable).parent), os.defpath)),
           "PATHEXT": ".COM;.EXE;.BAT;.CMD", "HOME": str(roots["home"]), "USERPROFILE": str(roots["home"]),
           "APPDATA": str(roots["app"]), "LOCALAPPDATA": str(roots["localapp"]),
           "TEMP": str(roots["temp"]), "TMP": str(roots["temp"]), "TMPDIR": str(roots["temp"]),
           "LINTEL_HOME": str(roots["lintel"]), "LINTEL_SOURCE_ROOT": str(ROOT), "LINTEL_REPO_ROOT": str(roots["target"]),
           "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(root / "empty.gitconfig"),
           "GIT_CEILING_DIRECTORIES": str(root), "GIT_TERMINAL_PROMPT": "0",
           "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1"}
    if os.name == "nt":
        env.update(SystemRoot="C:\\Windows", WINDIR="C:\\Windows",
                   HOMEDRIVE=roots["home"].drive, HOMEPATH=str(roots["home"])[2:],
                   ComSpec="C:\\Windows\\System32\\cmd.exe")
    os.environ.clear()
    os.environ.update(env)
    tempfile.tempdir = str(roots["temp"])
    sys.dont_write_bytecode = True
    closure = ("skills/generate-pdf/scripts/prepare_html.py", "skills/generate-pdf/scripts/check_pdf.py",
               "lib/context_safety.py", "lib/native_paths.py", "lib/profile_context.py",
               "lib/review_contract.py", "lib/review-schema.json", "lib/markdown_source.py")
    seals = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest() for name in closure}
    (root / "preflight.json").write_text(json.dumps({
        "environment": env, "source": str(ROOT), "native_root": str(OPTIONS.native_root) if OPTIONS.native_root else None,
        "boundary": "No browser, application or PDF rasterization by this runner.",
        "source_sha256": seals,
    }, indent=2), encoding="utf-8")
    print(f"preflight: {root / 'preflight.json'}", flush=True)
    PREP = load("pdf_prepare", ROOT / "skills/generate-pdf/scripts/prepare_html.py")
    CHECK = load("pdf_check", ROOT / "skills/generate-pdf/scripts/check_pdf.py")
    suite = unittest.TestSuite()
    for case in (Preparation, Reader) + ((NativePdf,) if OPTIONS.native_root else ()):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    (root / "result.json").write_text(json.dumps({
        "executed": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "success": result.wasSuccessful(),
        "native_print_or_raster_executed": False,
    }, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
