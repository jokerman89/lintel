#!/usr/bin/env python3
# component: document-workbook-tests
# implements: ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: synthetic OOXML fixtures; no calculation, cache publication or application launch
# last_intent_review: 2026-09-22
"""Read-only integrity regressions; synthetic cached values are not engine evidence."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
from io import BytesIO
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import warnings
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
XLSX_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
SHEET_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
SST_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"
RELS_TYPE = "application/vnd.openxmlformats-package.relationships+xml"
OPTIONS = None
RUN = None
CHECK = None
RC = None
PC = None
SOURCE = None


def expected(value=37.5):
    return {
        "cells": [
            {"sheet": "Inputs", "cell": "B2", "formula": None, "type": "number", "value": 3},
            {"sheet": "Inputs", "cell": "B3", "formula": None, "type": "number", "value": 12.5},
            {"sheet": "Inputs", "cell": "B4", "formula": None, "type": "text", "value": "=1+1"},
            {"sheet": "Calculation", "cell": "B2", "formula": "=Inputs!B2*Inputs!B3",
             "type": "number", "value": value},
            {"sheet": "Summary", "cell": "B2", "formula": "=SUM(Calculation!B2)",
             "type": "number", "value": value},
        ],
        "required_text": ["synthetic evidence and limitation"],
    }


def fixture(cache="37.5", formula="Inputs!B2*Inputs!B3", cell_type="n"):
    """Handcrafted test package, not a claimed native workbook or engine output."""
    parts = {
        "[Content_Types].xml": (
            f'<Types xmlns="{CT}"><Default Extension="rels" ContentType="{RELS_TYPE}"/>'
            '<Default Extension="xml" ContentType="application/xml"/>'
            '<Default Extension="bin" ContentType="application/octet-stream"/>'
            f'<Override PartName="/xl/workbook.xml" ContentType="{XLSX_TYPE}"/>'
            + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="{SHEET_TYPE}"/>'
                      for i in range(1, 4)) + "</Types>"
        ),
        "_rels/.rels": f'<Relationships xmlns="{P}"><Relationship Id="root" Type="{R}/officeDocument" Target="xl/workbook.xml"/></Relationships>',
        "xl/workbook.xml": f'<workbook xmlns="{S}" xmlns:r="{R}"><sheets><sheet name="Inputs" sheetId="1" r:id="r1"/><sheet name="Calculation" sheetId="2" r:id="r2"/><sheet name="Summary" sheetId="3" r:id="r3"/></sheets></workbook>',
        "xl/_rels/workbook.xml.rels": f'<Relationships xmlns="{P}"><Relationship Id="r1" Type="{R}/worksheet" Target="worksheets/sheet1.xml"/><Relationship Id="r2" Type="{R}/worksheet" Target="worksheets/sheet2.xml"/><Relationship Id="r3" Type="{R}/worksheet" Target="worksheets/sheet3.xml"/></Relationships>',
        "xl/worksheets/sheet1.xml": f'<worksheet xmlns="{S}"><sheetData><row r="2"><c r="B2"><v>3</v></c></row><row r="3"><c r="B3"><v>12.5</v></c></row><row r="4"><c r="B4" t="inlineStr"><is><t>=1+1</t></is></c></row><row r="5"><c r="A5" t="inlineStr"><is><t>synthetic evidence and limitation</t></is></c></row></sheetData></worksheet>',
        "xl/worksheets/sheet2.xml": f'<worksheet xmlns="{S}"><sheetData><row r="2"><c r="B2" t="{cell_type}"><f>{formula}</f>' + (f"<v>{cache}</v>" if cache is not None else "") + '</c></row></sheetData></worksheet>',
        "xl/worksheets/sheet3.xml": f'<worksheet xmlns="{S}"><sheetData><row r="2"><c r="B2"><f>SUM(Calculation!B2)</f><v>37.5</v></c></row></sheetData></worksheet>',
    }
    return package(parts)


def package(parts):
    data = BytesIO()
    with ZipFile(data, "w", ZIP_DEFLATED) as archive:
        for name, value in parts.items():
            archive.writestr(name, value)
    return data.getvalue()


def alter(data, name, transform):
    with ZipFile(BytesIO(data)) as archive:
        parts = {entry: archive.read(entry) for entry in archive.namelist()}
    parts[name] = transform(parts[name].decode("utf-8"))
    return package(parts)


def fixture_parts():
    with ZipFile(BytesIO(fixture())) as archive:
        return {name: archive.read(name) for name in archive.namelist()}


def add_part(parts, name, data, content_type):
    parts[name] = data.encode("utf-8") if isinstance(data, str) else data
    entry = f'<Override PartName="/{name}" ContentType="{content_type}"/>'
    parts["[Content_Types].xml"] = parts["[Content_Types].xml"].replace(b"</Types>", entry.encode() + b"</Types>")


def add_relationship(parts, identifier, kind, target, owner="xl/workbook.xml"):
    name = str(Path(owner).parent).replace("\\", "/")
    name = (name + "/" if name != "." else "") + "_rels/" + Path(owner).name + ".rels"
    if name not in parts:
        parts[name] = f'<Relationships xmlns="{P}"/>'.encode()
    tree = ET.fromstring(parts[name])
    ET.SubElement(tree, f"{{{P}}}Relationship", {"Id": identifier, "Type": kind, "Target": target})
    parts[name] = ET.tostring(tree)


def shared_string_parts(value=None):
    parts = fixture_parts()
    parts["xl/worksheets/sheet1.xml"] = parts["xl/worksheets/sheet1.xml"].replace(
        b'<c r="B4" t="inlineStr"><is><t>=1+1</t></is></c>',
        b'<c r="B4" t="s"><v>0</v></c>')
    add_relationship(parts, "strings", R + "/sharedStrings", "strings.xml")
    add_part(parts, "xl/strings.xml", value or f'<sst xmlns="{S}"><si><t>=1+1</t></si></sst>', SST_TYPE)
    return parts


class PackageContract(unittest.TestCase):
    def test_content_types_required_and_well_formed(self):
        for invalid in (None, b"<broken", f'<Types xmlns="{CT}/wrong"/>'.encode(),
                        f'<wrong xmlns="{CT}"/>'.encode()):
            with self.subTest(invalid=invalid):
                parts = fixture_parts()
                if invalid is None:
                    del parts["[Content_Types].xml"]
                else:
                    parts["[Content_Types].xml"] = invalid
                with self.assertRaises(CHECK.WorkbookError):
                    CHECK.inspect_workbook(package(parts))

    def test_type_declarations_are_unique_valid_and_resolve_real_parts(self):
        additions = (
            '<Default Extension="XML" ContentType="application/xml"/>',
            f'<Override PartName="/xl/workbook.xml" ContentType="{XLSX_TYPE}"/>',
            f'<Override PartName="/missing.xml" ContentType="{SHEET_TYPE}"/>',
            f'<Override PartName="xl/workbook.xml" ContentType="{XLSX_TYPE}"/>',
            '<Default Extension="../xml" ContentType="application/xml"/>',
            '<Default Extension="data" ContentType=""/>',
            '<Unknown/>',
        )
        for addition in additions:
            with self.subTest(addition=addition), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), "[Content_Types].xml",
                    lambda text: text.replace("</Types>", addition + "</Types>")))
        parts = fixture_parts()
        parts["custom/untyped.data"] = b"synthetic"
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        parts = fixture_parts()
        parts["custom/bin"] = b"extensionless; not covered by the bin default"
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))

    def test_workbook_sheet_and_shared_string_declared_kinds_match(self):
        for original in (XLSX_TYPE, SHEET_TYPE):
            with self.subTest(kind=original), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), "[Content_Types].xml",
                                             lambda text: text.replace(original, "application/xml")))
        parts = shared_string_parts()
        parts["[Content_Types].xml"] = parts["[Content_Types].xml"].replace(SST_TYPE.encode(), SHEET_TYPE.encode())
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))

    def test_every_internal_target_is_checked_even_if_not_consumed(self):
        for owner in ("xl/workbook.xml", "xl/worksheets/sheet1.xml"):
            for target in ("../../../escape.xml", "missing.xml", "//outside/item.xml",
                           "item.xml?query", "item.xml#fragment", "item%2e.xml", "C:/outside.xml"):
                with self.subTest(owner=owner, target=target), self.assertRaises(CHECK.WorkbookError):
                    parts = fixture_parts()
                    add_relationship(parts, "unconsumed", "urn:synthetic:relationship", target, owner)
                    CHECK.inspect_workbook(package(parts))

    def test_valid_internal_relative_and_absolute_targets_are_preserved(self):
        for target in ("../../custom/data.bin", "/custom/data.bin"):
            with self.subTest(target=target):
                parts = fixture_parts()
                add_part(parts, "custom/data.bin", b"ordinary inert data", "application/octet-stream")
                add_relationship(parts, "unconsumed", "urn:synthetic:relationship", target,
                                 owner="xl/worksheets/sheet1.xml")
                self.assertEqual(CHECK.check_workbook(package(parts), expected())["status"], "pass")
        for target in ("../../custom/data.bin/", "../../custom/data.bin/."):
            with self.subTest(target=target), self.assertRaises(CHECK.WorkbookError):
                parts = fixture_parts()
                add_part(parts, "custom/data.bin", b"ordinary inert data", "application/octet-stream")
                add_relationship(parts, "unconsumed", "urn:synthetic:relationship", target,
                                 owner="xl/worksheets/sheet1.xml")
                CHECK.inspect_workbook(package(parts))

    def test_relationship_parts_need_real_owners_and_required_fields(self):
        parts = fixture_parts()
        parts["custom/_rels/missing.xml.rels"] = f'<Relationships xmlns="{P}"/>'.encode()
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        parts = fixture_parts()
        add_part(parts, "custom", b"inert extensionless part", "application/octet-stream")
        parts["custom/_rels/.rels"] = f'<Relationships xmlns="{P}"/>'.encode()
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        for field in ("Id", "Type", "Target"):
            parts = fixture_parts()
            root = ET.fromstring(parts["xl/_rels/workbook.xml.rels"])
            del root[0].attrib[field]
            parts["xl/_rels/workbook.xml.rels"] = ET.tostring(root)
            with self.subTest(field=field), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(package(parts))

    def test_renamed_forbidden_mechanisms_refused_by_either_declaration(self):
        families = (
            ("http://schemas.microsoft.com/office/2006/relationships/vbaProject", "application/vnd.ms-office.vbaProject"),
            (R + "/oleObject", "application/vnd.openxmlformats-officedocument.oleObject"),
            (R + "/externalLink", "application/vnd.openxmlformats-officedocument.spreadsheetml.externalLink+xml"),
            ("http://schemas.microsoft.com/office/2006/relationships/xlMacrosheet", "application/vnd.ms-excel.macrosheet+xml"),
        )
        for relation, media_type in families:
            for mode in ("relation", "content-type", "both"):
                with self.subTest(relation=relation, mode=mode), self.assertRaises(CHECK.WorkbookError):
                    parts = fixture_parts()
                    add_part(parts, "custom/inert.bin", b"synthetic inert marker",
                             media_type if mode != "relation" else "application/octet-stream")
                    if mode != "content-type":
                        add_relationship(parts, "unsupported", relation, "../custom/inert.bin")
                    CHECK.inspect_workbook(package(parts))

    def test_macro_enabled_workbook_kind_is_not_normal_xlsx(self):
        for mime in ("application/vnd.ms-excel.sheet.macroEnabled.main+xml",
                     "application/vnd.ms-excel.template.macroEnabled.main+xml"):
            with self.subTest(mime=mime), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), "[Content_Types].xml",
                                             lambda text: text.replace(XLSX_TYPE, mime)))

    def test_relationship_kind_and_content_type_are_consistent(self):
        parts = fixture_parts()
        add_part(parts, "custom/plain.xml", "<plain/>", "application/xml")
        add_relationship(parts, "extra-sheet", R + "/worksheet", "../custom/plain.xml")
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        data = alter(fixture(), "[Content_Types].xml", lambda text: text.replace(RELS_TYPE, "application/xml"))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(data)

    def test_required_workbook_and_sheet_containers_are_unambiguous(self):
        for part, old, new in (
            ("xl/workbook.xml", "<sheets>", "<sheets></sheets><sheets>"),
            ("xl/worksheets/sheet1.xml", "<sheetData>", "<sheetData></sheetData><sheetData>"),
            ("xl/worksheets/sheet1.xml", "<sheetData>", "<notSheetData>"),
        ):
            with self.subTest(part=part, new=new), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), part, lambda text: text.replace(old, new)))


class CellShapes(unittest.TestCase):
    def test_phonetic_format_metadata_preserves_plain_and_rich_text(self):
        for payload in ("<t>=1+1</t>", "<r><t>=1</t></r><r><t>+1</t></r>"):
            for shared in (False, True):
                with self.subTest(payload=payload, shared=shared):
                    value = payload + '<phoneticPr fontId="1"/>'
                    if shared:
                        data = package(shared_string_parts(f'<sst xmlns="{S}"><si>{value}</si></sst>'))
                    else:
                        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                                     lambda text: text.replace("<t>=1+1</t>", value))
                    self.assertEqual(CHECK.check_workbook(data, expected())["status"], "pass")
        duplicate = '<sst xmlns="' + S + '"><si><t>=1+1</t><phoneticPr fontId="1"/><phoneticPr fontId="2"/></si></sst>'
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(shared_string_parts(duplicate)))

    def test_shared_string_root_namespace_and_child_shapes(self):
        for xml in (f'<wrongRoot xmlns="{S}"><si><t>=1+1</t></si></wrongRoot>',
                    f'<sst xmlns="{S}/wrong"><si><t>=1+1</t></si></sst>',
                    f'<sst xmlns="{S}"><unknown><t>=1+1</t></unknown></sst>'):
            with self.subTest(xml=xml), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(package(shared_string_parts(xml)))

    def test_supported_shared_inline_rich_and_empty_strings(self):
        for shared in (False, True):
            for payload in ("<t>=1+1</t>", "<r><rPr><b/></rPr><t>=1</t></r><r><t>+1</t></r>", "<t/>"):
                with self.subTest(shared=shared, payload=payload):
                    wanted = expected()
                    if payload == "<t/>":
                        wanted["cells"][2]["value"] = ""
                    if shared:
                        data = package(shared_string_parts(f'<sst xmlns="{S}"><si>{payload}</si></sst>'))
                    else:
                        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                                     lambda text: text.replace("<t>=1+1</t>", payload))
                    self.assertEqual(CHECK.check_workbook(data, wanted)["status"], "pass")

    def test_literal_error_and_declaration_text_remain_plain_text(self):
        parts = shared_string_parts(f'<sst xmlns="{S}"><si><t>#DIV/0!</t></si></sst>')
        wanted = expected()
        wanted["cells"][2]["value"] = "#DIV/0!"
        self.assertEqual(CHECK.check_workbook(package(parts), wanted)["status"], "pass")
        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                     lambda text: text.replace("<t>=1+1</t>", "<t><![CDATA[<!DOCTYPE literal>]]></t>"))
        wanted["cells"][2]["value"] = "<!DOCTYPE literal>"
        self.assertEqual(CHECK.check_workbook(data, wanted)["status"], "pass")

    def test_blank_cell_is_preserved_but_unknown_empty_type_is_rejected(self):
        wanted = expected()
        wanted["cells"].append({"sheet": "Inputs", "cell": "A6", "formula": None, "type": "empty", "value": None})
        for type_attribute in ("", ' t="n"', ' t="not-a-cell-type"'):
            data = alter(fixture(), "xl/worksheets/sheet1.xml",
                         lambda text: text.replace("</sheetData>", f'<row r="6"><c r="A6"{type_attribute}/></row></sheetData>'))
            if "not-a-cell" in type_attribute:
                with self.assertRaises(CHECK.WorkbookError):
                    CHECK.check_workbook(data, wanted)
            else:
                self.assertEqual(CHECK.check_workbook(data, wanted)["status"], "pass")
        data = alter(fixture(cache=None), "xl/worksheets/sheet2.xml",
                     lambda text: text.replace('t="n"', 't="unknown"'))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(data)

    def test_ambiguous_payloads_are_checked_before_any_value_decode(self):
        changes = (
            ("<is><t>=1+1</t></is>", "<is><t>=1+1</t></is><is><t>other</t></is>"),
            ("<is><t>=1+1</t></is>", "<is><t>=1+1</t></is><v>2</v>"),
            ('<c r="B2"><v>3</v></c>', '<c r="B2"><v>3</v><is><t>other</t></is></c>'),
            ("<is><t>=1+1</t></is>", "<is><t>=1</t><t>+1</t></is>"),
            ("<is><t>=1+1</t></is>", "<is><t>=1</t><r><t>+1</t></r></is>"),
            ("<is><t>=1+1</t></is>", "<is><r><t>=1</t><t>+1</t></r></is>"),
            ("<is><t>=1+1</t></is>", '<is><t>=1+1</t></is><is xmlns="urn:foreign"><t>other</t></is>'),
            ('<c r="B2"><v>3</v></c>', '<c r="B2"><v>3</v><unknown/></c>'),
        )
        for old, new in changes:
            with self.subTest(new=new), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), "xl/worksheets/sheet1.xml",
                                             lambda text: text.replace(old, new)))


class XmlAndFormula(unittest.TestCase):
    def test_dtd_refusal_covers_supported_encodings_and_ordinary_utf16(self):
        for encoding in ("utf-8", "utf-16-le", "utf-16-be"):
            for declaration in ("", '<!DOCTYPE worksheet>', '<!DOCTYPE worksheet [<!ENTITY safe_value "3">]>'):
                with self.subTest(encoding=encoding, declaration=declaration):
                    parts = fixture_parts()
                    xml = parts["xl/worksheets/sheet1.xml"].decode()
                    if "ENTITY" in declaration:
                        xml = xml.replace("<v>3</v>", "<v>&safe_value;</v>")
                    declared = "UTF-8" if encoding == "utf-8" else "UTF-16"
                    xml = f'<?xml version="1.0" encoding="{declared}"?>' + declaration + xml
                    bom = {"utf-8": b"", "utf-16-le": b"\xff\xfe", "utf-16-be": b"\xfe\xff"}[encoding]
                    parts["xl/worksheets/sheet1.xml"] = bom + xml.encode(encoding)
                    if declaration:
                        with self.assertRaises(CHECK.WorkbookError):
                            CHECK.inspect_workbook(package(parts))
                    else:
                        self.assertEqual(CHECK.check_workbook(package(parts), expected())["status"], "pass")

    def test_declaration_guard_applies_to_all_consumed_xml_parts(self):
        for part in ("[Content_Types].xml", "_rels/.rels", "xl/workbook.xml",
                     "xl/_rels/workbook.xml.rels", "xl/worksheets/sheet1.xml", "xl/strings.xml"):
            parts = shared_string_parts()
            text = parts[part].decode()
            xml = '<?xml version="1.0" encoding="UTF-16"?>' + '<!DOCTYPE harmless [<!ENTITY safe_value "3">]>' + text
            parts[part] = xml.encode("utf-16")
            with self.subTest(part=part), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(package(parts))

    def test_explicit_normal_matches_omitted_normal_without_losing_cache_checks(self):
        for cache, outcome in (("37.5", "pass"), ("50", "fail"), (None, "unverified")):
            plain = CHECK.check_workbook(fixture(cache=cache), expected())
            explicit = CHECK.check_workbook(alter(fixture(cache=cache), "xl/worksheets/sheet2.xml",
                                                  lambda text: text.replace("<f>", '<f t="normal">')), expected())
            with self.subTest(cache=cache):
                self.assertEqual(plain["status"], outcome)
                self.assertEqual(explicit["status"], outcome)
                self.assertEqual(plain["issues"], explicit["issues"])

    def test_genuinely_unsupported_formula_attributes_remain_unverified(self):
        for attributes in ('t="shared" si="0"', 't="array" ref="B2:B3"', 't="dataTable" ref="B2:B3"',
                           't="unknown"', 't="normal" unknown="1"', 'ref="B2:B3"'):
            data = alter(fixture(), "xl/worksheets/sheet2.xml",
                         lambda text: text.replace("<f>", f"<f {attributes}>"))
            self.assertEqual(CHECK.check_workbook(data, expected())["status"], "unverified")

    def test_actual_input_part_expansion_and_entry_limits_remain(self):
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(b"x" * (CHECK.MAX_INPUT + 1))
        parts = fixture_parts()
        parts["custom/bounded.bin"] = b"x" * CHECK.MAX_PART
        self.assertEqual(CHECK.check_workbook(package(parts), expected())["status"], "pass")
        parts["custom/bounded.bin"] += b"x"
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        parts = fixture_parts()
        for index in range(4):
            parts[f"custom/large-{index}.bin"] = b"x" * CHECK.MAX_PART
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package({f"tiny/{index}.bin": b"" for index in range(10001)}))


class RetainedContrasts(unittest.TestCase):
    def test_numeric_lexical_equivalence_is_not_a_cache_recalculation(self):
        data = alter(fixture(), "xl/worksheets/sheet2.xml",
                     lambda text: text.replace("<v>37.5</v>", "<v>3.750e1</v>"))
        result = CHECK.check_workbook(data, expected())
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["calculation_execution_verified"])

    def test_typed_boolean_and_invalid_boolean_are_distinct(self):
        wanted = expected()
        wanted["cells"].append({"sheet": "Inputs", "cell": "A6", "formula": None, "type": "bool", "value": True})
        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                     lambda text: text.replace("</sheetData>", '<row r="6"><c r="A6" t="b"><v>1</v></c></row></sheetData>'))
        self.assertEqual(CHECK.check_workbook(data, wanted)["status"], "pass")
        invalid = alter(data, "xl/worksheets/sheet1.xml", lambda text: text.replace("<v>1</v>", "<v>2</v>"))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(invalid)

    def test_promoted_literal_and_very_hidden_formula_still_fail(self):
        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                     lambda text: text.replace('<c r="B4" t="inlineStr"><is><t>=1+1</t></is></c>',
                                               '<c r="B4"><f>1+1</f><v>2</v></c>'))
        self.assertEqual(CHECK.check_workbook(data, expected())["status"], "fail")
        data = alter(fixture(), "xl/workbook.xml",
                     lambda text: text.replace('name="Summary"', 'name="Summary" state="veryHidden"'))
        wanted = expected()
        wanted["cells"].pop()
        self.assertEqual(CHECK.check_workbook(data, wanted)["status"], "fail")

    def test_cell_bounds_namespaces_and_duplicate_values_remain_refused(self):
        for part, old, new in (
            ("xl/worksheets/sheet1.xml", 'r="B4"', 'r="XFE1"'),
            ("xl/worksheets/sheet1.xml", S, S + "/wrong"),
            ("xl/worksheets/sheet2.xml", "<v>37.5</v>", "<v>37.5</v><v>99</v>"),
            ("xl/worksheets/sheet2.xml", "<f>Inputs!B2*Inputs!B3</f>", "<f>Inputs!B2*Inputs!B3</f><f>1</f>"),
            ("xl/_rels/workbook.xml.rels", 'Id="r3"', 'Id="r2"'),
        ):
            with self.subTest(part=part, new=new), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(alter(fixture(), part, lambda text: text.replace(old, new)))
        wanted = expected()
        wanted["cells"][0]["cell"] = "A1048577"
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.check_workbook(fixture(), wanted)

    def test_duplicate_and_escaping_package_parts_remain_refused(self):
        parts = fixture_parts()
        stream = BytesIO()
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            with ZipFile(stream, "w", ZIP_DEFLATED) as archive:
                for name, data in parts.items():
                    archive.writestr(name, data)
                archive.writestr("xl/workbook.xml", parts["xl/workbook.xml"])
        with self.assertRaisesRegex(CHECK.WorkbookError, "Duplicate package part"):
            CHECK.inspect_workbook(stream.getvalue())
        parts["../escape.xml"] = b"<unused/>"
        with self.assertRaisesRegex(CHECK.WorkbookError, "Invalid package part"):
            CHECK.inspect_workbook(package(parts))

    def test_public_cli_duplicate_json_and_actual_input_bound(self):
        folder = Path(tempfile.mkdtemp(prefix="cli-limits-", dir=RUN))
        workbook = folder / "source.xlsx"
        workbook.write_bytes(fixture())
        oracle = folder / "expectations.json"
        oracle.write_text('{"cells":[],"cells":[]}', encoding="utf-8")
        command = [sys.executable, "-I", "-B", str(ROOT / "skills/generate-xlsx/scripts/check_xlsx.py"),
                   "--root", str(folder), "--workbook", workbook.name, "--expect", oracle.name]
        for label in ("duplicate-json", "input-bound"):
            if label == "input-bound":
                oracle.write_text(json.dumps(expected()), encoding="utf-8")
                with workbook.open("wb") as stream:
                    stream.truncate(CHECK.MAX_INPUT + 1)
            prefix = RUN / f"cli-{label}"
            prefix.with_suffix(".command.json").write_text(json.dumps({"argv": command, "cwd": str(folder)}), encoding="utf-8")
            with prefix.with_suffix(".stdout.log").open("wb") as out, prefix.with_suffix(".stderr.log").open("wb") as err:
                result = subprocess.run(command, cwd=folder, env=dict(os.environ), stdout=out, stderr=err)
            prefix.with_suffix(".exit.json").write_text(json.dumps({"exit": result.returncode}), encoding="utf-8")
            self.assertEqual(result.returncode, 2)
            self.assertEqual(json.loads(prefix.with_suffix(".stdout.log").read_text())["status"], "error")
        workbook.unlink()
        oracle.unlink()
        folder.rmdir()

class Integrity(unittest.TestCase):
    def test_exact_formula_and_cache_pass_only_integrity(self):
        result = CHECK.check_workbook(fixture(), expected())
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["calculation_execution_verified"])
        self.assertFalse(result["rendered_layout_verified"])
        self.assertFalse(result["release_clearance"])

    def test_absent_and_empty_caches_are_unverified(self):
        for cache in (None, ""):
            with self.subTest(cache=cache):
                result = CHECK.check_workbook(fixture(cache=cache), expected())
                self.assertEqual(result["status"], "unverified")
                self.assertIn("cache_missing", {issue["code"] for issue in result["issues"]})

    def test_stale_cache_fails(self):
        result = CHECK.check_workbook(fixture(cache="50"), expected())
        self.assertEqual(result["status"], "fail")
        self.assertIn("value_mismatch", {issue["code"] for issue in result["issues"]})

    def test_formula_replaced_by_constant_fails(self):
        data = alter(fixture(), "xl/worksheets/sheet2.xml",
                     lambda text: text.replace("<f>Inputs!B2*Inputs!B3</f>", ""))
        self.assertEqual(CHECK.check_workbook(data, expected())["status"], "fail")

    def test_changed_formula_fails_even_if_cache_matches(self):
        self.assertEqual(CHECK.check_workbook(fixture(formula="1+36.5"), expected())["status"], "fail")

    def test_formula_errors_never_pass(self):
        for error in ("#DIV/0!", "#NAME?", "#REF!", "#CIRCULAR!"):
            with self.subTest(error=error):
                self.assertEqual(CHECK.check_workbook(fixture(cache=error, cell_type="e"), expected())["status"], "fail")

    def test_formula_looking_text_is_not_executed_or_promoted(self):
        result = CHECK.inspect_workbook(fixture())
        cell = next(c for c in result["cells"] if c["sheet"] == "Inputs" and c["cell"] == "B4")
        self.assertIsNone(cell["formula"])
        self.assertEqual((cell["type"], cell["value"]), ("text", "=1+1"))

    def test_string_numeric_cache_is_not_numeric_value(self):
        self.assertEqual(CHECK.check_workbook(fixture(cell_type="str"), expected())["status"], "fail")

    def test_nonfinite_cache_rejected(self):
        for value in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(value=value), self.assertRaises(CHECK.WorkbookError):
                CHECK.inspect_workbook(fixture(cache=value))

    def test_hidden_unselected_formula_is_not_ignored(self):
        data = alter(fixture(), "xl/workbook.xml",
                     lambda text: text.replace('name="Summary"', 'name="Summary" state="hidden"'))
        limited = expected()
        limited["cells"].pop()
        result = CHECK.check_workbook(data, limited)
        self.assertEqual(result["status"], "fail")
        self.assertIn("unselected_formula", {issue["code"] for issue in result["issues"]})

    def test_shared_and_array_formula_semantics_are_unverified(self):
        for kind in ("shared", "array", "dataTable"):
            data = alter(fixture(), "xl/worksheets/sheet2.xml",
                         lambda text: text.replace("<f>", f'<f t="{kind}" ref="B2:B3">'))
            self.assertEqual(CHECK.check_workbook(data, expected())["status"], "unverified")

    def test_external_relationships_and_macros_refused(self):
        data = alter(fixture(), "xl/_rels/workbook.xml.rels",
                     lambda text: text.replace("</Relationships>", f'<Relationship Id="external" Type="{R}/externalLink" TargetMode="External" Target="https://example.invalid/book.xlsx"/></Relationships>'))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(data)
        with ZipFile(BytesIO(fixture())) as archive:
            parts = {name: archive.read(name) for name in archive.namelist()}
        parts["xl/vbaProject.bin"] = b"synthetic non-executable marker"
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(package(parts))

    def test_duplicate_cells_and_aliased_sheets_refused(self):
        data = alter(fixture(), "xl/worksheets/sheet1.xml",
                     lambda text: text.replace('<c r="B2"><v>3</v></c>', '<c r="B2"><v>3</v></c><c r="B2"><v>9</v></c>'))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(data)
        data = alter(fixture(), "xl/_rels/workbook.xml.rels",
                     lambda text: text.replace('Target="worksheets/sheet3.xml"', 'Target="worksheets/sheet2.xml"'))
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(data)

    def test_missing_source_paragraph_and_table_cell_fail(self):
        wanted = expected()
        wanted["required_text"].append("MATERIAL LIMITATION: absent from this test fixture")
        self.assertEqual(CHECK.check_workbook(fixture(), wanted)["status"], "fail")
        wanted = expected()
        wanted["cells"][0]["value"] = 4
        self.assertEqual(CHECK.check_workbook(fixture(), wanted)["status"], "fail")

    def test_unknown_or_duplicate_expectations_refused(self):
        for wanted in ({}, {"cells": [], "unknown": True},
                       {"cells": [expected()["cells"][0]] * 2},
                       {"cells": [{"sheet": "Inputs", "cell": "B2", "formula": None, "type": [], "value": 3}]}):
            with self.subTest(wanted=wanted), self.assertRaises(CHECK.WorkbookError):
                CHECK.check_workbook(fixture(), wanted)

    def test_numeric_boolean_and_empty_formula_are_not_silently_coerced(self):
        wanted = expected()
        wanted["cells"][0]["value"] = True
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.check_workbook(fixture(), wanted)
        with self.assertRaises(CHECK.WorkbookError):
            CHECK.inspect_workbook(fixture(cache="3_7.5"))
        data = fixture(formula="")
        self.assertEqual(CHECK.check_workbook(data, expected())["status"], "fail")

    def test_cli_is_read_only_and_reports_invalid_or_unverified(self):
        folder = Path(tempfile.mkdtemp(prefix="cli-", dir=RUN))
        file = folder / "input.xlsx"
        file.write_bytes(fixture(cache=None))
        oracle = folder / "expectations.json"
        oracle.write_text(json.dumps(expected()), encoding="utf-8")
        before = file.read_bytes()
        command = [sys.executable, "-I", "-B", str(ROOT / "skills/generate-xlsx/scripts/check_xlsx.py"),
                   "--root", str(folder), "--workbook", file.name, "--expect", oracle.name]
        for label, argv, expected_exit in (
            ("missing-cache", command, 3),
            ("escape", command[:-3] + ["..\\outside.xlsx", "--expect", oracle.name], 2),
        ):
            with (RUN / f"cli-{label}.stdout.log").open("wb") as stdout, \
                    (RUN / f"cli-{label}.stderr.log").open("wb") as stderr:
                completed = subprocess.run(argv, cwd=folder, env=dict(os.environ), stdout=stdout, stderr=stderr)
            self.assertEqual(completed.returncode, expected_exit)
        self.assertEqual(file.read_bytes(), before)
        self.assertFalse((folder.parent / "outside.xlsx").exists())
        file.unlink()
        oracle.unlink()
        folder.rmdir()

    def test_policy_does_not_clear_missing_cache_or_renderer(self):
        home = RUN / "profile-home"
        repo = RUN / "profile-target"
        home.mkdir(exist_ok=True)
        repo.mkdir(exist_ok=True)
        config = PC.ProfileConfig(ROOT, repo, home, home / "packs", home / "packs/active-pack",
                                  context_id="workbook-tests")
        pin = PC.bootstrap_profile_context(config)
        reference = PC.profile_reference(pin)
        PC.verify_profile_reference(reference, config)
        controls = []
        for identifier in ("persisted-cache", "rendered-layout"):
            controls.append({
                "id": identifier, "kind": "check", "requirement": "mandatory",
                "applicability": "applicable", "status": "unverified", "reason": "Actual observation unavailable",
                "policy": {"source": "P12.md", "version": "235d5bf", "applicability": "Required workbook observation",
                           "jurisdiction": None, "actor": None, "effective_date": None},
                "evidence": ["native-observation.json"], "observation": {}, "advisory_score": 100,
            })
        self.assertTrue(RC.evaluate_controls(controls, required_policy=PC.required_policy(pin))["blocked"])


class SourceContract(unittest.TestCase):
    def test_standalone_flags_and_complete_source_are_retained(self):
        text = (ROOT / "skills/generate-xlsx/SKILL.md").read_text(encoding="utf-8")
        for token in ("--brief", "--from-pipeline", "--update-data", "--out", "Inputs",
                      "Calculation", "Summary", "Sources", "Methods", "literal", "P05", "P07"):
            self.assertIn(token, text)
        self.assertNotIn("Non-tabular sections (narrative, vision) are excluded", text)
        self.assertIn("persisted", text)
        self.assertIn("unverified", text)

    def test_native_route_does_not_invent_cache_or_render_actions(self):
        text = (ROOT / "skills/generate-xlsx/references/native-xlsx.md").read_text(encoding="utf-8")
        for token in ("get_range", "set_formula", "read_package_entry", "37.5", "50",
                      "empty", "recalculate", "renderer", "not an OS sandbox"):
            self.assertIn(token, text)
        self.assertNotIn("npm install", text)


class NativeArtifacts(unittest.TestCase):
    def test_native_formulas_inputs_and_long_source_retained_but_caches_block(self):
        data = (OPTIONS.native_root / "formula-probe.xlsx").read_bytes()
        wanted = expected(50)
        wanted["cells"][0]["value"] = 4
        wanted["required_text"] = [p for _, paragraphs in SOURCE.SECTIONS for p in paragraphs]
        wanted["required_text"] += list(SOURCE.REFERENCES)
        result = CHECK.check_workbook(data, wanted)
        self.assertEqual(result["status"], "unverified")
        self.assertEqual({issue["code"] for issue in result["issues"]}, {"cache_missing"})
        self.assertEqual(len(result["issues"]), 2)

    def test_native_ledger_and_capacity_cells_are_real_cells(self):
        result = CHECK.inspect_workbook((OPTIONS.native_root / "formula-probe.xlsx").read_bytes())
        cells = {(item["sheet"], item["cell"]): item for item in result["cells"]}
        for row_index, row in enumerate(SOURCE.CLAIMS, 6):
            for col, value in zip(("A", "B", "C"), row):
                self.assertEqual(cells["Sources", f"{col}{row_index}"]["value"], value)
        for row_index, row in enumerate(SOURCE.CAPACITY, 12):
            for col, value in zip(("A", "B", "C"), row):
                self.assertEqual(str(cells["Sources", f"{col}{row_index}"]["value"]), value)

    def test_read_only_inspection_does_not_modify_native_artifact(self):
        path = OPTIONS.native_root / "formula-probe.xlsx"
        original = path.read_bytes()
        CHECK.inspect_workbook(original)
        self.assertEqual(path.read_bytes(), original)


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Missing trusted module: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def main():
    global OPTIONS, RUN, CHECK, RC, PC, SOURCE
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture-root", type=Path, default=Path(tempfile.gettempdir()))
    parser.add_argument("--native-root", type=Path)
    OPTIONS = parser.parse_args()
    OPTIONS.fixture_root.mkdir(parents=True, exist_ok=True)
    RUN = Path(tempfile.mkdtemp(prefix="workbook-", dir=OPTIONS.fixture_root.resolve()))
    roots = {name: RUN / name for name in ("home", "app", "localapp", "temp", "lintel", "target")}
    for path in roots.values():
        path.mkdir()
    env = {
        "PATH": os.pathsep.join((str(Path(sys.executable).parent), os.defpath)), "PATHEXT": ".COM;.EXE;.BAT;.CMD",
        "HOME": str(roots["home"]), "USERPROFILE": str(roots["home"]),
        "APPDATA": str(roots["app"]), "LOCALAPPDATA": str(roots["localapp"]),
        "TEMP": str(roots["temp"]), "TMP": str(roots["temp"]), "TMPDIR": str(roots["temp"]),
        "LINTEL_HOME": str(roots["lintel"]), "LINTEL_SOURCE_ROOT": str(ROOT),
        "LINTEL_REPO_ROOT": str(roots["target"]), "LINTEL_PROFILE_CONTEXT": "workbook-tests",
        "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(RUN / "empty.gitconfig"),
        "GIT_CEILING_DIRECTORIES": str(RUN), "GIT_TERMINAL_PROMPT": "0",
    }
    if os.name == "nt":
        env.update(SystemRoot="C:\\Windows", WINDIR="C:\\Windows",
                   HOMEDRIVE=roots["home"].drive, HOMEPATH=str(roots["home"])[2:],
                   ComSpec="C:\\Windows\\System32\\cmd.exe")
    os.environ.clear()
    os.environ.update(env)
    tempfile.tempdir = str(roots["temp"])
    sys.dont_write_bytecode = True
    (RUN / "empty.gitconfig").write_bytes(b"")
    closure = (
        "skills/generate-xlsx/scripts/check_xlsx.py",
        "lib/context_safety.py", "lib/native_paths.py", "lib/profile_context.py",
        "lib/profile-context-schema.json", "lib/pack-schema.yaml", "packs/_default/pack.yaml",
        "lib/review_contract.py", "lib/review-schema.json", "lib/markdown_source.py",
        ".claude-plugin/plugin.json", "tests/integration/document-format-pipeline.py",
    )
    hashes = {}
    for name in closure:
        path = ROOT / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError(f"Missing/linked trusted source dependency: {path}")
        hashes[name] = hashlib.sha256(path.read_bytes()).hexdigest()
    (RUN / "preflight.json").write_text(json.dumps({
        "environment": env, "source": str(ROOT), "source_sha256": hashes,
        "native_root": str(OPTIONS.native_root) if OPTIONS.native_root else None,
        "boundary": "No native/application execution or formula calculation by these tests.",
    }, indent=2), encoding="utf-8")
    print(f"preflight: {RUN / 'preflight.json'}", flush=True)
    sys.path.insert(0, str(ROOT / "lib"))
    RC = load("review_contract", ROOT / "lib/review_contract.py")
    PC = load("profile_context", ROOT / "lib/profile_context.py")
    CHECK = load("check_xlsx", ROOT / "skills/generate-xlsx/scripts/check_xlsx.py")
    SOURCE = load("document_source_fixture", ROOT / "tests/integration/document-format-pipeline.py")
    suite = unittest.TestSuite()
    for case in (Integrity, SourceContract, PackageContract, CellShapes, XmlAndFormula, RetainedContrasts) + ((NativeArtifacts,) if OPTIONS.native_root else ()):
        suite.addTests(unittest.defaultTestLoader.loadTestsFromTestCase(case))
    if not OPTIONS.native_root:
        print("No native specimens supplied; native calculation/editability/rendering acceptance is not included.")
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    removed = []
    for name in ("profile-home", "profile-target"):
        path = RUN / name
        if path.exists():
            if path.is_symlink() or path.parent != RUN:
                raise RuntimeError("Fixture cleanup scope changed")
            shutil.rmtree(Path("\\\\?\\" + str(path)) if os.name == "nt" else path)
            removed.append(name)
    (RUN / "result.json").write_text(json.dumps({
        "executed": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "success": result.wasSuccessful(),
        "calculation_or_render_executed": False,
        "retained_fixture": str(RUN),
        "removed_synthetic_profile_directories": removed,
    }, indent=2), encoding="utf-8")
    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
