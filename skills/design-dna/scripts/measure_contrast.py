#!/usr/bin/env python3
# component: design-contrast-measurement
# implements: ADR-0015, ADR-0028
# intent: skills/design-dna/references/design-contract.md#measured-text-contrast
# constraints: read-only, standard library; opaque solid sRGB only, no paint or browser execution
# last_intent_review: 2026-10-03
"""Calculate an observation from supplied colors; never produce a review/clearance record."""
from __future__ import annotations

import argparse
from decimal import Decimal, InvalidOperation
import json
import re
import sys
from typing import Any

NUMBER = re.compile(r"[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)(?:[eE][+-]?[0-9]+)?%?")
HEX = re.compile(r"#(?:[0-9a-f]{3}|[0-9a-f]{4}|[0-9a-f]{6}|[0-9a-f]{8})", re.I)
RGB = re.compile(r"(rgb|rgba)\(([^()]*)\)", re.I)
THRESHOLDS = {"normal": 4.5, "large": 3.0}


def _number(token: str, maximum: int) -> tuple[Decimal, int]:
    if not NUMBER.fullmatch(token):
        raise ValueError("Expected a finite sRGB number or percentage")
    percent = token.endswith("%")
    try:
        value = Decimal(token[:-1] if percent else token)
    except InvalidOperation as error:
        raise ValueError("Unrepresentable sRGB number") from error
    limit = 100 if percent else maximum
    if not value.is_finite() or not 0 <= value <= limit:
        raise ValueError("sRGB channel is nonfinite or out of range")
    return value, limit


def opaque_srgb(color: Any) -> tuple[float, float, float]:
    """Parse explicit #RGB[A], #RRGGBB[AA] or CSS rgb[a]; refuse all nonopaque input."""
    if not isinstance(color, str) or not color.strip() or len(color) > 128:
        raise ValueError("An explicit opaque solid sRGB color is required")
    color = color.strip()
    if HEX.fullmatch(color):
        digits = color[1:]
        if len(digits) in (3, 4):
            digits = "".join(char * 2 for char in digits)
        if len(digits) == 8 and digits[6:].lower() != "ff":
            raise ValueError("Alpha compositing is unsupported; color must be opaque")
        return tuple(int(digits[i:i + 2], 16) / 255 for i in (0, 2, 4))
    match = RGB.fullmatch(color)
    if match is None:
        raise ValueError("Unresolved, gradient/image or unsupported color; supply opaque sRGB")
    body = match.group(2).strip()
    if "," in body:
        if "/" in body:
            raise ValueError("Mixed CSS color syntax is unsupported")
        parts = [part.strip() for part in body.split(",")]
        if len(parts) not in (3, 4):
            raise ValueError("Expected three color channels and optional opaque alpha")
        channels, alpha = parts[:3], parts[3] if len(parts) == 4 else None
    else:
        parts = body.split("/")
        if len(parts) > 2:
            raise ValueError("Invalid CSS alpha syntax")
        channels, alpha = parts[0].split(), parts[1].strip() if len(parts) == 2 else None
        if len(channels) != 3:
            raise ValueError("Expected three color channels")
    if alpha is not None:
        value, limit = _number(alpha, 1)
        # Compare the original decimal exactly: near-one alpha must not round to opaque.
        if value != limit:
            raise ValueError("Alpha compositing is unsupported; color must be opaque")
    if len({channel.endswith("%") for channel in channels}) != 1:
        raise ValueError("Mixed number/percentage channels are unsupported")
    values = [_number(channel, 255) for channel in channels]
    return tuple(float(value / limit) for value, limit in values)


def contrast_observation(foreground: Any, background: Any, *, text_size: str) -> dict:
    """WCAG sRGB luminance and unrounded ratio; input is not proof of painted pixels."""
    if not isinstance(text_size, str) or text_size not in THRESHOLDS:
        raise ValueError("An observed normal or large text classification is required")

    def luminance(color: Any) -> float:
        channels = opaque_srgb(color)
        linear = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
                  for c in channels]
        return sum(weight * channel for weight, channel in zip((0.2126, 0.7152, 0.0722), linear))

    first, second = luminance(foreground), luminance(background)
    ratio = (max(first, second) + 0.05) / (min(first, second) + 0.05)
    return {"ratio": ratio, "text_size": text_size}


def browser_observation(element: Any, *, text_size: str, background_image: Any) -> dict:
    """Reuse web-session's color/background keys; require the missing paint observation."""
    if not isinstance(element, dict):
        raise ValueError("Expected one actual read element, not a page or invented browser result")
    if not isinstance(background_image, str) or background_image.strip().lower() != "none":
        raise ValueError("Background image/gradient is unresolved or unsupported")
    # Do not ignore contradictory additional computed-style observations from another provider.
    if "backgroundImage" in element and element["backgroundImage"] != "none":
        raise ValueError("Background image/gradient compositing is unsupported")
    if "opacity" in element:
        value, limit = _number(str(element["opacity"]), 1)
        if value != limit:
            raise ValueError("Element opacity compositing is unsupported")
    return contrast_observation(element.get("color"), element.get("background"), text_size=text_size)


def _unique_object(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate input field")
        result[key] = value
    return result


def _nonfinite(value: str) -> None:
    raise ValueError("Nonfinite JSON value is unsupported")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--foreground", help="Actual opaque foreground color, not a token name")
    inputs.add_argument("--element-json", help="Literal web-session read element JSON (not a file path)")
    parser.add_argument("--background", help="Actual opaque solid background for --foreground")
    parser.add_argument("--background-image", help="Separately observed CSS background-image; only none is supported")
    parser.add_argument("--text-size", required=True, choices=tuple(THRESHOLDS))
    args = parser.parse_args()
    try:
        if args.element_json is not None:
            if args.background is not None:
                raise ValueError("Do not replace a read element's observed background")
            element = json.loads(args.element_json, object_pairs_hook=_unique_object, parse_constant=_nonfinite)
            observation = browser_observation(element, text_size=args.text_size,
                                              background_image=args.background_image)
        else:
            if args.background_image is not None and args.background_image.strip().lower() != "none":
                raise ValueError("Gradient/image backgrounds are unsupported")
            observation = contrast_observation(args.foreground, args.background, text_size=args.text_size)
        print(json.dumps(observation, allow_nan=False))
        return 0 if observation["ratio"] >= THRESHOLDS[observation["text_size"]] else 1
    except ValueError as error:
        print(f"UNVERIFIED [lintel/contrast]: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
