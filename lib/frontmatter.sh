#!/usr/bin/env bash
# Shared installer/verifier contract: required metadata must be inside the
# opening frontmatter block. Body examples cannot satisfy missing fields.
validate_lintel_frontmatter() { # <file> [skill|agent]
  local file="$1" kind="${2:-agent}"
  awk -v kind="$kind" '
    BEGIN {
      n=split("name description color tools voice cli_support", required, " ")
      if (kind == "skill") required[++n]="layer"
    }
    { sub(/\r$/, "") }
    NR == 1 { if ($0 != "---") { print "missing frontmatter start"; bad=1; exit }; next }
    $0 == "---" { closed=1; exit }
    /^[A-Za-z_][A-Za-z_0-9-]*:/ { key=$0; sub(/:.*/, "", key); seen[key]=1 }
    END {
      if (bad) exit 1
      if (!closed) { print "missing frontmatter end"; exit 1 }
      for (i=1; i<=n; i++) if (!(required[i] in seen)) {
        printf "missing %s\n", required[i]; bad=1
      }
      exit bad
    }
  ' "$file"
}
