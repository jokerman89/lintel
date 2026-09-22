// component: document-pdf-request-tests
// implements: ADR-0028
// intent: .claude/plans/universal-implementation/packages/P12.md
// constraints: pure request validation; no browser, network or process launch
// last_intent_review: 2026-09-22
import assert from 'node:assert/strict';
import test from 'node:test';
import { validateRequest } from '../../skills/generate-pdf/scripts/print_pdf.mjs';

const request = () => ({
  url: 'http://127.0.0.1:54321/document', origin: 'http://127.0.0.1:54321',
  python: 'explicit-python', executable: 'explicit-browser', outputRoot: 'explicit-owned-root',
  name: 'document.pdf', context: { session_id: 'synthetic', work_map: 'work.json', profile_ref: { declared: true } },
});

test('carries explicit verified context without interpreting another schema', () => {
  const data = request();
  assert.equal(validateRequest(data), data);
});
test('refuses guessed launch or persistent-profile options', () => {
  for (const field of ['profile', 'headed', 'launchFlags']) {
    assert.throws(() => validateRequest({ ...request(), [field]: 'not-authorized' }), /explicit print request/);
  }
});
test('refuses different loopback port and unrelated origin', () => {
  for (const url of ['http://127.0.0.1:54322/document', 'https://example.invalid/document']) {
    assert.throws(() => validateRequest({ ...request(), url }), /differs/);
  }
});
test('refuses file input and credential-bearing origin', () => {
  for (const origin of ['file:///tmp/source.html', 'https://user:secret@example.invalid']) {
    assert.throws(() => validateRequest({ ...request(), origin }), /explicit HTTP/);
  }
});
test('refuses traversal and wrong artifact extension', () => {
  for (const name of ['../document.pdf', 'document.png', 'C:\\document.pdf']) {
    assert.throws(() => validateRequest({ ...request(), name }), /Artifact/);
  }
});
test('missing work and profile cannot masquerade as bound output', () => {
  assert.throws(() => validateRequest({ ...request(), context: { session_id: 'synthetic' } }), /verified/);
});
