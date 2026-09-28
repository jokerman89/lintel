#!/usr/bin/env python3
# component: reusable-patterns-launcher-roots-test
# implements: ADR-0038, ADR-0005
# intent: .claude/plans/reusable-patterns/plan.md
# constraints: synthetic temporary roots only; exercises the real bin/li-pattern launcher
# last_intent_review: 2026-09-28
"""Cards 2.1.a, 2.1.c, 2.1.d: launcher roots, explicit non-Git repositories and neutral no-op use."""
from __future__ import annotations

import json
import os
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pattern_pack_harness import Harness, codes, make_pattern, tree_digest  # noqa: E402


def native(path: Path) -> str:
    return path.resolve().as_posix()


class RootTests(unittest.TestCase):
    def roots(self, h, *prefix, cwd=None, **env):
        code, envelope, err = h.launch(*prefix, "roots", cwd=cwd, **env)
        self.assertEqual(code, 0, err)
        return envelope

    def assert_contained(self, h, envelope):
        text = json.dumps(envelope)
        for value in (envelope["repository"], envelope["personal"]):
            if value is not None:
                self.assertTrue(value.startswith(native(h.root)), value)
        self.assertNotIn(native(h.source) + '"', text, "the source bundle is never a pattern root")

    def test_git_top_level_from_a_subdirectory_with_awkward_paths(self):
        h = Harness(self)
        nested = h.repo / "deep dir" / "it's"
        nested.mkdir(parents=True)
        envelope = self.roots(h, cwd=nested)
        self.assertEqual((envelope["repository"], envelope["personal"]), (native(h.repo), native(h.home)))
        self.assertEqual(envelope["pack_context"]["status"], "neutral")
        self.assert_contained(h, envelope)

    def test_outside_git_there_is_no_repository_and_personal_work_still_runs(self):
        h = Harness(self, git=False)
        outside = h.root / "not a repo"
        outside.mkdir()
        for cwd in (outside, h.source):
            envelope = self.roots(h, cwd=cwd)
            self.assertIsNone(envelope["repository"], f"no fallback repository from {cwd}")
            self.assert_contained(h, envelope)
        draft = h.write_input("draft.json", make_pattern("example.mine", version="0.1.0", status="draft"))
        code, report, err = h.launch("capture", "--input", draft, "--scope", "personal", "--name", "example.mine",
                                     "--source-id", "me.personal", cwd=outside)
        self.assertEqual(code, 0, err)
        self.assertTrue((h.home / "patterns" / "catalog.json").is_file())
        code, listed, _ = h.launch("list", cwd=outside)
        self.assertEqual([(item["id"], item["scope"]) for item in listed["entries"]], [("example.mine", "personal")])
        code, shown, _ = h.launch("show", "--ref", "me.personal:example.mine@0.1.0", cwd=outside)
        self.assertEqual((code, shown["pattern"]["id"]), (0, "example.mine"))
        second = h.write_input("second.json", make_pattern("example.repo", version="0.1.0", status="draft"))
        before = tree_digest(h.root)
        code, report, _ = h.launch("capture", "--input", second, "--scope", "repo", "--name", "example.repo",
                                   "--source-id", "team.repo", cwd=outside)
        self.assertNotEqual(code, 0, "the core decides invalid vs unavailable; it is never success")
        self.assertIn("repository_required", codes(report, "error"))
        self.assertEqual(tree_digest(h.root), before, "a refused repository write leaves nothing behind")

    def test_explicit_repository_outside_git(self):
        h = Harness(self, git=False)
        outside = h.root / "elsewhere"
        outside.mkdir()
        for prefix, env in ((("--repo", h.repo), {}), ((f"--repo={h.repo}",), {}),
                            ((), {"LINTEL_REPO_ROOT": str(h.repo)})):
            envelope = self.roots(h, *prefix, cwd=outside, **env)
            self.assertEqual(envelope["repository"], native(h.repo), (prefix, env))
        draft = h.write_input("draft.json", make_pattern("example.repo", version="0.1.0", status="draft"))
        code, _, err = h.launch("--repo", h.repo, "capture", "--input", draft, "--scope", "repo",
                                "--name", "example.repo", "--source-id", "team.repo", cwd=outside)
        self.assertEqual(code, 0, err)
        self.assertTrue((h.repo_patterns / "catalog.json").is_file())
        self.assertFalse((outside / ".claude").exists())

    def test_invalid_invocations_refuse_before_any_work(self):
        h = Harness(self)
        context = h.context()
        before = tree_digest(h.root)
        cases = [
            (("--repo", h.root / "missing", "list"), {}),
            (("--repo", "", "list"), {}),
            (("--repo", h.repo, "envelope", "--personal", h.home, "--profile-error", "X"), {}),
            (("resolve", "--context", "-"), {}),
            (("resolve", "--context=-"), {}),
            ((), {}),
            (("list",), {"LINTEL_HOME": "relative/home"}),
        ]
        for args, env in cases:
            code, _, err = h.launch(*args, **env)
            self.assertEqual(code, 2, (args, err))
            self.assertIn("[lintel/pattern]", err)
        self.assertEqual(tree_digest(h.root), before)
        self.assertTrue(context.is_file())

    def test_passthrough_commands_take_no_derived_roots(self):
        h = Harness(self)
        pattern = h.write_input("pattern.json", make_pattern("example.checked"))
        code, report, err = h.launch("check", "--path", pattern)
        self.assertEqual((code, report["kind"]), (0, "pattern"), err)
        code, envelope, _ = h.launch("envelope", "--personal", native(h.home), "--profile-error", "PROFILE_REQUIRED",
                                     "--profile-error-message", "it's \"quoted\" $x")
        self.assertEqual(code, 0)
        self.assertEqual(envelope["pack_context"]["diagnostics"],
                         [{"code": "PROFILE_REQUIRED", "message": "it's \"quoted\" $x"}])


