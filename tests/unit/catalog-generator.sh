#!/usr/bin/env bash
# Public catalog generation must be deterministic, Unicode-safe, and fail on drift.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
command -v python3 >/dev/null 2>&1 || { echo 'SKIP: python3 unavailable'; exit 0; }
python3 - "$ROOT" <<'PY'
import importlib.util
import tempfile
from pathlib import Path
import sys

spec = importlib.util.spec_from_file_location('catalog', Path(sys.argv[1]) / 'bin/li-catalog.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
with tempfile.TemporaryDirectory() as tmp:
    root = Path(tmp)
    path = root / 'skills' / 'example' / 'SKILL.md'
    path.parent.mkdir(parents=True)
    path.write_text('---\nname: example\nlayer: foundation\ndescription: Use Unicode → and a pipe | safely\n---\nBody\n', encoding='utf-8')
    first = module.generate(root)
    assert first == module.generate(root)
    assert '→' in first and r'\|' in first
    assert '(example/SKILL.md)' in first
    path.write_text('---\nname: example\nlayer: new-layer\ndescription: Changed\n---\n', encoding='utf-8')
    assert module.generate(root) != first
    assert 'new-layer layer (1 skills)' in module.generate(root)
    path.write_text('---\nname: broken\n---\n', encoding='utf-8')
    try:
        module.generate(root)
    except ValueError:
        pass
    else:
        raise AssertionError('missing frontmatter field was accepted')
print('PASS: deterministic catalog, source links, Unicode, escaping, new layers, and invalid input')
PY
