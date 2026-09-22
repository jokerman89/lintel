#!/usr/bin/env python3
# component: document-pipeline-binding-tests
# implements: ADR-0028, ADR-0029, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: synthetic inputs and real data providers; no renderer, network or review-record publication
# last_intent_review: 2026-09-23
"""Exercise existing document pipeline input admission, not native artifact acceptance."""
from __future__ import annotations

import argparse
from copy import deepcopy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[2]
RUN = None
OPTIONS = None
PIPELINE = None
FIXTURE = None
SAFETY = None
PROFILE = None
REVIEW = None
DESIGN = None


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def encoded(value):
    return (json.dumps(value, ensure_ascii=True, allow_nan=False) + "\n").encode("utf-8")


class PipelineBinding(unittest.TestCase):
    maxDiff = 1600

    def setUp(self):
        self.base = Path(tempfile.mkdtemp(prefix="case-", dir=RUN))
        self.repo, self.home = self.base / "repo", self.base / "home"
        roots = {
            "HOME": self.home, "USERPROFILE": self.home,
            "APPDATA": self.home / "app", "LOCALAPPDATA": self.home / "local",
            "TEMP": self.base / "temp", "TMP": self.base / "temp", "TMPDIR": self.base / "temp",
            "XDG_CONFIG_HOME": self.home / "config", "XDG_CACHE_HOME": self.home / "cache",
            "XDG_DATA_HOME": self.home / "data", "LINTEL_HOME": self.home / "lintel",
            "LINTEL_PACKS_DIR": self.home / "lintel" / "packs",
            "LINTEL_AUDIT_DIR": self.repo / ".claude" / "runtime" / "audit",
        }
        for path in (self.repo, self.base / "hooks", *roots.values()):
            path.mkdir(parents=True, exist_ok=True)
            self.assertTrue(path.is_relative_to(self.base))
            SAFETY.checked_root(path)
        self.env = {key: os.environ[key] for key in (
            "PATH", "PATHEXT", "SystemRoot", "WINDIR", "ComSpec",
        ) if key in os.environ}
        self.env.update({key: str(path) for key, path in roots.items()})
        self.env.update({
            "LINTEL_SOURCE_ROOT": str(SOURCE), "LINTEL_REPO_ROOT": str(self.repo),
            "LINTEL_ACTIVE_PACK_FILE": str(roots["LINTEL_PACKS_DIR"] / "active-pack"),
            "LINTEL_PYTHON": sys.executable, "LINTEL_PROFILE_CONTEXT": "synthetic-pipeline",
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": str(self.base / "empty.gitconfig"),
            "GIT_CONFIG_SYSTEM": str(self.base / "empty.gitconfig"),
            "GIT_CEILING_DIRECTORIES": str(self.base), "GIT_TERMINAL_PROMPT": "0",
            "GIT_PAGER": "cat", "PAGER": "cat", "GCM_INTERACTIVE": "Never",
            "PYTHONNOUSERSITE": "1", "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
        })
        if os.name == "nt":
            self.env.update(HOMEDRIVE=self.home.drive, HOMEPATH=str(self.home)[2:])
        (self.base / "empty.gitconfig").write_bytes(b"")
        self.assertFalse(any(name in self.env for name in (
            "GH_TOKEN", "GITHUB_TOKEN", "BASH_ENV", "PYTHONPATH", "GIT_CONFIG_COUNT",
            "PACK_CACHE_FILE", "LINTEL_PROFILE_REFERENCE",
        )))
        (self.base / "preflight.json").write_bytes(encoded({
            "source": str(SOURCE), "roots": {key: str(path) for key, path in roots.items()},
            "environment": self.env, "test": self.id(),
            "boundary": "Synthetic file/API tests, not an OS sandbox or native application run.",
        }))
        environment = patch.dict(os.environ, self.env, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.count = 0
        outside = self.command([OPTIONS.git, "--no-pager", "-C", str(self.base),
                                "rev-parse", "--show-toplevel"])
        self.assertNotEqual(outside.returncode, 0, "Fixture inherited an ancestor Git repository")
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/synthetic")
        self.assertEqual(Path(self.git("rev-parse", "--show-toplevel").stdout.strip()).resolve(), self.repo)
        self.write(".gitignore", b".claude/runtime/\n")
        self.write("spec.md", b"# Synthetic document input acceptance\nR1: preserve original sources.\n")
        self.plan = (
            "# Original synthetic work\n\n"
            "- [x] A0 Establish inputs\n"
            "- [ ] A1 Bind documents\n"
            "  - [ ] A1.1 Preserve document sources\n"
            "- [ ] A2.1 Retain upstream analysis\n\n"
            "| Package ID | Leaf IDs | Dependencies | Review |\n"
            "|---|---|---|---|\n"
            "| BASE | A0 | | mechanical |\n"
            "| P12 | A1.1 | BASE | substantive |\n"
            "| P09 | A2.1 | BASE | substantive |\n"
        )
        self.write("plan.md", self.plan.encode())
        self.write("prompt.md", b"Read only the original synthetic inputs; no native operations.\n")
        self.write_json("work.json", {
            "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
            "spec": "spec.md", "plan": "plan.md", "tasks": "plan.md", "prompt": "prompt.md",
        })
        self.run_dir = "runs/run with spaces"
        FIXTURE.write_fixture(self.repo / self.run_dir)
        for name in ("outline.md", "content.md"):
            path = self.repo / self.run_dir / name
            path.write_bytes(path.read_bytes().replace(
                b"target_formats: [word, ppt]", b"target_formats: [word, ppt, pdf, xlsx, web]",
            ))
        self.rehash()
        self.refs = [f"\u00a7{index}" for index in range(1, len(FIXTURE.SECTIONS) + 1)]
        self.design = {
            "version": "1.0", "source_content_hash": self.ref("content.md")["sha256"],
            "palette": {"primary": "#224466"}, "fonts": {"body": "sans-serif"},
            "per_format": {
                "word": {"sections": [{
                    "section_ref": section, "heading_level": 1,
                    "elements": [{"slot": "heading", "content_field": "Title"},
                                 {"slot": "body", "content_field": "Body"}],
                    "design_pass_hook": "WordTechnicalEditor",
                } for section in self.refs]},
                "ppt": {"layouts": [{
                    "section_ref": section, "layout_name": "Title and content", "layout_index": 1,
                    "elements": [{"placeholder": "title", "content_field": "Title"},
                                 {"placeholder": "body", "content_field": "Body"}],
                    "design_pass_hook": "PPTNarrativeArchitect", "animation": "none",
                } for section in self.refs]},
            },
        }
        self.write_json(self.run_dir + "/design-spec.json", self.design)
        self.config = PROFILE.ProfileConfig(
            SOURCE, self.repo, self.home / "lintel", self.home / "lintel" / "packs",
            self.home / "lintel" / "packs" / "active-pack", context_id="synthetic-pipeline",
        )
        profile = PROFILE.load_profile_context(self.config, create=True)
        self.reference, self.policy = PROFILE.profile_reference(profile), PROFILE.required_policy(profile)
        self.git("add", ".")
        self.git("commit", "-qm", "test: establish synthetic pipeline inputs")
        self.base_ref = self.git("rev-parse", "HEAD").stdout.strip()
        self.requirement = {
            "id": "document-render", "kind": "check", "requirement": "mandatory",
            "applicability": "applicable",
            "policy": {"source": "spec.md", "version": "synthetic-1",
                       "applicability": "Required later artifact observation, not an input prerequisite.",
                       "jurisdiction": None, "actor": None, "effective_date": None},
        }
        self.prepare_input = {
            "work_map": "work.json", "package_id": "P12", "leaf_ids": ["A1.1"],
            "acceptance_paths": ["spec.md"], "base": self.base_ref,
            "selection": [self.run_dir], "record_path": None, "attempt_id": "synthetic-documents",
            "builder": {"id": "synthetic", "context": "pipeline-input-tests"},
            "independence_required": True, "purpose": "implementation", "profile": self.reference,
            "required_policy": self.policy, "required_controls": ["spec", "quality", "document-render"],
            "qa_requirements": [self.requirement],
        }

    def command(self, argv):
        self.count += 1
        prefix = self.base / f"command-{self.count}"
        command = [str(arg) for arg in argv]
        prefix.with_suffix(".preflight.json").write_bytes(encoded({
            "argv": command, "environment": self.env, "cwd": str(self.repo),
        }))
        with prefix.with_suffix(".stdout.log").open("wb") as out, prefix.with_suffix(".stderr.log").open("wb") as err:
            result = subprocess.run(command, cwd=self.repo, env=self.env, stdout=out, stderr=err,
                                    check=False, timeout=60)
        prefix.with_suffix(".exit.json").write_bytes(encoded({"exit": result.returncode}))
        return subprocess.CompletedProcess(command, result.returncode,
            prefix.with_suffix(".stdout.log").read_text(encoding="utf-8"),
            prefix.with_suffix(".stderr.log").read_text(encoding="utf-8"))

    def git(self, *args):
        result = self.command([
            OPTIONS.git, "--no-pager", "-c", "core.autocrlf=false", "-c", "core.fsmonitor=false",
            "-c", f"core.hooksPath={self.base / 'hooks'}", "-c", "user.name=Synthetic fixture",
            "-c", "user.email=fixture@example.invalid", "-c", "commit.gpgSign=false", *args,
        ])
        self.assertEqual(result.returncode, 0, result.stderr)
        return result

    def write(self, path, data):
        SAFETY.atomic_write(self.repo, path, data)

    def write_json(self, path, value):
        self.write(path, encoded(value))

    def ref(self, name, *, full=False):
        path = name if full else self.run_dir + "/" + name
        return {"path": path, "sha256": SAFETY.read_owned(self.repo, path)[1]["sha256"]}

    def rehash(self):
        for child, parent, field in (
            ("outline.md", "brief.md", "source_brief_hash"),
            ("content.md", "outline.md", "source_outline_hash"),
            ("speaker-notes.md", "content.md", "source_content_hash"),
        ):
            path = self.repo / self.run_dir / child
            digest = self.ref(parent)["sha256"].encode()
            path.write_bytes(re.sub(field.encode() + rb": [0-9a-f]{64}", field.encode() + b": " + digest, path.read_bytes()))

    def prepare(self, **overrides):
        request = deepcopy(self.prepare_input)
        request.update(overrides)
        self.write_json(".claude/runtime/prepare.json", request)
        result = self.command([sys.executable, "-I", "-B", SOURCE / "bin/li-review-evidence.py",
                               "prepare", "--repo", self.repo, "--request",
                               self.repo / ".claude/runtime/prepare.json"])
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def inspect(self, expected=None, **kwargs):
        return PIPELINE.load_pipeline_inputs(
            self.repo, kwargs.pop("run_dir", self.run_dir),
            expected=expected or self.prepare(), profile_config=self.config,
            package_id=kwargs.pop("package_id", "P12"), leaf_ids=kwargs.pop("leaf_ids", ["A1.1"]),
            formats=kwargs.pop("formats", ["word", "ppt"]), **kwargs,
        )

    def save_design(self):
        self.write_json(self.run_dir + "/design-spec.json", self.design)

    def inventory(self):
        return {str(path.relative_to(self.repo)): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in self.repo.rglob("*") if path.is_file()}

    def test_document_only_preserves_full_inputs_without_output_qa(self):
        expected = self.prepare()
        before = self.inventory()
        result = self.inspect(expected)
        self.assertEqual(result["design"], self.design)
        for name in ("brief.md", "outline.md", "content.md", "speaker-notes.md"):
            self.assertEqual(result["documents"][name]["text"].encode("utf-8"),
                             (self.repo / self.run_dir / name).read_bytes())
            self.assertEqual(result["documents"][name]["path"], self.run_dir + "/" + name)
        self.assertEqual(result["work"], expected["work"])
        self.assertEqual(result["profile_ref"], self.reference)
        self.assertEqual(result["section_fields"][self.refs[0]], ["Title", "Body"])
        self.assertEqual(result["design_validation"], "document-projections")
        self.assertFalse(result["release_clearance"])
        self.assertFalse(result["executed"])
        self.assertEqual(before, self.inventory())
        self.assertFalse((self.repo / self.run_dir / "qa-report.json").exists())

    def test_pdf_xlsx_reuse_content_without_invented_layouts(self):
        result = self.inspect(formats=["pdf", "xlsx"])
        self.assertNotIn("pdf", result["design"]["per_format"])
        self.assertNotIn("xlsx", result["design"]["per_format"])
        self.assertIn(FIXTURE.SECTIONS[0][1][0], result["documents"]["content.md"]["text"])
        self.assertFalse(result["executed"])

    def test_same_bytes_wrong_sibling_selection_is_refused(self):
        files = ["brief.md", "outline.md", "content.md", "speaker-notes.md", "design-spec.json"]
        for omitted in files:
            with self.subTest(omitted=omitted):
                alternate = "same-" + omitted
                self.write(alternate, (self.repo / self.run_dir / omitted).read_bytes())
                selection = [self.run_dir + "/" + name for name in files if name != omitted] + [alternate]
                with self.assertRaisesRegex(ValueError, "selected"):
                    self.inspect(self.prepare(selection=selection))

    def test_each_hash_link_rejects_freshly_selected_but_stale_content(self):
        for name in ("brief.md", "outline.md", "content.md", "speaker-notes.md"):
            path = self.repo / self.run_dir / name
            original = path.read_bytes()
            try:
                if name == "speaker-notes.md":
                    path.write_bytes(original.replace(self.ref("content.md")["sha256"].encode(), b"0" * 64))
                else:
                    path.write_bytes(original + b"\nAn extra retained fact.\n")
                with self.subTest(name=name), self.assertRaisesRegex(ValueError, "hash"):
                    self.inspect()
            finally:
                path.write_bytes(original)

    def test_snapshot_drift_rejects_before_returning_content(self):
        expected = self.prepare()
        path = self.repo / self.run_dir / "content.md"
        path.write_bytes(path.read_bytes() + b"\nChanged source.\n")
        with self.assertRaises(ValueError):
            self.inspect(expected)

    def test_original_language_formats_and_anchors_cannot_drift(self):
        path = self.repo / self.run_dir / "content.md"
        original = path.read_bytes()
        for old, new in ((b"language: en-GB", b"language: sv"),
                         (b"[word, ppt, pdf, xlsx, web]", b"[word]"),
                         (b"{#sec-1}", b"{#sec-900}")):
            with self.subTest(new=new):
                path.write_bytes(original.replace(old, new))
                self.rehash()
                self.design["source_content_hash"] = self.ref("content.md")["sha256"]
                self.save_design()
                with self.assertRaises(ValueError):
                    self.inspect()
        path.write_bytes(original)

    def test_literal_markers_do_not_become_sections_or_fields(self):
        path = self.repo / self.run_dir / "content.md"
        text = path.read_bytes()
        literal = (
            "\n```markdown\n## \u00a7999 - Not a section {#sec-999}\n**Body:** fake\n```\n"
            "\n> ## \u00a7998 - Quoted\n> **Title:** fake\n"
            "\n<!--\n## \u00a7997 - Comment\n**Body:** fake\n-->\n"
            "\n<pre>\n## \u00a7996 - Raw\n**Body:** fake\n</pre>\n"
        ).encode()
        path.write_bytes(text + literal)
        self.rehash()
        self.design["source_content_hash"] = self.ref("content.md")["sha256"]
        self.save_design()
        result = self.inspect()
        self.assertEqual(list(result["section_fields"]), self.refs)
        self.assertEqual(result["documents"]["content.md"]["text"].encode(), text + literal)
        self.design["per_format"]["word"]["sections"][0]["section_ref"] = "\u00a7999"
        self.save_design()
        with self.assertRaisesRegex(ValueError, "section"):
            self.inspect()

    def test_missing_duplicate_or_unknown_source_section_refuses(self):
        for value in (self.design["per_format"]["word"]["sections"][1:],
                      [{**self.design["per_format"]["word"]["sections"][0], "section_ref": "\u00a7999"}]):
            with self.subTest(value=value):
                old = self.design["per_format"]["word"]["sections"]
                self.design["per_format"]["word"]["sections"] = value
                self.save_design()
                with self.assertRaisesRegex(ValueError, "section"):
                    self.inspect()
                self.design["per_format"]["word"]["sections"] = old
        self.save_design()
        path = self.repo / self.run_dir / "content.md"
        path.write_bytes(path.read_bytes() + b"\n## \xc2\xa71 - Duplicate {#sec-1}\n")
        self.rehash()
        self.design["source_content_hash"] = self.ref("content.md")["sha256"]
        self.save_design()
        with self.assertRaisesRegex(ValueError, "section"):
            self.inspect()

    def test_unknown_missing_and_ambiguous_slot_references_refuse(self):
        mapping = self.design["per_format"]["word"]["sections"][0]
        original = deepcopy(mapping["elements"])
        for elements in (
            [{"slot": "body", "content_field": "NotAField"}],
            [{"slot": "body", "content_field": "Subtitle"}],
            [{"content_field": "Body"}],
            [{"slot": "unknown-slot", "content_field": "Body"}],
            [original[0], original[0]],
        ):
            with self.subTest(elements=elements):
                mapping["elements"] = elements
                self.save_design()
                with self.assertRaises(ValueError):
                    self.inspect()

    def test_document_layout_types_and_hooks_are_not_guessed(self):
        for format_name, key, field, value in (
            ("word", "sections", "heading_level", True), ("word", "sections", "heading_level", 7),
            ("ppt", "layouts", "layout_index", -1), ("ppt", "layouts", "layout_name", ""),
            ("word", "sections", "design_pass_hook", "UnknownWriter"),
        ):
            row = self.design["per_format"][format_name][key][0]
            previous = row[field]
            row[field] = value
            self.save_design()
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                self.inspect()
            row[field] = previous

    def test_continuation_layouts_preserve_original_section_identity(self):
        self.design["per_format"]["ppt"]["layouts"].append(
            deepcopy(self.design["per_format"]["ppt"]["layouts"][0]))
        self.save_design()
        result = self.inspect()
        self.assertEqual(len(result["design"]["per_format"]["ppt"]["layouts"]), len(self.refs) + 1)
        self.assertEqual(list(result["section_fields"]), self.refs)

    def test_wrong_package_parent_and_unapproved_work_refuse(self):
        with self.assertRaises(ValueError):
            self.inspect(self.prepare(package_id="P12", leaf_ids=["A2.1"]), leaf_ids=["A2.1"])
        with self.assertRaises(ValueError):
            self.inspect(self.prepare(leaf_ids=["A1"]), leaf_ids=["A1"])
        with self.assertRaises(ValueError):
            self.inspect(package_id="P09")
        expected = self.prepare()
        mapping = json.loads((self.repo / "work.json").read_bytes())
        mapping["status"] = "DRAFT"
        self.write_json("work.json", mapping)
        with self.assertRaises(ValueError):
            self.inspect(expected)

    def test_linked_package_requires_explicit_bound_original_authority(self):
        self.write("plan.md", b"- [ ] A1.1 Preserve original document source\n")
        self.write("handoff.md", b"Original P12 assignment: A1.1, document inputs only.\n")
        expected = self.prepare(acceptance_paths=["spec.md", "handoff.md"])
        with self.assertRaises(ValueError):
            self.inspect(expected)
        result = self.inspect(expected, linked_authority="handoff.md")
        self.assertEqual(result["membership"], "linked-authority")
        self.assertFalse(result["release_clearance"])
        with self.assertRaises(ValueError):
            self.inspect(self.prepare(), linked_authority="handoff.md")

    def test_prerequisite_status_is_preserved_not_called_acceptance(self):
        self.write("plan.md", self.plan.replace("[x] A0", "[ ] A0").encode())
        result = self.inspect()
        self.assertEqual(result["prerequisites"], {"BASE": False})
        self.assertEqual(result["task_evidence"], "source-status-only")
        self.assertFalse(result["release_clearance"])

    def test_profile_pin_and_required_policy_drift_refuse(self):
        expected = self.prepare()
        forged = deepcopy(expected)
        forged["profile"]["generation"] += 1
        with self.assertRaises(ValueError):
            self.inspect(forged)
        forged = deepcopy(expected)
        forged["required_policy"] = {
            "required": True, "status": "loaded", "source": "made-up", "version": "1",
            "applicability": "applicable",
        }
        with self.assertRaises(ValueError):
            self.inspect(forged)
        self.write_json(".claude/profile-requirements.json",
                        {"schema_version": 1, "required_pack": "missing-synthetic"})
        with self.assertRaises(ValueError):
            self.inspect(expected)

    def test_selected_template_config_and_logo_cannot_be_unbound_or_changed(self):
        self.write("template.txt", b"Synthetic selected template bytes, not an Office file.\n")
        self.write("print.css", b"@page {size: A4}\n")
        self.design["per_format"]["word"]["template_path"] = "template.txt"
        self.save_design()
        with self.assertRaisesRegex(ValueError, "selected"):
            self.inspect()
        expected = self.prepare(selection=[self.run_dir, "template.txt", "print.css"])
        result = self.inspect(expected, selected_inputs=["print.css"])
        self.assertIn("print.css", {item["path"] for item in result["selected_inputs"]})
        self.write("print.css", b"@page {size: letter}\n")
        with self.assertRaises(ValueError):
            self.inspect(expected, selected_inputs=["print.css"])
        self.design["logo"] = {"path": "unselected-logo.svg", "position": "top-right"}
        self.write("unselected-logo.svg", b"<svg/>")
        self.save_design()
        with self.assertRaises(ValueError):
            self.inspect(self.prepare(selection=[self.run_dir, "template.txt"]))

    def mixed(self):
        self.write("retrieval.txt", b"Synthetic retained design decision input.\n")
        self.write("font-source.txt", b"Synthetic fixture, not verified font licensing.\n")
        profile = PROFILE.verify_profile_reference(self.reference, self.config)
        asset, _ = DESIGN.profile_asset(profile, self.config)
        self.design.update(schema_version=1, source="pipeline")
        self.design["fonts"] = {"heading": "Poppins", "body": "Lora"}
        self.design["palette"] = {"text_dark": "#141413", "background": "#faf9f5"}
        self.design["per_format"]["web"] = {"sections": []}
        self.design["web_design"] = {
            "target_format": "single-file",
            "typography": {"schema_version": 1, "font_stacks": [
                {"role": "heading", "family": "Poppins", "fallback_stack": ["sans-serif"]},
                {"role": "body", "family": "Lora", "fallback_stack": ["serif"]},
            ], "size_scale": {"base_px": 16, "ratio": 1.25}},
            "motion": {"schema_version": 1, "mode": "none", "libraries": [], "key_animations": [],
                       "perf_budget": {"fallback_for_prefers_reduced_motion": "no-animation"}},
            "shader": None, "component_libraries": [], "layout_grammar": {"max_width": "1152px"},
            "interaction_signature": {"scroll_smoothing": False, "page_transitions": "none"},
            "visual_thesis": "Synthetic editorial design", "voice_tier": "internal",
            "palette": {"tokens": {"ink": "#141413", "paper": "#faf9f5"}},
        }
        self.design["binding"] = {
            "profile_ref": self.reference, "profile_asset": asset, "brief": self.ref("content.md"),
            "retrieval": [self.ref("retrieval.txt", full=True)],
            "project": {"existing": False, "stack": "html", "manifests": []},
            "customer_share": False, "overrides": [],
            "provenance": [{
                "kind": "font", "name": name, "version": "synthetic-1",
                "source": "fixture:font-source.txt", "license": "synthetic-not-a-license",
                "rationale": "Existing profile test case", "evidence": [self.ref("font-source.txt", full=True)],
            } for name in ("Poppins", "Lora")],
        }
        self.save_design()
        self.prepare_input["selection"] += ["retrieval.txt", "font-source.txt"]

    def test_mixed_input_runs_existing_full_p11_validation(self):
        self.mixed()
        result = self.inspect()
        self.assertEqual(result["design_validation"], "mixed-web-and-document-projections")
        self.assertEqual(result["design"], self.design)
        self.assertFalse(result["executed"])
        self.design["fonts"]["heading"] = "Contradictory font"
        self.save_design()
        with self.assertRaisesRegex(ValueError, "projection"):
            self.inspect()

    def test_mixed_same_bytes_wrong_content_path_refuses(self):
        self.mixed()
        self.write("identical-content.md", (self.repo / self.run_dir / "content.md").read_bytes())
        self.design["binding"]["brief"] = self.ref("identical-content.md", full=True)
        self.save_design()
        self.prepare_input["selection"].append("identical-content.md")
        with self.assertRaisesRegex(ValueError, "sibling"):
            self.inspect()

    def test_legacy_web_presence_is_not_document_only_clearance(self):
        self.design["per_format"]["web"] = {"sections": []}
        self.save_design()
        with self.assertRaisesRegex(ValueError, "unresolved"):
            self.inspect()

    def test_required_later_qa_remains_unverified_without_circular_admission(self):
        expected = self.prepare()
        self.assertFalse(self.inspect(expected)["release_clearance"])
        self.write("unverified.txt", b"No native rendering was performed.\n")
        final = self.prepare(selection=[self.run_dir, "unverified.txt"])
        control = {**self.requirement, "status": "unverified", "reason": "Native rendering not performed.",
                   "evidence": ["unverified.txt"], "observation": {}, "advisory_score": 100}
        qa = {"schema_version": 2, "context_digest": REVIEW.content_digest(final),
              "controls": [control], "evidence": REVIEW.evidence_manifest(self.repo, [control])}
        checked = REVIEW.verify_qa(self.repo, qa, expected=final)
        self.assertTrue(checked["blocked"])
        self.assertNotEqual(checked["status"], "pass")

    def test_cli_reads_exact_files_and_refuses_unknown_options_without_writes(self):
        expected = self.prepare()
        self.write_json(".claude/runtime/expected.json", expected)
        command = [
            sys.executable, "-I", "-B", SOURCE / "skills/generate/scripts/pipeline_inputs.py",
            "--repo", self.repo, "--from-pipeline", self.run_dir, "--format", "word", "--format", "ppt",
            "--expected", ".claude/runtime/expected.json", "--package", "P12", "--leaf", "A1.1",
            "--profile-home", self.config.home, "--profile-packs", self.config.packs,
            "--profile-pointer", self.config.pointer,
        ]
        before = self.inventory()
        result = self.command(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["documents"]["content.md"]["path"],
                         self.run_dir + "/content.md")
        self.assertEqual(before, self.inventory())
        invalid = self.command(command + ["--out", "new-envelope.json"])
        self.assertEqual(invalid.returncode, 2)
        self.assertFalse(invalid.stdout.strip())
        self.assertFalse((self.repo / "new-envelope.json").exists())
        duplicate = self.command(command + ["--expected", ".claude/runtime/expected.json"])
        self.assertEqual(duplicate.returncode, 2)
        self.assertFalse(duplicate.stdout.strip())

    def test_windows_separator_and_root_escape_controls(self):
        self.assertEqual(self.inspect(run_dir=self.run_dir.replace("/", "\\"))["design"], self.design)
        for path in ("../outside", "C:\\outside", "run with spaces\\..\\outside"):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.inspect(run_dir=path)

    def test_unknown_design_version_and_invalid_json_refuse(self):
        self.design["version"] = "2.0"
        self.save_design()
        with self.assertRaises(ValueError):
            self.inspect()
        self.write(self.run_dir + "/design-spec.json", b'{"version":"1.0","version":"1.0"}')
        with self.assertRaises(ValueError):
            self.inspect()

    def test_crlf_and_optional_source_fields_are_preserved_not_normalized(self):
        path = self.repo / self.run_dir / "content.md"
        value = path.read_bytes() + b"\n**Bullets:**\n- Retained evidence [S1].\n\n**Data-viz:** source-backed table\n"
        path.write_bytes(value)
        for name in ("brief.md", "outline.md", "content.md", "speaker-notes.md"):
            current = self.repo / self.run_dir / name
            current.write_bytes(current.read_bytes().replace(b"\n", b"\r\n"))
        self.rehash()
        self.design["source_content_hash"] = self.ref("content.md")["sha256"]
        self.save_design()
        result = self.inspect()
        for name in ("brief.md", "outline.md", "content.md", "speaker-notes.md"):
            self.assertEqual(result["documents"][name]["text"].encode("utf-8"),
                             (self.repo / self.run_dir / name).read_bytes())
        self.assertEqual(result["section_fields"][self.refs[-1]], ["Title", "Body", "Bullets", "Data-viz"])

    def test_root_run_directory_retains_existing_relative_entry(self):
        names = ["brief.md", "outline.md", "content.md", "speaker-notes.md", "design-spec.json"]
        for name in names:
            self.write(name, (self.repo / self.run_dir / name).read_bytes())
        result = self.inspect(self.prepare(selection=names), run_dir=".")
        self.assertEqual(result["documents"]["content.md"]["path"], "content.md")

    def test_explicit_source_read_bound_refuses_instead_of_truncating(self):
        self.write(self.run_dir + "/brief.md", b"x" * (PIPELINE.MAX_BYTES + 1))
        with self.assertRaisesRegex(ValueError, "byte bound"):
            self.inspect()

    def test_all_released_callers_reference_the_same_admission(self):
        for name in ("generate", "generate-word", "generate-ppt", "generate-qa", "generate-pdf", "generate-xlsx"):
            text = (SOURCE / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
            self.assertIn("fidelity-and-evidence.md#existing-pipeline-input-admission", text, name)
            self.assertIn("--from-pipeline", text if name != "generate-qa" else
                          (SOURCE / "skills/generate-write/references/fidelity-and-evidence.md").read_text(encoding="utf-8"))

    def test_content_anchor_api_and_cli_distinguish_literal_spans(self):
        original = (self.repo / self.run_dir / "content.md").read_bytes()
        cases = (
            ("ordinary", "{#sec-1}", 0),
            ("inline-only", "`{#sec-1}`", 2),
            ("comment-only", "<!-- {#sec-1} -->", 2),
            ("attribute-only", '<span data-example="{#sec-1}"></span>', 2),
            ("escaped-only", r"\{#sec-1}", 2),
            ("real-plus-inline", "{#sec-1} `{#sec-999}`", 0),
            ("real-plus-comment", "{#sec-1} <!-- {#sec-999} -->", 0),
            ("real-plus-attribute", '{#sec-1} <span data-example="{#sec-999}"></span>', 0),
            ("real-mismatch", "{#sec-900}", 2),
        )
        for label, anchor, expected_exit in cases:
            with self.subTest(case=label):
                content = original.replace(b"{#sec-1}", anchor.encode("utf-8"), 1)
                self.write(self.run_dir + "/content.md", content)
                self.rehash()
                self.design["source_content_hash"] = self.ref("content.md")["sha256"]
                self.save_design()
                expected = self.prepare()
                self.write_json(".claude/runtime/anchor-expected.json", expected)
                before = self.inventory()
                try:
                    value = self.inspect(expected)
                except ValueError:
                    accepted = False
                else:
                    accepted = True
                    self.assertEqual(value["documents"]["content.md"]["text"].encode("utf-8"), content)
                    self.assertFalse(value["executed"])
                    self.assertFalse(value["release_clearance"])
                result = self.command([
                    sys.executable, "-I", "-B", SOURCE / "skills/generate/scripts/pipeline_inputs.py",
                    "--repo", self.repo, "--from-pipeline", self.run_dir,
                    "--expected", ".claude/runtime/anchor-expected.json", "--package", "P12",
                    "--leaf", "A1.1", "--format", "word", "--format", "ppt",
                    "--profile-home", self.config.home, "--profile-packs", self.config.packs,
                    "--profile-pointer", self.config.pointer,
                ])
                self.assertEqual(before, self.inventory())
                self.assertEqual(result.returncode, expected_exit, result.stderr)
                self.assertEqual(accepted, expected_exit == 0)
                if result.returncode:
                    self.assertFalse(result.stdout.strip())
                    self.assertEqual(json.loads(result.stderr)["status"], "error")

    def test_optional_anchors_ignore_examples_but_reject_real_multiplicity(self):
        valid = ("", "`{#sec-999}`", "<!-- {#sec-999} -->",
                 '<span data-example="{#sec-999}"></span>', r"\{#sec-999}",
                 "{#sec-1}", "{#sec-1} `{#sec-999}`")
        invalid = ("{#sec-900}", "{#sec-1} {#sec-1}", "{#sec-1} {#sec-900}")
        for anchor in (*valid, *invalid):
            text = "## \u00a71 - Optional outline or notes " + anchor + "\n\nComplete source.\n"
            source = PIPELINE.classify_markdown(text)
            with self.subTest(anchor=anchor):
                if anchor in invalid:
                    with self.assertRaisesRegex(ValueError, "anchor"):
                        PIPELINE._sections(source, 0)
                else:
                    self.assertEqual(PIPELINE._sections(source, 0), {"\u00a71": []})
                self.assertEqual(source.original, text)
        for name in ("outline.md", "speaker-notes.md"):
            path = self.repo / self.run_dir / name
            modified = re.sub(rb"(## \xc2\xa71[^\r\n]*)",
                              rb"\1 <!-- {#sec-999} -->", path.read_bytes(), count=1)
            path.write_bytes(modified)
        self.rehash()
        self.design["source_content_hash"] = self.ref("content.md")["sha256"]
        self.save_design()
        result = self.inspect()
        for name in ("outline.md", "speaker-notes.md"):
            self.assertEqual(result["documents"][name]["text"].encode("utf-8"),
                             (self.repo / self.run_dir / name).read_bytes())

    def test_anchor_offsets_use_original_unicode_crlf_and_real_duplicates(self):
        cases = (
            ("{#sec-1}", True),
            ("{#sec-1} `{#sec-999}`", True),
            (r"{#sec-1} \{#sec-999}", True),
            ("`{#sec-1}`", False),
            ("<!-- {#sec-1} -->", False),
            ('<span title="{#sec-1}"></span>', False),
            (r"\{#sec-1}", False),
            ("{#sec-1} {#sec-1}", False),
            ("{#sec-1} {#sec-2}", False),
            ("{#sec-2}", False),
        )
        for newline in ("\n", "\r\n", "\r"):
            for anchor, accepted in cases:
                prefix = "Earlier \u00e9 and \U0001f642, not byte offsets." + newline * 2
                text = prefix + "   ## \u00a71 - \u00e9 " + anchor + newline + "**Body:** full text" + newline
                source = PIPELINE.classify_markdown(text)
                with self.subTest(newline=repr(newline), anchor=anchor):
                    if accepted:
                        self.assertEqual(PIPELINE._sections(source, len(prefix), content=True),
                                         {"\u00a71": ["Body"]})
                    else:
                        with self.assertRaisesRegex(ValueError, "anchor"):
                            PIPELINE._sections(source, len(prefix), content=True)
                    self.assertEqual(source.original, text)

    def upstream_fixture(self):
        """Existing-shape inert input records, not checkpoint or review publication."""
        upstream_config = PROFILE.ProfileConfig(
            SOURCE, self.repo, self.home / "lintel", self.home / "lintel" / "packs",
            self.home / "lintel" / "packs" / "active-pack", context_id="synthetic-upstream",
        )
        profile = PROFILE.load_profile_context(upstream_config, create=True)
        requirement = {
            **deepcopy(self.requirement), "id": "upstream-check",
            "policy": {**self.requirement["policy"], "applicability": "Inert upstream input fixture."},
        }
        selection = ["upstream-source.txt"]
        self.write(selection[0], b"Synthetic upstream analytical input, not a domain execution.\n")
        request_options = {
            "selection": selection, "package_id": "P09", "leaf_ids": ["A2.1"],
            "attempt_id": "synthetic-upstream", "profile": PROFILE.profile_reference(profile),
            "required_policy": PROFILE.required_policy(profile),
            "required_controls": ["spec", "quality", "upstream-check"], "qa_requirements": [requirement],
        }
        initial = self.prepare(**request_options)
        record_root = ".claude/runtime/state/domains/pipeline-fixture/i0001/ta"
        start_path, result_path = record_root + "/01-start.json", record_root + "/01-result.json"
        request_path, artifact_path, evidence_path = "upstream-request.json", "analysis.txt", "analysis-evidence.txt"
        receiver = {"role": "SystemArchitect", "mode": "synthetic-input-only"}
        request = {
            "schema_version": 1, "kind": "domain-request", "operation_id": "pipeline-fixture",
            "iteration": 1, "input_context": initial, "advisory_preferences": {}, "release_clearance": False,
            "domains": [{"id": "ta", "checkpoints": [{
                "id": "analysis", "receiver": receiver, "control_ids": ["upstream-check"],
                "artifacts": [artifact_path],
                "start": {"path": start_path, "expected_state": None},
                "result": {"path": result_path, "expected_state": None},
            }]}],
        }
        PIPELINE.domain_result.validate_request(request)
        self.write_json(request_path, request)
        common = {
            "schema_version": 1, "request": self.ref(request_path, full=True),
            "domain": "ta", "checkpoint": "analysis", "receiver": receiver,
            "producer": initial["builder"], "provenance": "declared", "release_clearance": False,
        }
        self.write_json(start_path, {**common, "kind": "domain-checkpoint"})
        self.write(artifact_path, b"Synthetic source claim with an explicit uncertainty.\n")
        self.write(evidence_path, b"Inert fixture observation; no live specialist or independent review.\n")
        control = {**requirement, "status": "pass", "reason": "Synthetic recorded input.",
                   "evidence": [evidence_path], "observation": {"fixture_only": True}}
        self.write_json(result_path, {
            **common, "kind": "domain-result", "start": self.ref(start_path, full=True),
            "status": "pass", "reason": "Inert accepted-contract fixture, not execution proof.",
            "controls": [control], "evidence": REVIEW.evidence_manifest(self.repo, [control]),
            "artifacts": [self.ref(artifact_path, full=True)],
            "decisions": [{"requirement": "R1", "rationale": "Preserve the synthetic uncertainty.",
                           "artifact": artifact_path}],
            "limitations": ["No actor authentication, independent acceptance or native action."],
            "next": {"owner": "fixture", "action": "Read-only consumption test."},
        })
        selection += [request_path, start_path, result_path, artifact_path, evidence_path]
        final = self.prepare(**{**request_options, "selection": selection})
        return request_path, final, upstream_config, selection

    def test_upstream_uses_its_own_context_profile_and_selected_artifacts(self):
        path, upstream_context, upstream_profile, selection = self.upstream_fixture()
        expected = self.prepare(selection=[self.run_dir, *selection])
        before = self.inventory()
        result = self.inspect(expected, upstream_request=path, upstream_expected=upstream_context,
                              upstream_profile=upstream_profile)
        self.assertEqual(result["upstream"]["verification"], "current_inputs")
        self.assertEqual(result["upstream"]["review"], "not_evaluated")
        self.assertFalse(result["upstream"]["release_clearance"])
        self.assertEqual(result["upstream"]["qa"]["context_digest"], REVIEW.content_digest(upstream_context))
        self.assertNotEqual(result["upstream"]["qa"]["context_digest"], REVIEW.content_digest(expected))
        self.assertEqual(before, self.inventory())
        with self.assertRaisesRegex(ValueError, "Upstream"):
            self.inspect(expected, upstream_request=path, upstream_expected=expected,
                         upstream_profile=self.config)

    def test_upstream_unselected_artifact_or_stale_result_never_becomes_input(self):
        path, upstream_context, upstream_profile, selection = self.upstream_fixture()
        expected = self.prepare(selection=[self.run_dir, *[name for name in selection if name != "analysis.txt"]])
        with self.assertRaisesRegex(ValueError, "selected"):
            self.inspect(expected, upstream_request=path, upstream_expected=upstream_context,
                         upstream_profile=upstream_profile)
        self.write("analysis.txt", b"Changed after the recorded observation.\n")
        expected = self.prepare(selection=[self.run_dir, *selection])
        with self.assertRaisesRegex(ValueError, "Upstream"):
            self.inspect(expected, upstream_request=path, upstream_expected=upstream_context,
                         upstream_profile=upstream_profile)

    def test_upstream_partial_arguments_and_changed_profile_are_refused(self):
        with self.assertRaises(ValueError):
            self.inspect(upstream_request="unselected-request.json")
        path, upstream_context, upstream_profile, selection = self.upstream_fixture()
        changed = deepcopy(upstream_context)
        changed["profile"]["generation"] += 1
        with self.assertRaisesRegex(ValueError, "Upstream"):
            self.inspect(self.prepare(selection=[self.run_dir, *selection]), upstream_request=path,
                         upstream_expected=changed, upstream_profile=upstream_profile)


def main():
    global RUN, OPTIONS, PIPELINE, FIXTURE, SAFETY, PROFILE, REVIEW, DESIGN
    parser = argparse.ArgumentParser(allow_abbrev=False)
    parser.add_argument("--fixture-root", type=Path, required=True)
    parser.add_argument("--git", required=True)
    parser.add_argument("--test", action="append",
                        choices=sorted(name for name in PipelineBinding.__dict__ if name.startswith("test_")))
    OPTIONS = parser.parse_args()
    OPTIONS.fixture_root.mkdir(parents=True, exist_ok=True)
    RUN = Path(tempfile.mkdtemp(prefix="pipeline-tests-", dir=OPTIONS.fixture_root.resolve()))
    sys.path.insert(0, str(SOURCE / "lib"))
    import context_safety
    import profile_context
    import review_contract
    SAFETY, PROFILE, REVIEW = context_safety, profile_context, review_contract
    SAFETY.checked_root(RUN)
    paths = (
        "skills/generate/scripts/pipeline_inputs.py", "bin/li-work-artifacts.py",
        "lib/swarm_contract.py", "lib/swarm_snapshot.py", "lib/swarm-schema.json", "lib/markdown_source.py",
        "lib/context_safety.py", "lib/native_paths.py", "lib/profile_context.py",
        "lib/profile-context-schema.json", "lib/review_contract.py", "lib/review-schema.json",
        "lib/domain_result.py", "lib/domain-result-schema.json", "bin/li-review-evidence.py",
        "skills/design-dna/scripts/design_contract.py", "skills/design-dna/scripts/emit_tokens.py",
        "skills/design-dna/references/design-contract.schema.json",
        "lib/pack-schema.yaml", "packs/_default/pack.yaml", ".claude-plugin/plugin.json",
        "skills/design-dna/profiles/anthropic-default.yaml",
        "tests/integration/document-format-pipeline.py", "tests/integration/document-pipeline-binding.py",
    )
    seals = {name: hashlib.sha256((SOURCE / name).read_bytes()).hexdigest()
             if (SOURCE / name).is_file() else None for name in paths}
    (RUN / "preflight.json").write_bytes(encoded({
        "source": str(SOURCE), "source_sha256": seals, "environment": dict(os.environ),
        "fixture_root": str(RUN), "native_execution": False,
    }))
    print(f"preflight: {RUN / 'preflight.json'}", flush=True)
    FIXTURE = load("pipeline_long_source_fixture", SOURCE / "tests/integration/document-format-pipeline.py")
    PIPELINE = load("pipeline_inputs", SOURCE / "skills/generate/scripts/pipeline_inputs.py")
    DESIGN = PIPELINE.design_contract
    suite = unittest.TestSuite(PipelineBinding(name) for name in OPTIONS.test) if OPTIONS.test else \
        unittest.defaultTestLoader.loadTestsFromTestCase(PipelineBinding)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    unchanged = all(hashlib.sha256((SOURCE / name).read_bytes()).hexdigest() == digest for name, digest in seals.items())
    (RUN / "result.json").write_bytes(encoded({
        "executed": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
        "skipped": len(result.skipped), "success": result.wasSuccessful(), "sources_unchanged": unchanged,
        "native_execution": False, "review_record_publication": False,
    }))
    return 0 if result.wasSuccessful() and unchanged else 1


if __name__ == "__main__":
    sys.exit(main())
