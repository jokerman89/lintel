#!/usr/bin/env python3
# component: pptx-checker-tests
# implements: ADR-0028, ADR-0033
# intent: .claude/plans/v2-findings/plan.md
# constraints: synthetic ZIP/XML only; no application, network, extraction or cleanup
# last_intent_review: 2026-10-03
"""Behavioral checks of the shipped read-only PPTX checker, not Office acceptance."""
from dataclasses import replace
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import struct
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
from xml.sax.saxutils import escape
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
HELPER = ROOT / "skills/generate-ppt/scripts/check_pptx.py"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PR = "http://schemas.openxmlformats.org/package/2006/relationships"
DETAIL = "MATERIAL LIMITATION: storage failure remains untested. [S2]"
SOURCE = "A durable checkpoint.\n\n" + DETAIL + "\n\n100 ms\n"


def relationships(*items):
    return (f'<Relationships xmlns="{PR}">' + "".join(
        f'<Relationship Id="{ident}" Type="{R}/{kind}" Target="{target}"{mode}/>'
        for ident, kind, target, mode in items) + "</Relationships>").encode()


def document(kind, text):
    return (f'<p:{kind} xmlns:p="{P}" xmlns:a="{A}"><p:cSld><p:spTree>'
            f'<p:sp><p:txBody><a:p><a:r><a:t>{escape(text)}</a:t></a:r></a:p>'
            f'</p:txBody></p:sp></p:spTree></p:cSld></p:{kind}>').encode()


