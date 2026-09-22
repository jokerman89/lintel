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

test('fault injection: transient owned endpoint EBUSY reaches readiness within the original poll budget', async () => {
  const browser = new BrowserSession();
  browser.profileDir = join(process.env.TEMP, 'synthetic-endpoint-profile');
  const reads = [];
  const waits = [];
  const errors = ['ENOENT', 'EBUSY', 'EBUSY'];
  const endpoint = await browser._waitForOwnedEndpoint({
    readEndpoint: async (path, encoding) => {
      reads.push({ path, encoding });
      const code = errors.shift();
      if (code) throw Object.assign(new Error(`Injected ${code}`), { code });
      return '41000\r\n/devtools/browser/synthetic-owned-endpoint\r\n';
    },
    pause: async ms => { waits.push(ms); },
  });
  assert.deepEqual(endpoint, ['41000', '/devtools/browser/synthetic-owned-endpoint']);
  assert.deepEqual(reads, Array(4).fill({
    path: join(browser.profileDir, 'DevToolsActivePort'), encoding: 'utf8',
  }));
  assert.deepEqual(waits, [100, 100, 100]);
  assert.equal(browser.child, undefined);
});

test('fault injection: exhausted owned endpoint EBUSY stops at exactly 100 reads and 100ms delays', async () => {
  const browser = new BrowserSession();
  browser.profileDir = join(process.env.TEMP, 'synthetic-endpoint-profile');
  let reads = 0;
  const waits = [];
  await assert.rejects(browser._waitForOwnedEndpoint({
    readEndpoint: async (path, encoding) => {
      assert.equal(path, join(browser.profileDir, 'DevToolsActivePort'));
      assert.equal(encoding, 'utf8');
      reads++;
      throw Object.assign(new Error('Injected EBUSY'), { code: 'EBUSY' });
    },
    pause: async ms => { waits.push(ms); },
  }), /No verified owned browser endpoint/);
  assert.equal(reads, 100);
  assert.deepEqual(waits, Array(100).fill(100));
  assert.equal(browser.child, undefined);
});

test('fault injection: permissions and other endpoint read errors are never retried', async () => {
  for (const code of ['EACCES', 'EPERM', 'EIO']) {
    const browser = new BrowserSession();
    browser.profileDir = join(process.env.TEMP, 'synthetic-endpoint-profile');
    const failure = Object.assign(new Error(`Injected ${code}`), { code });
    let reads = 0;
    let waits = 0;
    await assert.rejects(browser._waitForOwnedEndpoint({
      readEndpoint: async () => { reads++; throw failure; },
      pause: async () => { waits++; },
    }), error => error === failure);
    assert.equal(reads, 1);
    assert.equal(waits, 0);
  }
});

test('fault injection: endpoint polling preserves launch and child-exit failures', async () => {
  for (const state of ['launch-error', 'already-exited', 'exit-during-wait']) {
    const browser = new BrowserSession();
    browser.profileDir = join(process.env.TEMP, 'synthetic-endpoint-profile');
    const failure = new Error('Injected launch failure');
    if (state === 'launch-error') browser.launchError = failure;
    if (state === 'already-exited') browser.exit = { code: 1, signal: null };
    let reads = 0;
    let waits = 0;
    await assert.rejects(browser._waitForOwnedEndpoint({
      readEndpoint: async () => {
        reads++;
        throw Object.assign(new Error('Injected ENOENT'), { code: 'ENOENT' });
      },
      pause: async ms => {
        assert.equal(ms, 100);
        waits++;
        browser.exit = { code: 1, signal: null };
      },
    }), state === 'launch-error' ? error => error === failure : /Browser exited before its owned endpoint was ready/);
    assert.equal(reads, state === 'exit-during-wait' ? 1 : 0);
    assert.equal(waits, reads);
  }
});

test('fault injection: invalid owned endpoint contents still fail without retry', async () => {
  for (const contents of ['', 'not-a-port\n/devtools/browser/owned',
    '41000\nws://outside.test/devtools/browser/owned', '41000\n/devtools/page/owned']) {
    const browser = new BrowserSession();
    browser.profileDir = join(process.env.TEMP, 'synthetic-endpoint-profile');
    let reads = 0;
    let waits = 0;
    await assert.rejects(browser._waitForOwnedEndpoint({
      readEndpoint: async () => { reads++; return contents; },
      pause: async () => { waits++; },
    }), /No verified owned browser endpoint/);
    assert.equal(reads, 1);
    assert.equal(waits, 0);
  }
});

