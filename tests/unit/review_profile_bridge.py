# component: review-profile-bridge-test
# implements: ADR-0028
# intent: .claude/plans/universal-implementation/packages/P05.md
# constraints: explicit approved P07 source; synthetic target/home; no private profiles
# last_intent_review: 2026-09-20
"""Run after P07 is available: python review_profile_bridge.py --profile-source <trusted root>."""
import argparse
import json
import os
from pathlib import Path
import sys
import unittest

from review_evidence import Fixture, control
from review_contract import evaluate_controls, validate_shape


class ProfileBridge(Fixture):
    def setUp(self):
        super().setUp()
        from profile_context import ProfileConfig
        home = self.root / "profile-home"
        self.manifest = home / "packs" / "synthetic-strict" / "pack.yaml"
        self.manifest.parent.mkdir(parents=True)
        self.manifest.write_text(
            'schema_version: "1"\nname: synthetic-strict\nversion: 1.0.0\n'
            'voice:\n  default_tier: internal\n'
            'compliance:\n  mode: hard\n  hooks: [synthetic-evidence]\n'
            'navigation:\n  default_workflow: cycle\n',
            encoding="utf-8",
        )
        self.write_json(".claude/profile-requirements.json", {
            "schema_version": 1, "required_pack": "synthetic-strict",
        })
        self.cfg = ProfileConfig(
            source=PROFILE_SOURCE.resolve(), repo=self.repo.resolve(),
            home=home.resolve(), packs=(home / "packs").resolve(),
            pointer=(home / "packs" / "active-pack").resolve(), context_id="synthetic-work",
        )

    def produce(self):
        from profile_context import load_profile_context, profile_reference, required_policy, verify_profile_reference
        record = load_profile_context(self.cfg, create=True)
        reference = profile_reference(record)
        validate_shape(reference, "profile")
        verified = verify_profile_reference(reference, self.cfg)
        policy = required_policy(verified)
        validate_shape(policy, "requiredPolicy")
        return reference, policy

    def test_real_required_profile_producer_to_review_and_ship(self):
        reference, policy = self.produce()
        self.assertTrue(policy["required"])
        self.assertEqual(policy["status"], "loaded")
        required_control = control("synthetic-evidence")
        result = evaluate_controls([required_control], required_policy=policy)
        self.assertFalse(result["blocked"])
        self.request.update(profile=reference, required_policy=policy)
        self.request["required_controls"].append("synthetic-evidence")
        self.record(controls=[control(), control("quality"), required_control])
        self.log()
        self.corroborate()
        self.assertEqual(self.qa().returncode, 0)
        self.read()
        self.ship()

    def test_missing_required_policy_cannot_become_neutral(self):
        from profile_context import ProfileError, load_profile_context
        self.manifest.unlink()
        with self.assertRaises(ProfileError) as raised:
            load_profile_context(self.cfg, create=True)
        self.assertEqual("PROFILE_REQUIRED", raised.exception.code)

    def test_same_mtime_profile_drift_stops_reference_consumption(self):
        from profile_context import ProfileError, verify_profile_reference
        reference, _ = self.produce()
        before = self.manifest.stat()
        text = self.manifest.read_text(encoding="utf-8")
        self.manifest.write_text(text.replace("mode: hard", "mode: advisory"), encoding="utf-8")
        os.utime(self.manifest, ns=(before.st_atime_ns, before.st_mtime_ns))
        with self.assertRaises(ProfileError) as raised:
            verify_profile_reference(reference, self.cfg)
        self.assertEqual("PROFILE_DRIFT", raised.exception.code)

    def test_public_shell_cold_resume_policy_into_review_gate(self):
        # Invocation-required selection must survive without a repository selector
        # or the original host's ambient session ID.
        (self.repo / ".claude/profile-requirements.json").unlink()
        original_environment = dict(self.env)
        shell_environment = dict(self.env)
        for name in list(shell_environment):
            if name.startswith("LINTEL_PROFILE") or name in ("LINTEL_SESSION_ID", "CLAUDE_SESSION_ID"):
                shell_environment.pop(name)
        shell_environment.update({
            "LINTEL_SOURCE_ROOT": PROFILE_SOURCE.resolve().as_posix(),
            "LINTEL_HOME": self.cfg.home.as_posix(),
            "LINTEL_PACKS_DIR": self.cfg.packs.as_posix(),
            "LINTEL_ACTIVE_PACK_FILE": self.cfg.pointer.as_posix(),
        })
        script = self.root / "public-profile.sh"
        reference_file = self.root / "shell-reference.json"
        verified_file = self.root / "shell-verified.json"
        policy_file = self.root / "shell-policy.json"
        mode_file = self.root / "shell-mode.txt"
        shell_environment.update({
            "BRIDGE_REFERENCE": reference_file.as_posix(),
            "BRIDGE_VERIFIED": verified_file.as_posix(),
            "BRIDGE_POLICY": policy_file.as_posix(),
            "BRIDGE_MODE": mode_file.as_posix(),
        })
        try:
            self.env = {**shell_environment, "LINTEL_PROFILE_PACK": "synthetic-strict"}
            script.write_bytes(
                b'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                b'bind_profile_context shell-profile-work\n'
            )
            produced = self.run_command(["bash", script], ok=0)
            reference_file.write_text(produced.stdout, encoding="utf-8")
            reference = json.loads(produced.stdout)
            validate_shape(reference, "profile")
            for ambient in ("", "different-cold-host"):
                with self.subTest(ambient=ambient or "no-host-id"):
                    self.env = dict(shell_environment)
                    if ambient:
                        self.env["CLAUDE_SESSION_ID"] = ambient
                    script.write_bytes(
                        b'set -euo pipefail\nsource "$LINTEL_SOURCE_ROOT/lib/pack-resolver.sh"\n'
                        b'verify_profile_context "$BRIDGE_REFERENCE" > "$BRIDGE_VERIFIED"\n'
                        b'profile_required_policy > "$BRIDGE_POLICY"\n'
                        b'resolve_pack_field compliance.mode > "$BRIDGE_MODE"\n'
                    )
                    self.run_command(["bash", script], ok=0)
                    self.assertEqual(reference, json.loads(verified_file.read_text(encoding="utf-8")))
                    policy = json.loads(policy_file.read_text(encoding="utf-8"))
                    self.assertTrue(policy["required"], "Verified required selection became optional/neutral")
                    self.assertEqual(policy["status"], "loaded")
                    self.assertEqual("hard", mode_file.read_text(encoding="utf-8").strip())
                    validate_shape(policy, "requiredPolicy")
                    self.env = original_environment
                    self.request.update(profile=reference, required_policy=policy)
                    if "synthetic-evidence" not in self.request["required_controls"]:
                        self.request["required_controls"].append("synthetic-evidence")
                    self.prepare()
                    self.record(controls=[control(), control("quality"), control("synthetic-evidence")])
                    self.log()
                    self.corroborate()
                    self.assertEqual(self.qa().returncode, 0)
                    self.read()
                    self.ship()
        finally:
            self.env = original_environment


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile-source", type=Path, required=True)
    args = parser.parse_args()
    PROFILE_SOURCE = args.profile_source
    if not (PROFILE_SOURCE / "lib" / "profile_context.py").is_file():
        parser.error("P07's approved profile_context.py is required; the bridge is not a stub/skip")
    sys.path.insert(0, str(PROFILE_SOURCE / "lib"))
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(ProfileBridge)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
