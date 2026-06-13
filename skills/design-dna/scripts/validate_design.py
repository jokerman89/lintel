#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# component: design-dna-validator
# implements: ADR-0015
# intent: docs/design/lintel-v5.4-design-dna-design.md
# constraints: stdlib-only (no pip) — portability contract
# last_intent_review: 2026-06-13
# Lintel rewrite inspired by ui-ux-pro-max-skill's html-token-validator.py
# (MIT, Copyright (c) 2024 Next Level Builder) — generalized: profile-aware,
# no project-structure assumptions, forbidden-pattern set from the corpus's
# non-negotiables instead of token-compliance-only.
"""
Design DNA validator - mechanical pre-delivery gate for rendered HTML/CSS.

Errors (exit 1) are objective violations of the non-negotiables; warnings are
heuristics for the reviewer. Usage:

  python3 validate_design.py <file.html> [<file2.html> ...] [--profile profiles/anthropic-default.yaml] [-v]
"""

import argparse
import re
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

EMOJI_RE = re.compile(
    "[\U0001F300-\U0001FAFF\U00002600-\U000027BF\U0001F000-\U0001F02F\U00002190-\U000021FF\U00002B00-\U00002BFF]"
)
HEX_RE = re.compile(r"#[0-9A-Fa-f]{3,8}\b")
NEUTRAL_HEX = {"#fff", "#ffffff", "#000", "#000000"}


def load_profile_hexes(profile_path):
    """Collect every hex token from a profile YAML (regex — stdlib has no YAML)."""
    text = Path(profile_path).read_text(encoding="utf-8")
    return {h.lower() for h in HEX_RE.findall(text)}


def check(content, path, profile_hexes, verbose=False):
    errors, warnings = [], []
    lower = content.lower()
    is_document = "<html" in lower

    # --- hard violations (the non-negotiables) ---
    if re.search(r"user-scalable\s*=\s*no|maximum-scale\s*=\s*1(?:\.0)?\b", lower):
        errors.append("zoom disabled in viewport meta (user-scalable=no / maximum-scale=1)")

    if is_document and "viewport" not in lower:
        errors.append("missing viewport meta on a full HTML document")

    if re.search(r"outline\s*:\s*(none|0)\b", lower) and ":focus" not in lower:
        errors.append("focus outline removed with no :focus/:focus-visible replacement anywhere")

    for m in EMOJI_RE.finditer(content):
        pre = content[max(0, m.start() - 160): m.start()]
        if re.search(r"<(button|a|nav)\b[^>]*>(?:(?!</)[\s\S])*$", pre) or re.search(
            r'class\s*=\s*"[^"]*icon[^"]*"[^<]*$', pre
        ):
            errors.append(f"emoji used as icon near: …{content[m.start()-30:m.start()+10]!r} — use SVG (Lucide/Heroicons)")
            break  # one finding is enough to gate
        else:
            warnings.append("emoji present in markup — verify it is content, not an icon")
            break

    # --- heuristic warnings ---
    if "transition: all" in lower or "transition:all" in lower:
        warnings.append("transition: all — animate specific transform/opacity properties instead")

    if re.search(r"\b100vh\b", lower):
        warnings.append("100vh used — prefer 100dvh/min-h-dvh on mobile")

    for m in re.finditer(r"font-size\s*:\s*(\d+(?:\.\d+)?)px", lower):
        if float(m.group(1)) < 12:
            warnings.append(f"font-size {m.group(1)}px < 12px — likely unreadable body/label text")
            break

    if ("@keyframes" in lower or "transition" in lower) and "prefers-reduced-motion" not in lower:
        warnings.append("animations present but prefers-reduced-motion is not respected")

    if profile_hexes:
        styles = " ".join(re.findall(r"<style[^>]*>([\s\S]*?)</style>", content, re.I))
        styles += " ".join(re.findall(r'style\s*=\s*"([^"]*)"', content))
        off_palette = {
            h.lower() for h in HEX_RE.findall(styles)
            if h.lower() not in profile_hexes and h.lower() not in NEUTRAL_HEX
        }
        if off_palette:
            sample = ", ".join(sorted(off_palette)[:6])
            warnings.append(f"{len(off_palette)} hex value(s) outside the active profile palette: {sample}")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(description="Design DNA pre-delivery validator")
    parser.add_argument("files", nargs="+", help="HTML/CSS files to validate")
    parser.add_argument("--profile", help="Path to active design profile YAML (enables palette check)")
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()

    profile_hexes = load_profile_hexes(args.profile) if args.profile else set()

    total_errors = 0
    for f in args.files:
        p = Path(f)
        if not p.exists():
            print(f"x {f}: file not found")
            total_errors += 1
            continue
        errors, warnings = check(p.read_text(encoding="utf-8", errors="replace"), p, profile_hexes, args.verbose)
        status = "x" if errors else "ok"
        print(f"{status} {p.name}: {len(errors)} error(s), {len(warnings)} warning(s)")
        for e in errors:
            print(f"   ERROR  {e}")
        for w in warnings:
            print(f"   warn   {w}")
        total_errors += len(errors)

    sys.exit(1 if total_errors else 0)


if __name__ == "__main__":
    main()
