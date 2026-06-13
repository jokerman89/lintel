#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# component: design-dna-token-emitter
# implements: ADR-0017
# intent: docs/design/lintel-v5.4-design-dna-design.md
# constraints: stdlib-only (no pip) — portability contract
# last_intent_review: 2026-06-13
# Three-layer token architecture (primitive -> semantic -> component) inspired by
# ui-ux-pro-max-skill's design-system token system (MIT, (c) 2024 Next Level Builder);
# Lintel rewrite: reads a Lintel design profile YAML, emits layered CSS custom properties.
"""
Emit a three-layer design-tokens.css from an active design profile.

  primitive  — raw values (--dna-ink, --dna-space-4, --dna-radius-md)
  semantic   — purpose aliases (--color-primary, --color-bg, --spacing-section)
  component  — per-component starters (--button-bg, --card-radius)

Usage:
  python3 emit_tokens.py --profile profiles/anthropic-default.yaml [--out design-tokens.css]

Tolerant line parser (stdlib has no YAML): captures scalar leaves by indent-path,
skips inline maps/lists it cannot parse. Enough for the themeable primitives
(colors, radius, spacing) — the rest degrade to sensible defaults.
"""

import argparse
import re
import sys
import io
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

HEX = re.compile(r"^#[0-9A-Fa-f]{3,8}$")


def parse_profile(text):
    """Indent-aware scalar-leaf capture → {dotted.path: value}. Lists/inline-maps skipped."""
    leaves, stack = {}, []  # stack: (indent, key)
    for raw in text.splitlines():
        if raw.lstrip().startswith("#") or not raw.strip():
            continue
        indent = len(raw) - len(raw.lstrip())
        m = re.match(r"\s*([A-Za-z0-9_\-]+):\s*(.*)$", raw)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        while stack and stack[-1][0] >= indent:
            stack.pop()
        path = ".".join(k for _, k in stack)
        if val == "":  # a mapping header
            stack.append((indent, key))
            continue
        if val.startswith("[") or val.startswith("{"):
            continue  # inline list/map — not a scalar primitive
        if val[0] in "\"'":  # quoted scalar — take up to the closing quote (protects "#hex")
            q = val[0]
            end = val.find(q, 1)
            val = val[1:end] if end > 0 else val[1:]
        else:  # bare scalar — a trailing " # comment" is a real comment
            val = re.split(r"\s+#", val, 1)[0].strip()
        full = f"{path}.{key}" if path else key
        leaves[full] = val
    return leaves


def emit(leaves, profile_id):
    colors = {k.split(".")[-1]: v for k, v in leaves.items()
              if k.startswith("color.") and HEX.match(v)}
    semantic = {k.split(".")[-1]: v for k, v in leaves.items()
                if k.startswith("semantic.") and HEX.match(v)}
    radius = {k.split(".")[-1]: v for k, v in leaves.items() if k.startswith("shape.radius.")}

    out = [f"/* design-tokens.css — generated from profile '{profile_id}' (design-dna, ADR-0017) */",
           "/* Three layers: primitive (raw) -> semantic (purpose) -> component (per-element). */",
           "/* Theme by remapping semantic->primitive; components never touch raw values. */",
           ":root {"]

    out.append("  /* ---- Layer 1: primitive ---- */")
    for name, hexv in colors.items():
        out.append(f"  --dna-{name.replace('_','-')}: {hexv};")
    for step in (4, 8, 12, 16, 24, 32, 48, 64):
        out.append(f"  --dna-space-{step}: {step/16:.3f}rem;")
    for name, val in (radius or {"sm": "6", "md": "10", "lg": "16"}).items():
        out.append(f"  --dna-radius-{name}: {val}px;")

    out.append("  /* ---- Layer 2: semantic (purpose aliases) ---- */")
    alias = {  # values are profile color keys (underscore form, as parsed from YAML)
        "--color-bg": "paper", "--color-fg": "ink",
        "--color-primary": "accent_primary", "--color-secondary": "accent_secondary",
        "--color-muted": "neutral_mid", "--color-surface": "neutral_subtle",
    }
    for sem, prim in alias.items():
        if prim in colors:
            out.append(f"  {sem}: var(--dna-{prim.replace('_','-')});")
    for name, hexv in semantic.items():
        out.append(f"  --color-{name.replace('_','-')}: {hexv};")
    out.append("  --spacing-section: var(--dna-space-64);")
    out.append("  --spacing-block: var(--dna-space-24);")

    out.append("  /* ---- Layer 3: component (starters — override per component) ---- */")
    out.append("  --button-bg: var(--color-primary);")
    out.append("  --button-fg: var(--color-bg);")
    out.append("  --button-radius: var(--dna-radius-md, 10px);")
    out.append("  --card-bg: var(--color-surface, var(--color-bg));")
    out.append("  --card-padding: var(--dna-space-24);")
    out.append("  --card-radius: var(--dna-radius-lg, 16px);")
    out.append("  --focus-ring: var(--color-focus, var(--color-primary));")
    out.append("}")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Emit three-layer design-tokens.css from a profile")
    ap.add_argument("--profile", required=True, help="Path to a design profile YAML")
    ap.add_argument("--out", help="Write to file (default: stdout)")
    args = ap.parse_args()

    p = Path(args.profile)
    if not p.exists():
        print(f"x profile not found: {args.profile}")
        sys.exit(1)
    leaves = parse_profile(p.read_text(encoding="utf-8"))
    pid = leaves.get("profile.id", p.stem)
    css = emit(leaves, pid)

    if args.out:
        Path(args.out).write_text(css, encoding="utf-8")
        print(f"ok wrote {args.out} ({css.count('--')} tokens, 3 layers)")
    else:
        sys.stdout.write(css)


if __name__ == "__main__":
    main()
