#!/usr/bin/env python3
# component: design-fragment-emission-tests
# implements: ADR-0015, ADR-0028, ADR-0029
# intent: .claude/plans/v2-findings/plan.md
# constraints: inert rooted publication only; no Git writes, model, browser or cleanup
# last_intent_review: 2026-10-03
"""Execute the shared fragment emitter and all three actual caller recipes."""
from contextlib import redirect_stderr
from copy import deepcopy
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT / "lib"), str(ROOT / "skills/design-dna/scripts")]
import context_safety as safety
import design_contract as design

FRAGMENTS = {
    "typography": {"schema_version": 1, "font_stacks": [
        {"role": "heading", "family": "Fixture heading", "fallback_stack": ["serif"]},
        {"role": "body", "family": "Fixture body", "fallback_stack": ["sans-serif"]}],
        "size_scale": {"base_px": 16, "ratio": 1.25}, "line_heights": {"normal": 1.5}},
    "motion": {"schema_version": 1, "mode": "none", "libraries": [], "key_animations": [],
               "perf_budget": {"fallback_for_prefers_reduced_motion": "none"}},
    "shader": {"schema_version": 1, "visual_thesis": "none", "library": None,
               "glsl_snippets": [], "lygia_imports": []},
}


class FragmentEmission(unittest.TestCase):
    def test_large_integer_refuses_through_api_cli_and_actual_callers(self):
        fragment = deepcopy(FRAGMENTS["typography"])
        fragment["size_scale"]["base_px"] = 10 ** 400
        self.assert_numeric_refusal(fragment, "typography", "oversized")

    def test_shared_text_numbers_refuse_through_api_cli_and_actual_callers(self):
        for kind in FRAGMENTS:
            with self.subTest(kind=kind):
                fragment = deepcopy(FRAGMENTS[kind])
                if kind == "typography":
                    fragment["font_stacks"][0]["family"] = 10 ** 400
                elif kind == "motion":
                    fragment.update(mode="library", libraries=[{"name": 10 ** 400}])
                else:
                    fragment.update(visual_thesis="noise-field", library={"name": 10 ** 400},
                                    perf_budget={"respect_prefers_reduced_motion": True,
                                                 "fallback_strategy_low_end": "static",
                                                 "fallback_strategy_no_webgl": "static"})
                self.assert_numeric_refusal(fragment, kind, f"shared-text-{kind}")

    def assert_numeric_refusal(self, fragment, kind, label):
        before = deepcopy(fragment)
        with self.assertRaises(ValueError):
            design.validate_spec(fragment, kind)
        self.assertEqual(fragment, before)
        path = self.root / f"{label}.json"
        path.write_text(json.dumps(fragment), encoding="utf-8")
        input_bytes = path.read_bytes()
        result = subprocess.run(
            [sys.executable, "-I", "-B", str(ROOT / "skills/design-dna/scripts/design_contract.py"),
             "validate", "--repo", str(self.root), "--file", path.name, "--kind", kind],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 2, result.stderr)
        self.assertEqual(result.stdout, "")
        self.assertIn("ERROR [lintel/design]", result.stderr)
        self.assertNotIn("Traceback", result.stderr)
        source = (ROOT / f"skills/frontend-{kind}/SKILL.md").read_text(encoding="utf-8")
        recipe = re.search(r"```python\n(.*?)\n```", source.split("### Step 4", 1)[1], re.S).group(1)
        output = f"{label}-must-not-publish.json"
        for out in (None, output):
            error = io.StringIO()
            with redirect_stderr(error), self.assertRaises(SystemExit) as refused:
                exec(compile(recipe, f"{kind}:large-integer", "exec"),
                     {"fragment": fragment, "repo": self.root, "out": out,
                      "original_output_state": None})
            self.assertEqual(refused.exception.code, 2)
            self.assertIn("ERROR [lintel/design]", error.getvalue())
            self.assertFalse((self.root / output).exists())
            self.assertEqual(path.read_bytes(), input_bytes)
            self.assertEqual(fragment, before)

    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="fragment-emission-"))
        self.root.joinpath("source.txt").write_bytes(b"Preserve the actual source.")
        self.stdout = io.BytesIO()

    def emit(self, fragment, kind, **options):
        with patch.object(sys, "stdout", SimpleNamespace(buffer=self.stdout)):
            return design.emit_fragment(fragment, kind, repo=self.root, **options)

    def test_shared_emitter_is_the_only_publication_owner_in_all_callers(self):
        for kind in FRAGMENTS:
            with self.subTest(kind=kind):
                text = (ROOT / f"skills/frontend-{kind}/SKILL.md").read_text(encoding="utf-8")
                section = text.split("### Step 4", 1)[1]
                recipe = re.search(r"```python\n(.*?)\n```", section, re.S).group(1)
                self.assertIn("emit_fragment", recipe)
                for duplicated in ("atomic_write", "canonical_json", "read_owned", "validate_spec"):
                    self.assertNotIn(duplicated, recipe)
                namespace = {"fragment": deepcopy(FRAGMENTS[kind]), "repo": self.root,
                             "out": f"{kind}.json", "original_output_state": None}
                exec(compile(recipe, f"frontend-{kind}:publication", "exec"), namespace)
                self.assertEqual(json.loads(self.root.joinpath(f"{kind}.json").read_bytes()), FRAGMENTS[kind])
                namespace["fragment"]["schema_version"] = 99
                error = io.StringIO()
                with redirect_stderr(error), self.assertRaises(SystemExit) as refused:
                    exec(compile(recipe, f"frontend-{kind}:publication", "exec"), namespace)
                self.assertEqual(refused.exception.code, 2)
                self.assertIn("ERROR [lintel/design]", error.getvalue())
                self.assertEqual(json.loads(self.root.joinpath(f"{kind}.json").read_bytes()), FRAGMENTS[kind])

    def test_exact_partial_fields_and_source_profile_references_survive(self):
        for kind, original in FRAGMENTS.items():
            with self.subTest(kind=kind):
                fragment = deepcopy(original)
                fragment.update(source_content_hash="a" * 64,
                                profile_ref={"context_id": "fixture", "generation": 1, "digest": "b" * 64},
                                operator_instructions_md="No implicit dependency installation.")
                preserved = deepcopy(fragment)
                self.stdout = io.BytesIO()
                self.assertIsNone(self.emit(fragment, kind))
                self.assertEqual(json.loads(self.stdout.getvalue()), preserved)
                self.assertEqual(fragment, preserved)
                self.emit(fragment, kind, out=f"out/{kind}.json")
                self.assertEqual(json.loads(safety.read_owned(self.root, f"out/{kind}.json")[0]), preserved)
        self.assertEqual(self.root.joinpath("source.txt").read_bytes(), b"Preserve the actual source.")

    def test_actual_stdout_recipes_do_not_require_a_named_output_state(self):
        for kind, fragment in FRAGMENTS.items():
            with self.subTest(kind=kind):
                source = (ROOT / f"skills/frontend-{kind}/SKILL.md").read_text(encoding="utf-8")
                section = source.split("### Step 4", 1)[1]
                recipe = re.search(r"```python\n(.*?)\n```", section, re.S).group(1)
                namespace = {"fragment": deepcopy(fragment), "repo": self.root, "out": None}
                output = io.BytesIO()
                with patch.object(sys, "stdout", SimpleNamespace(buffer=output)):
                    exec(compile(recipe, f"frontend-{kind}:stdout", "exec"), namespace)
                self.assertEqual(json.loads(output.getvalue()), fragment)
                self.assertFalse(self.root.joinpath(f"{kind}.json").exists())
        self.assertEqual(self.root.joinpath("source.txt").read_bytes(), b"Preserve the actual source.")

    def test_none_css_library_and_both_no_shader_forms(self):
        css = {**deepcopy(FRAGMENTS["motion"]), "mode": "css",
               "key_animations": [{"name": "focus", "library": "css"}]}
        library = {**deepcopy(FRAGMENTS["motion"]), "mode": "library",
                   "libraries": [{"name": "fixture-runtime"}],
                   "key_animations": [{"name": "reveal", "library": "fixture-runtime"}]}
        active = {"schema_version": 1, "visual_thesis": "noise-field",
                  "library": {"name": "fixture-gpu"}, "perf_budget": {
                      "respect_prefers_reduced_motion": True,
                      "fallback_strategy_low_end": "static", "fallback_strategy_no_webgl": "static"}}
        for i, (kind, value) in enumerate((
            ("motion", FRAGMENTS["motion"]), ("motion", css), ("motion", library),
            ("shader", None), ("shader", FRAGMENTS["shader"]), ("shader", active),
        )):
            with self.subTest(kind=kind, value=value):
                self.emit(value, kind, out=f"branches/{i}.json")
                self.assertEqual(json.loads(safety.read_owned(self.root, f"branches/{i}.json")[0]), value)

    def test_invalid_fragments_never_publish(self):
        for kind, value in (
            ("pipeline", FRAGMENTS["motion"]),
            ("typography", {**FRAGMENTS["typography"], "font_stacks": []}),
            ("motion", {**FRAGMENTS["motion"], "mode": "css", "libraries": [{"name": "unrequested"}]}),
            ("motion", {**FRAGMENTS["motion"], "mode": "library"}),
            ("motion", {**FRAGMENTS["motion"], "key_animations": [{"library": "css"}]}),
            ("shader", {**FRAGMENTS["shader"], "library": {"name": "contradicts-none"}}),
            ("shader", {"schema_version": 1, "visual_thesis": "noise-field", "library": {"name": "gpu"}}),
        ):
            with self.subTest(kind=kind, value=value):
                for out in (None, "invalid.json"):
                    with self.assertRaises(ValueError):
                        self.emit(value, kind, out=out)
                self.assertEqual(self.stdout.getvalue(), b"")
                self.assertFalse(self.root.joinpath("invalid.json").exists())

    def test_collision_authorized_exact_replacement_and_stale_preimage(self):
        fragment = FRAGMENTS["motion"]
        self.emit(fragment, "motion", out="owned.json")
        old_bytes, state = safety.read_owned(self.root, "owned.json")
        with self.assertRaises((ValueError, OSError)):
            self.emit(fragment, "motion", out="owned.json")
        changed = {**fragment, "brief_summary": "Authorized replacement"}
        self.emit(changed, "motion", out="owned.json", original_output_state=state)
        self.assertNotEqual(safety.read_owned(self.root, "owned.json")[0], old_bytes)
        with self.assertRaises((ValueError, OSError)):
            self.emit(fragment, "motion", out="owned.json", original_output_state=state)
        self.assertEqual(json.loads(safety.read_owned(self.root, "owned.json")[0]), changed)

    def test_unsafe_unavailable_outputs_and_readback_failure_are_visible(self):
        for out in ("", "../escape.json", "/dev/stdout", str(self.root / "absolute.json")):
            with self.subTest(out=out), self.assertRaises((ValueError, OSError)):
                self.emit(FRAGMENTS["motion"], "motion", out=out)
        with self.assertRaises((ValueError, OSError)):
            design.emit_fragment(FRAGMENTS["motion"], "motion", repo=self.root / "missing", out="out.json")
        # Inject a readback mismatch after an actual write; it must not report success or clean it up.
        with patch.object(safety, "read_owned", return_value=(b"wrong bytes", {})):
            with self.assertRaisesRegex(ValueError, "readback"):
                self.emit(FRAGMENTS["motion"], "motion", out="partial.json")
        self.assertTrue(self.root.joinpath("partial.json").is_file())
        self.assertEqual(self.stdout.getvalue(), b"")


if __name__ == "__main__":
    unittest.main(verbosity=2)
