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
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
PREP = None
CHECK = None
OPTIONS = None
RUN = None
DEFAULT_UNIT = object()


def readable_pdf(*, unit=DEFAULT_UNIT, media=None, crop=None, translation=None):
    """Existing pypdf authors a tiny synthetic PDF 1.7, not a rendered artifact."""
    from pypdf import PdfWriter, Transformation
    from pypdf._page import PageObject
    from pypdf.generic import (
        BooleanObject, DecodedStreamObject, DictionaryObject, FloatObject,
        NameObject, NullObject, NumberObject, RectangleObject, TextStringObject,
    )
    page = PageObject.create_blank_page(width=612, height=792)
    font = DictionaryObject({
        NameObject("/Type"): NameObject("/Font"), NameObject("/Subtype"): NameObject("/Type1"),
        NameObject("/BaseFont"): NameObject("/Helvetica"),
    })
    page[NameObject("/Resources")] = DictionaryObject({NameObject("/Font"): DictionaryObject({NameObject("/F1"): font})})
    stream = DecodedStreamObject()
    stream.set_data(b"BT /F1 12 Tf 72 720 Td (Synthetic source and limitation.) Tj ET")
    page[NameObject("/Contents")] = stream
    if unit is not DEFAULT_UNIT:
        if unit is None:
            value = NullObject()
        elif type(unit) is bool:
            value = BooleanObject(unit)
        elif isinstance(unit, str):
            value = TextStringObject(unit)
        elif type(unit) is int:
            value = NumberObject(unit)
        else:
            value = FloatObject(unit)
        page[NameObject("/UserUnit")] = value
    if media is not None:
        page.mediabox = RectangleObject(media)
    if crop is not None:
        page.cropbox = RectangleObject(crop)
    if translation is not None:
        page.add_transformation(Transformation().translate(*translation))
    writer = PdfWriter()
    writer.add_page(page)
    writer.pdf_header = "%PDF-1.7"
    output = BytesIO()
    writer.write(output)
    return output.getvalue()


