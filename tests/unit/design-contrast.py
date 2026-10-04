#!/usr/bin/env python3
# component: design-contrast-tests
# implements: ADR-0015, ADR-0028
# intent: .claude/plans/v2-findings/plan.md (lane-d-06)
# constraints: standard library, inert color data; no browser, model or profile binding
# last_intent_review: 2026-10-03
"""Numerical and refusal regressions against the shipped contrast helper."""
from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[2]
SCRIPTS = ROOT / "skills/design-dna/scripts"
sys.path[:0] = [str(SCRIPTS), str(ROOT / "lib")]
import measure_contrast as contrast
from review_contract import evaluate_controls
import validate_design


class ContrastTests(unittest.TestCase):
    def measure(self, foreground, background, size="normal"):
        return contrast.contrast_observation(foreground, background, text_size=size)

    def cli(self, *args):
        return subprocess.run(
            [sys.executable, "-I", "-B", "-X", "utf8", str(SCRIPTS / "measure_contrast.py"), *args],
            cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False,
        )

    def test_black_white_is_twenty_one_in_both_directions(self):
        for foreground, background in (("#000", "#fff"), ("#FFFFFF", "#000000")):
            with self.subTest(foreground=foreground):
                self.assertEqual(self.measure(foreground, background),
                                 {"ratio": 21.0, "text_size": "normal"})

    def test_identical_colors_are_one(self):
        for color in ("#000", "#fff", "#123456", "rgb(42.5, 42.5, 42.5)"):
            with self.subTest(color=color):
                self.assertEqual(self.measure(color, color, "large"),
                                 {"ratio": 1.0, "text_size": "large"})

    def test_computed_css_rgb_and_opaque_alpha(self):
        for foreground in ("rgb(0, 0, 0)", "rgba(0, 0, 0, 1)", "rgb(0 0 0 / 100%)",
                           "rgb(0% 0% 0%)", "#000f", "#000000ff"):
            with self.subTest(foreground=foreground):
                self.assertEqual(self.measure(foreground, "rgb(255, 255, 255)")["ratio"], 21.0)

    def test_known_srgb_ratio(self):
        self.assertAlmostEqual(self.measure("#777777", "#ffffff")["ratio"],
                               4.478089453577214, places=12)

    def test_normal_and_large_thresholds_without_rounding_to_pass(self):
        for foreground, size, code in (("#767676", "normal", 0), ("#777777", "normal", 1),
                                       ("#777777", "large", 0), ("#949494", "large", 0),
                                       ("#959595", "large", 1), ("#fff", "normal", 1)):
            with self.subTest(foreground=foreground, size=size):
                result = self.cli("--foreground", foreground, "--background", "#fff",
                                  "--text-size", size)
                self.assertEqual(result.returncode, code, result.stderr)
                self.assertEqual(json.loads(result.stdout), self.measure(foreground, "#fff", size))
        normal = self.measure("#777", "#fff")["ratio"]
        large = self.measure("#959595", "#fff", "large")["ratio"]
        self.assertEqual(round(normal, 1), 4.5)
        self.assertLess(normal, 4.5)
        self.assertEqual(round(large, 2), 3.0)
        self.assertLess(large, 3.0)

    def test_missing_invalid_unresolved_or_nonfinite_colors_are_refused(self):
        invalid = (None, "", "white", "transparent", "currentColor", "inherit", "var(--paper)",
                   "#12", "#12345", "#gggggg", "linear-gradient(#000,#fff)", "url(bg.png)",
                   "rgb(256,0,0)", "rgb(-1,0,0)", "rgb(NaN,0,0)", "rgb(Infinity,0,0)",
                   "rgb(1e999,0,0)", "rgb(1e999999999999999999999999999999,0,0)",
                   "rgb(0,0)", "rgb(0 0,0)", "rgb(0 0 0) trailing",
                   "color(display-p3 1 1 1)", float("nan"), float("inf"), float("-inf"),
                   True, False, 10 ** 400, -(10 ** 400), [0, 0, 0])
        for value in invalid:
            with self.subTest(value=value, channel="background"):
                with self.assertRaises(ValueError):
                    self.measure("#000", value)
            with self.subTest(value=value, channel="foreground"):
                with self.assertRaises(ValueError):
                    self.measure(value, "#fff")

    def test_translucency_is_refused_not_composited_or_rounded_to_opaque(self):
        for color in ("#0000", "#000000fe", "rgba(0,0,0,0)", "rgb(0 0 0 / .5)",
                      "rgba(0,0,0,0.9999999999999999999999999)", "rgba(0,0,0,2)"):
            with self.subTest(color=color):
                with self.assertRaises(ValueError):
                    self.measure(color, "#fff")
                with self.assertRaises(ValueError):
                    self.measure("#000", color)

    def test_size_must_be_explicit_and_recognized(self):
        for size in (None, "", "body", "LARGE", 24, True):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    self.measure("#000", "#fff", size)

    def test_browser_element_shape_is_reused_without_mutation(self):
        # Shape from chromium.mjs read(), not a browser execution claim.
        element = {"text": "Synthetic", "tag": "P", "color": "rgb(0, 0, 0)",
                   "background": "rgb(255, 255, 255)", "animation": "none",
                   "display": "block", "box": {"x": 0, "y": 0, "width": 40, "height": 20}}
        before = deepcopy(element)
        measured = contrast.browser_observation(element, text_size="normal", background_image="none")
        self.assertEqual(measured, {"ratio": 21.0, "text_size": "normal"})
        self.assertEqual(element, before)
        self.assertNotIn("executed", measured)
        self.assertNotIn("release_clearance", measured)

    def test_computed_background_color_alone_does_not_resolve_painted_background(self):
        element = {"color": "#000", "background": "#fff"}
        for image in (None, "", "linear-gradient(#000,#fff)", "url(bg.png)", "unknown"):
            with self.subTest(image=image):
                with self.assertRaises(ValueError):
                    contrast.browser_observation(element, text_size="normal", background_image=image)
        for element in ({"color": "#000"}, {"color": "#000", "background": "rgba(0,0,0,0)"}):
            with self.subTest(element=element):
                with self.assertRaises(ValueError):
                    contrast.browser_observation(element, text_size="normal", background_image="none")

    def test_browser_cli_needs_explicit_paint_and_size_observations(self):
        element = json.dumps({"color": "rgb(0,0,0)", "background": "rgb(255,255,255)"})
        good = self.cli("--element-json", element, "--background-image", "none", "--text-size", "large")
        self.assertEqual(good.returncode, 0, good.stderr)
        self.assertEqual(json.loads(good.stdout), {"ratio": 21.0, "text_size": "large"})
        for args in (("--element-json", element, "--text-size", "normal"),
                     ("--foreground", "#000", "--background", "#fff"),
                     ("--foreground", "#000", "--text-size", "normal")):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2)
                self.assertEqual(result.stdout, "")

    def test_extra_paint_observations_cannot_be_contradicted_by_a_none_argument(self):
        for extra in ({"backgroundImage": "url(bg.png)"}, {"backgroundImage": None},
                      {"opacity": "0.5"}, {"opacity": float("nan")}, {"opacity": 2},
                      {"opacity": 10 ** 400}, {"opacity": -(10 ** 400)},
                      {"opacity": True}, {"opacity": float("inf")}, {"opacity": float("-inf")}):
            with self.subTest(extra=extra):
                element = {"color": "#000", "background": "#fff", **extra}
                with self.assertRaises(ValueError):
                    contrast.browser_observation(element, text_size="normal", background_image="none")

    def test_invalid_cli_never_emits_success_shaped_observation(self):
        for args in (("--foreground", "#000", "--background", "transparent", "--text-size", "normal"),
                     ("--foreground", "rgb(1e999999999999999999999999999999,0,0)",
                      "--background", "#fff", "--text-size", "normal"),
                     ("--element-json", '{"color":"#000","color":"#fff","background":"#fff"}',
                      "--background-image", "none", "--text-size", "normal"),
                     ("--element-json", '{"color":NaN,"background":"#fff"}',
                      "--background-image", "none", "--text-size", "normal"),
                     ("--element-json", "[]", "--background-image", "none", "--text-size", "normal"),
                     ("--foreground", "#000", "--background", "#fff", "--text-size", "normal",
                      "--background-image", "url(bg.png)")):
            with self.subTest(args=args):
                result = self.cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertEqual(result.stdout, "")
                self.assertIn("unverified", result.stderr.lower())

    def test_observation_uses_existing_p05_evaluator(self):
        for foreground, size, blocked in (("#000", "normal", False), ("#777", "normal", True),
                                         ("#777", "large", False), ("#959595", "large", True)):
            with self.subTest(foreground=foreground, size=size):
                control = {
                    "id": "fixture-contrast", "kind": "contrast", "requirement": "mandatory",
                    "applicability": "applicable", "status": "pass",
                    "reason": "Inert numerical fixture, not observed UI or clearance.",
                    "policy": {"source": "fixture-requirements.md", "version": "1",
                               "applicability": "Synthetic numeric unit test", "jurisdiction": None,
                               "actor": None, "effective_date": None},
                    "evidence": ["fixture-colors.json"],
                    "observation": self.measure(foreground, "#fff", size),
                }
                result = evaluate_controls([control], required_policy={
                    "required": False, "status": "not_required", "source": "fixture",
                    "version": "1", "applicability": "not_applicable",
                })
                self.assertEqual(result["blocked"], blocked)

    def test_existing_static_validator_remains_separate(self):
        good = '<html><meta name="viewport" content="width=device-width"><p>Text</p></html>'
        bad = '<html><meta name="viewport" content="user-scalable=no"><button>🚀</button></html>'
        errors, _ = validate_design.check(good, Path("good.html"), set())
        self.assertEqual(errors, [])
        errors, _ = validate_design.check(bad, Path("bad.html"), set())
        self.assertTrue(any("zoom disabled" in error for error in errors))
        self.assertTrue(any("emoji used as icon" in error for error in errors))


if __name__ == "__main__":
    unittest.main(verbosity=2)
