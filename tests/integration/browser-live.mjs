// component: browser-live-fixture
// implements: ADR-0028, ADR-0029
// intent: .claude/plans/universal-implementation/packages/P11.md
// constraints: explicit owned loopback fixtures; no personal profiles or credentials
// last_intent_review: 2026-09-22
import assert from 'node:assert/strict';
import childProcess from 'node:child_process';
import { readFile, writeFile } from 'node:fs/promises';
import { syncBuiltinESMExports } from 'node:module';
import { join } from 'node:path';
import { Admission, BrowserSession } from '../../skills/web-session/scripts/chromium.mjs';
import { diffRecords, extractPage } from '../../skills/web-session/scripts/extract.mjs';

const request = JSON.parse(await readFile(process.argv[2], 'utf8'));
const { origin, trapOrigin, denyProxy, executable, outputRoot, context } = request;
const proxy = new URL(denyProxy);
assert.equal(proxy.protocol, 'http:');
assert.equal(proxy.hostname, '127.0.0.1');
assert(proxy.port && !proxy.username && !proxy.password && proxy.pathname === '/' && !proxy.search && !proxy.hash);
const launches = [];
const originalSpawn = childProcess.spawn;
childProcess.spawn = (program, args, options) => {
  assert.equal(program, executable);
  assert(args.some(arg => arg.startsWith(`--user-data-dir=${outputRoot}`)));
  args.splice(args.length - 1, 0, `--proxy-server=${proxy.origin}`);
  const child = originalSpawn(program, args, options);
  launches.push({ executable: program, args: [...args], pid: child.pid });
  return child;
};
syncBuiltinESMExports();
const cases = [];
const admission = new Admission({ python: process.env.LINTEL_PYTHON, hosts: ['127.0.0.1'], origins: [origin] });
let failure;

async function scenario(name, run) {
  const item = { name, outcome: 'error' };
  cases.push(item);
  let browser;
  try {
    browser = await BrowserSession.start({ executable, outputRoot, admission, context, captureConsole: true });
    item.run = browser.runDir;
    item.result = await run(browser);
    item.outcome = 'pass';
  } catch (error) { item.reason = error.message; throw error; }
  finally {
    if (browser) {
      await browser.close();
      item.evidence = join(browser.runDir, 'evidence.json');
      assert.deepEqual(browser.evidence.context, context);
      assert(browser.evidence.lifecycle.some(x => x.event === 'context-disposed'));
      assert(browser.evidence.lifecycle.some(x => x.event === 'owned-profile-removed'));
      assert.equal(browser.evidence.lifecycle.find(x => x.event === 'closed').errors.length, 0);
    }
  }
}