def package_parts():
    parts = {
        "ppt/presentation.xml": (
            f'<p:presentation xmlns:p="{P}" xmlns:r="{R}"><p:sldIdLst>'
            '<p:sldId id="256" r:id="s1"/><p:sldId id="257" r:id="s2"/>'
            '</p:sldIdLst></p:presentation>').encode(),
        "ppt/_rels/presentation.xml.rels": relationships(
            ("s1", "slide", "slides/slide1.xml", ""),
            ("s2", "slide", "slides/slide2.xml", "")),
    }
    for i, text in enumerate(("A durable checkpoint.", DETAIL + " 100 ms"), 1):
        parts[f"ppt/slides/slide{i}.xml"] = document("sld", f"Visible summary {i}")
        parts[f"ppt/slides/_rels/slide{i}.xml.rels"] = relationships(
            ("n1", "notesSlide", f"../notesSlides/notesSlide{i}.xml", ""))
        parts[f"ppt/notesSlides/notesSlide{i}.xml"] = document("notes", text)
        parts[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = relationships(
            ("s1", "slide", f"../slides/slide{i}.xml", ""))
    return parts


class PptxChecker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location("shipped_pptx_checker", HELPER)
        cls.checker = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = cls.checker
        spec.loader.exec_module(cls.checker)

    def setUp(self):
        # Preserve fixtures under the caller's explicit test-parent temp root.
        self.root = Path(tempfile.mkdtemp(prefix="pptx-checker-"))
        self.source = self.root / "source.txt"
        self.source.write_text(SOURCE, encoding="utf-8")

    def test_limits_reject_nonrepresentable_or_invalid_numeric_domains(self):
        original = self.checker.Limits()
        for field in vars(original):
            for value in (0, -1, True, False, float("nan"), float("inf"), float("-inf"),
                          -(10 ** 400)):
                with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                    replace(original, **{field: value})
            for value in (10 ** 400, sys.maxsize, sys.maxsize + 1):
                with self.subTest(field=field, value=value):
                    if field in ("archive_bytes", "xml_bytes", "source_bytes"):
                        with self.assertRaises(ValueError):
                            replace(original, **{field: value})
                    else:
                        self.assertEqual(getattr(replace(original, **{field: value}), field), value)
            with self.subTest(field=field, boundary="largest representable read bound"):
                self.assertEqual(getattr(replace(original, **{field: sys.maxsize - 1}), field),
                                 sys.maxsize - 1)
        self.assertEqual(original, self.checker.Limits())
        logical_limits = replace(original, total_bytes=10 ** 400, member_bytes=10 ** 400,
                                 entries=10 ** 400, compression_ratio=10 ** 400)
        self.assertEqual(self.check(limits=logical_limits)["status"], "pass")

    def archive(self, parts=None, extra=()):
        path = self.root / f"deck-{len(list(self.root.glob('*.pptx')))}.pptx"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(path, "x", ZIP_DEFLATED) as package:
                for name, data in (parts if parts is not None else package_parts()).items():
                    package.writestr(name, data)
                for name, data in extra:
                    package.writestr(name, data)
        return path

    def check(self, parts=None, **kwargs):
        return self.checker.check_pptx(self.archive(parts), [self.source], **kwargs)

    def test_real_package_retains_source_without_writes_or_render_claims(self):
        artifact = self.archive()
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        result = self.checker.check_pptx(artifact, [self.source])
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["missing"], [])
        self.assertEqual(result["slides"], 2)
        self.assertEqual(result["sources"][0]["sha256"], hashlib.sha256(before["source.txt"]).hexdigest())
        self.assertEqual(result["artifact"]["sha256"], hashlib.sha256(before[artifact.name]).hexdigest())
        for key in ("native_reopen", "editability", "rendered_layout"):
            self.assertEqual(result[key], "unverified")
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})

    def test_missing_source_detail_and_orphan_notes_never_pass(self):
        parts = package_parts()
        parts["ppt/notesSlides/notesSlide2.xml"] = document("notes", "100 ms")
        parts["ppt/notesSlides/notesSlide99.xml"] = document("notes", DETAIL)
        parts["ppt/slides/slide99.xml"] = document("sld", DETAIL)
        result = self.check(parts)
        self.assertEqual(result["status"], "fail")
        self.assertIn(DETAIL, result["missing"])

    def test_presentation_order_and_split_text_runs(self):
        parts = package_parts()
        parts["ppt/presentation.xml"] = parts["ppt/presentation.xml"].replace(
            b'r:id="s1"', b'r:id="tmp"').replace(b'r:id="s2"', b'r:id="s1"').replace(
                b'r:id="tmp"', b'r:id="s2"')
        parts["ppt/notesSlides/notesSlide1.xml"] = parts["ppt/notesSlides/notesSlide1.xml"].replace(
            b"durable", b"dur</a:t></a:r><a:r><a:t>able")
        artifact = self.archive(parts)
        self.assertIn(DETAIL, self.checker.slide_notes(artifact)[0])
        self.assertEqual(self.checker.check_pptx(artifact, [self.source])["status"], "pass")

    def test_alias_and_duplicate_notes_relationships_are_refused(self):
        for links in (
            (("n1", "notesSlide", "../notesSlides/./notesSlide1.xml", ""),),
            (("n1", "notesSlide", "../notesSlides/notesSlide2.xml", ""),
             ("n2", "notesSlide", "../notesSlides/notesSlide2.xml", "")),
            (("n1", "notesSlide", "../notesSlides/notesSlide2.xml", ""),
             ("n1", "notesSlide", "../notesSlides/notesSlide2.xml", "")),
        ):
            with self.subTest(links=links):
                parts = package_parts()
                parts["ppt/slides/_rels/slide2.xml.rels"] = relationships(*links)
                with self.assertRaises(ValueError):
                    self.check(parts)

    def test_external_empty_encoded_and_traversing_notes_targets_refused(self):
        for target, mode in (
            ("https://example.invalid/notes.xml", ' TargetMode="External"'),
            ("../notesSlides/notesSlide1.xml", ' TargetMode="External"'),
            ("", ""), ("../../../outside.xml", ""), ("file:///tmp/notes.xml", ""),
            ("../notesSlides/%6eotesSlide2.xml", ""), ("../notesSlides/notesSlide2.xml#x", ""),
            ("..\\notesSlides\\notesSlide2.xml", ""),
        ):
            with self.subTest(target=target, mode=mode):
                parts = package_parts()
                parts["ppt/slides/_rels/slide2.xml.rels"] = relationships(
                    ("n1", "notesSlide", target, mode))
                with self.assertRaises(ValueError):
                    self.check(parts)

    def test_missing_relationship_part_note_and_backlink_refused(self):
        for name in ("ppt/presentation.xml", "ppt/_rels/presentation.xml.rels",
                     "ppt/slides/_rels/slide2.xml.rels", "ppt/notesSlides/notesSlide2.xml",
                     "ppt/notesSlides/_rels/notesSlide2.xml.rels"):
            with self.subTest(name=name):
                parts = package_parts()
                del parts[name]
                with self.assertRaises(ValueError):
                    self.check(parts)
        parts = package_parts()
        parts["ppt/notesSlides/_rels/notesSlide2.xml.rels"] = relationships(
            ("s1", "slide", "../slides/slide1.xml", ""))
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_malformed_xml_wrong_namespace_and_dtd_are_refused(self):
        for content in (b"<broken", b"<Relationships/>", b"<notes/>",
                        b'<!DOCTYPE notes [<!ENTITY x "test">]><notes>&x;</notes>',
                        '<!DOCTYPE notes><notes/>'.encode("utf-16")):
            with self.subTest(content=content):
                parts = package_parts()
                parts["ppt/notesSlides/notesSlide2.xml"] = content
                with self.assertRaises(ValueError):
                    self.check(parts)
        parts = package_parts()
        parts["ppt/slides/_rels/slide2.xml.rels"] = b"<Relationships/>"
        with self.assertRaises(ValueError):
            self.check(parts)

    def test_duplicate_aliased_and_unsafe_zip_members_refused(self):
        for member in ("ppt/notesSlides/notesSlide1.xml", "PPT/NOTESSLIDES/NOTESSLIDE1.XML",
                       "../outside.xml", "ppt/notesSlides/../notesSlides/notesSlide7.xml"):
            with self.subTest(member=member):
                with self.assertRaises(ValueError):
                    self.checker.check_pptx(self.archive(extra=[(member, b"<x/>")]), [self.source])

    def test_bounded_archive_total_member_xml_source_and_entry_reads(self):
        defaults = self.checker.Limits()
        for change in ({"archive_bytes": 64}, {"total_bytes": 32}, {"member_bytes": 32},
                       {"xml_bytes": 32}, {"source_bytes": 16}, {"entries": 2}):
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    self.check(limits=replace(defaults, **change))
        bomb = self.archive(extra=[("media/inert.bin", b"0" * 500_000)])
        with self.assertRaises(ValueError):
            self.checker.check_pptx(bomb, [self.source])

    def test_missing_blank_and_invalid_utf8_sources_refused(self):
        artifact = self.archive()
        with self.assertRaises(ValueError):
            self.checker.check_pptx(artifact, [])
        with self.assertRaises((ValueError, OSError)):
            self.checker.check_pptx(artifact, [self.root / "absent.txt"])
        for raw in (b" \n\n ", b"\xff"):
            self.source.write_bytes(raw)
            with self.assertRaises(ValueError):
                self.checker.check_pptx(artifact, [self.source])

    def test_nonregular_input_is_rejected_before_open(self):
        # A real directory supplies the nonregular stat. Opening a special input
        # can block on other platforms, so admission must happen before open.
        with patch.object(Path, "open", side_effect=AssertionError("nonregular input opened")):
            with self.assertRaises(ValueError):
                self.checker.inspect_pptx(self.root)

    def test_retention_uses_explicit_required_paragraphs_and_cells(self):
        parts = self.checker.document_text(self.archive())
        self.assertEqual(self.checker.missing_content(parts, [DETAIL, "100 ms"]), [])
        self.assertEqual(self.checker.missing_content(parts, ["unretained detail"]), ["unretained detail"])

    def test_existing_long_brief_regression_consumes_the_shipped_algorithm(self):
        spec = importlib.util.spec_from_file_location(
            "fidelity_original_document_fixture", ROOT / "tests/integration/document-format-pipeline.py")
        original = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(original)  # main is deliberately not run
        original.write_fixture(self.root / "original-source")
        source_before = (self.root / "original-source/brief.md").read_bytes()
        required = [p for _, paragraphs in original.SECTIONS for p in paragraphs]
        required += list(original.REFERENCES)
        required += [cell for rows in (original.CAPACITY, original.CLAIMS) for row in rows for cell in row]
        parts = package_parts()
        parts["ppt/notesSlides/notesSlide1.xml"] = document("notes", "\n\n".join(required))
        good = original.document_text(self.archive(parts))
        self.assertEqual(original.missing_content(good), [])
        self.assertEqual(Path(original.check_pptx.__file__).resolve(), HELPER.resolve())
        self.assertIs(original.slide_notes, original.check_pptx.slide_notes)
        lost = original.SECTIONS[3][1][0]
        parts["ppt/notesSlides/notesSlide1.xml"] = document("notes", "\n\n".join(required).replace(lost, ""))
        self.assertIn(lost, original.missing_content(original.document_text(self.archive(parts))))
        self.assertEqual((self.root / "original-source/brief.md").read_bytes(), source_before)

    def test_corrupt_deflate_is_an_invalid_input_not_a_traceback(self):
        valid = self.archive()
        with ZipFile(valid) as package:
            offset = package.getinfo("ppt/presentation.xml").header_offset
        raw = bytearray(valid.read_bytes())
        name_length, extra_length = struct.unpack_from("<HH", raw, offset + 26)
        start = offset + 30 + name_length + extra_length
        raw[start] = (raw[start] & ~6) | 6  # reserved DEFLATE block type
        broken = self.root / "corrupt.pptx"
        broken.write_bytes(raw)
        with self.assertRaises(ValueError):
            self.checker.check_pptx(broken, [self.source])
        result = subprocess.run(
            [sys.executable, str(HELPER), "--artifact", str(broken), "--source", str(self.source)],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)
        self.assertNotIn("Traceback", result.stderr)

    def test_cli_requires_actual_inputs_and_distinguishes_failure_from_invalid(self):
        artifact = self.archive()
        args = [sys.executable, str(HELPER), "--artifact", str(artifact), "--source", str(self.source)]
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "pass")
        self.source.write_text("Missing reasoning paragraph.", encoding="utf-8")
        result = subprocess.run(args, cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 1, result.stderr)
        result = subprocess.run(args[:2], cwd=ROOT, capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
