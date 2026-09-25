# component: browser-design-consolidation-tests
# implements: ADR-0015, ADR-0028, ADR-0029
# intent: .claude/plans/legacy-cleanup/spec.md
# constraints: source contracts and synthetic module calls; no live browser or PDF reader
# last_intent_review: 2026-09-25
"""Check consolidated entrypoints and their retained resource/consumer contracts."""
from __future__ import annotations

import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[2]


class Consolidation(unittest.TestCase):
    def read(self, relative: str) -> str:
        return (ROOT / relative).read_text(encoding="utf-8")

    def requires(self, relative: str, *tokens: str) -> str:
        text = self.read(relative)
        for token in tokens:
            self.assertTrue(token in text, f"{relative}: missing {token}")
        return text

    def test_web_modes_keep_distinct_inputs_and_real_resources(self):
        self.requires(
            "skills/web-session/SKILL.md", "name: web-session",
            "--mode", "browse", "scrape", "open", "cookies",
            "references/browser-operations.md", "references/browse.md",
            "references/scrape.md", "references/open.md", "references/cookies.md",
        )
        self.requires(
            "skills/web-session/references/browse.md",
            "--actions", "--viewport", "--out", "--headed",
            "P03", "profile_ref", "redirect", "Close",
        )
        self.requires(
            "skills/web-session/references/scrape.md",
            "--urls", "--schema", "--concurrency", "--rate-limit", "--diff",
            "1000ms", "maximum 10", "effective concurrency 1", "Retry-After",
            "number_extract", "extractPage", "diffRecords", "robots",
        )
        self.requires(
            "skills/web-session/references/open.md",
            "--url", "--profile", "--check", "--devtools",
            "checkProvider", "executed:false", "version:null", "headed:true",
        )
        self.requires(
            "skills/web-session/references/cookies.md",
            "--service", "--login-url", "--profile", "--check",
            "MFA", "non-secret", "user-reported", "cookie export/import",
        )

    def test_old_commands_retired_without_removing_pdf_writer(self):
        for name in (
            "browse", "scrape", "open-managed-browser", "setup-browser-cookies",
            "design-consultation", "design-shotgun", "design-html", "design-review",
            "document-generate",
        ):
            self.assertFalse((ROOT / "skills" / name / "SKILL.md").exists(), name)
        self.requires(
            "skills/make-pdf/SKILL.md", "--input", "--format", "--orientation",
            "--header-footer", "--print-css", "--no-background",
            "../generate-pdf/SKILL.md", "deferred",
        )

    def test_compatibility_resources_are_the_same_provider_not_forks(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required; no dependency install is performed")
        script = """
import assert from 'node:assert/strict';
import * as current from './skills/web-session/scripts/chromium.mjs';
import * as old from './skills/browse/scripts/chromium.mjs';
import * as extraction from './skills/web-session/scripts/extract.mjs';
import * as oldExtraction from './skills/scrape/scripts/extract.mjs';
assert.deepEqual(Object.keys(current), Object.keys(old));
for (const key of Object.keys(current)) assert.equal(current[key], old[key]);
assert.deepEqual(Object.keys(extraction), Object.keys(oldExtraction));
for (const key of Object.keys(extraction)) assert.equal(extraction[key], oldExtraction[key]);
for (const method of ['open', 'read', 'act', 'media', 'screenshot', 'print', 'close'])
  assert.equal(typeof current.BrowserSession.prototype[method], 'function');
console.log('same provider and extraction exports; seven operations retained');
"""
        result = subprocess.run(
            [node, "--input-type=module", "--eval", script], cwd=ROOT,
            text=True, capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.requires(
            "skills/browse/references/browser-operations.md",
            "../../web-session/references/browser-operations.md",
        )

    def test_provider_data_operations_need_no_launch_or_personal_state(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required; no dependency install is performed")
        script = """
import assert from 'node:assert/strict';
import { BrowserSession, artifactName, validateAction } from './skills/web-session/scripts/chromium.mjs';
import { extractPage, diffRecords } from './skills/web-session/scripts/extract.mjs';
await assert.rejects(BrowserSession.start({ profile: 'unselected' }), /Unknown browser option/);
await assert.rejects(BrowserSession.start({ args: ['--no-sandbox'] }), /Unknown browser option/);
assert.equal(artifactName('preview.pdf', 'pdf'), 'preview.pdf');
assert.throws(() => artifactName('../preview.pdf', 'pdf'));
assert.throws(() => validateAction({ kind: 'evaluate', code: 'not executed' }));
assert.deepEqual(validateAction({ kind: 'press', key: 'Tab' }), { kind: 'press', key: 'Tab' });
const page = { read: async selector => ({
  url: 'https://fixture.example.test/',
  elements: (selector === '.price' ? ['-$9.50'] :
    selector === '.items' ? [' One ', ' Two '] : []).map(text => ({ text })),
}) };
const first = await extractPage(page, { fields: [
  { name: 'price', selector: '.price', transform: 'number_extract' },
  { name: 'items', selector: '.items', multi: true },
] });
assert.deepEqual(first.fields, { price: -9.5, items: ['One', 'Two'] });
assert.equal(first.ok, true);
const missing = await extractPage(page, { fields: [{ name: 'missing', selector: '.absent' }] });
assert.equal(missing.ok, false);
assert.deepEqual(missing.fields, { missing: null });
assert.equal(missing.errors.length, 1);
assert.deepEqual(diffRecords([first], [missing]), {
  added: [], removed: [], changed: ['https://fixture.example.test/'],
});
console.log('no-launch option/artifact/action refusals and synthetic extraction/diff passed');
"""
        result = subprocess.run(
            [node, "--input-type=module", "--eval", script], cwd=ROOT,
            text=True, capture_output=True, timeout=30, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_design_modes_preserve_advice_and_variant_work(self):
        self.requires(
            "skills/frontend-design/SKILL.md", "--mode",
            "references/advice.md", "references/variants.md",
            "frontend-design-spec.json", "schema_version", "renderer-args",
            "--from-frontend-design", "design_contract", "profile_ref",
        )
        self.requires(
            "skills/frontend-design/references/advice.md",
            "--scope", "--read-design-system", "--cross-check",
            "three", "cost", "risk", "upside", "downside", "No code",
        )
        self.requires(
            "skills/frontend-design/references/variants.md",
            "--seed", "--count", "--axis", "--only", "--brief", "--out",
            "2-8", "default 4", "palette", "layout", "density",
            "motion-language", "type-system", "index.html", "50MB",
            "generate-web", "disjoint", "P05", "failed",
        )

    def test_built_review_extends_rather_than_replaces_json_contract(self):
        self.requires(
            "skills/frontend-design-review/SKILL.md", "references/built-review.md",
            "design-review.json", "normalize_dimensions", "validate_review",
            "typography_hierarchy", "motion_coherence", "shader_perf_budget",
            "accessibility_wcag", "brand_conformance", "responsive_fidelity",
            "release_clearance", "4.5:1",
        )
        self.requires(
            "skills/frontend-design-review/references/built-review.md",
            "--url", "--routes", "--viewport", "--baseline-ref",
            "--include-copy-pillar", "1440x900,375x812",
            "Visual polish", "Accessibility", "Motion", "Copy",
            "Layout/density", "Brand consistency", "file:line",
            "screenshot", "web-session --mode browse", "unverified",
            "standalone", "snapshot/inspect", "never an invented",
        )

    def test_mockup_remains_a_real_single_file_rendering_route(self):
        self.requires(
            "skills/generate-web/SKILL.md", "--mode", "references/mockup.md",
            "--from-pipeline", "--from-frontend-design", "content.md",
            "design-spec.json", "frontend-design-spec.json", "schema_version",
        )
        self.requires(
            "skills/generate-web/references/mockup.md", "--brief", "--reference",
            "--tokens", "--inherit-project", "--copy-tier", "--out", "--preview",
            "internal", "placeholder", "pack-voice", "single-file",
            "<style>", "<script>", "design_contract.load_design",
            "web-session --mode", "loopback", "health",
        )

    def test_generate_docs_keeps_targets_source_fidelity_and_handoff(self):
        self.requires(
            "skills/generate-docs/SKILL.md", "name: generate-docs", "--source",
            "--target", "--voice", "--depth", "--out",
            "reference", "customer-guide", "tutorial", "DRAFT",
            "public exports", "errors", "units", "limitations", "source",
            "DocWriter", "generate", "Markdown", "overwrite",
        )

    def test_current_owned_routing_has_no_retired_entrypoint(self):
        retired = (
            "browse", "scrape", "open-managed-browser", "setup-browser-cookies",
            "design-consultation", "design-shotgun", "design-html", "design-review",
            "document-generate", "plan-eng-review", "plan-design-review",
        )
        expression = re.compile(r"/(?:li:|li-)?(?:" + "|".join(retired) + r")(?=[`\s])")
        for name in (
            "web-session", "frontend-design", "frontend-design-review", "generate-docs",
            "generate-web", "generate-app", "generate-ppt", "generate-qa", "make-pdf",
        ):
            for path in (ROOT / "skills" / name).rglob("*.md"):
                self.assertIsNone(expression.search(path.read_text(encoding="utf-8")), str(path))

    def test_workbook_and_pipeline_writers_remain_available(self):
        for name in ("generate-ppt", "generate-word", "generate-xlsx", "generate-visio"):
            self.assertTrue((ROOT / "skills" / name / "SKILL.md").is_file(), name)
        self.assertTrue((ROOT / "skills/generate-xlsx/scripts/check_xlsx.py").is_file())
        self.assertTrue((ROOT / "skills/generate/scripts/pipeline_inputs.py").is_file())
        schema = json.loads(self.read("skills/design-dna/references/design-contract.schema.json"))
        self.assertIn("x-renderers", schema)
        self.assertEqual(schema["x-renderers"]["single-file"]["skill"], "generate-web")


if __name__ == "__main__":
    unittest.main(verbosity=2)
