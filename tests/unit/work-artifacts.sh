#!/usr/bin/env bash
# tag: unit spec-kit continuity
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 - "$ROOT" <<'PY'
import importlib.util
import json
from pathlib import Path
import tempfile
import sys
root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("work_artifacts", root / "bin/li-work-artifacts.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix="lintel-work-map-") as tmp:
    repo = Path(tmp).resolve()
    feature = repo / "specs/001-example"
    feature.mkdir(parents=True)
    for name, text in (("spec.md", "# Expected behavior"), ("plan.md", "# Technical design"), ("tasks.md", "- [ ] T001 Build the real change")):
        (feature / name).write_text(text)
    handoff = repo / ".claude/plans/example"
    handoff.mkdir(parents=True)
    (handoff / "prompt.md").write_text("Continue T001 from the original tasks.")
    data = dict(schema_version=1, workflow="spec-kit", status="APPROVED", spec="specs/001-example/spec.md", plan="specs/001-example/plan.md", tasks="specs/001-example/tasks.md", prompt=".claude/plans/example/prompt.md")
    mapping = handoff / "work.json"
    mapping.write_text(json.dumps(data))
    result = module.load_work_map(repo, mapping)
    assert result["tasks"] != result["plan"]
    assert not (repo / ".claude/runtime").exists()
    assert (feature / "plan.md").read_text() == "# Technical design"
    # Native Lintel maps use the actual plan checklist, with no duplicate task store.
    native = dict(data, workflow="lintel", tasks=data["plan"])
    mapping.write_text(json.dumps(native))
    assert module.load_work_map(repo, mapping)["tasks"] == data["plan"]
    for bad in (dict(data, schema_version=True), dict(data, tasks="../../outside.md"), dict(data, tasks="missing.md"), dict(data, tasks="C:/private.md"), dict(data, status="INVENTED")):
        mapping.write_text(json.dumps(bad))
        try:
            module.load_work_map(repo, mapping)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid map accepted: {bad}")
    # Every workflow consumes the same map rather than defining a second contract.
    for name in ("plan", "build", "review", "resume", "spec-kit"):
        body = (root / f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
        assert "work-map.md" in body and "li-work-artifacts.py" in body, name
print("PASS: Spec Kit and native task mappings work without a local ledger; unsafe/missing artifacts fail")
PY