class HardeningTests(unittest.TestCase):
    """Review F4-F7: cd hardening, MSYS input paths, the no-repository profile context, run IDs."""

    def test_dash_relative_repository_and_exported_cdpath(self):
        h = Harness(self, git=False)
        dash = h.root / "-dash repo"
        dash.mkdir()
        code, envelope, err = h.launch("--repo", "-dash repo", "roots", cwd=h.root)
        self.assertEqual((code, envelope["repository"]), (0, native(dash)), err)
        decoy = h.root / "cdpath" / "work repo"
        decoy.mkdir(parents=True)
        code, envelope, err = h.launch("--repo", "work repo", "roots", cwd=h.root,
                                       CDPATH=h.posix_spelling(decoy.parent))
        self.assertEqual((code, envelope["repository"]), (0, native(h.repo)), "CDPATH never redirects the root")
        code, _, err = h.launch("--repo", "-dash repo", "roots", cwd=h.inputs)
        self.assertEqual(code, 2)
        self.assertEqual(err.strip().splitlines(), ["[lintel/pattern] repository root is not a directory: -dash repo"])

    def test_posix_spellings_of_awkward_input_paths_reach_the_core(self):
        h = Harness(self)
        context = h.posix_spelling(h.context())
        for args in (("resolve", "--context", context), ("resolve", f"--context={context}"),
                     ("explain", "--context", context, "--refs", h.posix_spelling(h.write_input("refs.json", [])))):
            code, report, err = h.launch(*args)
            self.assertEqual((code, report["status"]), (0, "empty"), (args, err))
        pattern = h.posix_spelling(h.write_input("pattern.json", make_pattern("example.checked")))
        self.assertEqual(h.launch("check", "--path", pattern)[0], 0, "pass-through commands convert too")
        draft = h.posix_spelling(h.write_input("draft.json", make_pattern("example.mine", version="0.1.0",
                                                                        status="draft")))
        code, report, err = h.launch("capture", "--input", draft, "--scope", "personal", "--name", "example.mine",
                                     "--source-id", "me.personal")
        self.assertEqual(code, 0, err)
        # Opaque values stay verbatim in the launcher (MSYS itself skips this spelling).
        opaque = "/c/it's (opaque) & data"
        code, envelope, _ = h.launch("envelope", "--personal", native(h.home), "--profile-error", "E",
                                     "--profile-error-message", opaque)
        self.assertEqual(envelope["pack_context"]["diagnostics"][0]["message"], opaque)

    def test_msys_conversion_is_off_for_opaque_values_but_known_paths_still_convert(self):
        """Review L-P1: plain /c/... spellings are the ones MSYS itself would rewrite."""
        h = Harness(self, root_name="plain roots")
        for opaque in ("/etc/x", "/c/not/a/path"):
            for spelling in (("--profile-error-message", opaque), (f"--profile-error-message={opaque}",)):
                code, envelope, err = h.launch("envelope", "--personal", native(h.home), "--profile-error", "E",
                                               *spelling)
                self.assertEqual((code, envelope["pack_context"]["diagnostics"][0]["message"]), (0, opaque), err)
        draft = h.write_input("draft.json", make_pattern("example.mine", version="0.1.0", status="draft"))
        for spelling in (("--name", "/etc/x"), ("--name=/etc/x",)):
            code, report, err = h.launch("capture", "--input", h.posix_spelling(draft), "--scope", "personal",
                                         *spelling, "--source-id", "me.personal")
            self.assertNotEqual(code, 0, err)
            text = json.dumps(report)
            self.assertIn("/etc/x", text, "the core sees and reports the raw name")
            self.assertNotIn("Program Files", text)
        self.assertFalse((h.home / "patterns").exists(), "a refused name writes nothing")
        context_path = h.context()
        context = h.posix_spelling(context_path)
        if h.shell("command -v cygpath >/dev/null 2>&1")[0] == 0:
            # Any mount alias (including a shared /tmp) is valid if it names this exact file in the
            # launcher's own environment; a forbidden prefix would reject legitimate hosts.
            self.assertTrue(context.startswith("/"), context)
            self.assertNotEqual(context, native(context_path), "a real POSIX spelling, not the native path")
            code, back, err = h.shell('cygpath -m -- "$2"', context)
            self.assertEqual(code, 0, err)
            back = back.rstrip("\n")
            self.assertEqual(os.path.normcase(os.path.normpath(back)),
                             os.path.normcase(os.path.normpath(native(context_path))), (context, back))
            self.assertTrue(os.path.samefile(back, context_path), (context, back))
        for args in (("resolve", "--context", context), ("resolve", f"--context={context}")):
            code, report, err = h.launch(*args)
            self.assertEqual((code, report["status"]), (0, "empty"), (args, err))
        pattern = h.posix_spelling(h.write_input("pattern.json", make_pattern("example.checked")))
        for args in (("check", "--path", pattern), ("check", f"--path={pattern}")):
            self.assertEqual(h.launch(*args)[0], 0, args)
        roots = h.launch("roots")[1]
        roots_file = h.posix_spelling(h.write_input("roots.json", roots))
        for args in (("list", "--roots-file", roots_file), ("list", f"--roots-file={roots_file}")):
            code, listed, err = h.launch(*args)
            self.assertEqual((code, listed["sources"]), (0, []), (args, err))
        assets = h.inputs / "assets"
        assets.mkdir()
        code, report, err = h.launch("capture", "--input", h.posix_spelling(draft), "--scope", "personal",
                                     "--name", "example.mine", "--source-id", "me.personal",
                                     f"--files-from={h.posix_spelling(assets)}")
        self.assertEqual(code, 0, (err, report))
        self.assertTrue((h.home / "patterns" / "catalog.json").is_file())
        script = h.posix_spelling(h.source / "bin" / "li-pattern")
        code, out, err = h.shell('exec bash "$2" roots', script)
        self.assertEqual((code, json.loads(out)["personal"]), (0, native(h.home)), err)

    def test_outside_git_home_is_the_profile_context_not_a_repository(self):
        h = Harness(self, git=False)
        outside = h.root / "outside"
        outside.mkdir()
        h.publish(h.home / ".claude" / "patterns", "home.not-a-repo", [make_pattern("example.hidden")])
        code, listed, _ = h.launch("list", cwd=outside)
        self.assertEqual((code, listed["sources"]), (0, []), "no repository catalog under LINTEL_HOME")
        (h.home / ".claude" / "profile-requirements.json").write_text(
            json.dumps({"schema_version": 1, "required_pack": "missing"}), encoding="utf-8")
        envelope = h.launch("roots", cwd=outside)[1]
        self.assertIsNone(envelope["repository"])
        self.assertEqual((envelope["pack_context"]["status"], envelope["pack_context"]["diagnostics"][0]["code"]),
                         ("error", "PROFILE_REQUIRED"), "the profile working context's declarations apply")
        self.assertEqual(h.launch("list", cwd=outside)[0], 5, "never forced through as personal-only success")


