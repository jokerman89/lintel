#!/usr/bin/env bash
# tag: unit compatibility release
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
python3 - "$ROOT" <<'PY'
from pathlib import Path
import os
import shutil
import subprocess
import sys
import tempfile

source = Path(sys.argv[1]).resolve() / "bin/li-compat-audit"
with tempfile.TemporaryDirectory(prefix="lintel-compat-") as directory:
    repo = Path(directory)
    env = dict(os.environ, GIT_AUTHOR_NAME="Test", GIT_AUTHOR_EMAIL="test@example.invalid",
               GIT_COMMITTER_NAME="Test", GIT_COMMITTER_EMAIL="test@example.invalid")
    def git(*args):
        return subprocess.run(["git", *args], cwd=repo, env=env, text=True,
                              capture_output=True, check=True).stdout.strip()
    git("init", "-q")
    (repo / "bin").mkdir()
    shutil.copyfile(source, repo / "bin/li-compat-audit")
    skill = repo / "skills/example/SKILL.md"
    skill.parent.mkdir(parents=True)
    skill.write_text("---\nname: example\nlayer: foundation\n---\nBody.\n")
    git("add", ".")
    git("commit", "-qm", "test: baseline")
    baseline = git("rev-parse", "HEAD")
    skill.write_text(skill.read_text().replace("layer: foundation", "layer: workflows"))
    git("add", "skills")
    def audit(*args):
        return subprocess.run(["bash", "bin/li-compat-audit", *args], cwd=repo,
                              env=env, capture_output=True, text=True)
    def report(result):
        assert result.returncode == 0, result.stderr
        return (repo / result.stdout.strip()).read_text(encoding="utf-8")
    staged = report(audit("--output", "staged"))
    assert "Q1 — Frontmatter contract changes (1)" in staged, staged
    assert "Q3 — New-defaults on previously-optional fields (1)" in staged, staged
    git("commit", "-qm", "test: change contract")
    committed = report(audit("--against", baseline, "--output", "committed"))
    assert "Q1 — Frontmatter contract changes (1)" in committed, committed
    assert "Q3 — New-defaults on previously-optional fields (1)" in committed, committed
    git("mv", "skills/example/SKILL.md", "skills/example/RENAMED.md")
    renamed = report(audit("--output", "renamed"))
    assert "Q2 — Renames or moves (1)" in renamed, renamed
    before = set(repo.rglob("*.md"))
    for args in (("--against", "does-not-exist"), ("--against",), ("--against", ""),
                 ("--output", "../../escape"), ("--output",), ("--output", "")):
        assert audit(*args).returncode == 2, args
    assert before == set(repo.rglob("*.md")), "invalid input must not write a green report"
print("PASS: compatibility audit sees staged/committed contracts and renames; invalid input fails closed")
PY
