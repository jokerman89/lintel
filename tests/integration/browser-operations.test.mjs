// component: browser-operation-tests
// implements: ADR-0028
// intent: .claude/plans/universal-implementation/packages/P11.md
// constraints: policy and ownership tests; not live browser evidence
// last_intent_review: 2026-09-22
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
import test from 'node:test';
import {
  Admission, artifactName, BrowserSession, checkProvider, validateAction,
} from '../../skills/browse/scripts/chromium.mjs';
import { diffRecords, extractPage, validateSchema } from '../../skills/scrape/scripts/extract.mjs';

const policy = (hosts = ['app.example.test'], origins = ['https://app.example.test']) =>
  new Admission({ python: process.env.LINTEL_PYTHON, hosts, origins });

test('P03 exact and explicit wildcard host rules remain different', () => {
  assert.equal(policy().check('https://APP.example.test:443/a#part'), 'https://app.example.test/a');
  for (const url of ['https://sub.app.example.test/', 'https://app.example.test.evil.test/']) {
    assert.throws(() => policy().check(url), /allowlist/);
  }
  const wildcard = policy(['*.example.test'], ['https://a.example.test']);
  assert.equal(wildcard.check('https://a.example.test/'), 'https://a.example.test/');
  assert.throws(() => wildcard.check('https://example.test/'), /allowlist/);
});

test('raw URL and redirect admission refuse ambiguous or credential-bearing inputs', () => {
  for (const url of ['file:///tmp/page', 'javascript:alert(1)', '//app.example.test',
    'https://user:secret@app.example.test', 'https://app.example.test\\@evil.test',
    'https://app.example.test/\nnext']) {
    assert.throws(() => policy().check(url));
  }
  assert.throws(() => policy().redirect('https://app.example.test/', '\t/next'), /Ambiguous/);
  assert.throws(() => policy().redirect('https://app.example.test/', 'http://app.example.test/'), /downgrade/);
  assert.throws(() => policy().redirect('https://app.example.test/', 'https://evil.test/'), /allowlist/);
  assert.equal(policy().redirect('https://app.example.test/a', '/b'), 'https://app.example.test/b');
});

test('an allowed host does not authorize another scheme or local service port', () => {
  const local = policy(['127.0.0.1'], ['http://127.0.0.1:41000']);
  assert.equal(local.check('http://127.0.0.1:41000/read'), 'http://127.0.0.1:41000/read');
  assert.throws(() => local.check('http://127.0.0.1:41001/read'), /origin/);
  assert.throws(() => local.check('https://127.0.0.1:41000/read'), /origin/);
  assert.throws(() => local.check('http://127.1:41000/read'), /allowlist/);
  assert.throws(() => policy([], []).check('https://app.example.test/'));
});

test('policy helper failures never emit a successful admission', () => {
  assert.throws(() => new Admission({ python: join(process.env.TEMP, 'missing-python'),
    hosts: ['app.example.test'], origins: ['https://app.example.test'] }).check('https://app.example.test/'),
  /URL policy|ENOENT/);
});

test('existing-profile and arbitrary launch options fail before any browser process', async () => {
  await assert.rejects(BrowserSession.start({ profile: 'personal' }), /Unknown browser option/);
  await assert.rejects(BrowserSession.start({ args: ['--no-sandbox'] }), /Unknown browser option/);
});

test('unavailable printing stays an operation error rather than poisoning independent work', async () => {
  const browser = new BrowserSession();
  browser.evidence = { operations: [] };
  browser.printAvailable = false;
  await assert.rejects(browser.print(), /print remains unverified/);
  assert.equal(browser.evidence.operations[0].status, 'error');
  assert.equal(browser.fault, undefined);
  assert.equal(browser.closed, undefined);
});

test('a profile directory or absent executable cannot establish browser availability', async t => {
  const directory = await mkdtemp(join(process.env.TEMP, 'browser-profile-only-'));
  t.after(() => rm(directory, { recursive: true }));
  await assert.rejects(checkProvider(directory), /regular file/);
  await assert.rejects(checkProvider(join(directory, 'missing.exe')), /ENOENT/);
  const placeholder = join(directory, 'not-a-browser');
  await writeFile(placeholder, 'synthetic non-executable fixture', { flag: 'wx' });
  const result = await checkProvider(placeholder);
  assert.equal(result.binary_present, true);
  assert.equal(result.executed, false);
  assert.equal(result.version, null);
});

