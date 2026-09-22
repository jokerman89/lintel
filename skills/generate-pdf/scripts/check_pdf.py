#!/usr/bin/env python3
# component: pdf-text-inspection
# implements: ADR-0028, ADR-0031
# intent: .claude/plans/universal-implementation/packages/P12.md
# constraints: explicit existing pypdf reader; text/page/origin checks, never raster or full glyph geometry
# last_intent_review: 2026-09-22
"""Read searchable PDF text, page boxes and transformed text origins with pypdf."""
from __future__ import annotations

import argparse
import hashlib
from io import BytesIO
import importlib.metadata
import json
import math
from pathlib import Path
import sys
from typing import Any

SOURCE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(SOURCE / "lib"))
from context_safety import checked_root, read_owned, selector_path  # noqa: E402
from review_contract import load_json  # noqa: E402


def inspect_pdf(data: bytes, expected: dict[str, Any]) -> dict[str, Any]:
    from pypdf import PdfReader, Transformation

    if not isinstance(expected, dict) or set(expected) - {"required_text", "min_pages", "paper_points", "page_text"} \
            or not isinstance(expected.get("required_text"), list) or not expected["required_text"] \
            or any(not isinstance(text, str) or not text.strip() for text in expected["required_text"]):
        raise ValueError("Expected nonempty required_text and optional min_pages/paper_points/page_text")
    minimum = expected.get("min_pages", 1)
    if type(minimum) is not int or minimum < 1:
        raise ValueError("min_pages must be a positive integer")
    size = expected.get("paper_points")
    if size is not None and (not isinstance(size, list) or len(size) != 2
                             or any(type(x) not in (int, float) or not math.isfinite(x) or x <= 0 for x in size)):
        raise ValueError("paper_points must be two finite positive dimensions")
    page_text = expected.get("page_text", {})
    if not isinstance(page_text, dict) or any(not key.isdigit() or int(key) < 1
                                             or not isinstance(value, str) or not value.strip() for key, value in page_text.items()):
        raise ValueError("page_text maps positive page numbers to nonempty expected text")
    reader = PdfReader(BytesIO(data), strict=True)
    if reader.is_encrypted:
        raise ValueError("Encrypted PDF inspection needs separate authorization; no password attempted")
    pages, issues = [], []
    for index, page in enumerate(reader.pages, 1):
        try:
            media, crop = [float(x) for x in page.mediabox], [float(x) for x in page.cropbox]
            unit = page.user_unit
            if hasattr(unit, "get_object"):
                unit = unit.get_object()
            if isinstance(unit, bool) or not isinstance(unit, (int, float)):
                raise ValueError("UserUnit must be numeric")
            unit = float(unit)
        except (AttributeError, AssertionError, KeyError, TypeError, ValueError, OverflowError) as error:
            raise ValueError(f"Invalid or unavailable page metadata on page {index}: {error}") from error
        if not math.isfinite(unit) or unit <= 0:
            raise ValueError(f"UserUnit must be finite and positive on page {index}")
        if len(media) != 4 or len(crop) != 4 or not all(math.isfinite(x) for x in media + crop) \
                or not (media[0] < media[2] and media[1] < media[3]) \
                or not (crop[0] < crop[2] and crop[1] < crop[3]):
            raise ValueError(f"Invalid page box on page {index}")
        effective = [max(media[0], crop[0]), max(media[1], crop[1]),
                     min(media[2], crop[2]), min(media[3], crop[3])]
        if effective[0] >= effective[2] or effective[1] >= effective[3]:
            raise ValueError(f"Empty effective MediaBox/CropBox intersection on page {index}")
        physical_media = [(media[2] - media[0]) * unit, (media[3] - media[1]) * unit]
        physical_effective = [(effective[2] - effective[0]) * unit, (effective[3] - effective[1]) * unit]
        if any(not math.isfinite(value) or value <= 0 for value in physical_media + physical_effective):
            raise ValueError(f"Invalid physical page dimensions on page {index}")
        if page.rotation:
            issues.append({"page": index, "check": "rotation", "status": "unverified",
                           "reason": "This text-origin checker does not establish rotated glyph bounds"})
        origins = []

        def observe(text, current, text_matrix, _font, font_size):
            if not text.strip():
                return
            point = Transformation(current).apply_on(Transformation(text_matrix).apply_on((0, 0)))
            if not all(math.isfinite(x) for x in point):
                raise ValueError(f"Non-finite text origin on page {index}")
            in_crop = crop[0] <= point[0] <= crop[2] and crop[1] <= point[1] <= crop[3]
            in_media = media[0] <= point[0] <= media[2] and media[1] <= point[1] <= media[3]
            inside = in_crop and in_media
            origins.append({"text": text, "origin": list(point), "font_size": font_size,
                            "within_crop_box": in_crop, "within_media_box": in_media, "within_effective_box": inside})
            if not inside:
                issues.append({"page": index, "check": "text_origin", "status": "fail",
                               "reason": "Text origin lies outside the effective MediaBox/CropBox intersection"})

        text = page.extract_text(visitor_text=observe)
        if not text.strip() or not origins:
            issues.append({"page": index, "check": "searchable_text", "status": "fail", "reason": "No searchable text observed"})
        if size and any(abs(actual - wanted) > 2 for actual, wanted in zip(physical_media, size)):
            issues.append({"page": index, "check": "paper", "status": "fail", "reason": "Printed dimensions differ from requested paper"})
        pages.append({"page": index, "media_box": media, "crop_box": crop, "effective_box": effective,
                      "user_unit": unit, "physical_media_points": physical_media,
                      "physical_effective_points": physical_effective, "text": text, "text_origins": origins})
    normalized = " ".join("\n".join(page["text"] for page in pages).split())
    missing = [text for text in expected["required_text"] if " ".join(text.split()) not in normalized]
    if missing:
        issues.append({"check": "source_retention", "status": "fail", "missing": missing})
    if len(pages) < minimum:
        issues.append({"check": "page_count", "status": "fail", "reason": "Fewer pages than the explicit source case requires"})
    for number, text in page_text.items():
        if int(number) > len(pages) or " ".join(text.split()) not in " ".join(pages[int(number) - 1]["text"].split()):
            issues.append({"check": "page_content", "status": "fail", "page": int(number), "reason": "Required text missing from selected page"})
    status = "fail" if any(item["status"] == "fail" for item in issues) else "unverified" if issues else "pass"
    def observed_status(names):
        selected = [item["status"] for item in issues if item["check"] in names]
        return "fail" if "fail" in selected else "unverified" if selected else "pass"

    return {
        "status": status, "pdf_sha256": hashlib.sha256(data).hexdigest(),
        "reader": {"name": "pypdf", "version": importlib.metadata.version("pypdf")},
        "page_count": len(pages), "pages": pages, "issues": issues,
        "source_text_status": observed_status({"source_retention", "searchable_text"}),
        "page_status": observed_status({"page_count", "page_content", "paper"}),
        "text_origin_status": observed_status({"text_origin", "rotation"}),
        "text_matching": "Whitespace normalization only; not a visual comparison",
        "geometry": "Raw user-space boxes/origins and their effective intersection; physical dimensions include UserUnit. Not full glyph bounds.",
        "complete_visual_inspection": "unverified", "release_clearance": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--input", required=True)
    parser.add_argument("--expect", required=True)
    args = parser.parse_args()
    try:
        from pypdf.errors import PyPdfError
    except ImportError as error:
        print(json.dumps({"status": "error", "reason": f"Selected pypdf reader unavailable: {error}", "release_clearance": False}), file=sys.stderr)
        return 2
    try:
        root = checked_root(args.root)
        data, _ = read_owned(root, selector_path(args.input), max_bytes=64 * 1024 * 1024)
        oracle, _ = read_owned(root, selector_path(args.expect), max_bytes=16 * 1024 * 1024)
        result = inspect_pdf(data, load_json(oracle.decode("utf-8-sig")))
        print(json.dumps(result, ensure_ascii=True, allow_nan=False))
        return 0 if result["status"] == "pass" else 3
    except (ImportError, OSError, ValueError, TypeError, PyPdfError) as error:
        print(json.dumps({"status": "error", "reason": str(error), "release_clearance": False}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
