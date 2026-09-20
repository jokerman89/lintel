#!/usr/bin/env bash
# DESCRIPTION: Swarm workflow links preserve opt-in execution and one task authority.
# TAGS: shape,swarm,codex-compatible
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export LINTEL_SOURCE_ROOT="$ROOT"

if command -v python3 >/dev/null 2>&1; then PYTHON=python3
elif command -v python >/dev/null 2>&1; then PYTHON=python
else echo "FAIL swarm-contract: Python 3.9+ is required" >&2; exit 1
fi

"$PYTHON" - "$ROOT" <<'PY'
import json
from pathlib import Path
import sys

root = Path(sys.argv[1])
swarm_skill = root / "skills/swarm/SKILL.md"
assert swarm_skill.is_file(), "canonical swarm skill is missing"
skill_body = swarm_skill.read_text(encoding="utf-8")
for marker in (
    "name: swarm",
    "workflow_root: true",
    "cli_support: [claude-code, codex, copilot]",
    "execution_mode: \"swarm\"",
    "evidence/topology candidate frontier",
    "Never dispatch from `wave` alone",
    "/li:brief-forge",
    "sequenced",
    "no-subagent",
    "integrated REVIEW",
):
    assert marker in skill_body, f"swarm skill missing contract marker: {marker}"

workflow_markers = {
    "skills/plan/SKILL.md": ("Step 6a", "operator opts in", "li-swarm.py"),
    "skills/build/SKILL.md": ("Mapped swarm entry condition", "legacy sequential BUILD unchanged", "never dispatch from `wave` alone", "authoritative prerequisites", "check-scope"),
    "skills/review/SKILL.md": ("Swarm integrated-tree close gate", "li-swarm.py", "reconciled"),
    "skills/resume/SKILL.md": ("Swarm-aware committed resume", "status", "Runtime loss cancels attempts"),
    "skills/capture/SKILL.md": ("Reaffirm swarm evidence", "M4", "COMPLETE"),
    "skills/cycle/SKILL.md": ("not a phase", "/li:cycle --swarm", "ordinary sequential BUILD"),
    "skills/full-engineering-pass/SKILL.md": ("parallel-eligible", "/li:swarm run", "serial fallback"),
    "skills/spec-kit/references/work-map.md": ("optional but atomic", "lib/swarm_contract.py", "task text"),
}
for relative, markers in workflow_markers.items():
    body = (root / relative).read_text(encoding="utf-8")
    for marker in markers:
        assert marker in body, f"{relative} missing swarm workflow marker: {marker}"

trusted_source_workflows = (
    "skills/swarm/SKILL.md",
    "skills/plan/SKILL.md",
    "skills/build/SKILL.md",
    "skills/review/SKILL.md",
    "skills/resume/SKILL.md",
    "skills/capture/SKILL.md",
    "skills/cycle/SKILL.md",
    "skills/spec-kit/references/work-map.md",
)
unsafe_repo_fallback = "${LINTEL_SOURCE_ROOT:-" + "$repo}"
for relative in trusted_source_workflows:
    body = (root / relative).read_text(encoding="utf-8")
    assert unsafe_repo_fallback not in body, f"{relative} trusts the working repo as helper source"
for relative in (
    "skills/swarm/SKILL.md",
    "skills/build/SKILL.md",
    "skills/review/SKILL.md",
    "skills/resume/SKILL.md",
):
    body = (root / relative).read_text(encoding="utf-8")
    for marker in ("LINTEL_SOURCE_ROOT", "CLAUDE_PLUGIN_ROOT", "NEEDS_CONTEXT", '--repo "$repo"'):
        assert marker in body, f"{relative} missing trusted-source/fail-closed marker: {marker}"
for relative in ("tests/shape/swarm-contract.sh", "tests/integration/swarm-workflow.sh"):
    body = (root / relative).read_text(encoding="utf-8")
    assert 'export LINTEL_SOURCE_ROOT="$ROOT"' in body, f"{relative} does not export explicit source root"

engineering_pass = (root / "skills/full-engineering-pass/SKILL.md").read_text(encoding="utf-8")
assert '[ "${#stage2_modules[@]}" -gt 0 ]' in engineering_pass, "empty DA/SC stage can invoke swarm"
assert 'module_status["$module"]="FAILED"' in engineering_pass, "swarm failure does not fail each selected DA/SC module"

loader = (root / "bin/li-work-artifacts.py").read_text(encoding="utf-8")
assert "from swarm_contract import validate_work_map_swarm_fields" in loader
assert "def validate_work_map_swarm_fields" not in loader, "work-map loader duplicated the swarm parser"

coordination = json.loads(
    (root / ".claude/plans/swarming-work/swarm/coordination.json").read_text(encoding="utf-8")
)
task_authority_fields = {"title", "description", "depends_on", "dependencies", "acceptance", "status", "checkboxes"}
seen = set()
for lane in coordination["lanes"]:
    assert not task_authority_fields.intersection(lane), f"lane duplicates task authority: {lane['task_id']}"
    assert lane["task_id"] not in seen, f"duplicate lane: {lane['task_id']}"
    seen.add(lane["task_id"])

wrapper = root / "tests/integration/swarm-workflow.sh"
assert wrapper.is_file(), "discovered integration wrapper is missing"
wrapper_body = wrapper.read_text(encoding="utf-8")
assert "tests/unit/swarm-contract.py" in wrapper_body
assert "tests/integration/swarm-workflow.py" in wrapper_body
print("PASS: swarm workflow links, opt-in fallback, shared parser, and unique task authority are present")
PY