test('schema/transform negatives fail before page reads and preserve missing fields as errors', async () => {
  let reads = 0;
  const browser = { read: async () => {
    reads++;
    return { url: 'https://app.example.test/', elements: [] };
  } };
  await assert.rejects(extractPage(browser, { fields: [{ name: 'price', selecter: '.price' }] }), /Invalid/);
  assert.equal(reads, 0);
  for (const fields of [
    [{ name: 'x', selector: 'h1', multi: 'false' }],
    [{ name: 'x', selector: 'h1', transform: 'eval' }],
    [{ name: 'x', selector: 'h1' }, { name: 'x', selector: 'p' }],
  ]) assert.throws(() => validateSchema({ fields }));
  const result = await extractPage(browser, { fields: [{ name: 'title', selector: 'h1' },
    { name: 'features', selector: 'li', multi: true }] });
  assert.equal(result.ok, false);
  assert.deepEqual(result.fields, { title: null, features: [] });
  assert.equal(result.errors.length, 2);
});

test('extraction preserves trim, numeric and multiple values without guessing locale', async () => {
  const browser = { read: async selector => ({ url: 'https://app.example.test/', elements:
    (selector === 'price' ? ['$99.50'] : selector === 'ambiguous' ? ['1,234.50 EUR'] : [' A ', ' B '])
      .map(text => ({ text })) }) };
  const result = await extractPage(browser, { fields: [
    { name: 'price', selector: 'price', transform: 'number_extract' },
    { name: 'features', selector: 'li', multi: true },
    { name: 'ambiguous', selector: 'ambiguous', transform: 'number_extract' },
    { name: 'single', selector: 'li' },
  ] });
  assert.deepEqual(result.fields, { price: 99.5, features: ['A', 'B'], ambiguous: null, single: null });
  assert.equal(result.errors.length, 2);
});

test('prior-run diff includes failures and is not confused by JSON property order', () => {
  assert.deepEqual(diffRecords([{ url: 'a', fields: { title: 'A' }, ok: true }],
    [{ ok: true, fields: { title: 'A' }, url: 'a' }]), { added: [], removed: [], changed: [] });
  assert.deepEqual(diffRecords([{ url: 'a' }, { url: 'b' }],
    [{ url: 'a', errors: ['missing selector'], ok: false }, { url: 'c' }]),
  { added: ['c'], removed: ['b'], changed: ['a'] });
  assert.throws(() => diffRecords([], [{ url: 'a' }, { url: 'a' }]), /unique/);
});

test('artifact names cannot escape an owned run or overwrite nested user paths', () => {
  assert.equal(artifactName('screen.png', 'png'), 'screen.png');
  for (const name of ['../screen.png', '..\\screen.png', '/screen.png', 'C:\\screen.png',
    'nested/screen.png', '.png', 'screen.pdf', 'a.png:secret']) {
    assert.throws(() => artifactName(name, 'png'));
  }
});

test('action arguments are bounded data, not executable page code or invented verbs', () => {
  assert.deepEqual(validateAction({ kind: 'click', selector: '#increment' }),
    { kind: 'click', selector: '#increment' });
  assert.deepEqual(validateAction({ kind: 'fill', selector: '#name', value: 'Synthetic Ada' }),
    { kind: 'fill', selector: '#name', value: 'Synthetic Ada' });
  for (const action of [
    { kind: 'evaluate', code: 'fetch("https://outside.test")' },
    { kind: 'click', selector: '', force: true },
    { kind: 'fill', selector: '#name', value: 42 },
    { kind: 'press', key: 'Control+Alt+Delete' },
    { kind: 'wait', selector: '#missing', timeout: -1 },
  ]) assert.throws(() => validateAction(action));
});

test('all four retained entry points share the same operation and ownership reference', async () => {
  for (const name of ['browse', 'open-managed-browser', 'setup-browser-cookies', 'scrape']) {
    const text = await readFile(new URL(`../../skills/${name}/SKILL.md`, import.meta.url), 'utf8');
    assert.match(text, /references\/browser-operations\.md/);
    assert.doesNotMatch(text, /Codex and Copilot do not have native browser-control|--force-prod|Browser detached/);
  }
});
