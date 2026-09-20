# component: profile-path-identity-tests
# implements: ADR-0029
# intent: docs/concepts/pack-resolver.md
# constraints: synthetic local filesystem fixtures; UNC comparison is data-only, never network I/O
# last_intent_review: 2026-09-20
"""Discriminate Windows namespace spelling from physical runtime containment."""

import argparse
from dataclasses import replace
import json
import ntpath
import os
from pathlib import Path, PureWindowsPath
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


PARSER = argparse.ArgumentParser()
PARSER.add_argument("--root", required=True, type=Path)
OPTIONS, TEST_ARGS = PARSER.parse_known_args()
sys.path.insert(0, str(OPTIONS.root / "lib"))
import profile_context as profile


def extended(path):
    text = str(path)
    return Path("\\\\?\\UNC\\" + text[2:]) if text.startswith("\\\\") else Path("\\\\?\\" + text)


class ProfilePathIdentity(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="lintel-profile-path-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.repo, self.home = self.root / "target", self.root / "home"
        self.repo.mkdir()
        self.home.mkdir()
        self.outside = self.root / "outside"
        self.outside.mkdir()
        self.config = profile.ProfileConfig(
            OPTIONS.root, self.repo, self.home, self.home / "packs",
            self.home / "packs/active-pack", context_id="path-fixture",
        )

    def test_windows_drive_and_unc_comparison_aliases(self):
        for normal, alias in (
            (r"C:\approved\child\file.json", r"\\?\C:\approved\child\file.json"),
            (r"\\server\share\approved\child.json", r"\\?\UNC\server\share\approved\child.json"),
            (r"\\server\share\approved\child.json", r"\\?\unc\server\share\approved\child.json"),
        ):
            with self.subTest(normal=normal, alias=alias):
                normal_path, alias_path = PureWindowsPath(normal), PureWindowsPath(alias)
                before = str(alias_path)
                self.assertEqual(profile._path_identity(normal_path), profile._path_identity(alias_path))
                self.assertEqual(str(alias_path), before, "comparison rewrote the I/O path")
                root = profile._path_identity(normal_path.parent)
                self.assertEqual(profile._path_identity(alias_path)[:len(root)], root)

    def test_windows_comparison_preserves_roots_and_component_boundaries(self):
        for root, outside in (
            (r"C:\approved", r"\\?\D:\approved\file"),
            (r"C:\approved", r"\\?\C:\approved-sibling\file"),
            (r"C:\Approved", r"\\?\C:\approved\file"),
            (r"\\server\share\approved", r"\\?\UNC\other\share\approved\file"),
            (r"\\server\share\approved", r"\\?\UNC\server\other\approved\file"),
            (r"\\server\share\approved", r"\\?\UNC\server\share\approved-sibling\file"),
            (r"\\server\share\Approved", r"\\?\UNC\server\share\approved\file"),
        ):
            with self.subTest(root=root, outside=outside):
                root_identity = profile._path_identity(PureWindowsPath(root))
                self.assertNotEqual(profile._path_identity(PureWindowsPath(outside))[:len(root_identity)],
                                    root_identity)

    def test_windows_device_ambiguous_and_unresolved_paths_are_not_normalized_into_files(self):
        invalid = (
            r"\\.\C:\approved\file", r"\\.\pipe\profile", r"\??\C:\approved\file",
            r"\\?\GLOBALROOT\Device\HarddiskVolume1\approved\file",
            r"\\?\Volume{11111111-1111-1111-1111-111111111111}\file",
            r"\\?\C:relative", r"C:relative", r"\root-relative", r"relative\path",
            r"\\server", r"\\?\UNC\server", r"\\?\UNC\.\share\file",
            r"\\?\C:\approved\..\outside", r"C:\approved\..\outside",
            r"\\?\UNC\server\share\approved\..\outside",
            r"\\?\C:\approved\file:stream", r"C:\approved\trailing.",
            "C:\\approved\\trailing ", r"\\?\C:\approved\NUL", r"C:\approved\COM1.txt",
        )
        for text in invalid:
            with self.subTest(path=text), self.assertRaises(profile.ProfileError) as error:
                profile._path_identity(PureWindowsPath(text))
            self.assertEqual(error.exception.code, "PROFILE_IO")

    def test_ordinary_physical_roots_and_lexical_traversal_remain_bounded(self):
        for path in (self.home / "session.json", self.repo / ".claude/runtime/profiles/selected.json"):
            profile._runtime_path(self.config, path)
        for path in (
            self.outside / "file.json", self.repo / "unapproved.json",
            self.root / "home-sibling/file.json", self.home / ".." / "outside/file.json",
        ):
            with self.subTest(path=str(path)), self.assertRaises(profile.ProfileError):
                profile._write_json(self.config, path, {"synthetic": True})
            self.assertFalse(path.exists())

    @unittest.skipUnless(os.name == "nt", "native extended-length drive I/O requires Windows")
    def test_native_extended_drive_runtime_io_preserves_same_physical_file(self):
        for extended_roots in (False, True):
            config = replace(self.config, repo=extended(self.repo), home=extended(self.home)) \
                if extended_roots else self.config
            for extended_candidate in (False, True):
                for normal in (
                    self.home / "nested/session.json",
                    self.repo / ".claude/runtime/profiles/selected.json",
                ):
                    with self.subTest(path=str(normal), extended_roots=extended_roots,
                                      extended_candidate=extended_candidate):
                        expected = {"fixture": normal.name}
                        before = (str(config.repo), str(config.home), str(normal))
                        profile._write_json(config, extended(normal) if extended_candidate else normal, expected)
                        self.assertEqual(json.loads(normal.read_text(encoding="utf-8")), expected)
                        self.assertEqual(extended(normal).read_bytes(), normal.read_bytes())
                        self.assertEqual((str(config.repo), str(config.home), str(normal)), before)

    @unittest.skipUnless(os.name == "nt", "native extended-length drive resolution requires Windows")
    def test_injected_resolve_alias_only_never_changes_io_or_approved_roots(self):
        selected = self.repo / ".claude/runtime/profiles/selected.json"
        original_resolve = Path.resolve
        before = (str(self.config.repo), str(self.config.home))

        def spelling_only(path, *args, **kwargs):
            resolved = original_resolve(path, *args, **kwargs)
            return extended(resolved) if path == selected else resolved

        for present in (False, True):
            with self.subTest(existing_leaf=present):
                with mock.patch.object(Path, "resolve", spelling_only):
                    profile._write_json(self.config, selected, {"present": present})
                self.assertEqual(json.loads(selected.read_text(encoding="utf-8")), {"present": present})
                self.assertEqual((str(self.config.repo), str(self.config.home)), before)

    @unittest.skipUnless(os.name == "nt", "native extended-length drive resolution requires Windows")
    def test_injected_bootstrap_alias_preserves_reference_provenance_and_record_bytes(self):
        config = replace(self.config, context_id="")
        original_resolve = Path.resolve

        def runtime_spelling_only(path, *args, **kwargs):
            resolved = original_resolve(path, *args, **kwargs)
            if path.name in ("selected.json", "current-profile.json") and not str(resolved).startswith("\\\\?\\"):
                return extended(resolved)
            return resolved

        with mock.patch.object(Path, "resolve", runtime_spelling_only):
            first = profile.bootstrap_profile_context(config)
        reference = profile.profile_reference(first)
        selected_path = profile.context_path(replace(config, context_id=reference["context_id"]))
        before = selected_path.read_bytes()
        ordinary = profile.bootstrap_profile_context(config)
        with mock.patch.object(Path, "resolve", runtime_spelling_only):
            resumed = profile.bootstrap_profile_context(config)
        self.assertEqual(profile.profile_reference(ordinary), reference)
        self.assertEqual(profile.profile_reference(resumed), reference)
        self.assertEqual(resumed["profile"]["provenance"], first["profile"]["provenance"])
        self.assertEqual(resumed["profile"]["inputs"], first["profile"]["inputs"])
        self.assertEqual(selected_path.read_bytes(), before)

    @unittest.skipUnless(os.name == "nt", "native Windows realpath scheduling reproduction")
    def test_native_parent_creation_race_accepts_authorized_extended_result(self):
        triggered, returns = [], []

        def schedule(frame, event, argument):
            if frame.f_code is ntpath.realpath.__code__:
                if (event == "exception" and isinstance(argument[1], OSError)
                        and getattr(argument[1], "winerror", None) == 3
                        and str(frame.f_locals.get("path")) == str(self.config.selected)):
                    self.config.selected.parent.mkdir(parents=True, exist_ok=True)
                    triggered.append(True)
                if event == "return" and triggered and isinstance(argument, str) \
                        and argument.endswith("\\selected.json"):
                    returns.append(argument)
                return schedule
            return None

        previous_trace = sys.gettrace()
        sys.settrace(schedule)
        try:
            profile._runtime_path(self.config, self.config.selected)
        finally:
            sys.settrace(previous_trace)
        self.assertEqual(triggered, [True])
        self.assertTrue(any(value.startswith("\\\\?\\") for value in returns), returns)
        profile._runtime_path(self.config, self.config.selected)
        with self.assertRaises(profile.ProfileError):
            profile._runtime_path(self.config, self.outside / "record.json")
        self.assertFalse((self.outside / "record.json").exists())

    @unittest.skipUnless(os.name == "nt", "native Windows runtime path preflight")
    def test_device_namespaces_and_traversal_are_rejected_before_resolution(self):
        for text in (r"\\.\pipe\profile", r"\\?\GLOBALROOT\Device\Disk\file",
                     str(self.home / ".." / "outside/file.json")):
            with self.subTest(path=text), mock.patch.object(
                Path, "resolve", side_effect=AssertionError("unsafe path reached filesystem resolution"),
            ), self.assertRaises(profile.ProfileError) as error:
                profile._runtime_path(self.config, Path(text))
            self.assertEqual(error.exception.code, "PROFILE_IO")

    @unittest.skipUnless(os.name == "nt", "native Windows physical path casing")
    def test_injected_case_distinct_physical_sibling_is_not_authorized(self):
        config = replace(self.config, home=self.home / "Approved")
        candidate = config.home / "record.json"
        outside_identity = config.home.parent / "approved/record.json"
        with mock.patch.object(Path, "resolve", return_value=outside_identity), \
                self.assertRaises(profile.ProfileError) as error:
            profile._runtime_path(config, candidate)
        self.assertEqual(error.exception.code, "PROFILE_IO")

    @unittest.skipUnless(os.name == "nt", "native case-sensitive Windows directory fixture")
    def test_native_case_sensitive_sibling_root_is_rejected(self):
        case_root = self.root / "case-sensitive"
        case_root.mkdir()
        enabled = subprocess.run(
            ["fsutil.exe", "file", "SetCaseSensitiveInfo", str(case_root), "enable"],
            capture_output=True, text=True, timeout=30,
        )
        if enabled.returncode:
            self.skipTest("fixture-only case sensitivity unavailable: " + enabled.stdout + enabled.stderr)
        approved, outside = case_root / "Approved", case_root / "approved"
        approved.mkdir()
        outside.mkdir()
        self.assertFalse(approved.samefile(outside), "fixture did not create distinct filesystem objects")
        config = replace(self.config, home=approved)
        profile._write_json(config, approved / "inside.json", {"allowed": True})
        for candidate in (outside / "outside.json", extended(outside / "outside.json")):
            with self.subTest(path=str(candidate)), self.assertRaises(profile.ProfileError):
                profile._write_json(config, candidate, {"must_not_write": True})
            self.assertFalse((outside / "outside.json").exists())
        self.assertEqual(json.loads((approved / "inside.json").read_text()), {"allowed": True})

    def test_real_symlink_escape_rejected_and_inside_link_remains_inside(self):
        link = self.home / "outside-link"
        try:
            link.symlink_to(self.outside, target_is_directory=True)
        except OSError as error:
            self.skipTest("native symlinks unavailable: " + str(error))
        self.addCleanup(link.unlink)
        for candidate in (link / "escaped.json", extended(link / "escaped.json")) if os.name == "nt" \
                else (link / "escaped.json",):
            with self.subTest(path=str(candidate)), self.assertRaises(profile.ProfileError):
                profile._write_json(self.config, candidate, {"must_not_write": True})
        self.assertFalse((self.outside / "escaped.json").exists())
        destination = self.home / "inside"
        destination.mkdir()
        inside = self.home / "inside-link"
        inside.symlink_to(destination, target_is_directory=True)
        self.addCleanup(inside.unlink)
        profile._write_json(self.config, inside / "allowed.json", {"inside": True})
        self.assertEqual(json.loads((destination / "allowed.json").read_text()), {"inside": True})
        outside_file = self.outside / "existing.json"
        outside_file.write_text('{"preserved":true}', encoding="utf-8")
        file_link = self.home / "file-link.json"
        file_link.symlink_to(outside_file)
        self.addCleanup(file_link.unlink)
        with self.assertRaises(profile.ProfileError):
            profile._write_json(self.config, file_link, {"must_not_write": True})
        self.assertEqual(outside_file.read_text(encoding="utf-8"), '{"preserved":true}')

    @unittest.skipUnless(os.name == "nt", "native Windows junction case")
    def test_real_junction_escape_and_redirected_runtime_boundary_are_rejected(self):
        for link in (self.home / "junction", self.repo / ".claude/runtime"):
            with self.subTest(link=str(link)):
                link.parent.mkdir(parents=True, exist_ok=True)
                env = dict(os.environ, PROFILE_TEST_LINK=str(link), PROFILE_TEST_DEST=str(self.outside))
                result = subprocess.run(
                    ["powershell", "-NoProfile", "-NonInteractive", "-Command",
                     "$ErrorActionPreference='Stop'; New-Item -ItemType Junction "
                     "-Path $env:PROFILE_TEST_LINK -Target $env:PROFILE_TEST_DEST | Out-Null"],
                    env=env, capture_output=True, text=True, timeout=30,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                try:
                    for candidate in (link / "escaped.json", extended(link / "escaped.json")):
                        with self.subTest(candidate=str(candidate)), self.assertRaises(profile.ProfileError):
                            profile._write_json(self.config, candidate, {"must_not_write": True})
                    self.assertFalse((self.outside / "escaped.json").exists())
                finally:
                    link.rmdir()
                self.assertTrue(self.outside.is_dir())


if __name__ == "__main__":
    unittest.main(argv=[__file__, *TEST_ARGS], verbosity=2)