class PhysicalGeometry(unittest.TestCase):
    def oracle(self, size=(612, 792)):
        return {"required_text": ["Synthetic source and limitation."], "paper_points": list(size)}

    def test_omitted_and_explicit_unit_one_are_equivalent(self):
        for data in (readable_pdf(), readable_pdf(unit=1)):
            with self.subTest(sha=hashlib.sha256(data).hexdigest()):
                result = CHECK.inspect_pdf(data, self.oracle())
                page = result["pages"][0]
                self.assertEqual(result["status"], "pass")
                self.assertEqual(page["user_unit"], 1)
                self.assertEqual(page["physical_media_points"], [612, 792])
                self.assertEqual(page["media_box"], [0, 0, 612, 792])
                self.assertEqual(page["text_origins"][0]["origin"], [72, 720])
                self.assertFalse(result["release_clearance"])

    def test_unit_two_changes_physical_paper_not_raw_origins(self):
        data = readable_pdf(unit=2)
        raw = CHECK.inspect_pdf(data, self.oracle())
        physical = CHECK.inspect_pdf(data, self.oracle((1224, 1584)))
        self.assertEqual(raw["page_status"], "fail")
        self.assertEqual(physical["status"], "pass")
        self.assertEqual(physical["pages"][0]["physical_media_points"], [1224, 1584])
        self.assertEqual(physical["pages"][0]["media_box"], [0, 0, 612, 792])
        self.assertEqual(physical["pages"][0]["text_origins"][0]["origin"], [72, 720])
        self.assertEqual(physical["complete_visual_inspection"], "unverified")

    def test_fractional_unit_with_nonzero_media_origin(self):
        result = CHECK.inspect_pdf(readable_pdf(unit=0.5, media=[10, 20, 622, 812]), self.oracle((306, 396)))
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["pages"][0]["user_unit"], 0.5)
        self.assertEqual(result["pages"][0]["physical_media_points"], [306, 396])

    def test_invalid_user_units_are_reader_errors_not_unit_one_fallback(self):
        for unit in (0, -1, True, "2", "Infinity", None, 10 ** 309):
            with self.subTest(unit=unit), self.assertRaises(ValueError):
                CHECK.inspect_pdf(readable_pdf(unit=unit), self.oracle())

    def test_larger_crop_cannot_hide_translated_out_of_media_origin(self):
        translated = readable_pdf(translation=(0, 1000))
        enlarged = readable_pdf(translation=(0, 1000), crop=[0, 0, 612, 1792])
        ordinary = CHECK.inspect_pdf(translated, self.oracle())
        masked = CHECK.inspect_pdf(enlarged, self.oracle())
        self.assertEqual(ordinary["text_origin_status"], "fail")
        self.assertEqual(masked["text_origin_status"], "fail")
        self.assertEqual(masked["status"], "fail")
        page = masked["pages"][0]
        self.assertEqual(page["crop_box"], [0, 0, 612, 1792])
        self.assertEqual(page["effective_box"], [0, 0, 612, 792])
        origin = page["text_origins"][0]
        self.assertEqual(origin["origin"], ordinary["pages"][0]["text_origins"][0]["origin"])
        self.assertTrue(origin["within_crop_box"])
        self.assertFalse(origin["within_media_box"])
        self.assertFalse(origin["within_effective_box"])

    def test_contained_and_oversized_crops_use_the_same_intersection_rule(self):
        for crop, expected_box, status in (
            ([0, 0, 612, 792], [0, 0, 612, 792], "pass"),
            ([-10, -20, 700, 900], [0, 0, 612, 792], "pass"),
            ([50, 700, 200, 750], [50, 700, 200, 750], "pass"),
            ([0, 0, 20, 20], [0, 0, 20, 20], "fail"),
        ):
            with self.subTest(crop=crop):
                result = CHECK.inspect_pdf(readable_pdf(crop=crop), self.oracle())
                self.assertEqual(result["status"], status)
                self.assertEqual(result["pages"][0]["effective_box"], expected_box)

    def test_empty_inverted_and_disjoint_regions_are_rejected(self):
        for box in ([0, 0, 0, 792], [10, 0, 0, 792], [700, 0, 800, 792], [612, 0, 700, 792]):
            with self.subTest(crop=box), self.assertRaises(ValueError):
                CHECK.inspect_pdf(readable_pdf(crop=box), self.oracle())
        with self.assertRaises(ValueError):
            CHECK.inspect_pdf(readable_pdf(media=[612, 0, 0, 792]), self.oracle())

    def test_actual_cli_physical_dimensions_and_invalid_regions(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            data = root / "input.pdf"
            oracle = root / "expectations.json"
            for label, pdf, dimensions, expected_exit in (
                ("default", readable_pdf(), [612, 792], 0),
                ("scaled-wrong", readable_pdf(unit=2), [612, 792], 3),
                ("scaled-physical", readable_pdf(unit=2), [1224, 1584], 0),
                ("invalid-scale", readable_pdf(unit=0), [612, 792], 2),
                ("disjoint", readable_pdf(crop=[700, 0, 800, 792]), [612, 792], 2),
                ("masked-origin", readable_pdf(translation=(0, 1000), crop=[0, 0, 612, 1792]), [612, 792], 3),
            ):
                data.write_bytes(pdf)
                oracle.write_text(json.dumps(self.oracle(dimensions)), encoding="utf-8")
                command = [sys.executable, "-I", "-B", str(ROOT / "skills/generate-pdf/scripts/check_pdf.py"),
                           "--root", str(root), "--input", data.name, "--expect", oracle.name]
                prefix = RUN / f"cli-{label}"
                prefix.with_suffix(".command.json").write_text(json.dumps(command), encoding="utf-8")
                with prefix.with_suffix(".stdout.log").open("wb") as out, prefix.with_suffix(".stderr.log").open("wb") as err:
                    result = subprocess.run(command, cwd=root, env=dict(os.environ), stdout=out, stderr=err)
                prefix.with_suffix(".exit.json").write_text(json.dumps({"exit": result.returncode}), encoding="utf-8")
                self.assertEqual(result.returncode, expected_exit, label)
                self.assertEqual(data.read_bytes(), pdf)


class TextContexts(unittest.TestCase):
    def document(self, title="Source notation", body=""):
        return ('<!doctype html><html><head><title>' + title + '</title></head><body>'
                '<p>Complete source and limitation [S1].</p>' + body + '</body></html>')

    def assert_only_insertion(self, original, result):
        marker = '<style data-lintel-pdf="print">'
        start = result.index("\n" + marker)
        stop = result.index("</style>\n", start) + len("</style>\n")
        self.assertEqual(result[:start] + result[stop:], original)
        self.assertLess(result.index("</title>"), start)
        self.assertLess(start, result.index("</head><body>"))

    def test_raw_and_escaped_title_markers_are_literal_context(self):
        titles = ("Source </head> notation", "Source &lt;/head&gt; notation",
                  "Source &#60;/head&#62; notation", "Source </HEAD> notation")
        for title in titles:
            with self.subTest(title=title):
                original = self.document(title)
                result, metadata = PREP.prepare_document(original, input_format="html")
                self.assert_only_insertion(original, result)
                self.assertFalse(metadata["rendered"])

    def test_raw_and_escaped_textarea_markers_preserve_complete_body(self):
        for content in ("Example </head> token", "Example &lt;/head&gt; token",
                        "<title>Not the document title</title> </head> &amp;"):
            with self.subTest(content=content):
                original = self.document(body="<textarea>" + content + "</textarea>")
                result, _ = PREP.prepare_document(original, input_format="html", header_footer={"header": "{{title}}"})
                self.assert_only_insertion(original, result)
                self.assertIn('content:"Source notation"', result)

    def test_title_entities_are_decoded_once_not_copied_as_raw_or_double_decoded(self):
        for title, wanted in (("A &amp; B", "A & B"), ("A &amp;amp; B", "A &amp; B")):
            with self.subTest(title=title):
                original = self.document(title)
                result, _ = PREP.prepare_document(original, input_format="html", header_footer={"header": "{{title}}"})
                self.assert_only_insertion(original, result)
                self.assertIn("content:" + PREP._css_text(wanted), result)
                self.assertIn(title, result)

    def test_existing_comment_script_style_and_lf_controls_are_retained(self):
        for separator in ("\n", "\r\n", "\r", "\x0b", "\u2028"):
            original = self.document("Title </head> &amp; text").replace(
                "<head>", "<!-- </head> -->" + separator + "<head><style>/* </head> */</style>"
                '<script type="text/plain">literal </head></script>')
            result, _ = PREP.prepare_document(original, input_format="html")
            self.assert_only_insertion(original, result)
        invalid = self.document("Title </head> text").replace("</head><body>", "</head></head><body>")
        with self.assertRaisesRegex(PREP.PreparationError, "multiple closing heads"):
            PREP.prepare_document(invalid, input_format="html")


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
    global OPTIONS, PREP, CHECK, RUN
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument("--native-root", type=Path)
    OPTIONS = parser.parse_args()
    OPTIONS.fixture_root.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="pdf-tests-", dir=OPTIONS.fixture_root.resolve()))
    RUN = root
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
    for case in (Preparation, Reader, PhysicalGeometry, TextContexts) + ((NativePdf,) if OPTIONS.native_root else ()):
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
