# component: direct-design-contract-tests
# implements: ADR-0015, ADR-0016, ADR-0017, ADR-0028, ADR-0029
# intent: .claude/plans/universal-implementation/packages/P11.md
# constraints: synthetic data, explicit roots and real shared APIs; no browser or renderer
# last_intent_review: 2026-09-22
"""Exercise direct design consumers; these fixtures are not rendered-artifact evidence."""
from __future__ import annotations

import argparse
from contextlib import nullcontext
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

parser = argparse.ArgumentParser(allow_abbrev=False)
parser.add_argument("--root", type=Path, required=True)
parser.add_argument("--git", required=True)
args = parser.parse_args()
SOURCE = args.root.resolve()
sys.path[:0] = [str(SOURCE / "lib"), str(SOURCE / "skills/design-dna/scripts")]
import context_safety as safety
from profile_context import ProfileConfig, load_profile_context, profile_reference, required_policy
from review_contract import content_digest, evidence_manifest, verify_context, verify_qa
from profile_context import verify_profile_reference
import domain_result
import design_contract as design
import patterns as pat
import pattern_visual as pv

RUNTIME = SOURCE / ".claude/runtime/p11-a14"
safety.native_io_path(RUNTIME).mkdir(parents=True, exist_ok=True)
RUN = Path(tempfile.mkdtemp(prefix="d-", dir=safety.native_io_path(RUNTIME)))
RUN = Path(*safety.path_identity(RUN))
SEAL_PATHS = [
    "skills/design-dna/scripts/design_contract.py",
    "skills/design-dna/references/design-contract.schema.json",
    "skills/design-dna/scripts/emit_tokens.py", "lib/context_safety.py", "lib/native_paths.py",
    "lib/profile_context.py", "lib/profile-context-schema.json", "lib/review_contract.py",
    "lib/review-schema.json", "lib/domain_result.py", "lib/domain-result-schema.json",
    "lib/markdown_source.py", "bin/li-review-evidence.py", "tests/integration/design-contract.py",
    "skills/generate-web/SKILL.md", "skills/generate-app/SKILL.md",
    "skills/design-dna/references/design-contract.md",
    "skills/frontend-typography/SKILL.md", "skills/frontend-motion/SKILL.md",
    "skills/frontend-shader/SKILL.md",
]


def seals():
    return {path: safety.read_owned(SOURCE, path)[1]["sha256"] for path in SEAL_PATHS}


SEALS = seals()
safety.native_io_path(RUN / "source-seals.json").write_text(json.dumps(SEALS, indent=2), encoding="utf-8")


def encoded(data):
    return (json.dumps(data, sort_keys=True, allow_nan=False) + "\n").encode()


WEBSITE = {"artifact": ["website"]}
PATTERN_TS = "2026-09-01T00:00:00Z"
FOREIGN_PATH = "Unsafe relative path"
CHANGED_PIN = r"not current \(unavailable\): .*reference_digest_mismatch"


def brand_pattern(value="#112233", level="default", pid="example.brand"):
    """A synthetic approved universal pattern whose one clause binds visual.palette.ink."""
    return {"schema_version": 1, "id": pid, "version": "1.0.0", "status": "approved",
            "summary": f"Summary of {pid}", "owner": "platform team", "applies_to": WEBSITE, "includes": [],
            "sources": [{"kind": "operator-statement", "ref": "The operator stated this expectation.",
                         "root": "statement", "section": "", "observed_at": PATTERN_TS,
                         "confidence": "confirmed", "reuse": "internal use"}],
            "requirements": [{"id": "INK", "level": level, "text": "Ink colour", "verify": "check INK",
                              "setting": "visual.palette.ink", "value": value}],
            "guidance": "", "assets": [],
            "approval": {"by": "architecture board", "reference": "ADR-0038", "at": PATTERN_TS}}


def pattern_ref(source, pattern):
    return {"source": source, "id": pattern["id"], "version": pattern["version"],
            "sha256": pat.content_digest(pattern)}


def pattern_binding(bid, uses, role="required"):
    return {"id": bid, "when": WEBSITE, "use": uses, "role": role, "approved_by": "lead",
            "approval_ref": "decision-1"}