test('owned page attachment follows the created handle, not the first context event', async () => {
  const browser = new BrowserSession();
  browser.contextId = 'synthetic-owned-context';
  browser.startupTargets = new Map();
  browser.evidence = { lifecycle: [] };
  browser.protocol = { call: async (method, params) => {
    assert.equal(method, 'Target.createTarget');
    assert.deepEqual(params, { url: 'about:blank', browserContextId: browser.contextId });
    for (const [targetId, type, browserContextId] of [
      ['unrelated-page', 'page', 'different-synthetic-context'],
      ['auxiliary-target', 'browser_ui', browser.contextId],
      ['selected-page', 'page', browser.contextId],
    ]) {
      await browser._event({ method: 'Target.attachedToTarget', params: {
        targetInfo: { targetId, type, browserContextId }, waitingForDebugger: true,
        sessionId: `${targetId}-session`,
      } });
    }
    return { targetId: 'selected-page' };
  } };
  await browser._createOwnedPage();
  assert.equal(browser.targetId, 'selected-page');
  assert.equal(browser.sessionId, 'selected-page-session');
  assert.deepEqual([...browser.startupTargets.keys()], ['auxiliary-target', 'selected-page']);
  assert.equal(browser.fault, undefined);
});

test('an unpaused created page cannot establish the guarded session', async () => {
  const browser = new BrowserSession();
  browser.contextId = 'synthetic-owned-context';
  browser.startupTargets = new Map([['selected-page', {
    targetInfo: { targetId: 'selected-page', type: 'page' }, waitingForDebugger: false,
  }]]);
  browser.evidence = { lifecycle: [] };
  browser.protocol = { call: async () => ({ targetId: 'selected-page' }) };
  await assert.rejects(browser._createOwnedPage(), /owned paused page/);
  assert.equal(browser.sessionId, undefined);
});

test('later owned targets are refused and an unsuccessful close remains an error', async () => {
  const browser = new BrowserSession();
  browser.contextId = 'synthetic-owned-context';
  browser.targetId = 'selected-page';
  browser.sessionId = 'selected-page-session';
  browser.evidence = { lifecycle: [] };
  browser.protocol = { call: async (method, params) => {
    assert.equal(method, 'Target.closeTarget');
    assert.deepEqual(params, { targetId: 'popup' });
    return { success: false };
  } };
  await assert.rejects(browser._event({ method: 'Target.attachedToTarget', params: {
    targetInfo: { targetId: 'popup', type: 'page', browserContextId: browser.contextId },
    waitingForDebugger: true, sessionId: 'popup-session',
  } }), /did not close/);
  assert.match(browser.fault.message, /Additional pages/);
  assert.equal(browser.evidence.lifecycle.at(-1).event, 'refused-target');
});

test('Enter carries its character event while navigation keys remain text-free', async () => {
  const browser = new BrowserSession();
  browser.evidence = { operations: [] };
  browser.tasks = new Set();
  const calls = [];
  browser._page = async (method, params) => { calls.push({ method, params }); };
  browser._ready = async () => {};
  browser.read = async () => ({ activeElement: 'synthetic-button' });
  await browser.act({ kind: 'press', key: 'Enter' });
  await browser.act({ kind: 'press', key: 'Tab' });
  assert(calls.every(call => call.method === 'Input.dispatchKeyEvent'));
  assert.equal(calls[0].params.text, '\r');
  assert.equal(calls[0].params.unmodifiedText, '\r');
  assert.equal(calls[1].params.type, 'keyUp');
  assert.equal(calls[1].params.text, undefined);
  assert.equal(calls[2].params.key, 'Tab');
  assert.equal(calls[2].params.text, undefined);
});

