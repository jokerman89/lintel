#!/usr/bin/env python3
# component: generation-safety-tests
# implements: ADR-0014, ADR-0028, ADR-0029
# intent: .claude/plans/v2-findings/plan.md (lane-d-04, lane-d-05, lane-d-12)
# constraints: source contracts and inert rooted publication; no generation/model efficacy
# last_intent_review: 2026-10-03
"""Scoped generation procedure guards; these do not execute a model or native renderer."""
from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import io
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
import context_safety as safety


def skill(name):
    return (ROOT / "skills" / name / "SKILL.md").read_text(encoding="utf-8")


class GenerationSafety(unittest.TestCase):
    def test_palette_child_admits_retained_capture_not_url_string(self):
        root = self.fixture()
        capture = root / "admitted-capture.html"
        capture.write_text("<html><p>Synthetic retained capture.</p></html>", encoding="utf-8")
        source = skill("generate-style-learn").split("### Step 1", 1)[1]
        recipe = re.search(r"```bash\n(.*?)\n```", source, re.S).group(1)
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = dict(os.environ, OUT_DIR="palette", NAME="fixture")
        accepted = subprocess.run([bash, "-c", recipe, "caller", capture.as_posix()],
                                  cwd=root, env=env, capture_output=True, text=True)
        rejected = subprocess.run([bash, "-c", recipe, "caller", "https://example.invalid/input"],
                                  cwd=root, env=env, capture_output=True, text=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertEqual(rejected.returncode, 2)
        self.assertFalse((root / "palette").exists())
        self.assertEqual(capture.read_text(encoding="utf-8"),
                         "<html><p>Synthetic retained capture.</p></html>")

    def test_retrieval_isolates_parent_and_producer_from_target_modules(self):
        root = self.fixture()
        marker = root / "target-module-ran"
        for name in ("pathlib.py", "subprocess.py", "core.py"):
            (root / name).write_text(
                f"open({str(marker)!r}, 'w').write({name!r})\n"
                "raise RuntimeError('owned target shadow fixture')\n",
                encoding="utf-8",
            )
        section = skill("frontend-design").split("### Step 1.5", 1)[1].split("### Step 2", 1)[0]
        recipe = re.search(r"```bash\n(.*?)\n```", section, re.S).group(1)
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_"))}
        env.update(LINTEL_SOURCE_ROOT=ROOT.as_posix(), LINTEL_REPO_ROOT=root.as_posix(),
                   OUT="retrieval", DESIGN_QUERY="developer dashboard", PROJECT_NAME="Isolated fixture",
                   OVERWRITE="0", PYTHONPATH=str(root))
        result = subprocess.run([bash, "-c", recipe], cwd=root, env=env,
                                capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse(marker.exists())
        self.assertTrue((root / "retrieval/design-dna.md").read_bytes().strip())

    def test_actual_retrieval_recipe_preserves_existing_and_failed_outputs(self):
        base = self.fixture()
        source, target = base / "trusted", base / "target"
        target.mkdir()
        shutil.copytree(ROOT / "lib", source / "lib", ignore=shutil.ignore_patterns("__pycache__"))
        producer = source / "skills/design-dna/scripts/search.py"
        producer.parent.mkdir(parents=True)
        producer.write_text(
            "import os,sys\nfrom pathlib import Path\n"
            "Path(os.environ['TEST_RETRIEVAL_CALLED']).write_text('called')\n"
            "if os.environ.get('TEST_RETRIEVAL_LATE') == '1':\n"
            "    Path(os.environ['TEST_RETRIEVAL_TARGET']).write_bytes(b'later edit')\n"
            "if os.environ['TEST_RETRIEVAL_EXIT'] != '0':\n"
            "    print('fixture retrieval failed', file=sys.stderr)\n"
            "    raise SystemExit(int(os.environ['TEST_RETRIEVAL_EXIT']))\n"
            "sys.stdout.buffer.write(b'retrieved fixture\\n')\n",
            encoding="utf-8",
        )
        destination = target / "design/design-dna.md"
        destination.parent.mkdir()
        destination.write_bytes(b"retained retrieval")
        called = base / "called.txt"
        section = skill("frontend-design").split("### Step 1.5", 1)[1].split("### Step 2", 1)[0]
        recipe = re.search(r"```bash\n(.*?)\n```", section, re.S).group(1)
        bash = os.environ.get("LINTEL_TEST_BASH") or shutil.which("bash")
        self.assertTrue(bash)
        env = {key: value for key, value in os.environ.items()
               if not key.startswith(("LINTEL_", "CLAUDE_"))}
        env.update(LINTEL_SOURCE_ROOT=source.as_posix(), LINTEL_REPO_ROOT=target.as_posix(),
                   OUT="design", out_dir="design", DESIGN_QUERY="fixture", PROJECT_NAME="Fixture",
                   TEST_RETRIEVAL_CALLED=str(called), TEST_RETRIEVAL_TARGET=str(destination))

        def invoke(overwrite, exit_code, late=False):
            if called.exists():
                called.unlink()
            run_env = dict(env, OVERWRITE=str(overwrite), TEST_RETRIEVAL_EXIT=str(exit_code),
                           TEST_RETRIEVAL_LATE="1" if late else "0")
            return subprocess.run([bash, "-c", recipe], cwd=target, env=run_env,
                                  capture_output=True, text=True, encoding="utf-8")

        failed = invoke(1, 41)
        self.assertNotEqual(failed.returncode, 0)
        self.assertEqual(destination.read_bytes(), b"retained retrieval")
        refused = invoke(0, 0)
        self.assertNotEqual(refused.returncode, 0)
        self.assertFalse(called.exists())
        self.assertEqual(destination.read_bytes(), b"retained retrieval")
        self.assertEqual(invoke(1, 0).returncode, 0)
        self.assertEqual(destination.read_bytes(), b"retrieved fixture\n")
        self.assertNotEqual(invoke(1, 0, late=True).returncode, 0)
        self.assertEqual(destination.read_bytes(), b"later edit")
        destination.unlink()
        self.assertNotEqual(invoke(0, 41).returncode, 0)
        self.assertFalse(destination.exists())
        self.assertEqual(invoke(0, 0).returncode, 0)
        self.assertEqual(destination.read_bytes(), b"retrieved fixture\n")

    def fixture(self):
        # The explicitly selected parent owns all fixture output; never remove its tree.
        return Path(tempfile.mkdtemp(prefix="generation-safety-", dir=Path(os.environ["TMPDIR"])))

    def test_selected_share_procedures_are_named_and_real(self):
        contract = (ROOT / "skills/design-dna/references/design-contract.md").read_text(encoding="utf-8")
        for name in ("font-licensing", "motion-licensing", "shader-licensing",
                     "brand-source", "brand-freshness"):
            with self.subTest(control=name):
                self.assertIn(f"`{name}`", contract)
        for requirement in ("qa_requirements", "unverified", "source/version", "kind: check",
                            "not a scanner", "manual", "mandatory", "not_applicable"):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, contract)
        self.assertIn("#selected-asset-evidence", skill("frontend-design"))

    def test_no_obsolete_gate_or_brand_command_remains_in_owned_callers(self):
        for name in ("frontend-typography", "frontend-motion", "frontend-shader",
                     "generate-ppt", "generate-style-learn", "frontend-style-extract"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertNotRegex(text, r"compliance-gate\s+--check|brand-staleness-warn|li-doctor\s+--brand-summary")
        for name in ("frontend-typography", "frontend-motion", "frontend-shader"):
            with self.subTest(skill=name):
                self.assertIn("licensing", skill(name))
                self.assertNotIn("final license-audit", skill(name))
        for name in ("generate-ppt", "generate-style-learn", "frontend-style-extract"):
            with self.subTest(skill=name):
                self.assertIn("#selected-asset-evidence", skill(name))

    def test_implicit_personal_paths_and_destination_fallbacks_are_gone(self):
        for name in ("generate-design", "generate-style-learn", "frontend-style-extract", "generate-app"):
            with self.subTest(skill=name):
                text = skill(name)
                self.assertNotRegex(text, r"~/\.lintel|\$HOME/|\$\{HOME\}|%USERPROFILE%")
                self.assertNotIn("./palettes/", text)
                self.assertIn("#owned-source-and-output-selection", text)
                self.assertRegex(text, r"(?i)(missing|unwritable|unavailable).{0,100}(output|destination)|"
                                      r"(?i:output).{0,100}(missing|unwritable|unavailable)")

    def test_output_options_are_explicit_at_entry(self):
        for name, option in (("generate-design", "--out"), ("generate-style-learn", "--out-dir"),
                             ("frontend-style-extract", "--out"), ("generate-app", "--out")):
            with self.subTest(skill=name):
                self.assertIn(f"Required `{option} <path>`", skill(name))
        self.assertIn('${OUT:?select an owned repository-relative output directory}',
                      skill("frontend-style-extract"))
        self.assertIn('${OUT_DIR:?select an owned repository-relative output directory}',
                      skill("generate-style-learn"))

    def test_source_retention_and_input_contracts_survive(self):
        self.assertIn("Never modifies input-files", skill("generate-style-learn"))
        self.assertIn("extraction_confidence", skill("frontend-style-extract"))
        self.assertIn("legacy_to_draft", skill("frontend-style-extract"))
        self.assertIn("stage_draft", skill("frontend-style-extract"))
        self.assertIn("original", skill("generate-style-learn"))
        self.assertIn("load_design", skill("generate-app"))
        self.assertIn("P05", skill("generate-design"))
        self.assertIn("P07", skill("generate-design"))

    def test_visio_slot_only_names_existing_mapped_roles(self):
        text = skill("generate-visio")
        self.assertIn("template slot", text)
        self.assertNotIn("NetworkArchitect", text)
        self.assertIn("name: generate-visio", text)
        self.assertRegex(text, r"(?m)^description: Use (when|to) ")
        mapping = (ROOT / "skills/generate/agent-mapping.yaml").read_text(encoding="utf-8")
        roles = re.findall(r"^- (?:Primary|Conditional): ([A-Za-z]+)", text, re.MULTILINE)
        self.assertEqual(roles, ["SystemArchitect", "SecurityAuditor"])
        for role in roles:
            self.assertIn(role, mapping)
            self.assertEqual(len(list((ROOT / "agents").glob(f"*/{role}.md"))), 1)
        self.assertIn("Missing writer/editor operations", text)

    def test_design_method_routes_measured_contrast_without_claiming_a_browser(self):
        dna = skill("design-dna")
        method = (ROOT / "skills/design-dna/references/design-contract.md").read_text(encoding="utf-8")
        self.assertIn("scripts/measure_contrast.py", dna)
        self.assertIn("browser_observation", method)
        self.assertIn("background_image", method)
        self.assertIn("text_size", method)
        self.assertIn("unverified", method)
        self.assertIn("validate_design", method)

    def test_extractor_entry_recipes_refuse_missing_output_without_writes(self):
        bash = os.environ.get("LINTEL_TEST_BASH")
        if bash is None and os.name != "nt":
            bash = shutil.which("bash")
        self.assertTrue(bash, "Select the real Bash executable with LINTEL_TEST_BASH")
        for name in ("generate-style-learn", "frontend-style-extract"):
            with self.subTest(skill=name):
                source = skill(name).split("### Step 1 —", 1)[1]
                recipe = re.search(r"```bash\n(.*?)\n```", source, re.S).group(1)
                base = self.fixture()
                artifact = base / "input.html"
                artifact.write_bytes(b"<p>Synthetic input; no extraction is run.</p>")
                env = {key: value for key, value in os.environ.items() if key not in ("OUT", "OUT_DIR")}
                env["NAME"] = "fixture"
                result = subprocess.run(
                    [bash, "--noprofile", "--norc", "-c", recipe, "recipe", str(artifact)],
                    cwd=base, env=env, capture_output=True, text=True, check=False,
                )
                self.assertNotEqual(result.returncode, 0, name)
                self.assertIn("select an owned repository-relative output", result.stderr)
                self.assertEqual(list(base.iterdir()), [artifact])

    def test_style_publication_recipe_executes_real_p03_and_preserves_inputs(self):
        source = skill("generate-style-learn").split("### Step 4 —", 1)[1]
        recipe = re.search(r"```python\n(.*?)\n```", source, re.S).group(1)
        code = compile(recipe, "skills/generate-style-learn/SKILL.md:publication", "exec")
        root = self.fixture()
        (root / "input.html").write_bytes(b"preserved input")
        context = {
            "repo": root, "out_dir": "out", "name": "fixture", "overwrite": False,
            "palette_json": '{"fixture":true}\n', "style_md": "# Fixture\n",
            "original_output_states": {"out/fixture.json": None, "out/fixture-STYLE.md": None},
        }
        exec(code, dict(context))
        self.assertEqual((root / "out/fixture.json").read_bytes(), b'{"fixture":true}\n')
        self.assertEqual((root / "out/fixture-STYLE.md").read_bytes(), b"# Fixture\n")
        states = {path: safety.file_state(root, path) for path in context["original_output_states"]}
        for changes in (
            {"out_dir": ""},
            {"out_dir": "../elsewhere"},
            {"repo": root / "missing-root"},
            {"original_output_states": states},  # no implicit overwrite
            {"name": "../escape"},
        ):
            with self.subTest(changes=changes):
                error = io.StringIO()
                with redirect_stderr(error), self.assertRaises(SystemExit) as failure:
                    exec(code, {**context, **changes})
                self.assertEqual(failure.exception.code, 2)
                self.assertIn("ERROR [lintel/style-learn]", error.getvalue())
        # An injected OS write denial tests this recipe's recovery, not actual host ACLs.
        with patch.object(safety, "atomic_write", side_effect=PermissionError("fixture write denied")):
            error = io.StringIO()
            with redirect_stderr(error), self.assertRaises(SystemExit) as failure:
                exec(code, dict(context))
            self.assertEqual(failure.exception.code, 2)
            self.assertIn("fixture write denied", error.getvalue())
        self.assertEqual((root / "input.html").read_bytes(), b"preserved input")
        self.assertEqual((root / "out/fixture.json").read_bytes(), b'{"fixture":true}\n')
        self.assertEqual((root / "out/fixture-STYLE.md").read_bytes(), b"# Fixture\n")
        self.assertEqual(sorted(path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()),
                         ["input.html", "out/fixture-STYLE.md", "out/fixture.json"])

    def test_real_owned_publication_and_refusals_preserve_other_destinations(self):
        # The parent selects TMPDIR; retain all synthetic files rather than deleting a tree.
        base = self.fixture()
        root = base / "repo"
        root.mkdir()
        (root / "out").mkdir()
        source = root / "source.txt"
        source.write_bytes(b"source must remain unchanged")
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        safety.atomic_write(root, "out/palette.json", b'{"fixture":true}\n',
                            expected=None, check_expected=True)
        self.assertEqual(safety.read_owned(root, "out/palette.json")[0], b'{"fixture":true}\n')
        for relative in ("../escape.json", "/absolute.json", ""):
            with self.subTest(relative=relative):
                with self.assertRaises((ValueError, OSError)):
                    safety.atomic_write(root, relative, b"no", expected=None, check_expected=True)
        blocked = root / "not-a-directory"
        blocked.write_bytes(b"preserve")
        with self.assertRaises((ValueError, OSError)):
            safety.atomic_write(root, "not-a-directory/palette.json", b"no",
                                expected=None, check_expected=True)
        with self.assertRaises((ValueError, OSError)):
            safety.atomic_write(root, "out/palette.json", b"no",
                                expected=None, check_expected=True)
        self.assertEqual(blocked.read_bytes(), b"preserve")
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), before)
        self.assertFalse((root / "palettes").exists())
        self.assertFalse((base / "escape.json").exists())
        self.assertEqual(safety.read_owned(root, "out/palette.json")[0], b'{"fixture":true}\n')


if __name__ == "__main__":
    unittest.main(verbosity=2)