class RunIdTests(unittest.TestCase):
    def test_run_ids_follow_portable_segment_rules_without_echoing_input(self):
        h = Harness(self)
        # The ID travels in the environment: Windows argv transport would split "x\ny".
        body = 'source "$1/lib/paths.sh"; if [ -n "${RUN_ID+set}" ]; then lintel_pattern_runtime_dir "$RUN_ID"; ' \
               'else lintel_pattern_runtime_dir; fi'
        base = f"{h.posix_spelling(h.repo)}/.claude/runtime/patterns"
        for value in ("ok-1.2_x", "a" * 128, "CONSOLE", "com10", "nul_x"):
            code, out, err = h.shell(body, RUN_ID=value)
            self.assertEqual((code, out, err), (0, f"{base}/{value}", ""), value)
        for value in ("", ".", "..", "...", "a..b", ".hidden", "-dash", "a.", "a/b", "a b", "a\\b", "é",
                      "x\ny", "*", "a:b", "a" * 129, "CON", "nul", "Aux.txt", "COM1", "lpt9.log", "prn."):
            code, out, err = h.shell(body, RUN_ID=value)
            self.assertEqual((code, out), (2, ""), repr(value))
            self.assertEqual(len(err.splitlines()), 1, repr(value))
            if len(value) >= 4 or not value.isascii() or "\n" in value:
                self.assertNotIn(value, err, "the refusal never echoes raw input")
        self.assertEqual(h.shell(body)[1], base)
        code, out, _ = h.shell('cd "$2"; unset LINTEL_REPO_ROOT; source "$1/lib/paths.sh"; '
                               'lintel_pattern_runtime_dir x; echo "rc=$?"; lintel_patterns_dir; echo "rc=$?"',
                               h.inputs.as_posix(), repo=h.inputs)
        self.assertEqual(out.split(), ["rc=1", "rc=1"], "outside a repository: no path, never /")


