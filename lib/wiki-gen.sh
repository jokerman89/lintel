#!/usr/bin/env bash
# lib/wiki-gen.sh — wiki-gen helpers, sourced by bin/li-wiki-gen.
#
# Provides helpers that bin/li-wiki-gen uses for parsing + rendering.
# Phase 3 keeps most logic inline in bin/li-wiki-gen for portability;
# this file holds reusable helpers that may also be sourced by other tools.

set -uo pipefail

# Read the authoring contracts with the same stdlib parser as profile resolution.
wgen_schema_summary() {
  local file="${1:?}" kind="${2:?}" python_bin lib_root
  python_bin="$(command -v python3 || command -v python)" || {
    echo "ERROR: schema reference requires Python 3.9+" >&2
    return 2
  }
  lib_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" || return 2
  "$python_bin" -I -B -S - "$lib_root" "$file" "$kind" <<'PY'
from pathlib import Path
import sys

sys.path.insert(0, str(Path(sys.argv[1]).resolve()))
from profile_context import parse_manifest, read_json


def required_fields(value: object) -> list[str]:
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item or item != item.strip()
        or any(char in item for char in "\r\n|") for item in value
    ):
        raise ValueError("required fields must be a nonempty string list")
    if len(set(value)) != len(value):
        raise ValueError("duplicate required field")
    return value


path = Path(sys.argv[2])
kind = sys.argv[3]
try:
    text = path.read_text(encoding="utf-8-sig")
    data = read_json(text) if text.lstrip().startswith("{") else parse_manifest(text)
    version = data.get("schema_version")
    if not isinstance(version, str) or not version.strip() or any(
        char.isspace() for char in version
    ):
        raise ValueError("schema_version must be a nonempty version string")
    if data.get("schema_kind") != kind:
        raise ValueError("schema_kind does not match the requested reference")
    if kind == "pack-manifest":
        detail = "Required top-level fields: " + ", ".join(required_fields(data.get("required_fields")))
    elif kind == "envelope":
        sections = {}
        for name in ("head", "body", "tail"):
            section = data.get(name)
            if not isinstance(section, dict):
                raise ValueError(f"missing or invalid {name} section")
            sections[name] = required_fields(section.get("required"))
        if "content_type" not in sections["body"]:
            raise ValueError("body is missing its content_type discriminator")
        detail = (
            f"Structure: HEAD ({len(sections['head'])} required) + "
            f"BODY (content_type discriminator; {len(sections['body'])} required) + "
            f"TAIL ({len(sections['tail'])} required)"
        )
    else:
        raise ValueError("unsupported schema reference")
except (OSError, UnicodeError, ValueError) as error:
    print(f"ERROR: schema reference {path.name}: {error}", file=sys.stderr)
    raise SystemExit(2)

print(f"schema_version: {version}\n\n{detail}")
PY
}

# Parse a YAML scalar (handles inline-flow and block form).
# Usage: wgen_yaml_scalar <file> <key>
wgen_yaml_scalar() {
  local file="${1:?}" key="${2:?}"
  grep -E "^${key}:" "$file" 2>/dev/null | head -1 | awk -F': *' '{print $2}' | tr -d '"' | tr -d "'" | tr -d '[:space:]'
}

# Parse a frontmatter scalar from a markdown file's YAML frontmatter.
wgen_fm_scalar() {
  local file="${1:?}" field="${2:?}"
  awk -v field="$field" '
    /^---$/ { if (++fm == 2) exit; next }
    fm == 1 && $0 ~ "^"field":" {
      sub("^"field":[[:space:]]*", "")
      sub("[[:space:]]*#.*$", "")
      gsub(/^[[:space:]]+|[[:space:]]+$/, "")
      print
      exit
    }
  ' "$file"
}

# Detect if a markdown file declares workflow_root: true in frontmatter.
wgen_is_workflow_root() {
  local file="${1:?}"
  awk '
    /^---$/ { if (++fm == 2) exit; next }
    fm == 1 && /^workflow_root:[[:space:]]*true/ { print "yes"; exit }
  ' "$file"
}

# Render a markdown table row from given cells.
wgen_render_row() {
  local IFS='|'
  printf '| %s |\n' "$*"
}

# Count entries in a directory matching a glob.
wgen_count() {
  local dir="${1:?}" pattern="${2:-*}"
  find "$dir" -name "$pattern" -type f 2>/dev/null | wc -l | tr -d ' '
}

# Generate a deterministic timestamp for output headers (stable by default,
# can be overridden via WGEN_TS env var for reproducible builds).
wgen_ts() {
  printf '%s' "${WGEN_TS:-source snapshot; see Git history}"
}