class DesignContract(unittest.TestCase):
    counter = 0

    def setUp(self):
        DesignContract.counter += 1
        self.base = RUN / str(self.counter)
        self.repo = self.base / "repo"
        self.home = self.base / "home"
        for path in (self.repo, self.home, self.base / "tmp", self.home / "app", self.home / "local"):
            safety.native_io_path(path).mkdir(parents=True)
        self.env = {key: os.environ[key] for key in (
            "PATH", "PATHEXT", "SystemRoot", "WINDIR", "COMSPEC", "OS",
        ) if key in os.environ}
        self.env.update({
            "HOME": str(self.home), "USERPROFILE": str(self.home),
            "APPDATA": str(self.home / "app"), "LOCALAPPDATA": str(self.home / "local"),
            "TEMP": str(self.base / "tmp"), "TMP": str(self.base / "tmp"),
            "TMPDIR": str(self.base / "tmp"), "XDG_CONFIG_HOME": str(self.home / "config"),
            "XDG_CACHE_HOME": str(self.home / "cache"),
            "LINTEL_SOURCE_ROOT": str(SOURCE), "LINTEL_REPO_ROOT": str(self.repo),
            "LINTEL_HOME": str(self.home / "lintel"), "LINTEL_PYTHON": sys.executable,
            "LINTEL_PACKS_DIR": str(self.home / "lintel/packs"),
            "LINTEL_ACTIVE_PACK_FILE": str(self.home / "lintel/packs/active-pack"),
            "LINTEL_AUDIT_DIR": str(self.repo / ".claude/runtime/audit"),
            "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull, "GIT_CEILING_DIRECTORIES": str(self.base),
            "GIT_TERMINAL_PROMPT": "0", "PYTHONNOUSERSITE": "1",
            "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1",
        })
        for key in ("XDG_CONFIG_HOME", "XDG_CACHE_HOME", "LINTEL_HOME", "LINTEL_PACKS_DIR",
                    "LINTEL_AUDIT_DIR"):
            path = Path(self.env[key])
            self.assertTrue(path.is_relative_to(self.base))
            safety.native_io_path(path).mkdir(parents=True, exist_ok=True)
        environment = patch.dict(os.environ, self.env, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.command_count = 0
        self.git("init", "-q")
        self.git("symbolic-ref", "HEAD", "refs/heads/synthetic")
        self.write(".gitignore", b".claude/runtime/\n")
        self.write("spec.md", b"# Synthetic A14 contract acceptance\n")
        self.write("plan.md", b"- [ ] A14.1 Read one design contract\n")
        self.write("prompt.md", b"Synthetic direct data only; no renderer or browser.\n")
        self.write_json("work.json", {
            "schema_version": 1, "workflow": "lintel", "status": "APPROVED",
            "spec": "spec.md", "plan": "plan.md", "tasks": "plan.md", "prompt": "prompt.md",
        })
        self.write("brief with spaces.md", b"Keep the chosen profile. No animation or shader.\n")
        self.write("font-source.txt", b"Synthetic font provenance, not a real font/license observation.\n")
        self.write("design-dna.md", b"Synthetic retained retrieval: restrained editorial layout.\n")
        self.config = ProfileConfig(
            SOURCE, self.repo, self.home / "lintel", self.home / "lintel/packs",
            self.home / "lintel/packs/active-pack", context_id="synthetic-design",
        )
        self.profile = load_profile_context(self.config, create=True)
        self.reference = profile_reference(self.profile)
        self.asset, self.leaves = design.profile_asset(self.profile, self.config)
        self.spec = {
            "schema_version": 1, "source": "frontend-design", "target_format": "single-file",
            "typography": {"schema_version": 1, "font_stacks": [
                {"role": "heading", "family": "Poppins", "fallback_stack": ["sans-serif"]},
                {"role": "body", "family": "Lora", "fallback_stack": ["serif"]},
            ], "size_scale": {"base_px": 16, "ratio": 1.25}},
            "motion": {"schema_version": 1, "mode": "none", "libraries": [], "key_animations": [],
                       "perf_budget": {"fallback_for_prefers_reduced_motion": "no-animation"}},
            "shader": None, "component_libraries": [],
            "layout_grammar": {"max_width": "1152px"},
            "interaction_signature": {"scroll_smoothing": False, "page_transitions": "none"},
            "visual_thesis": "Synthetic restrained editorial page", "voice_tier": "internal",
            "palette": {"tokens": {"ink": "#141413", "paper": "#faf9f5"}},
            "binding": {
                "profile_ref": self.reference, "profile_asset": self.asset,
                "brief": self.ref("brief with spaces.md"), "overrides": [],
                "retrieval": [self.ref("design-dna.md")],
                "project": {"existing": False, "stack": "html", "manifests": []},
                "customer_share": False,
                "provenance": [
                    {"kind": "font", "name": name, "version": "synthetic-1",
                     "source": "fixture:font-source.txt", "license": "synthetic-not-a-license",
                     "rationale": "Synthetic profile-consumer fixture",
                     "evidence": [self.ref("font-source.txt")]} for name in ("Poppins", "Lora")
                ],
            },
        }
        self.write_json("run with spaces/frontend-design-spec.json", self.spec)
        self.git("add", ".")
        self.git("commit", "-qm", "test: synthetic design inputs")
        self.base_ref = self.git("rev-parse", "HEAD").stdout.strip()
        self.requirement = {
            "id": "design-contrast", "kind": "contrast", "requirement": "mandatory",
            "applicability": "applicable",
            "policy": {"source": "spec.md", "version": "synthetic-1",
                       "applicability": "Synthetic normal text", "jurisdiction": None,
                       "actor": None, "effective_date": None},
        }
        self.prepare_input = {
            "work_map": "work.json", "package_id": "P11", "leaf_ids": ["A14.1"],
            "acceptance_paths": ["spec.md"], "base": self.base_ref,
            "selection": ["run with spaces", "brief with spaces.md", "font-source.txt", "design-dna.md"],
            "record_path": ".claude/runtime/reviews/result.json", "attempt_id": "a14-synthetic",
            "builder": {"id": "fixture", "context": "design-tests"}, "independence_required": True,
            "purpose": "implementation", "profile": self.reference,
            "required_policy": required_policy(self.profile),
            "required_controls": ["spec", "quality", "design-contrast"],
            "qa_requirements": [self.requirement],
        }

    def run_process(self, argv, *, separate_stderr=False):
        self.command_count += 1
        stem = self.base / f"command-{self.command_count}"
        error_path = safety.native_io_path(stem.with_suffix(".stderr.log"))
        with safety.native_io_path(stem.with_suffix(".log")).open("wb") as out, \
                (error_path.open("wb") if separate_stderr else nullcontext(subprocess.STDOUT)) as err:
            result = subprocess.run([str(x) for x in argv], cwd=self.repo, env=self.env,
                                    stdout=out, stderr=err, timeout=60, check=False)
        stdout = safety.native_io_path(stem.with_suffix(".log")).read_text(encoding="utf-8")
        safety.native_io_path(stem.with_suffix(".json")).write_bytes(encoded({
            "argv": [str(x) for x in argv], "exit": result.returncode,
            "environment": self.env, "cwd": str(self.repo),
        }))
        stderr = error_path.read_text(encoding="utf-8") if separate_stderr else ""
        return subprocess.CompletedProcess(argv, result.returncode, stdout, stderr)

    def git(self, *argv):
        result = self.run_process([
            args.git, "--no-pager", "-c", "core.autocrlf=false", "-c", "core.fsmonitor=false",
            "-c", f"core.hooksPath={self.base / 'hooks'}", "-c", "user.name=Synthetic fixture",
            "-c", "user.email=fixture@example.invalid", *argv,
        ])
        self.assertEqual(result.returncode, 0, result.stdout[-1600:])
        return result

    def write(self, path, content):
        safety.atomic_write(self.repo, path, content)

    def write_json(self, path, content):
        self.write(path, encoded(content))

    def ref(self, path):
        return {"path": path, "sha256": safety.read_owned(self.repo, path)[1]["sha256"]}

    def prepare(self, selection=()):
        request = deepcopy(self.prepare_input)
        request["selection"] += list(selection)
        self.write_json(".claude/runtime/prepare.json", request)
        result = self.run_process([
            sys.executable, "-B", SOURCE / "bin/li-review-evidence.py", "prepare", "--repo", self.repo,
            "--request", self.repo / ".claude/runtime/prepare.json",
        ])
        self.assertEqual(result.returncode, 0, result.stdout[-2000:])
        return json.loads(result.stdout)

    def load(self, spec=None):
        self.write_json("run with spaces/frontend-design-spec.json", spec or self.spec)
        return design.load_design(self.repo, "run with spaces/frontend-design-spec.json",
                                  expected=self.prepare(), profile_config=self.config)

    def test_current_none_design_is_bound_without_rendering(self):
        result = self.load()
        self.assertEqual(result["profile_ref"], self.reference)
        self.assertEqual(result["verification"], "current_inputs")
        self.assertFalse(result["release_clearance"])
        self.assertEqual(design.renderer_args(result, out="out with spaces"), {
            "skill": "generate-web",
            "args": ["--from-frontend-design", "run with spaces", "--variant", "single-file",
                     "--out", "out with spaces"],
        })
        self.write_json(".claude/runtime/expected.json", self.prepare())
        mapped = self.run_process([
            sys.executable, "-B", SOURCE / "skills/design-dna/scripts/design_contract.py",
            "renderer-args", "--repo", self.repo, "--file", "run with spaces/frontend-design-spec.json",
            "--expected", ".claude/runtime/expected.json", "--out", "out with spaces",
            "--profile-home", self.config.home, "--profile-packs", self.config.packs,
            "--profile-pointer", self.config.pointer,
        ])
        self.assertEqual(mapped.returncode, 0, mapped.stdout)
        self.assertFalse(json.loads(mapped.stdout)["executed"])
        self.assertEqual(json.loads(mapped.stdout)["args"][-1], "out with spaces")
        self.assertFalse(safety.native_io_path(self.repo / "out with spaces").exists())

    def test_renderer_variants_stack_and_customer_share_roundtrip(self):
        for target, stack, skill, option in [
            ("single-file", "html", "generate-web", ["--variant", "single-file"]),
            ("nextjs", "next-app", "generate-web", ["--variant", "nextjs-scaffold"]),
            ("app", "vite-react", "generate-app", ["--stack", "vite-react"]),
            ("app", "svelte-kit", "generate-app", ["--stack", "svelte-kit"]),
        ]:
            spec = deepcopy(self.spec)
            spec["target_format"] = target
            spec["binding"]["project"]["stack"] = stack
            spec["binding"]["customer_share"] = True
            result = design.renderer_args(self.load(spec), out="selected output")
            self.assertEqual(result["skill"], skill)
            self.assertEqual(result["args"][2:4], option)
            self.assertEqual(result["args"][-1], "--customer-share")
        spec["binding"]["project"]["stack"] = "vue"
        with self.assertRaises(ValueError):
            self.load(spec)

    def test_renderer_refuses_alternate_filenames_without_losing_canonical_routes(self):
        for kind, filename, alternate_target, alternate_stack in (
            ("frontend", "frontend-design-spec.json", "app", "vite-react"),
            ("pipeline", "design-spec.json", "nextjs", "next-app"),
        ):
            directory = f"{kind} run with spaces"
            if kind == "frontend":
                canonical = deepcopy(self.spec)
                alternate = deepcopy(canonical)
                alternate["target_format"] = alternate_target
            else:
                web = deepcopy(self.spec)
                binding = web.pop("binding")
                del web["source"]
                self.write(f"{directory}/content.md", b"Selected pipeline content.\n")
                binding["brief"] = self.ref(f"{directory}/content.md")
                canonical = {
                    "version": "1.0", "schema_version": 1, "source": "pipeline",
                    "palette": {"text_dark": "#141413", "background": "#faf9f5"},
                    "fonts": {"heading": "Poppins", "body": "Lora"},
                    "per_format": {"web": {"sections": []}}, "web_design": web, "binding": binding,
                }
                alternate = deepcopy(canonical)
                alternate["web_design"]["target_format"] = alternate_target
            alternate["binding"]["project"]["stack"] = alternate_stack
            self.write_json(f"{directory}/{filename}", canonical)
            self.write_json(f"{directory}/alternate.json", alternate)
            expected = self.prepare([directory])
            selected = design.load_design(self.repo, f"{directory}/alternate.json",
                                          expected=expected, profile_config=self.config)
            with self.assertRaisesRegex(ValueError, "canonical"):
                design.renderer_args(selected, out="output with spaces")
            selected = design.load_design(self.repo, f"{directory}/{filename}",
                                          expected=expected, profile_config=self.config)
            mapped = design.renderer_args(selected, out="output with spaces")
            self.assertEqual(mapped["skill"], "generate-web")
            self.assertEqual(mapped["args"], [
                "--from-frontend-design" if kind == "frontend" else "--from-pipeline",
                directory, "--variant", "single-file", "--out", "output with spaces",
            ])
            self.assertEqual(selected["spec"], self.ref(f"{directory}/{filename}"))

    def test_bound_manifest_cannot_be_bypassed_as_a_new_project(self):
        self.assertEqual(design.renderer_args(self.load(), out="new output")["skill"], "generate-web")
        self.write_json("nested/package.JSON", {"dependencies": {"react": "18.3.1", "react-scripts": "5.0.1"}})
        self.prepare_input["selection"].append("nested")
        nested = deepcopy(self.spec)
        nested["target_format"] = "app"
        nested["binding"]["project"] = {
            "existing": False, "stack": "next-app", "manifests": [self.ref("nested/package.JSON")],
        }
        with self.assertRaisesRegex(ValueError, "technology"):
            self.load(nested)
        self.write_json("package.json", {"dependencies": {"react": "18.3.1", "react-scripts": "5.0.1"}})
        self.prepare_input["selection"].append("package.json")
        value = deepcopy(self.spec)
        value["target_format"] = "app"
        for existing in (False, True):
            value["binding"]["project"] = {
                "existing": existing, "stack": "next-app", "manifests": [self.ref("package.json")],
            }
            with self.assertRaisesRegex(ValueError, "technology"):
                self.load(value)
        for stack, dependencies, development in (
            ("next-app", {"next": "15.0.0", "react": "19.0.0"}, {}),
            ("vite-react", {"react": "19.0.0"}, {"vite": "6.0.0"}),
            ("svelte-kit", {"@sveltejs/kit": "2.0.0"}, {}),
        ):
            self.write_json("package.json", {"dependencies": dependencies, "devDependencies": development})
            for existing in (False, True):
                value["binding"]["project"] = {
                    "existing": existing, "stack": stack, "manifests": [self.ref("package.json")],
                }
                mapped = design.renderer_args(self.load(value), out="supported output")
                self.assertEqual(mapped["args"][2:4], ["--stack", stack])

    def test_web_and_app_methods_preserve_both_no_shader_forms(self):
        for shader in (None, {"schema_version": 1, "visual_thesis": "none", "library": None}):
            value = deepcopy(self.spec)
            value["shader"] = shader
            for target, stack in (("single-file", "html"), ("app", "vite-react")):
                value["target_format"] = target
                value["binding"]["project"]["stack"] = stack
                checked = design.validate_spec(value)
                self.assertEqual(checked["design"]["shader"], shader)
                self.assertEqual(checked["design"]["component_libraries"], [])
                self.assertEqual(checked["design"]["motion"]["libraries"], [])
            value["target_format"] = "single-file"
            value["binding"]["project"]["stack"] = "html"
            binding = value.pop("binding")
            del value["source"]
            pipeline = {
                "version": "1.0", "schema_version": 1, "source": "pipeline",
                "palette": {"text_dark": "#141413", "background": "#faf9f5"},
                "fonts": {"heading": "Poppins", "body": "Lora"},
                "per_format": {"web": {"sections": []}}, "web_design": value, "binding": binding,
            }
            checked = design.validate_spec(pipeline, "pipeline")
            self.assertEqual(checked["design"]["shader"], shader)
            self.assertEqual(checked["design"]["component_libraries"], [])
        web = (SOURCE / "skills/generate-web/SKILL.md").read_text(encoding="utf-8")
        self.assertTrue("if `shader != null`" not in web, "Web method still uses the unsafe non-null-only shader branch")
        self.assertTrue('shader.visual_thesis != "none"' in web, "Web method must exclude the explicit none branch")
        self.assertTrue("no GPU" in web, "Web method must retain the no-GPU result")
        app = (SOURCE / "skills/generate-app/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("active non-`none` shader", app)

    def test_legacy_frontend_and_pipeline_are_readable_not_renderable(self):
        legacy = deepcopy(self.spec)
        del legacy["binding"]
        del legacy["motion"]["mode"]
        value = design.validate_spec(legacy)
        self.assertFalse(value["renderable"])
        with self.assertRaises(ValueError):
            self.load(legacy)
        pipeline = {"version": "1.0", "palette": {"text_dark": "#141413"},
                    "fonts": {"heading": "Poppins", "body": "Lora"}, "per_format": {"web": {"sections": []}}}
        self.assertFalse(design.validate_spec(pipeline, "pipeline")["renderable"])
        pipeline["version"] = "2.0"
        with self.assertRaises(ValueError):
            design.validate_spec(pipeline, "pipeline")

    def test_resolved_pipeline_uses_the_same_design_and_rejects_conflicting_projection(self):
        web = deepcopy(self.spec)
        binding = web.pop("binding")
        del web["source"]
        self.write("run with spaces/content.md", b"Selected pipeline content.\n")
        binding["brief"] = self.ref("run with spaces/content.md")
        pipeline = {"version": "1.0", "schema_version": 1, "source": "pipeline",
                    "palette": {"text_dark": "#141413", "background": "#faf9f5"},
                    "fonts": {"heading": "Poppins", "body": "Lora"},
                    "per_format": {"web": {"sections": []}}, "web_design": web, "binding": binding}
        path = "run with spaces/design-spec.json"
        self.write_json(path, pipeline)
        result = design.load_design(self.repo, path, expected=self.prepare(), profile_config=self.config)
        self.assertEqual(design.renderer_args(result, out="site")["args"][:2],
                         ["--from-pipeline", "run with spaces"])
        pipeline["fonts"]["body"] = "Unrelated font"
        with self.assertRaises(ValueError):
            design.validate_spec(pipeline, "pipeline")

    def test_pipeline_binds_the_actual_consumed_content_path_and_bytes(self):
        for case in ("canonical", "different-brief", "same-bytes-other-path",
                     "stale-content-hash", "unselected-content", "missing-content"):
            with self.subTest(case=case):
                directory = f"pipeline {case} with spaces"
                content_path = f"{directory}/content.md"
                spec_path = f"{directory}/design-spec.json"
                actual = b"# Actual sibling content, consumed by the renderer.\n"
                if case == "same-bytes-other-path":
                    actual = safety.read_owned(self.repo, "brief with spaces.md")[0]
                if case != "missing-content":
                    self.write(content_path, actual)
                binding = deepcopy(self.spec["binding"])
                binding["brief"] = {"path": content_path, "sha256": hashlib.sha256(actual).hexdigest()}
                if case in ("different-brief", "same-bytes-other-path"):
                    binding["brief"] = self.ref("brief with spaces.md")
                if case == "stale-content-hash":
                    self.write(content_path, b"# Changed current sibling content.\n")
                web = deepcopy(self.spec)
                del web["binding"], web["source"]
                pipeline = {
                    "version": "1.0", "schema_version": 1, "source": "pipeline",
                    "source_content_hash": binding["brief"]["sha256"],
                    "palette": {"text_dark": "#141413", "background": "#faf9f5"},
                    "fonts": {"heading": "Poppins", "body": "Lora"},
                    "per_format": {"web": {"sections": []}}, "web_design": web, "binding": binding,
                }
                self.write_json(spec_path, pipeline)
                expected = self.prepare([spec_path if case == "unselected-content" else directory])
                if case == "canonical":
                    loaded = design.load_design(self.repo, spec_path, expected=expected,
                                                profile_config=self.config)
                    self.assertEqual(loaded["binding"]["brief"], self.ref(content_path))
                    self.assertEqual(design.renderer_args(loaded, out="output with spaces")["args"], [
                        "--from-pipeline", directory, "--variant", "single-file", "--out", "output with spaces",
                    ])
                else:
                    with self.assertRaises((ValueError, OSError)):
                        design.load_design(self.repo, spec_path, expected=expected, profile_config=self.config)
        self.assertEqual(self.load()["binding"]["brief"], self.ref("brief with spaces.md"))

    def _fragment_emission(self, kind):
        method = (SOURCE / f"skills/frontend-{kind}/SKILL.md").read_text(encoding="utf-8")
        section = method.split("### Step 4", 1)[1]
        recipe = re.search(r"```python\n(.*?)\n```", section, re.S)
        self.assertIsNotNone(recipe, f"{kind}: validate the parsed value before stdout/file emission")
        if kind == "shader":
            fragment = {"schema_version": 1, "visual_thesis": "none", "library": None}
        else:
            fragment = deepcopy(self.spec[kind])
        driver = """
import os, sys
from pathlib import Path
sys.path[:0] = [str(Path(os.environ["LINTEL_SOURCE_ROOT"]) / "lib"),
               str(Path(os.environ["LINTEL_SOURCE_ROOT"]) / "skills/design-dna/scripts")]
from review_contract import load_json
import context_safety as safety
repo = safety.checked_root(Path(os.environ["LINTEL_REPO_ROOT"]))
inputs = load_json(safety.read_owned(repo, sys.argv[1], 2097152)[0].decode("utf-8"))
fragment = inputs["fragment"]
out = inputs["out"]
original_output_state = inputs["original_output_state"]
""" + recipe.group(1)

        def emit(value, out=None, state=None):
            self.write_json("fragment-input.json", {
                "fragment": value, "out": out, "original_output_state": state,
            })
            return self.run_process([sys.executable, "-B", "-c", driver, "fragment-input.json"],
                                    separate_stderr=True)

        stdout = emit(fragment)
        self.assertEqual(stdout.returncode, 0, stdout.stderr)
        self.assertEqual(json.loads(stdout.stdout), fragment)
        self.assertEqual(stdout.stderr, "")
        output = f"fragment output/{kind}.json"
        named = emit(fragment, output)
        self.assertEqual(named.returncode, 0, named.stderr)
        self.assertEqual(named.stdout, "")
        self.assertEqual(named.stderr, "")
        self.assertEqual(json.loads(safety.read_owned(self.repo, output)[0]), fragment)
        named_validation = self.run_process([
            sys.executable, "-B", SOURCE / "skills/design-dna/scripts/design_contract.py",
            "validate", "--repo", self.repo, "--file", output, "--kind", kind,
        ])
        self.assertEqual(named_validation.returncode, 0, named_validation.stdout)
        alternate = deepcopy(fragment)
        invalid_branch = deepcopy(fragment)
        if kind == "motion":
            alternate.update(mode="css", key_animations=[{"name": "focus-color", "library": "css"}])
            invalid_branch.update(mode="css", libraries=[{"name": "unrequested-js"}])
        elif kind == "shader":
            alternate.update(
                visual_thesis="noise-field", library={"name": "synthetic-gpu"},
                perf_budget={"fallback_strategy_low_end": "static",
                             "fallback_strategy_no_webgl": "static",
                             "respect_prefers_reduced_motion": True},
            )
            invalid_branch.update(library={"name": "contradicts-none"})
        else:
            alternate["font_stacks"][0]["family"] = "Synthetic alternative family"
            invalid_branch["font_stacks"] = []
        for out in (None, f"alternate output/{kind}.json"):
            valid = emit(alternate, out)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            emitted = valid.stdout if out is None else safety.read_owned(self.repo, out)[0]
            self.assertEqual(json.loads(emitted), alternate)
            refused = emit(invalid_branch, out)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertEqual(refused.stdout, "")
            self.assertIn("ERROR", refused.stderr)
            if out is not None:
                self.assertEqual(json.loads(safety.read_owned(self.repo, out)[0]), alternate)
        original = safety.read_owned(self.repo, output)
        for out in (None, f"invalid output/{kind}.json", output):
            invalid = deepcopy(fragment)
            invalid["schema_version"] = 2
            refused = emit(invalid, out)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertEqual(refused.stdout, "")
            self.assertIn("ERROR", refused.stderr)
        self.assertFalse(safety.native_io_path(self.repo / f"invalid output/{kind}.json").exists())
        self.assertEqual(safety.read_owned(self.repo, output)[0], original[0])
        collision = emit(fragment, output)
        self.assertEqual(collision.returncode, 2)
        self.assertEqual(collision.stdout, "")
        self.assertEqual(safety.read_owned(self.repo, output)[0], original[0])
        changed = {**fragment, "brief_summary": "Authorized replacement of the exact owned output"}
        replaced = emit(changed, output, original[1])
        self.assertEqual(replaced.returncode, 0, replaced.stderr)
        self.assertEqual(replaced.stdout, "")
        self.assertEqual(json.loads(safety.read_owned(self.repo, output)[0]), changed)
        stale = emit(fragment, output, original[1])
        self.assertEqual(stale.returncode, 2)
        self.assertEqual(stale.stdout, "")
        for unsafe in ("/dev/stdout", "../escape.json", str(self.base / "absolute.json")):
            refused = emit(fragment, unsafe)
            self.assertEqual(refused.returncode, 2, refused.stderr)
            self.assertEqual(refused.stdout, "")
            self.assertIn("ERROR", refused.stderr)

    def test_typography_solo_stdout_and_named_output(self):
        self._fragment_emission("typography")

    def test_motion_solo_stdout_and_named_output(self):
        self._fragment_emission("motion")

    def test_shader_solo_stdout_and_named_output(self):
        self._fragment_emission("shader")

    def test_none_css_and_shader_short_circuits_reject_contradictions(self):
        self.assertTrue(design.validate_spec(self.spec)["renderable"])
        self.assertFalse(design.validate_spec(self.spec["motion"], "motion")["renderable"])
        self.assertFalse(design.validate_spec(self.spec["typography"], "typography")["renderable"])
        self.assertFalse(design.validate_spec(
            {"schema_version": 1, "visual_thesis": "none", "library": None}, "shader")["renderable"])
        css = deepcopy(self.spec)
        css["motion"]["mode"] = "css"
        css["motion"]["key_animations"] = [{"name": "focus", "library": "css"}]
        css["shader"] = {"schema_version": 1, "visual_thesis": "none", "library": None}
        self.assertTrue(design.validate_spec(css)["renderable"])
        for mutate in (
            lambda s: s["motion"].update(libraries=[{"name": "gsap"}]),
            lambda s: s["interaction_signature"].update(scroll_smoothing=True),
            lambda s: s.update(shader={"schema_version": 1, "visual_thesis": "none",
                                      "library": {"name": "ogl"}}),
            lambda s: s["motion"].update(mode="unknown"),
        ):
            value = deepcopy(self.spec)
            mutate(value)
            with self.assertRaises(ValueError):
                design.validate_spec(value)
        library = deepcopy(self.spec)
        library["motion"].update(mode="library", libraries=[{"name": "synthetic-motion"}])
        library["binding"]["provenance"].append({
            "kind": "library", "name": "synthetic-motion", "version": "1.0.0",
            "source": "fixture:font-source.txt", "license": "synthetic",
            "rationale": "Synthetic library branch", "evidence": [self.ref("font-source.txt")],
            "stacks": ["html"],
        })
        self.assertTrue(design.validate_spec(library)["renderable"])
        library["binding"]["provenance"][-1]["stacks"] = ["svelte-kit"]
        with self.assertRaises(ValueError):
            design.validate_spec(library)
        active_shader = {"schema_version": 1, "visual_thesis": "noise-field",
                         "library": {"name": "synthetic-gpu"},
                         "perf_budget": {"fallback_strategy_low_end": "static",
                                         "fallback_strategy_no_webgl": "static",
                                         "respect_prefers_reduced_motion": True}}
        design.validate_spec(active_shader, "shader")
        for invalid in (False, "false", "true", 1):
            active_shader["perf_budget"]["respect_prefers_reduced_motion"] = invalid
            with self.assertRaises(ValueError):
                design.validate_spec(active_shader, "shader")

    def test_profile_drift_required_failure_and_asset_identity_block(self):
        expected = self.prepare()
        altered = deepcopy(self.spec)
        altered["binding"]["profile_ref"]["generation"] += 1
        self.write_json("run with spaces/frontend-design-spec.json", altered)
        with self.assertRaises(ValueError):
            design.load_design(self.repo, "run with spaces/frontend-design-spec.json",
                               expected=expected, profile_config=self.config)
        altered = deepcopy(self.spec)
        altered["binding"]["profile_asset"]["sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            self.load(altered)
        for mutate in (
            lambda value: value.update(brief_hash="0" * 64),
            lambda value: value["palette"].update(source_profile="another-brand"),
        ):
            altered = deepcopy(self.spec)
            mutate(altered)
            with self.assertRaises(ValueError):
                self.load(altered)
        self.write_json(".claude/profile-requirements.json",
                        {"schema_version": 1, "required_pack": "missing-design-policy"})
        with self.assertRaises(ValueError):
            self.load()

    def test_explicit_profile_asset_does_not_fallback_to_another_brand(self):
        home = self.home / "custom"
        pack = home / "packs/synthetic"
        safety.native_io_path(pack).mkdir(parents=True)
        safety.native_io_path(pack / "pack.yaml").write_text(
            "name: synthetic\nversion: 1.0.0\nextends: _default\n"
            "design: {profile: selected-brand}\n", encoding="utf-8")
        config = ProfileConfig(SOURCE, self.repo, home, home / "packs", home / "packs/active-pack",
                               context_id="selected-brand", explicit_pack="synthetic")
        profile = load_profile_context(config, create=True)
        with self.assertRaises(FileNotFoundError):
            design.profile_asset(profile, config)
        asset = pack / "profiles/selected-brand.yaml"
        safety.native_io_path(asset.parent).mkdir()
        safety.native_io_path(asset).write_text(
            "profile: {id: selected-brand}\ncolor:\n  ink: '#112233'\n  paper: '#ffffff'\n",
            encoding="utf-8")
        selected, leaves = design.profile_asset(profile, config)
        self.assertEqual(selected["origin"], "pack")
        self.assertEqual(leaves["color.ink"], "#112233")
        spec = deepcopy(self.spec)
        spec["binding"]["profile_ref"] = profile_reference(profile)
        spec["binding"]["profile_asset"] = selected
        spec["palette"]["tokens"] = {"ink": "#112233", "paper": "#ffffff"}
        self.config = config
        self.prepare_input.update(profile=profile_reference(profile), required_policy=required_policy(profile))
        self.load(spec)
        safety.native_io_path(pack / "pack.yaml").write_text(
            "name: synthetic\nversion: 1.0.1\nextends: _default\n"
            "design: {profile: selected-brand}\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.load(spec)

    def test_brief_override_is_explicit_and_project_manifest_constrains_stack(self):
        spec = deepcopy(self.spec)
        spec["palette"]["tokens"]["ink"] = "#223344"
        with self.assertRaises(ValueError):
            self.load(spec)
        spec["binding"]["overrides"] = [{"field": "palette.ink", "reason": "Explicit fixture direction",
                                        "evidence": self.ref("brief with spaces.md")}]
        self.load(spec)
        self.write_json("package.json", {"dependencies": {"vue": "3.5.0"}})
        spec["target_format"] = "app"
        spec["binding"]["project"] = {"existing": True, "stack": "vite-react",
                                      "manifests": [self.ref("package.json")]}
        self.prepare_input["selection"].append("package.json")
        with self.assertRaises(ValueError):
            self.load(spec)
        spec["binding"]["project"]["existing"] = False
        with self.assertRaises(ValueError):
            self.load(spec)
        spec["binding"]["project"]["manifests"] = []
        with self.assertRaises(ValueError):
            self.load(spec)

    def test_dimensions_share_one_vocabulary_and_never_average_mandatory_failure(self):
        dimensions = design.normalize_dimensions(["typography", "motion", "shader",
                                                   "accessibility", "brand", "responsive"])
        self.assertEqual(dimensions, ["typography_hierarchy", "motion_coherence", "shader_perf_budget",
                                      "accessibility_wcag", "brand_conformance", "responsive_fidelity"])
        for invalid in (["motion", "motion_coherence"], ["unknown"], [], [{}]):
            with self.assertRaises(ValueError):
                design.normalize_dimensions(invalid)
        review = {"schema_version": 1, "dimensions": {
            name: {"score": 100, "findings": ["Synthetic advisory"]} for name in dimensions
        }}
        self.assertEqual(design.validate_review(review)["overall_verdict"], "green")
        with self.assertRaises(ValueError):
            design.validate_review(review, [])
        self.write("contrast.txt", b"Synthetic measured fixture ratio: 3.5 normal\n")
        control = {**self.requirement, "status": "pass", "reason": "Synthetic supplied measurement",
                   "evidence": ["contrast.txt"], "observation": {"ratio": 3.5, "text_size": "normal"}}
        expected = self.prepare(["contrast.txt"])
        qa = {"schema_version": 2, "context_digest": content_digest(expected), "controls": [control],
              "evidence": evidence_manifest(self.repo, [control])}
        review_args = {"repo": self.repo, "expected": expected, "qa": qa,
                       "design_path": "run with spaces/frontend-design-spec.json",
                       "profile_config": self.config}
        self.assertTrue(design.review_result(review, **review_args)["blocked"])
        for status in ("error", "unverified", "fail"):
            qa["controls"][0]["status"] = status
            self.assertTrue(design.review_result(review, **review_args)["blocked"])
        qa["controls"] = []
        with self.assertRaises(ValueError):
            design.review_result(review, **review_args)

    def test_real_p09_checkpoint_consumes_design_artifact_and_rejects_later_drift(self):
        initial = self.prepare()
        root = ".claude/runtime/state/domains/design/i0001"
        checkpoint = {"id": "design_contract", "receiver": {"role": "FrontendArchitect", "mode": "artifact-only"},
                      "control_ids": ["design-contrast"],
                      "artifacts": ["run with spaces/frontend-design-spec.json"],
                      "start": {"path": root + "/ta/start.json", "expected_state": None},
                      "result": {"path": root + "/ta/result.json", "expected_state": None}}
        request = {"schema_version": 1, "kind": "domain-request", "operation_id": "design",
                   "iteration": 1, "input_context": initial, "domains": [{"id": "ta", "checkpoints": [checkpoint]}],
                   "advisory_preferences": {}, "release_clearance": False}
        domain_result.validate_request(request)
        self.write_json("domain-request.json", request)
        common = {"schema_version": 1, "request": self.ref("domain-request.json"), "domain": "ta",
                  "checkpoint": "design_contract", "receiver": checkpoint["receiver"],
                  "producer": initial["builder"], "provenance": "declared", "release_clearance": False}
        domain_result.record_checkpoint(self.repo, "domain-request.json",
                                        {**common, "kind": "domain-checkpoint"},
                                        output=checkpoint["start"]["path"], expected_file_state=None)
        self.write("measurement.txt", b"Synthetic ratio 16.8; not a rendered-font observation.\n")
        control = {**self.requirement, "status": "pass", "reason": "Synthetic data-contract fixture",
                   "evidence": ["measurement.txt"], "observation": {"ratio": 16.8, "text_size": "normal"}}
        result = {**common, "kind": "domain-result", "start": self.ref(checkpoint["start"]["path"]),
                  "status": "pass", "reason": "Design data only", "controls": [control],
                  "evidence": evidence_manifest(self.repo, [control]),
                  "artifacts": [self.ref("run with spaces/frontend-design-spec.json")],
                  "decisions": [{"requirement": "A14.1", "rationale": "Reuse one contract",
                                "artifact": "run with spaces/frontend-design-spec.json"}],
                  "limitations": ["No rendered artifact or independent review."],
                  "next": {"owner": "coordinator", "action": "Arrange independent review."}}
        domain_result.record_checkpoint(self.repo, "domain-request.json", result,
                                        output=checkpoint["result"]["path"], expected_file_state=None)
        expected = self.prepare(["domain-request.json", root, "measurement.txt"])
        observed = domain_result.verify_result(self.repo, "domain-request.json",
                                                expected=expected, profile_config=self.config)
        self.assertTrue(observed["ok"], observed)
        self.assertFalse(observed["release_clearance"])
        self.assertEqual(observed["review"], "not_evaluated")
        self.assertFalse(verify_qa(self.repo, observed["qa"], expected=expected)["blocked"])
        self.write("run with spaces/frontend-design-spec.json", b"{}\n")
        self.assertFalse(domain_result.verify_result(self.repo, "domain-request.json",
                                                    expected=expected, profile_config=self.config)["ok"])

    # ---- reusable patterns: the spec section 9 precedence join (ADR-0038, R12, RN-15)
    SPEC_PATH = "run with spaces/frontend-design-spec.json"
    LOCK = "run with spaces/patterns.lock.json"
    CONTEXT = "run with spaces/pattern-context.json"

    def publish_patterns(self, directory, source_id, patterns, bindings=(), revocations=None):
        entries = []
        for item in patterns:
            relative = f"{item['id']}/{item['version']}/pattern.json"
            target = safety.native_io_path(Path(directory) / relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(encoded(item))
            entries.append({"id": item["id"], "version": item["version"], "path": relative,
                            "sha256": pat.content_digest(item), "summary": item["summary"],
                            "status": item["status"], "applies_to": item["applies_to"]})
        catalog = {"schema_version": 1, "source_id": source_id, "entries": entries, "includes": [],
                   "bindings": list(bindings), "lifecycle": []}
        if revocations is not None:
            catalog["revocations"] = list(revocations)
        safety.native_io_path(Path(directory) / "catalog.json").write_bytes(encoded(catalog))
        return catalog

    def repository_pattern(self, **kwargs):
        pattern = brand_pattern(**kwargs)
        self.publish_patterns(self.repo / ".claude/patterns", "repo.main", [pattern])
        self.write_json(".claude/patterns/bindings.json", {"schema_version": 1, "bindings": [
            pattern_binding("brand", [pattern_ref("repo.main", pattern)])]})
        return pattern

    def pattern_roots(self):
        return pat.parse_roots(pat.build_envelope(self.repo, self.config.home,
                                                  pat.pack_context_from_profile(self.profile)))

    def pattern_lock(self, overrides=None, lock=None):
        """Resolve with the real core and write the lock where the direct-entry rule puts it."""
        context = {"schema_version": 1, "facts": {"artifact": "website"}, "evidence": {"artifact": "brief with spaces.md"}}
        self.write_json(self.CONTEXT, context)
        parsed = pat.parse_context(context)
        report = pat.resolve(self.pattern_roots(), parsed,
                             overrides=pat.parse_overrides(overrides) if overrides else ())
        self.assertEqual(report["status"], "ready", report["diagnostics"])
        built = pat.build_lock(report, parsed)
        pat.write_lock(self.pattern_roots(), self.repo / (lock or self.LOCK), built)
        return built

    def load_patterned(self, spec, *, lock=LOCK, context=CONTEXT, extra=(), path=None):
        target = path or self.SPEC_PATH
        self.write_json(target, spec)
        selection = [".claude/patterns"] if safety.native_io_path(self.repo / ".claude/patterns").exists() else []
        kwargs = {} if lock is None else {"pattern_lock": lock, "pattern_context": context}
        return design.load_design(self.repo, target, expected=self.prepare([*selection, *extra]),
                                  profile_config=self.config, **kwargs)

    def profiles_digest(self):
        root = safety.native_io_path(SOURCE / "skills/design-dna/profiles")
        return {item.name: hashlib.sha256(item.read_bytes()).hexdigest() for item in sorted(root.rglob("*"))
                if item.is_file()}

    def test_verified_repository_pattern_default_outranks_the_pinned_profile_palette(self):
        before = self.profiles_digest()
        self.assertEqual(self.leaves["color.ink"].lower(), "#141413")
        self.repository_pattern()
        lock = self.pattern_lock()
        spec = pv.project_visual(self.spec, lock)["spec"]
        self.assertEqual(spec["palette"]["tokens"]["ink"], "#112233")
        loaded = self.load_patterned(spec)
        self.assertEqual(loaded["design"]["palette"]["tokens"]["ink"], "#112233")
        self.assertEqual(loaded["verification"], "current_inputs")
        self.write_json(".claude/runtime/expected.json", self.prepare([".claude/patterns"]))
        mapped = self.run_process([
            sys.executable, "-B", SOURCE / "skills/design-dna/scripts/design_contract.py",
            "renderer-args", "--repo", self.repo, "--file", self.SPEC_PATH,
            "--expected", ".claude/runtime/expected.json", "--out", "out with spaces",
            "--profile-home", self.config.home, "--profile-packs", self.config.packs,
            "--profile-pointer", self.config.pointer,
            "--pattern-lock", self.LOCK, "--pattern-context", self.CONTEXT,
        ])
        self.assertEqual(mapped.returncode, 0, mapped.stdout)
        self.assertEqual(self.profiles_digest(), before, "profile files are never modified")
        self.assertEqual(design.profile_asset(self.profile, self.config)[1]["color.ink"].lower(), "#141413")

    def test_verified_pack_pattern_default_outranks_the_pinned_profile_palette(self):
        packs = Path(self.env["LINTEL_PACKS_DIR"])
        team = packs / "team"
        safety.native_io_path(team).mkdir(parents=True)
        safety.native_io_path(team / "pack.yaml").write_bytes(
            b"name: team\nversion: 1.0.0\nvoice: {default_tier: internal}\ncompliance: {mode: advisory}\n"
            b"navigation: {default_workflow: cycle}\npatterns: {source: patterns/catalog.json}\n")
        safety.native_io_path(packs / "active-pack").write_bytes(b"team\n")
        pattern = brand_pattern()
        self.publish_patterns(team / "patterns", "team.patterns", [pattern], bindings=[
            pattern_binding("team-brand", [pattern_ref("team.patterns", pattern)], role="default")])
        self.config = ProfileConfig(SOURCE, self.repo, self.home / "lintel", packs, packs / "active-pack",
                                    context_id="synthetic-pack")
        self.profile = load_profile_context(self.config, create=True)
        self.assertEqual(pat.pack_context_from_profile(self.profile)["identity"]["name"], "team")
        spec = deepcopy(self.spec)
        spec["binding"]["profile_ref"] = profile_reference(self.profile)
        spec["binding"]["profile_asset"] = design.profile_asset(self.profile, self.config)[0]
        self.prepare_input["profile"] = profile_reference(self.profile)
        self.prepare_input["required_policy"] = required_policy(self.profile)
        lock = self.pattern_lock()
        self.assertEqual([item["scope"] for item in lock["selected"]], ["pack"])
        projected = pv.project_visual(spec, lock)["spec"]
        self.assertEqual(self.load_patterned(projected)["design"]["palette"]["tokens"]["ink"], "#112233")
        self.assertFalse(safety.native_io_path(self.repo / ".claude/patterns").exists())
        with self.assertRaisesRegex(ValueError, "pattern_context", msg="pack projection without its lock"):
            self.load_patterned(projected, lock=None)
        self.publish_patterns(team / "patterns", "team.patterns", [brand_pattern(value="#998877")], bindings=[
            pattern_binding("team-brand", [pattern_ref("team.patterns", brand_pattern(value="#998877"))],
                            role="default")])
        self.write_json(self.SPEC_PATH, projected)
        expected = self.prepare()
        verify_context(self.repo, expected)
        self.assertEqual(verify_profile_reference(self.prepare_input["profile"], self.config)["digest"],
                         self.prepare_input["profile"]["digest"],
                         "P05 and P07 alone do not see the republished pack pattern")
        with self.assertRaisesRegex(ValueError, CHANGED_PIN, msg="the loader re-verifies the pack pin"):
            design.load_design(self.repo, self.SPEC_PATH, expected=expected, profile_config=self.config,
                               pattern_lock=self.LOCK, pattern_context=self.CONTEXT)

    def test_without_a_verified_selection_the_profile_palette_still_needs_a_brief_override(self):
        self.repository_pattern()
        lock = self.pattern_lock()
        projected = pv.project_visual(self.spec, lock)["spec"]
        with self.assertRaisesRegex(ValueError, "pattern_context"):
            self.load_patterned(projected, lock=None)
        bare = deepcopy(self.spec)
        bare["palette"]["tokens"]["ink"] = "#112233"
        with self.assertRaisesRegex(ValueError, "without a brief override"):
            self.load_patterned(bare, lock=None)
        bare["binding"]["overrides"] = [{"field": "palette.ink", "reason": "Explicit brief direction",
                                         "evidence": self.ref("brief with spaces.md")}]
        self.assertEqual(self.load_patterned(bare, lock=None)["design"]["palette"]["tokens"]["ink"], "#112233")

    def test_forged_contexts_projections_and_winners_never_authorize_the_palette(self):
        self.repository_pattern()
        lock = self.pattern_lock()
        projected = pv.project_visual(self.spec, lock)["spec"]
        claimed = deepcopy(projected)
        claimed["palette"]["tokens"]["ink"] = "#445566"
        with self.assertRaisesRegex(ValueError, "differs from the verified pattern selection: visual.palette.ink",
                                    msg="a caller-claimed winner differs from the verified lock"):
            self.load_patterned(claimed)
        forged = deepcopy(projected)
        forged["pattern_context"]["selection_digest"] = "f" * 64
        with self.assertRaisesRegex(ValueError, "pattern_context does not match the verified pattern lock",
                                    msg="a forged pattern_context digest"):
            self.load_patterned(forged)
        edited = deepcopy(lock)
        edited["settings"]["visual.palette.ink"]["value"] = "#445566"
        self.write_json(self.LOCK, edited)
        with self.assertRaisesRegex(ValueError, r"Pattern selection is unusable \(invalid\): \w+",
                                    msg="an edited lock"):
            self.load_patterned(claimed)
        self.write_json("locks/forged.lock.json", lock)
        with self.assertRaisesRegex(ValueError, "not bound", msg="a lock outside the P05 selection"):
            self.load_patterned(projected, lock="locks/forged.lock.json")
        for foreign in ("../outside.lock.json", str(self.base / "outside.lock.json")):
            with self.subTest(foreign=foreign), self.assertRaisesRegex(
                    ValueError, FOREIGN_PATH, msg="a caller-selected foreign lock path"):
                self.load_patterned(projected, lock=foreign)
        with self.assertRaisesRegex(ValueError, "supplied together"):
            self.load_patterned(projected, context=None)

    def test_stale_revoked_missing_or_conflicting_selections_block_before_output(self):
        pattern = self.repository_pattern()
        lock = self.pattern_lock()
        projected = pv.project_visual(self.spec, lock)["spec"]
        self.assertEqual(self.load_patterned(projected)["design"]["palette"]["tokens"]["ink"], "#112233")
        self.write_json(self.CONTEXT, {"schema_version": 1, "facts": {"artifact": "report"},
                                       "evidence": {"artifact": "brief with spaces.md"}})
        with self.assertRaisesRegex(ValueError, "context_changed"):
            self.load_patterned(projected)
        self.pattern_lock_path_reset(pattern)
        with self.assertRaisesRegex(ValueError, r"not current \(unavailable\): .*pinned_revoked", msg="revoked pin"):
            self.load_patterned(projected)
        self.publish_patterns(self.repo / ".claude/patterns", "repo.main", [brand_pattern(value="#998877")])
        with self.assertRaisesRegex(ValueError, CHANGED_PIN, msg="changed pinned source"):
            self.load_patterned(projected)
        safety.native_io_path(self.repo / self.LOCK).unlink()
        with self.assertRaisesRegex(ValueError, "unreadable", msg="missing lock"):
            self.load_patterned(projected)
        self.assertFalse(safety.native_io_path(self.repo / "out with spaces").exists())

    def pattern_lock_path_reset(self, pattern):
        """Restore the current context, then revoke the pinned version in its catalog."""
        self.write_json(self.CONTEXT, {"schema_version": 1, "facts": {"artifact": "website"},
                                       "evidence": {"artifact": "brief with spaces.md"}})
        self.publish_patterns(self.repo / ".claude/patterns", "repo.main", [pattern], revocations=[{
            "id": pattern["id"], "version": pattern["version"], "sha256": pat.content_digest(pattern),
            "reason": "Synthetic revocation", "reference": "decision-2", "at": PATTERN_TS}])

    def test_brief_beats_a_pattern_default_but_never_a_mandatory_clause(self):
        self.repository_pattern()
        override = {"schema_version": 1, "items": [{
            "setting": "visual.palette.ink", "value": "#aabbcc", "reason": "brief",
            "approval_ref": "brief with spaces.md", "replaces": ["example.brand@1.0.0#INK"]}]}
        lock = self.pattern_lock(overrides=override)
        self.assertEqual(lock["settings"]["visual.palette.ink"]["value"].lower(), "#aabbcc")
        spec = pv.project_visual(self.spec, lock)["spec"]
        spec["binding"]["overrides"] = [{"field": "palette.ink", "reason": "Explicit brief direction",
                                         "evidence": self.ref("brief with spaces.md")}]
        self.assertEqual(self.load_patterned(spec)["design"]["palette"]["tokens"]["ink"], "#aabbcc")
        safety.native_io_path(self.repo / self.LOCK).unlink()
        self.repository_pattern(level="must")
        context = pat.parse_context({"schema_version": 1, "facts": {"artifact": "website"},
                                     "evidence": {"artifact": "brief with spaces.md"}})
        refused = pat.resolve(self.pattern_roots(), context, overrides=pat.parse_overrides(override))
        self.assertEqual(refused["status"], "conflict", "a brief override never bypasses a must clause")
        must = self.pattern_lock()
        briefed = pv.project_visual(self.spec, must)["spec"]
        briefed["palette"]["tokens"]["ink"] = "#aabbcc"
        briefed["binding"]["overrides"] = spec["binding"]["overrides"]
        with self.assertRaisesRegex(ValueError, "differs from the verified pattern selection: visual.palette.ink",
                                    msg="the brief colour contradicts the mandatory winner"):
            self.load_patterned(briefed)

    def test_pattern_inputs_must_be_current_in_the_p05_selection(self):
        self.repository_pattern()
        lock = self.pattern_lock()
        projected = pv.project_visual(self.spec, lock)["spec"]
        self.write_json(self.SPEC_PATH, projected)
        expected = self.prepare()
        with self.assertRaisesRegex(ValueError, "not bound", msg="repository pattern sources are unselected"):
            design.load_design(self.repo, self.SPEC_PATH, expected=expected, profile_config=self.config,
                               pattern_lock=self.LOCK, pattern_context=self.CONTEXT)
        expected = self.prepare([".claude/patterns"])
        self.write_json(".claude/patterns/bindings.json", {"schema_version": 1, "bindings": []})
        with self.assertRaisesRegex(ValueError, "not bound|content changed",
                                    msg="a pattern source changed after selection"):
            design.load_design(self.repo, self.SPEC_PATH, expected=expected, profile_config=self.config,
                               pattern_lock=self.LOCK, pattern_context=self.CONTEXT)

    def test_no_pattern_and_pipeline_routes_through_the_real_loader(self):
        pattern = brand_pattern()
        self.publish_patterns(self.repo / ".claude/patterns", "repo.main", [pattern])
        self.write_json(".claude/patterns/bindings.json", {"schema_version": 1, "bindings": [
            dict(pattern_binding("brand", [pattern_ref("repo.main", pattern)]), when={"artifact": ["service"]})]})
        context = pat.parse_context({"schema_version": 1, "facts": {"artifact": "website"},
                                     "evidence": {"artifact": "brief with spaces.md"}})
        empty = pat.resolve(self.pattern_roots(), context)
        self.assertEqual((empty["status"], empty["selected"]), ("empty", []))
        unchanged = pv.project_visual(self.spec, empty, context=context)["spec"]
        self.assertEqual(unchanged, self.spec)
        self.assertEqual(self.load_patterned(unchanged, lock=None)["design"]["palette"]["tokens"]["ink"], "#141413")
        self.repository_pattern()
        lock = self.pattern_lock()
        web = pv.project_visual(self.spec, lock)["spec"]
        binding = web.pop("binding")
        del web["source"], web["pattern_context"]
        self.write("run with spaces/content.md", b"Selected pipeline content.\n")
        binding["brief"] = self.ref("run with spaces/content.md")
        pipeline = {"version": "1.0", "schema_version": 1, "source": "pipeline",
                    "palette": {"text_dark": "#112233", "background": "#faf9f5"},
                    "fonts": {"heading": "Poppins", "body": "Lora"}, "per_format": {"web": {"sections": []}},
                    "web_design": web, "binding": binding,
                    "pattern_context": pv.design_attachment(lock, "patterns.lock.json")}
        path = "run with spaces/design-spec.json"
        loaded = self.load_patterned(pipeline, path=path)
        self.assertEqual(loaded["design"]["palette"]["tokens"]["ink"], "#112233")
        with self.assertRaisesRegex(ValueError, "pattern_context", msg="pipeline attachment without its lock"):
            self.load_patterned(pipeline, lock=None, path=path)
        drifted = deepcopy(pipeline)
        drifted["web_design"]["palette"]["tokens"]["ink"] = "#445566"
        drifted["palette"]["text_dark"] = "#445566"
        with self.assertRaisesRegex(ValueError, "verified pattern selection"):
            self.load_patterned(drifted, path=path)

    # ---- D1/A6 (owner decision (a), RN-16): the compound consumer re-verifies at use
    def use_pack(self, value="#112233"):
        packs = Path(self.env["LINTEL_PACKS_DIR"])
        team = packs / "team"
        if not safety.native_io_path(team / "pack.yaml").exists():
            safety.native_io_path(team).mkdir(parents=True)
            safety.native_io_path(team / "pack.yaml").write_bytes(
                b"name: team\nversion: 1.0.0\nvoice: {default_tier: internal}\ncompliance: {mode: advisory}\n"
                b"navigation: {default_workflow: cycle}\npatterns: {source: patterns/catalog.json}\n")
            safety.native_io_path(packs / "active-pack").write_bytes(b"team\n")
            self.config = ProfileConfig(SOURCE, self.repo, self.home / "lintel", packs, packs / "active-pack",
                                        context_id="synthetic-pack")
            self.profile = load_profile_context(self.config, create=True)
            self.spec["binding"]["profile_ref"] = profile_reference(self.profile)
            self.spec["binding"]["profile_asset"] = design.profile_asset(self.profile, self.config)[0]
            self.prepare_input["profile"] = profile_reference(self.profile)
            self.prepare_input["required_policy"] = required_policy(self.profile)
        pattern = brand_pattern(value=value)
        self.publish_patterns(team / "patterns", "team.patterns", [pattern], bindings=[
            pattern_binding("team-brand", [pattern_ref("team.patterns", pattern)], role="default")])
        return team / "patterns"

    def use_personal(self, value="#112233"):
        pattern = brand_pattern(value=value)
        self.publish_patterns(self.config.home / "patterns", "personal.me", [pattern])
        return [{"ref": pattern_ref("personal.me", brand_pattern()), "role": "default",
                 "approved_by": "operator", "approval_ref": "brief with spaces.md"}]

    def compound_inputs(self, refs=None):
        """A genuine positive selected lock, a bound spec and a bound passing QA record."""
        context = {"schema_version": 1, "facts": {"artifact": "website"}, "evidence": {"artifact": "brief with spaces.md"}}
        self.write_json(self.CONTEXT, context)
        parsed = pat.parse_context(context)
        invocation = pat.parse_refs(refs) if refs else ()
        report = pat.resolve(self.pattern_roots(), parsed, refs=invocation)
        self.assertEqual(report["status"], "ready", report["diagnostics"])
        pat.write_lock(self.pattern_roots(), self.repo / self.LOCK, pat.build_lock(report, parsed, refs=invocation))
        lock = json.loads(safety.native_io_path(self.repo / self.LOCK).read_text(encoding="utf-8"))
        self.write_json(self.SPEC_PATH, pv.project_visual(self.spec, lock)["spec"])
        self.write("contrast.txt", b"Synthetic measured fixture ratio: 16.8 normal\n")
        expected = self.prepare(["contrast.txt"])
        control = {**self.requirement, "status": "pass", "reason": "Synthetic supplied measurement",
                   "evidence": ["contrast.txt"], "observation": {"ratio": 16.8, "text_size": "normal"}}
        qa = {"schema_version": 2, "context_digest": content_digest(expected), "controls": [control],
              "evidence": evidence_manifest(self.repo, [control])}
        review = {"schema_version": 1, "dimensions": {
            name: {"score": 100, "findings": ["Synthetic advisory"]}
            for name in design.normalize_dimensions(["typography", "accessibility"])}}
        return expected, qa, review

    def compound(self, expected, qa, review):
        """The design review consumer: live verify_lock, then the P05/P07 and QA gates."""
        return design.review_result(review, repo=self.repo, expected=expected, qa=qa,
                                    design_path=self.SPEC_PATH, profile_config=self.config,
                                    dimensions=["typography", "accessibility"],
                                    pattern_lock=self.LOCK, pattern_context=self.CONTEXT)

    def assert_external_drift_revokes_old_clearance(self, source, republish, restore):
        expected, qa, review = self.compound_inputs(**source)
        repo_files = {path: safety.read_owned(self.repo, path)[1]["sha256"]
                      for path in (self.LOCK, self.CONTEXT, self.SPEC_PATH, "contrast.txt")}
        first = self.compound(expected, qa, review)
        self.assertFalse(first["blocked"], first["controls"])
        self.assertFalse(first["release_clearance"])
        republish()
        verify_context(self.repo, expected)
        self.assertFalse(verify_qa(self.repo, qa, expected=expected)["blocked"],
                         "P05 and QA alone are repository-only and still accept")
        with self.assertRaisesRegex(ValueError, CHANGED_PIN, msg="the same consumer refuses the old clearance"):
            self.compound(expected, qa, review)
        self.assertEqual({path: safety.read_owned(self.repo, path)[1]["sha256"] for path in repo_files}, repo_files,
                         "no repository lock or P05 file was touched")
        restore()
        again = self.compound(expected, qa, review)
        self.assertFalse(again["blocked"], "unchanged external content stays admissible")

    def test_compound_consumer_refuses_old_clearance_after_pack_drift(self):
        self.use_pack()
        self.assert_external_drift_revokes_old_clearance(
            {}, lambda: self.use_pack(value="#998877"), lambda: self.use_pack())

    def test_compound_consumer_refuses_old_clearance_after_personal_drift(self):
        refs = self.use_personal()
        self.assert_external_drift_revokes_old_clearance(
            {"refs": refs}, lambda: self.use_personal(value="#998877"), lambda: self.use_personal())

    def test_review_cli_forwards_the_pattern_selection(self):
        self.use_pack()
        self.write_json("design-review.json", {"schema_version": 1, "dimensions": {
            name: {"score": 100, "findings": ["Synthetic advisory"]}
            for name in design.normalize_dimensions(["typography", "accessibility"])}})
        self.prepare_input["selection"].append("design-review.json")
        expected, qa, _ = self.compound_inputs()
        self.write_json(".claude/runtime/expected.json", expected)
        self.write_json(".claude/runtime/qa.json", qa)
        cli = [sys.executable, "-B", SOURCE / "skills/design-dna/scripts/design_contract.py", "review",
               "--repo", self.repo, "--file", "design-review.json",
               "--expected", ".claude/runtime/expected.json", "--qa", ".claude/runtime/qa.json",
               "--design", self.SPEC_PATH, "--dimensions", "typography,accessibility",
               "--profile-home", self.config.home, "--profile-packs", self.config.packs,
               "--profile-pointer", self.config.pointer]
        flags = ["--pattern-lock", self.LOCK, "--pattern-context", self.CONTEXT]
        accepted = self.run_process([*cli, *flags], separate_stderr=True)
        self.assertEqual(accepted.returncode, 0, accepted.stderr)
        self.assertFalse(json.loads(accepted.stdout)["blocked"])
        omitted = self.run_process(cli, separate_stderr=True)
        self.assertEqual(omitted.returncode, 2)
        self.assertIn("pattern_context", omitted.stderr)
        self.assertEqual(self.run_process([*cli, flags[0], flags[1]], separate_stderr=True).returncode, 2)
        self.use_pack(value="#998877")
        drifted = self.run_process([*cli, *flags], separate_stderr=True)
        self.assertEqual(drifted.returncode, 2)
        self.assertRegex(drifted.stderr, CHANGED_PIN)
        self.assertFalse(drifted.stdout.strip(), "no review result is emitted for a stale selection")

    def test_cli_rejects_duplicates_unknown_options_and_unknown_versions(self):
        cli = [sys.executable, "-B", SOURCE / "skills/design-dna/scripts/design_contract.py",
               "validate", "--repo", self.repo, "--file", "run with spaces/frontend-design-spec.json"]
        good = self.run_process(cli)
        self.assertEqual(good.returncode, 0, good.stdout)
        for extra in (["--file", "elsewhere.json"], ["--unknown"], ["--kind", "unknown"]):
            result = self.run_process([*cli, *extra])
            self.assertNotEqual(result.returncode, 0)
        for version in (2, True, "1"):
            invalid = deepcopy(self.spec)
            invalid["schema_version"] = version
            with self.assertRaises(ValueError):
                design.validate_spec(invalid)
        self.write("run with spaces/frontend-design-spec.json", b'{"schema_version":1,"schema_version":2}')
        self.assertNotEqual(self.run_process(cli).returncode, 0)
        for mutate in (
            lambda value: value["binding"]["provenance"][0].update(version="latest"),
            lambda value: value["binding"]["provenance"][0].update(evidence=[]),
            lambda value: value["binding"].update(retrieval=[]),
            lambda value: value["binding"]["project"].update(stack="unknown"),
        ):
            value = deepcopy(self.spec)
            mutate(value)
            with self.assertRaises(ValueError):
                design.validate_spec(value)


suite = unittest.defaultTestLoader.loadTestsFromTestCase(DesignContract)
result = unittest.TextTestRunner(verbosity=2).run(suite)
assert SEALS == seals(), "Executing source changed"
summary = {"tests": result.testsRun, "failures": len(result.failures), "errors": len(result.errors),
           "skipped": len(result.skipped), "browser": "not_run", "rendered_artifacts": "not_run",
           "source_seals_unchanged": True, "run": str(RUN), "python": sys.version,
           "git_executable": args.git,
           "source_revision": subprocess.run(
               [args.git, "--no-pager", "rev-parse", "HEAD"], cwd=SOURCE,
               capture_output=True, check=True, text=True,
               # After patch.dict restores os.environ, an inherited child environment on Windows can
               # drop entries whose value is empty (for example GIT_CONFIG_VALUE_n=''), which breaks
               # Git's counted config. Passing the mapping explicitly preserves every entry.
               env=os.environ,
           ).stdout.strip()}
safety.native_io_path(RUN / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print(json.dumps(summary, indent=2))
sys.exit(0 if result.wasSuccessful() else 1)
