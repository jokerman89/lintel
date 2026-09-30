# component: review-headers
# implements: ADR-0036, ADR-0040
# intent: skills/review/references/method.md
# constraints: pure stdlib text/data operations; family schemas, errors and rendering remain caller-owned
# last_intent_review: 2026-09-30
"""Shared fenced-header parsing and validation without either family's runtime dependencies."""
from __future__ import annotations

import re
from typing import Any, Callable, Dict, Pattern

HEADER_KEY = re.compile(r"^[a-z][a-z0-9_]*$")


def parse_header(body: str, opener: str, prefix: str, kind: str,
                 require: Callable[[bool, str], None], header_key: Pattern[str]) -> Dict[str, str]:
    """Consume the caller's normalized body and opener, retaining its exception boundary."""
    require(body.startswith(opener + "\n") or body.startswith(opener + "\r\n"),
            f"message must begin with a ```{prefix}-{kind} header block")
    end = body.find("\n```", len(opener))
    require(end != -1, f"unterminated {prefix}-{kind} header block")
    fields: Dict[str, str] = {}
    for raw in body[len(opener):end].splitlines():
        line = raw.strip()
        if not line:
            continue
        key, sep, value = line.partition(":")
        key = key.strip()
        require(sep == ":" and header_key.match(key) is not None, f"malformed header line: {line!r}")
        require(key not in fields, f"duplicate header key: {key}")
        fields[key] = value.strip()
    return fields


def validate_header(kind: str, fields: Dict[str, str], schema: Dict[str, Any], prefix: str,
                    require: Callable[[bool, str], None]) -> Dict[str, str]:
    """Validate the supplied family schema in its existing first-error order."""
    spec = schema["headers"].get(kind)
    require(spec is not None, f"unknown header kind: {kind}")
    missing = [key for key in spec["required"] if not fields.get(key)]
    require(not missing, f"{prefix}-{kind} header missing: {', '.join(missing)}")
    unknown = set(fields) - set(spec["required"]) - set(spec["optional"])
    require(not unknown, f"{prefix}-{kind} header has unknown keys: {', '.join(sorted(unknown))}")
    require(fields[prefix] == kind and fields["version"] == "1", f"not a {prefix}-{kind} v1 header")
    for key, allowed in spec.get("enums", {}).items():
        if key in fields:
            require(fields[key] in allowed, f"{key} must be one of {allowed}")
    for key in spec.get("integers", []):
        require(re.fullmatch(r"\d+", fields.get(key, "")) is not None, f"{key} must be a non-negative integer")
    return fields
