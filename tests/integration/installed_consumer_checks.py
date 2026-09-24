# component: installed-consumer-test-checks
# implements: ADR-0028, ADR-0029, ADR-0030
# intent: .claude/plans/universal-implementation/packages/P09.md
# constraints: test-only shared assertions; supplied installed code and synthetic targets
# last_intent_review: 2026-09-24
"""Joined installed assertions shared by the kit and domain consumer tests."""
import json
import os
from pathlib import Path
import subprocess
import sys

REVIEW_RUNTIME_RESOURCES = (
    "bin/li-review-evidence.py", "bin/li-review-log", "bin/li-review-read",
    "lib/review_contract.py", "lib/review-schema.json",
    "lib/markdown_source.py", "bin/_audit.sh", "lib/paths.sh",
)


def review_controls(test, bundle, target, *, run=subprocess.run):
    for relative in REVIEW_RUNTIME_RESOURCES:
        test.assertTrue((bundle / relative).is_file(), relative)
    request = target / "control-input.json"
    control = {
        "id": "synthetic-evidence", "kind": "check", "requirement": "mandatory",
        "applicability": "applicable", "status": "pass",
        "reason": "Synthetic installed-consumer observation.",
        "policy": {"source": "spec.md", "version": "fixture-1", "applicability": "Synthetic package",
                   "jurisdiction": None, "actor": None, "effective_date": None},
        "evidence": ["checks.txt"], "observation": {},
    }
    policy = {"required": False, "status": "not_required", "source": None,
              "version": None, "applicability": "not_applicable"}
    for status, code in (("pass", 0), ("fail", 3), ("unverified", 3)):
        control["status"] = status
        request.write_text(json.dumps({"controls": [control], "required_policy": policy}), encoding="utf-8")
        result = run(
            [sys.executable, "-I", "-B", "-S", str(bundle / "bin/li-review-evidence.py"),
             "controls", "--repo", str(target), "--input", str(request)],
            cwd=target, capture_output=True, text=True, encoding="utf-8",
        )
        test.assertEqual(result.returncode, code, result.stdout + result.stderr)
        test.assertEqual(json.loads(result.stdout)["blocked"], status != "pass")


def profile_continuity(test, bundle, target, home, bash, *, run=subprocess.run):
    (target / ".claude").mkdir(exist_ok=True)
    (target / ".claude/profile-requirements.json").write_text(
        json.dumps({"schema_version": 1, "required_pack": "_default"}), encoding="utf-8")
    home.mkdir()
    env = {key: value for key, value in os.environ.items()
           if not key.startswith("LINTEL_") and key != "CLAUDE_SESSION_ID"}
    env.update(HOME=str(home), USERPROFILE=str(home), PYTHONDONTWRITEBYTECODE="1")
    test.assertFalse(any(key.startswith("LINTEL_") for key in env))
    script = '''set -e
source "$1/lib/copilot-env.sh"
lintel_copilot_env "$2"
printf '%s\\n' "$LINTEL_PROFILE_REFERENCE"
'''

    def bootstrap():
        return run([bash, "--noprofile", "--norc", "-c", script, "installed-profile",
                    Path(bundle).as_posix(), Path(target).as_posix()], cwd=target, env=env,
                   capture_output=True, text=True, encoding="utf-8")

    first = bootstrap()
    test.assertEqual(first.returncode, 0, first.stdout + first.stderr)
    reference = json.loads(first.stdout)
    test.assertEqual(reference["name"], "_default")
    repeated = bootstrap()
    test.assertEqual(repeated.returncode, 0, repeated.stdout + repeated.stderr)
    test.assertEqual(json.loads(repeated.stdout), reference)
    selected = target / ".claude/runtime/profiles/selected.json"
    pin = selected.read_bytes()
    manifest = bundle / "packs/_default/pack.yaml"
    content, times = manifest.read_bytes(), manifest.stat()
    manifest.write_bytes(content + b"\n# Same-mtime input drift\n")
    os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
    try:
        refused = bootstrap()
        test.assertNotEqual(refused.returncode, 0, refused.stdout + refused.stderr)
        test.assertIn("PROFILE_", refused.stderr)
        test.assertEqual(refused.stdout, "")
        test.assertEqual(selected.read_bytes(), pin)
    finally:
        manifest.write_bytes(content)
        os.utime(manifest, ns=(times.st_atime_ns, times.st_mtime_ns))
    restored = bootstrap()
    test.assertEqual(restored.returncode, 0, restored.stdout + restored.stderr)
    test.assertEqual(json.loads(restored.stdout), reference)
    test.assertEqual(list(home.iterdir()), [])
    return reference
