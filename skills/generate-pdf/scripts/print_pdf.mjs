// component: pdf-print-adapter
// implements: ADR-0028, ADR-0029
// intent: .claude/plans/universal-implementation/packages/P12.md
// constraints: accepted A16 provider; explicit source/context/URL authority; no daemon or rasterizer
// last_intent_review: 2026-09-22
import { readFile } from 'node:fs/promises';
import { pathToFileURL } from 'node:url';
import { Admission, BrowserSession, artifactName } from '../../browse/scripts/chromium.mjs';

export function validateRequest(request) {
  if (!request || typeof request !== 'object' || Array.isArray(request)
      || Object.keys(request).some(key => !['url', 'origin', 'python', 'executable', 'outputRoot', 'name', 'context'].includes(key))) {
    throw new Error('Use the explicit print request fields; no launch flags or existing profile');
  }
  for (const key of ['url', 'origin', 'python', 'executable', 'outputRoot', 'name']) {
    if (typeof request[key] !== 'string' || !request[key].trim()) throw new Error(`Missing ${key}`);
  }
  const origin = new URL(request.origin);
  if (!['http:', 'https:'].includes(origin.protocol) || origin.username || origin.password
      || origin.pathname !== '/' || origin.search || origin.hash) throw new Error('Select an explicit HTTP(S) origin');
  if (new URL(request.url).origin !== origin.origin) throw new Error('Document URL differs from the selected origin');
  artifactName(request.name, 'pdf');
  if (!request.context?.session_id || !request.context?.work_map || !request.context?.profile_ref) {
    throw new Error('Caller must supply its verified work/session/profile references');
  }
  return request;
}

export async function printDocument(request) {
  validateRequest(request);
  const admission = new Admission({
    python: request.python, hosts: [new URL(request.origin).hostname], origins: [request.origin],
  });
  let browser;
  let result;
  try {
    browser = await BrowserSession.start({
      executable: request.executable, outputRoot: request.outputRoot, admission, context: request.context,
    });
    const page = await browser.open(request.url);
    await browser.media({ print: true, reducedMotion: true });
    const printState = await browser.read('body');
    const pdf = await browser.print(request.name);
    result = {
      status: 'printed', pdf, run: browser.runDir, provider: browser.evidence.version,
      page, printState, context: request.context,
      visual_inspection: 'unverified; no PDF rasterization or application inspection performed',
      release_clearance: false,
    };
  } finally {
    if (browser) await browser.close();
  }
  return result;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    if (process.argv.length !== 3) throw new Error('Usage: node print_pdf.mjs <explicit-request.json>');
    console.log(JSON.stringify(await printDocument(JSON.parse(await readFile(process.argv[2], 'utf8')))));
  } catch (error) {
    console.error(JSON.stringify({ status: 'error', reason: error.message, release_clearance: false }));
    process.exitCode = 1;
  }
}
