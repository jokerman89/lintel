#!/usr/bin/env bash
# component: reusable-patterns-contract-shape
# implements: ADR-0038
# intent: .claude/plans/reusable-patterns/contract.md
# constraints: read-only; validates the shipped template, example and wiring with the single core validator
# last_intent_review: 2026-09-28
# tag: shape patterns
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
if command -v python3 >/dev/null && python3 -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python3
elif command -v python >/dev/null && python -c 'import sys; assert sys.version_info >= (3, 10)' 2>/dev/null; then
  python=python
else
  echo 'ERROR: Python 3.10+ is required for the reusable-pattern contract shape check.' >&2
  exit 1
fi
PYTHONDONTWRITEBYTECODE=1 "$python" -I -B - "$root" <<'PY'
import hashlib, importlib.util, json, sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root / "lib"))
import patterns as p
failures = []
def check(ok, message):
    print(("  PASS: " if ok else "  FAIL: ") + message)
    if not ok:
        failures.append(message)

template = root / "scaffolding/01-foundation/templates/pattern"
draft = p.parse_pattern(json.loads((template / "pattern.template.json").read_text(encoding="utf-8")))
check(draft.status == "draft" and draft.approval is None, "pattern.template.json is a valid draft without approval")
example = template / "example"
catalog = p.parse_catalog(json.loads((example / "catalog.json").read_text(encoding="utf-8")))
check(len(catalog.entries) == 1, "the canonical example has exactly one pattern")
for entry in catalog.entries:
    body = p.parse_pattern(json.loads((example / entry.path).read_text(encoding="utf-8")))
    check(body.digest == entry.sha256, f"{entry.id}@{entry.version} catalog digest matches its body")
    for asset in body.assets:
        data = (example / Path(entry.path).parent / asset.path).read_bytes()
        check(hashlib.sha256(data).hexdigest() == asset.sha256, f"asset {asset.path} digest matches its bytes")
raw = [path for path in sorted(example.rglob("*")) if path.is_file()]
check(all(b"\r" not in path.read_bytes() for path in raw),
      "the example is LF-only, so the kit's LF text copy is byte-identical (bundle boundary)")
check((example / ".gitattributes").read_text(encoding="utf-8").splitlines()[-1].strip() == "* -text",
      "the example source keeps raw bytes with a source-local `* -text`")
skill = (root / "skills/pattern/SKILL.md").read_text(encoding="utf-8")
check("(references/consumer-contract.md)" in skill, "the pattern skill links the consumer contract")
check((root / "skills/pattern/references/consumer-contract.md").is_file(), "the consumer contract exists")
contract = (root / "skills/pattern/references/consumer-contract.md").read_text(encoding="utf-8")
check("pattern check unavailable" in contract, "the consumer contract states the missing-runtime rule")
spec = importlib.util.spec_from_file_location("li_copilot_shape", root / "bin/li-copilot.py")
generator = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generator)
check("pattern" in generator.WORKFLOWS, "the generator exposes the li-pattern native wrapper")
missing = [item for item in generator.PATTERN_RESOURCES if not (root / item).is_file()]
check(not missing, f"every PATTERN_RESOURCES path exists ({missing or 'none missing'})")
check("docs/concepts/patterns.md" in generator.DOCS, "the public patterns concept ships in the kit documentation")
wrapper = root / ".github/skills/li-pattern/SKILL.md"
check(wrapper.is_file() and "skills/pattern/SKILL.md" in wrapper.read_text(encoding="utf-8"),
      "the committed li-pattern wrapper points at the canonical workflow")
launcher = (root / "bin/li-pattern").read_text(encoding="utf-8")
check("pattern check unavailable" in launcher and "_fail 5" in launcher,
      "the launcher reports a missing runtime as unavailable (exit 5)")
print("pattern-contract: " + ("ALL PASS" if not failures else f"{len(failures)} FAILURES"))
sys.exit(1 if failures else 0)
PY
