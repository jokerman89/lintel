#!/usr/bin/env bash
# Verify protocol synchronization preserves project prose and rejects malformed ownership.
# tag: unit instructions copilot cross-cli
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
PYTHON="$(command -v python3 || command -v python || true)"
if [ -z "$PYTHON" ]; then
  echo "SKIP: Python 3.9+ required"
  exit 0
fi
"$PYTHON" - "$ROOT" <<'PY'
from pathlib import Path
import importlib.util
import os
import subprocess
import sys
import tempfile

root = Path(sys.argv[1])
spec = importlib.util.spec_from_file_location("session_sync", root / "bin/li-instructions.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory(prefix="lintel-protocol-") as folder:
    fixture = Path(folder).resolve()
    source = fixture / module.SOURCE
    source.parent.mkdir(parents=True)
    source.write_text("## Required discipline\n\nRead architecture before changing code.\n", encoding="utf-8")
    for target in module.TARGETS:
        path = fixture / target
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Project-owned title\n\nKeep this customer-free project command exactly.\n", encoding="utf-8")
    environment = dict(os.environ, HOME=str(fixture / "absent-home"), USERPROFILE=str(fixture / "absent-home"))
    def run(command):
        return subprocess.run([sys.executable, str(root / "bin/li-instructions.py"), command,
                               "--root", str(fixture)], capture_output=True, text=True, env=environment)
    assert run("check").returncode == 1, "missing inline blocks must be drift"
    assert run("sync").returncode == 0, "sync must work without personal instructions"
    before = {target: (fixture / target).read_bytes() for target in module.TARGETS}
    assert run("check").returncode == 0
    assert run("sync").returncode == 0
    assert before == {target: (fixture / target).read_bytes() for target in module.TARGETS}, "sync must be idempotent"

    entry = fixture / "AGENTS.md"
    entry.write_text(entry.read_text(encoding="utf-8") + "\n## Project-only tail\nExact trailing guidance.\n", encoding="utf-8")
    source.write_text("## Required discipline\n\nNew approved common requirement.\n", encoding="utf-8")
    snapshot = entry.read_bytes()
    assert run("check").returncode == 1, "source change must cause drift"
    assert entry.read_bytes() == snapshot, "check must not modify files"
    assert run("sync").returncode == 0
    updated = entry.read_text(encoding="utf-8")
    assert updated.startswith("# Project-owned title\n\nKeep this customer-free project command exactly.\n")
    assert updated.endswith("\n## Project-only tail\nExact trailing guidance.\n"), "project tail must survive an update"
    assert "New approved common requirement." in updated

    for malformed in (module.START + "\nunclosed", module.END + "\n" + module.START,
                      module.START + "\n" + module.START + "\n" + module.END):
        entry.write_text(malformed, encoding="utf-8")
        untouched = (fixture / "CLAUDE.md").read_bytes()
        assert run("sync").returncode == 2, "malformed ownership markers must fail"
        assert entry.read_text(encoding="utf-8") == malformed
        assert (fixture / "CLAUDE.md").read_bytes() == untouched, "validate all targets before writes"
print("PASS: protocol preserves project prose, detects drift, rejects malformed markers and needs no personal home")
PY