def link_directory(testcase, link: Path, target: Path) -> None:
    """A junction on Windows (no privilege needed), else a symlink; removed as a link only."""
    if os.name == "nt":
        import _winapi
        _winapi.CreateJunction(str(target), str(link))
    else:
        os.symlink(target, link, target_is_directory=True)
    testcase.addCleanup(lambda: os.rmdir(link) if os.name == "nt" else os.unlink(link))


class AnchorTests(unittest.TestCase):
    """R7 F2 through the real launcher: a linked anchor is refused; its real path is the remedy."""

    def test_linked_repository_and_home_are_refused_and_real_paths_work(self):
        h = Harness(self)
        linked_repo = h.root / "linked repo"
        link_directory(self, linked_repo, h.repo)
        code, report, err = h.launch("--repo", linked_repo, "roots", cwd=h.root)
        self.assertEqual(code, 2, err)
        self.assertIn("invalid_roots", codes(report, "error"))
        self.assertIn("real path", err)
        code, envelope, err = h.launch("--repo", h.repo, "roots", cwd=h.root)
        self.assertEqual((code, envelope["repository"]), (0, native(h.repo)), err)
        real_home = h.user / "real lintel"
        real_home.mkdir()
        linked_home = h.user / "linked lintel"
        link_directory(self, linked_home, real_home)
        code, report, err = h.launch("list", LINTEL_HOME=str(linked_home))
        self.assertEqual(code, 2, err)
        self.assertIn("invalid_roots", codes(report, "error"))
        code, envelope, err = h.launch("roots", LINTEL_HOME=str(real_home))
        self.assertEqual((code, envelope["personal"]), (0, native(real_home)), err)

    def test_git_physical_top_level_through_a_linked_working_directory(self):
        h = Harness(self)
        linked_repo = h.root / "linked repo"
        link_directory(self, linked_repo, h.repo)
        code, envelope, err = h.launch("roots", cwd=linked_repo)
        self.assertEqual(code, 0, err)
        self.assertEqual(envelope["repository"], native(h.repo), "Git reports the physical top level")


class NeutralTests(unittest.TestCase):
    def test_unconfigured_roots_create_nothing_and_prompt_nothing(self):
        h = Harness(self)
        context = h.context()
        before = tree_digest(h.root)
        for args in (("roots",), ("list",), ("check",), ("resolve", "--context", context),
                     ("explain", "--context", context)):
            code, report, err = h.launch(*args)
            self.assertEqual((code, err), (0, ""), args)
            if args[0] != "roots":
                self.assertIn(report["status"], ("ok", "empty"), args)
        self.assertEqual(tree_digest(h.root), before, "no home, repository, source or temporary artifact")
        self.assertEqual(list(h.temp.iterdir()), [])
        self.assertFalse((h.home / "patterns").exists())


if __name__ == "__main__":
    unittest.main(verbosity=2)