test('a policy refusal remains the operation error when its blocked input also times out', async () => {
  const browser = new BrowserSession();
  browser.evidence = { operations: [] };
  browser.tasks = new Set();
  const refusal = new Error('Additional pages are unsupported');
  const transport = new Error('Input.dispatchMouseEvent timed out');
  await assert.rejects(browser._operation('act', { kind: 'click' }, async () => {
    browser.fault = refusal;
    throw transport;
  }), error => error === refusal);
  assert.equal(browser.evidence.operations[0].status, 'error');
  assert.equal(browser.evidence.operations[0].reason, refusal.message);
  assert.equal(browser.evidence.operations[0].provider_error, transport.message);
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

for (const [text, expected] of [['$.50', 0.5], ['-.50', -0.5], ['-$9.50', -9.5]]) {
  test(`numeric extraction preserves the whole signed amount: ${text}`, async () => {
    const result = await extractPage({ read: async () => ({
      url: 'https://app.example.test/', elements: [{ text }],
    }) }, { fields: [{ name: 'amount', selector: '.amount', transform: 'number_extract' }] });
    assert.deepEqual(result, {
      url: 'https://app.example.test/', fields: { amount: expected }, errors: [], ok: true,
    });
  });
}

test('numeric extraction accepts complete ordinary and fractional amounts', async () => {
  for (const [text, expected] of [
    ['$99.50', 99.5], ['-9.50', -9.5], ['+9.50', 9.5], ['0.50 USD', 0.5],
    ['-0.50', -0.5], ['+.50', 0.5], ['$-.50', -0.5], ['-$.50', -0.5],
    ['+$9.50', 9.5], [' $ -0.50 ', -0.5], ['9.5 kg', 9.5], ['0', 0],
  ]) {
    const result = await extractPage({ read: async () => ({
      url: 'https://app.example.test/', elements: [{ text }],
    }) }, { fields: [{ name: 'amount', selector: '.amount', transform: 'number_extract' }] });
    assert.deepEqual(result.fields, { amount: expected }, text);
    assert.equal(result.ok, true, text);
    assert.deepEqual(result.errors, [], text);
  }
});

test('numeric extraction rejects incomplete, ambiguous and unsupported forms without partial values', async () => {
  for (const text of [
    '', 'NaN', 'Infinity', '1e3', '1e', '1,234.50 EUR', '1 234.50', '1\u00a0234.50',
    '1,50', '1.2.3', '9.50 10.50', '1-2', '--9.50', '-$-9.50', '++9', '+-9',
    '.$9.50', '9.', '0x10', '0b10', '1_000', '(9.50)', '\u22129.50', '$.', '-.',
    '--.50', '9/10', '9'.repeat(400),
  ]) {
    const result = await extractPage({ read: async () => ({
      url: 'https://app.example.test/', elements: [{ text }],
    }) }, { fields: [{ name: 'amount', selector: '.amount', transform: 'number_extract' }] });
    assert.equal(result.ok, false, text);
    assert.deepEqual(result.fields, { amount: null }, text);
    assert.equal(result.errors.length, 1, text);
    assert.equal(result.errors[0].field, 'amount', text);
    assert.match(result.errors[0].reason, /numeric|Numeric/, text);
  }
});

test('numeric errors preserve multi, text, trim and prototype-like field names', async () => {
  const result = await extractPage({ read: async selector => ({
    url: 'https://app.example.test/',
    elements: (selector === 'amounts' ? ['$.50', '-$9.50'] :
      selector === 'invalid' ? ['$.50', '--9.50'] : ['  unchanged text  '])
      .map(text => ({ text })),
  }) }, { fields: [
    { name: '__proto__', selector: 'amounts', transform: 'number_extract', multi: true },
    { name: 'constructor', selector: 'invalid', transform: 'number_extract', multi: true },
    { name: 'trimmed', selector: 'text', transform: 'trim' },
    { name: 'text', selector: 'text', transform: 'text' },
  ] });
  assert.equal(Object.getPrototypeOf(result.fields), Object.prototype);
  assert.deepEqual(result.fields.__proto__, [0.5, -9.5]);
  assert.deepEqual(result.fields.constructor, []);
  assert.equal(result.fields.trimmed, 'unchanged text');
  assert.equal(result.fields.text, '  unchanged text  ');
  assert.equal(result.ok, false);
  assert.deepEqual(result.errors.map(error => error.field), ['constructor']);
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