try {
  await scenario('read-action-keyboard-motion-screenshot-print-extract', async browser => {
    const first = await browser.open(`${origin}/start`);
    assert.equal(first.title, 'A16 Synthetic Preview');
    assert.equal(first.url, `${origin}/page`);
    assert.equal((await browser.read('#result')).elements[0].text, '0');
    const schema = { fields: [
      { name: 'title', selector: 'h1', transform: 'trim' },
      { name: 'price', selector: '#price', transform: 'number_extract' },
      { name: 'features', selector: '#features li', multi: true, transform: 'trim' },
    ] };
    const prior = await extractPage(browser, schema);
    assert.equal(prior.ok, true);
    assert.equal(prior.fields.price, 99.5);
    await browser.act({ kind: 'fill', selector: '#name', value: 'Synthetic Ada' });
    assert.equal((await browser.read('#name')).elements[0].value, 'Synthetic Ada');
    await browser.act({ kind: 'click', selector: '#increment' });
    await browser.act({ kind: 'wait', selector: '#result', text: '1' });
    await browser.act({ kind: 'fill', selector: '#name', value: 'Synthetic Ada' });
    await browser.act({ kind: 'press', key: 'Tab' });
    assert.equal((await browser.read()).activeElement, 'increment');
    await browser.act({ kind: 'press', key: 'Enter' });
    const after = await browser.act({ kind: 'wait', selector: '#result', text: '2' });
    await browser.media({ reducedMotion: true });
    const motion = await browser.read('#motion');
    assert.equal(motion.reducedMotion, true);
    assert.equal(motion.elements[0].animation, 'none');
    const contrast = await browser.read('#low-contrast');
    const extracted = await extractPage(browser, schema);
    assert.deepEqual(extracted.fields.features, ['Owned session', 'Checked redirects', 'Real print']);
    assert.equal(extracted.fields.price, 101.5);
    const diff = diffRecords([prior], [extracted]);
    assert.deepEqual(diff, { added: [], removed: [], changed: [`${origin}/page`] });
    const missing = await extractPage(browser, { fields: [{ name: 'missing', selector: '#missing' }] });
    assert.equal(missing.ok, false);
    assert.equal(missing.errors.length, 1);
    const dom = await browser.read('main', { html: true });
    const domPath = join(browser.runDir, 'dom.json');
    await writeFile(domPath, JSON.stringify(dom, null, 2), { flag: 'wx' });
    const screen = await browser.screenshot('screen.png');
    await browser.media({ print: true, reducedMotion: true });
    const printState = await browser.read('#print-summary');
    assert.equal(printState.elements[0].display, 'block');
    assert.equal(printState.elements[0].text, 'Print summary: 2');
    const printMedia = await browser.screenshot('print-media.png');
    const pdf = await browser.print('preview.pdf');
    const console = browser.consoleMessages();
    assert(console.some(x => x.values.includes('A16 synthetic ready')));
    await assert.rejects(browser.screenshot('screen.png'), /EEXIST/);
    await assert.rejects(browser.act({ kind: 'fill', selector: '#password', value: 'not-a-credential' }), /credential/);
    await assert.rejects(browser.act({ kind: 'click', selector: '#missing' }), /exactly one/);
    return { after, motion, contrast, prior, extracted, missing, diff, screen, printMedia, pdf, domPath, printState, console };
  });
  await scenario('initial-origin-refused-before-navigation', async browser => {
    await assert.rejects(browser.open(`${trapOrigin}/never`), /origin/);
    assert.equal(browser.evidence.network.length, 0);
    return { refused_before_navigate: true };
  });
  await scenario('second-hop-foreign-redirect-refused', async browser => {
    await assert.rejects(browser.open(`${origin}/redirect-chain`), /allowlist/);
    assert(browser.evidence.network.some(x => x.stage === 'response' && x.admitted === false));
    return { refused_before_destination: true };
  });
  await scenario('loop-refused-before-repeated-request', async browser => {
    await assert.rejects(browser.open(`${origin}/loop-a`), /loop|limit/);
    assert.equal(browser.evidence.network.filter(x => x.stage === 'request').length, 2);
    return { loop_requests: 2 };
  });
  await scenario('script-navigation-refused', async browser => {
    await assert.rejects(async () => {
      await browser.open(`${origin}/script-redirect`);
      await browser.act({ kind: 'wait', selector: '#never' });
    }, /origin/);
    return { script_destination_refused: true };
  });
  await scenario('subresource-origin-refused', async browser => {
    await assert.rejects(browser.open(`${origin}/foreign-image`), /origin/);
    return { resource_destination_refused: true };
  });
  await scenario('popup-paused-and-refused', async browser => {
    await browser.open(`${origin}/page`);
    await assert.rejects(browser.act({ kind: 'click', selector: '#popup' }), /Additional pages/);
    assert(browser.evidence.lifecycle.some(x => x.event === 'refused-target'));
    return { popup_refused: true };
  });
  await scenario('http-auth-remains-on-user-surface', async browser => {
    await assert.rejects(browser.open(`${origin}/basic-auth`), /Authentication|HTTP document/);
    return { no_credentials_supplied: true };
  });
} catch (error) {
  failure = error;
} finally {
  childProcess.spawn = originalSpawn;
  syncBuiltinESMExports();
  await writeFile(join(outputRoot, 'actual-launches.json'), JSON.stringify({
    authority: '75ca6ed4d549a1c757fc8886989b514e107e9e03',
    fixture_only: 'Added child-process deny-proxy argument; no forwarding or OS-wide egress claim.',
    denyProxy: proxy.origin, launches,
  }, null, 2), { flag: 'wx' });
  await writeFile(join(outputRoot, 'live-results.json'), JSON.stringify({ context, cases,
    outcome: failure ? 'error' : 'pass', reason: failure?.message ?? null }, null, 2), { flag: 'wx' });
}
for (const item of cases) console.log(`${item.outcome}: ${item.name}${item.reason ? `: ${item.reason}` : ''}`);
if (failure) throw failure;
