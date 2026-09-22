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
import xml.etree.ElementTree as ET
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[2]
S = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
P = "http://schemas.openxmlformats.org/package/2006/relationships"
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
    for case in (Integrity, SourceContract) + ((NativeArtifacts,) if OPTIONS.native_root else ()):
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
