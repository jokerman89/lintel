// component: owned-chromium-operations
// implements: ADR-0028
// intent: .claude/plans/universal-implementation/packages/P11.md
// constraints: one explicit executable, fresh owned context, P03 admission; no daemon or credentials
// last_intent_review: 2026-09-22
import { spawn, spawnSync } from 'node:child_process';
import { createWriteStream } from 'node:fs';
import { lstat, mkdir, mkdtemp, readFile, rm, writeFile } from 'node:fs/promises';
import { dirname, isAbsolute, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { setTimeout as delay } from 'node:timers/promises';

const source = resolve(dirname(fileURLToPath(import.meta.url)), '../../..');
const urlHelper = join(source, 'lib', 'url_policy.py');
const redirectStatuses = new Set([301, 302, 303, 307, 308]);
const timeout = 15000;

function requireValue(condition, reason) {
  if (!condition) throw new Error(reason);
}

export class Admission {
  constructor({ python, hosts, origins }) {
    requireValue(typeof python === 'string' && isAbsolute(python), 'Select an absolute Python executable for P03 URL policy');
    requireValue(Array.isArray(hosts) && hosts.length && hosts.every(x => typeof x === 'string'), 'Explicit host allowlist required');
    requireValue(Array.isArray(origins) && origins.length && origins.every(x => typeof x === 'string'), 'Explicit origin allowlist required');
    this.python = python;
    this.hosts = [...hosts];
    this.origins = origins.map(value => {
      const admitted = this._policy(value);
      const parsed = new URL(admitted);
      requireValue(parsed.pathname === '/' && !parsed.search, 'Origins must not contain paths or queries');
      return parsed.origin;
    });
  }

  _policy(url, location) {
    requireValue(typeof url === 'string' && (location === undefined || typeof location === 'string'), 'URLs must be strings');
    const args = [urlHelper, url, ...this.hosts.flatMap(host => ['--allow', host])];
    if (location !== undefined) args.push('--redirect', location);
    const result = spawnSync(this.python, args, { encoding: 'utf8', windowsHide: true, timeout, maxBuffer: 65536 });
    if (result.error || result.status !== 0) {
      throw new Error(`URL policy refused: ${result.error?.message || result.stderr.trim() || `exit ${result.status}`}`);
    }
    requireValue(Boolean(result.stdout.trim()), 'URL policy returned no admitted URL');
    return result.stdout.trim();
  }

  check(url) {
    const admitted = this._policy(url);
    requireValue(this.origins.includes(new URL(admitted).origin), 'URL origin is outside the explicit scheme/host/port boundary');
    return admitted;
  }

  redirect(current, location) {
    return this.check(this._policy(current, location));
  }
}

export async function checkProvider(executable) {
  requireValue(typeof globalThis.WebSocket === 'function', 'This provider requires Node.js with built-in WebSocket (22+)');
  requireValue(typeof executable === 'string' && isAbsolute(executable), 'Select an absolute browser executable; no profile discovery');
  const stat = await lstat(executable);
  requireValue(stat.isFile() && !stat.isSymbolicLink(), 'Browser executable must be an explicitly selected regular file');
  return { executable, binary_present: true, executed: false, version: null };
}

export function artifactName(name, extension) {
  requireValue(typeof name === 'string' && name.length <= 80
    && /^[a-zA-Z0-9][a-zA-Z0-9._-]*$/.test(name) && name.endsWith(`.${extension}`),
  'Artifact must be a simple filename of the requested format inside the owned run');
  return name;
}

export function validateAction(action) {
  requireValue(action && typeof action === 'object' && !Array.isArray(action), 'Action must be an object');
  const fields = {
    click: ['kind', 'selector'], fill: ['kind', 'selector', 'value'],
    press: ['kind', 'key'], wait: ['kind', 'selector', 'text'],
  };
  requireValue(Object.hasOwn(fields, action.kind), 'Unsupported action; use click, fill, press or wait');
  requireValue(Object.keys(action).every(key => fields[action.kind].includes(key)), 'Unexpected action argument');
  if (action.kind === 'press') {
    requireValue(['Tab', 'Enter', 'Escape', 'ArrowDown', 'ArrowUp'].includes(action.key), 'Unsupported page key');
  } else {
    requireValue(typeof action.selector === 'string' && action.selector.trim(), 'A nonempty selector is required');
  }
  if (action.kind === 'fill') requireValue(typeof action.value === 'string', 'Fill value must be text');
  if (action.kind === 'wait' && action.text !== undefined) requireValue(typeof action.text === 'string', 'Wait text must be text');
  return { ...action };
}

class Protocol {
  constructor(socket) {
    this.socket = socket;
    this.next = 0;
    this.pending = new Map();
    this.onEvent = () => {};
    socket.addEventListener('message', event => {
      const message = JSON.parse(event.data);
      if (!message.id) { this.onEvent(message); return; }
      const pending = this.pending.get(message.id);
      if (!pending) return;
      this.pending.delete(message.id);
      clearTimeout(pending.timer);
      if (message.error) pending.reject(new Error(`${pending.method}: ${message.error.message}`));
      else pending.resolve(message.result);
    });
    const closed = () => {
      for (const pending of this.pending.values()) {
        clearTimeout(pending.timer);
        pending.reject(new Error(`Browser connection closed during ${pending.method}`));
      }
      this.pending.clear();
    };
    socket.addEventListener('close', closed);
    socket.addEventListener('error', closed);
  }

  call(method, params = {}, sessionId) {
    return new Promise((resolveCall, reject) => {
      const id = ++this.next;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error(`${method} timed out`));
      }, timeout);
      this.pending.set(id, { resolve: resolveCall, reject, timer, method });
      this.socket.send(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }));
    });
  }
}

export class BrowserSession {
  static async start(options) {
    requireValue(options && typeof options === 'object' && Object.keys(options).every(key =>
      ['executable', 'outputRoot', 'admission', 'context', 'headed', 'viewport', 'captureConsole'].includes(key)),
    'Unknown browser option; existing profiles and arbitrary launch flags are not accepted');
    const { executable, outputRoot, admission, context, headed = false,
      viewport = { width: 1440, height: 900 }, captureConsole = false } = options;
    await checkProvider(executable);
    requireValue(admission instanceof Admission, 'Use the shared P03-backed admission');
    requireValue(context && typeof context.session_id === 'string' && context.session_id.trim(), 'Carry the actual host or selected work-context identity');
    requireValue(typeof headed === 'boolean' && typeof captureConsole === 'boolean'
      && viewport && Number.isInteger(viewport.width) && Number.isInteger(viewport.height)
      && viewport.width >= 320 && viewport.width <= 7680 && viewport.height >= 240 && viewport.height <= 4320, 'Invalid viewport/headed selection');
    requireValue(typeof outputRoot === 'string' && isAbsolute(outputRoot), 'Select an absolute owned output root');
    if (process.platform === 'win32') {
      for (const name of ['APPDATA', 'LOCALAPPDATA']) {
        requireValue(process.env[name] && (await lstat(process.env[name])).isDirectory(),
          `The declared ${name} directory must exist before browser launch`);
      }
    }
    const output = await lstat(outputRoot);
    requireValue(output.isDirectory() && !output.isSymbolicLink(), 'Choose an existing, unlinked output root');
    const run = new BrowserSession();
    run.admission = admission;
    run.runDir = await mkdtemp(join(outputRoot, 'browse-'));
    run.profileDir = join(run.runDir, 'profile');
    run.evidence = { context: structuredClone(context), provider: 'Chromium CDP', executable,
      node: process.version, run: run.runDir, profile: run.profileDir, operations: [], network: [], lifecycle: [] };
    run.chains = new Map();
    run.tasks = new Set();
    run.captureConsole = captureConsole;
    run.evidence.console = captureConsole ? [] : null;
    await mkdir(run.profileDir);
    await run._record('ownership.json', { owner: context.session_id, profile: run.profileDir, reuse: false });
    try {
      await run._launch(executable, headed, viewport);
      return run;
    } catch (error) {
      run.evidence.start_error = error.message;
      try { await run.close(); }
      catch (cleanupError) { throw new AggregateError([error, cleanupError], 'Browser start and owned cleanup both failed'); }
      throw error;
    }
  }

  async _record(name, value) {
    await writeFile(join(this.runDir, artifactName(name, 'json')), JSON.stringify(value, null, 2) + '\n', { flag: 'wx' });
  }

  _page(method, params = {}) {
    return this.protocol.call(method, params, this.sessionId);
  }

  async _waitForOwnedEndpoint({ readEndpoint = readFile, pause = delay } = {}) {
    let endpoint;
    for (let n = 0; n < 100; n++) {
      if (this.launchError) throw this.launchError;
      requireValue(!this.exit, 'Browser exited before its owned endpoint was ready');
      try { endpoint = (await readEndpoint(join(this.profileDir, 'DevToolsActivePort'), 'utf8')).trim().split(/\r?\n/); break; }
      catch (error) { if (error.code !== 'ENOENT' && error.code !== 'EBUSY') throw error; await pause(100); }
    }
    requireValue(endpoint && /^\d+$/.test(endpoint[0]) && /^\/devtools\/browser\/[a-zA-Z0-9-]+$/.test(endpoint[1]), 'No verified owned browser endpoint');
    return endpoint;
  }

  async _launch(executable, headed, viewport) {
    const args = [
      ...(headed ? [] : ['--headless=new']), `--user-data-dir=${this.profileDir}`,
      '--remote-debugging-port=0', '--remote-debugging-address=127.0.0.1',
      '--no-first-run', '--no-default-browser-check', '--disable-background-networking',
      '--disable-default-apps', '--disable-component-update', '--disable-sync', 'about:blank',
    ];
    this.evidence.argv = args;
    this.output = createWriteStream(join(this.runDir, 'browser.log'), { flags: 'wx' });
    this.output.on('error', error => { this.fault ??= new Error(`Browser log failed: ${error.message}`); });
    this.child = spawn(executable, args, { stdio: ['ignore', 'pipe', 'pipe'], windowsHide: !headed });
    this.child.stdout.pipe(this.output, { end: false });
    this.child.stderr.pipe(this.output, { end: false });
    this.exited = new Promise(resolveExit => {
      this.child.once('error', error => { this.launchError = error; this.exit = { error: error.message }; resolveExit(this.exit); });
      this.child.once('exit', (code, signal) => { this.exit = { code, signal }; resolveExit(this.exit); });
    });
    this.evidence.pid = this.child.pid;
    const endpoint = await this._waitForOwnedEndpoint();
    const origin = `http://127.0.0.1:${endpoint[0]}`;
    const response = await fetch(`${origin}/json/protocol`, { redirect: 'error', signal: AbortSignal.timeout(timeout) });
    requireValue(response.ok, 'Owned browser protocol endpoint did not respond');
    const schema = await response.json();
    const command = (domain, name) => schema.domains.find(x => x.domain === domain)?.commands?.find(x => x.name === name);
    for (const [domain, name] of [['Fetch', 'continueResponse'], ['Fetch', 'failRequest'],
      ['Target', 'createBrowserContext'], ['Target', 'setAutoAttach']]) {
      requireValue(command(domain, name), `Provider API unavailable: ${domain}.${name}`);
    }
    this.printAvailable = Boolean(command('Page', 'printToPDF'));
    this.evidence.print_api_available = this.printAvailable;
    requireValue(command('Fetch', 'continueRequest')?.parameters.some(x => x.name === 'interceptResponse'),
      'Provider lacks pre-redirect response interception');
    await this._record('provider-api.json', schema.domains.filter(x =>
      ['Browser', 'Target', 'Page', 'Runtime', 'Fetch', 'Network', 'Input', 'Emulation'].includes(x.domain)));
    const socket = new WebSocket(`ws://127.0.0.1:${endpoint[0]}${endpoint[1]}`);
    this.protocol = new Protocol(socket);
    await new Promise((resolveOpen, reject) => {
      const timer = setTimeout(() => reject(new Error('Owned browser WebSocket timed out')), timeout);
      socket.addEventListener('open', () => { clearTimeout(timer); resolveOpen(); }, { once: true });
      socket.addEventListener('error', () => { clearTimeout(timer); reject(new Error('Owned browser WebSocket failed')); }, { once: true });
    });
    this.protocol.onEvent = message => {
      const task = this._event(message).catch(error => {
        this.fault ??= error;
        this.evidence.lifecycle.push({ event: 'provider-error', reason: error.message });
      });
      this.tasks.add(task);
      task.finally(() => this.tasks.delete(task));
    };
    this.evidence.version = await this.protocol.call('Browser.getVersion');
    const { browserContextId } = await this.protocol.call('Target.createBrowserContext', { disposeOnDetach: true });
    this.contextId = browserContextId;
    this.evidence.lifecycle.push({ event: 'context-created', browserContextId });
    await this.protocol.call('Browser.setDownloadBehavior', { behavior: 'deny', browserContextId });
    this.startupTargets = new Map();
    await this.protocol.call('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true });
    await this._createOwnedPage();
    for (const method of ['Page.enable', 'Runtime.enable', 'Network.enable']) await this._page(method);
    await this._page('Network.setCacheDisabled', { cacheDisabled: true });
    await this._page('Network.setBypassServiceWorker', { bypass: true });
    await this._page('Network.setBlockedURLs', { urls: ['ws://*', 'wss://*', 'file://*', 'ftp://*'] });
    await this._page('Fetch.enable', { patterns: [{ urlPattern: '*', requestStage: 'Request' }], handleAuthRequests: true });
    await this._page('Target.setAutoAttach', { autoAttach: true, waitForDebuggerOnStart: true, flatten: true });
    await this._page('Emulation.setDeviceMetricsOverride', { ...viewport, deviceScaleFactor: 1, mobile: false });
    this.viewport = viewport;
    const startupTargets = this.startupTargets;
    this.startupTargets = null;
    for (const attached of startupTargets.values()) {
      if (attached.targetInfo.targetId !== this.targetId) await this._refuseTarget(attached.targetInfo);
    }
    await this._page('Runtime.runIfWaitingForDebugger');
    this.frameId = (await this._page('Page.getFrameTree')).frameTree.frame.id;
    this._healthy();
  }

  async _createOwnedPage() {
    const { targetId } = await this.protocol.call('Target.createTarget', { url: 'about:blank', browserContextId: this.contextId });
    this.targetId = targetId;
    this.evidence.lifecycle.push({ event: 'target-created', targetId });
    for (let n = 0; n < 100 && !this.startupTargets.has(targetId); n++) await delay(50);
    const attached = this.startupTargets.get(targetId);
    requireValue(attached?.targetInfo.type === 'page' && attached.waitingForDebugger === true,
      'Could not identify the newly owned paused page');
    this.sessionId = attached.sessionId;
    this.evidence.lifecycle.push({ event: 'created', browserContextId: this.contextId, targetId, sessionId: this.sessionId });
  }

  async _refuseTarget(targetInfo) {
    this.evidence.lifecycle.push({ event: 'refused-target', type: targetInfo.type, targetId: targetInfo.targetId });
    const result = await this.protocol.call('Target.closeTarget', { targetId: targetInfo.targetId });
    requireValue(result.success, 'Provider did not close an unselected target');
  }

  async _event({ method, params, sessionId }) {
    if (method === 'Target.attachedToTarget') {
      const ownedParent = this.sessionId && sessionId === this.sessionId;
      if (params.targetInfo.browserContextId !== this.contextId && !ownedParent) return;
      this.evidence.lifecycle.push({ event: 'target-attached', type: params.targetInfo.type,
        targetId: params.targetInfo.targetId, waitingForDebugger: params.waitingForDebugger });
      if (this.startupTargets) { this.startupTargets.set(params.targetInfo.targetId, params); return; }
      if (params.targetInfo.targetId === this.targetId) return;
      this.fault ??= new Error('Additional pages, frames and workers are unsupported by this single-page provider');
      await this._refuseTarget(params.targetInfo);
    } else if (sessionId === this.sessionId && method === 'Fetch.requestPaused') {
      await this._request(params);
    } else if (sessionId === this.sessionId && method === 'Fetch.authRequired') {
      this.fault ??= new Error('Authentication requires the user-chosen surface; credentials are never supplied');
      await this._page('Fetch.continueWithAuth', { requestId: params.requestId, authChallengeResponse: { response: 'CancelAuth' } });
    } else if (sessionId === this.sessionId && method === 'Page.javascriptDialogOpening') {
      this.fault ??= new Error('JavaScript dialog requires an explicit host/manual workflow');
      await this._page('Page.handleJavaScriptDialog', { accept: false });
    } else if (sessionId === this.sessionId && method === 'Runtime.consoleAPICalled' && this.captureConsole) {
      requireValue(this.evidence.console.length < 1000, 'Console capture exceeded the observation bound');
      requireValue(params.args.every(arg => typeof arg.value !== 'string' || arg.value.length <= 65536),
        'Console message exceeded the observation bound');
      this.evidence.console.push({ type: params.type, values: params.args.map(arg =>
        ['string', 'number', 'boolean'].includes(arg.type) ? arg.value : `[${arg.type}; not captured]`) });
    }
  }

  async _request(event) {
    const { requestId, request, responseStatusCode, responseErrorReason, redirectedRequestId } = event;
    try {
      this._healthy();
      const url = this.admission.check(request.url);
      if (responseErrorReason) throw new Error(`Browser transport failed: ${responseErrorReason}`);
      if (responseStatusCode === undefined) {
        const prior = redirectedRequestId ? this.chains.get(redirectedRequestId) : [];
        requireValue(prior && prior.length <= 5 && !prior.includes(url), 'Redirect chain missing, looping or longer than five hops');
        this.chains.set(requestId, [...prior, url]);
        this.evidence.network.push({ stage: 'request', url, method: request.method, admitted: true });
        await this._page('Fetch.continueRequest', { requestId, interceptResponse: true });
      } else {
        const observation = { stage: 'response', url, status: responseStatusCode, admitted: true };
        if (redirectStatuses.has(responseStatusCode)) {
          const locations = (event.responseHeaders || []).filter(x => x.name.toLowerCase() === 'location');
          requireValue(locations.length === 1, 'Redirect needs exactly one raw Location');
          observation.redirect = this.admission.redirect(url, locations[0].value);
          const chain = this.chains.get(requestId);
          requireValue(chain && chain.length <= 5 && !chain.includes(observation.redirect), 'Redirect loop or limit refused');
        }
        if (event.frameId === this.frameId && event.resourceType === 'Document') this.documentStatus = responseStatusCode;
        this.evidence.network.push(observation);
        await this._page('Fetch.continueResponse', { requestId });
      }
    } catch (error) {
      this.fault ??= error;
      this.evidence.network.push({ stage: responseStatusCode === undefined ? 'request' : 'response',
        url: request.url, admitted: false, reason: error.message });
      await this._page('Fetch.failRequest', { requestId, errorReason: 'BlockedByClient' });
    }
  }

  _healthy() {
    if (this.fault) throw this.fault;
    requireValue(!this.closed, 'Browser session is closed');
  }

  async _evaluate(expression) {
    this._healthy();
    const result = await this._page('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true });
    requireValue(!result.exceptionDetails, result.exceptionDetails?.exception?.description || result.exceptionDetails?.text || 'Page evaluation failed');
    this._healthy();
    return result.result.value;
  }

  async _ready() {
    for (let n = 0; n < 150; n++) {
      await Promise.all([...this.tasks]);
      this._healthy();
      if (await this._evaluate('document.readyState === "complete"')) return;
      await delay(100);
    }
    throw new Error('Page did not reach a complete state before timeout');
  }

  async _operation(name, input, perform) {
    const event = { operation: name, input, status: 'error' };
    this.evidence.operations.push(event);
    try {
      this._healthy();
      const result = await perform();
      await Promise.all([...this.tasks]);
      this._healthy();
      event.status = 'pass';
      return result;
    } catch (error) {
      const failure = this.fault ?? error;
      if (failure !== error) event.provider_error = error.message;
      event.reason = failure.message;
      throw failure;
    }
  }

  async open(url) {
    return this._operation('open', { url }, async () => {
      const admitted = this.admission.check(url);
      this.documentStatus = undefined;
      const response = await this._page('Page.navigate', { url: admitted });
      this._healthy();
      requireValue(!response.errorText && !response.isDownload, response.errorText || 'Navigation became a download');
      await this._ready();
      requireValue(this.documentStatus >= 200 && this.documentStatus < 300, `HTTP document did not succeed: ${this.documentStatus}`);
      return this.read();
    });
  }

  async read(selector = 'body', { html = false } = {}) {
    requireValue(typeof selector === 'string' && typeof html === 'boolean', 'Invalid read arguments');
    return this._operation('read', { selector, html }, () => this._evaluate(`(() => {
      const elements = [...document.querySelectorAll(${JSON.stringify(selector)})];
      if (elements.length > 1000) throw new Error('Read matched more than 1000 elements; narrow the selector');
      let characters = 0;
      return {url: location.href, title: document.title, ready: document.readyState,
        reducedMotion: matchMedia('(prefers-reduced-motion: reduce)').matches,
        activeElement: document.activeElement?.id || document.activeElement?.tagName,
        elements: elements.map(element => {
          const style = getComputedStyle(element);
          const box = element.getBoundingClientRect();
          const text = element.innerText ?? element.textContent;
          characters += text.length + ${html ? 'element.outerHTML.length' : '0'};
          if (characters > 65536) throw new Error('Read exceeded 65536 characters; narrow the selector');
          return {text, tag: element.tagName,
            value: ['password', 'file'].includes(element.type) ? null : element.value,
            color: style.color, background: style.backgroundColor, animation: style.animationName,
            display: style.display, box: {x:box.x,y:box.y,width:box.width,height:box.height},
            ${html ? 'html: element.outerHTML,' : ''}};
        })};
    })()`));
  }

  consoleMessages() {
    this._healthy();
    requireValue(this.captureConsole, 'Console capture was not enabled for this owned session');
    return structuredClone(this.evidence.console);
  }

  async act(input) {
    const action = validateAction(input);
    const { value, ...logged } = action;
    return this._operation('act', logged, async () => {
      if (action.kind === 'wait') {
        for (let n = 0; n < 100; n++) {
          const state = await this.read(action.selector);
          if (state.elements.length && (action.text === undefined || state.elements.some(x => x.text.includes(action.text)))) return state;
          await delay(100);
        }
        throw new Error('Requested selector/text was not observed before timeout');
      }
      if (action.kind === 'press') {
        const code = { Tab: 9, Enter: 13, Escape: 27, ArrowDown: 40, ArrowUp: 38 }[action.key];
        await this._page('Input.dispatchKeyEvent', { type: 'keyDown', key: action.key, code: action.key,
          windowsVirtualKeyCode: code, ...(action.key === 'Enter' ? { text: '\r', unmodifiedText: '\r' } : {}) });
        await this._page('Input.dispatchKeyEvent', { type: 'keyUp', key: action.key, code: action.key, windowsVirtualKeyCode: code });
      } else {
        const target = await this._evaluate(`(() => {
          const nodes = document.querySelectorAll(${JSON.stringify(action.selector)});
          if (nodes.length !== 1) throw new Error('Action requires exactly one element');
          const element = nodes[0];
          if (element.disabled || ['password','file'].includes(element.type)) throw new Error('Disabled, credential or file input refused');
          element.scrollIntoView({block:'center',inline:'center',behavior:'instant'});
          const box = element.getBoundingClientRect();
          const x = box.x + box.width/2, y = box.y + box.height/2;
          const hit = document.elementFromPoint(x,y);
          if (!box.width || !box.height || !hit || !(hit === element || element.contains(hit))) throw new Error('Element is hidden or obscured');
          ${action.kind === 'fill' ? "if (!['INPUT','TEXTAREA'].includes(element.tagName)) throw new Error('Fill requires a text input'); element.focus(); element.select();" : ''}
          return {x,y,href:element.closest('a')?.href || null};
        })()`);
        if (target.href) this.admission.check(target.href);
        if (action.kind === 'fill') await this._page('Input.insertText', { text: value });
        else {
          for (const type of ['mousePressed', 'mouseReleased']) {
            await this._page('Input.dispatchMouseEvent', { type, x: target.x, y: target.y, button: 'left', clickCount: 1 });
          }
        }
      }
      await this._ready();
      return this.read();
    });
  }

  async media({ print = false, reducedMotion = false } = {}) {
    requireValue(typeof print === 'boolean' && typeof reducedMotion === 'boolean', 'Media choices must be booleans');
    return this._operation('media', { print, reducedMotion }, () => this._page('Emulation.setEmulatedMedia',
      { media: print ? 'print' : 'screen', features: [{ name: 'prefers-reduced-motion', value: reducedMotion ? 'reduce' : 'no-preference' }] }));
  }

  async screenshot(name = 'screenshot.png') {
    artifactName(name, 'png');
    return this._operation('screenshot', { name, viewport: this.viewport }, async () => {
      await this._ready();
      const result = await this._page('Page.captureScreenshot', { format: 'png', fromSurface: true, captureBeyondViewport: false });
      const path = join(this.runDir, name);
      await writeFile(path, Buffer.from(result.data, 'base64'), { flag: 'wx' });
      return path;
    });
  }

  async print(name = 'page.pdf') {
    artifactName(name, 'pdf');
    return this._operation('print', { name }, async () => {
      requireValue(this.printAvailable, 'Provider print API unavailable; print remains unverified');
      await this._ready();
      const result = await this._page('Page.printToPDF', { printBackground: true, preferCSSPageSize: true, displayHeaderFooter: false });
      const path = join(this.runDir, name);
      await writeFile(path, Buffer.from(result.data, 'base64'), { flag: 'wx' });
      return path;
    });
  }

  async close() {
    if (this.closed) return;
    const errors = [];
    if (this.protocol && !this.exit) {
      try {
        if (this.contextId) {
          await this.protocol.call('Target.disposeBrowserContext', { browserContextId: this.contextId });
          this.evidence.lifecycle.push({ event: 'context-disposed', browserContextId: this.contextId });
        }
        await this.protocol.call('Browser.close');
      } catch (error) { errors.push(error.message); }
    }
    if (this.child && !this.exit) {
      await Promise.race([this.exited, delay(5000, undefined, { ref: false })]);
      if (!this.exit) {
        this.child.kill();
        await Promise.race([this.exited, delay(5000, undefined, { ref: false })]);
        if (!this.exit) errors.push('Owned browser process did not stop; profile retained');
        else this.evidence.lifecycle.push({ event: 'owned-process-terminated', pid: this.child.pid });
      }
    }
    this.protocol?.socket.close();
    if (this.output) await new Promise(resolveEnd => this.output.end(resolveEnd));
    this.closed = true;
    if (!this.child || this.exit) {
      try {
        const profile = await lstat(this.profileDir);
        requireValue(profile.isDirectory() && !profile.isSymbolicLink(), 'Owned profile changed type; cleanup refused');
        await rm(this.profileDir, { recursive: true });
        this.evidence.lifecycle.push({ event: 'owned-profile-removed', path: this.profileDir });
      } catch (error) { errors.push(`Owned profile cleanup failed: ${error.message}`); }
    }
    this.evidence.lifecycle.push({ event: 'closed', exit: this.exit ?? null, errors });
    await this._record('evidence.json', this.evidence);
    requireValue(!errors.length, `Browser cleanup was incomplete: ${errors.join('; ')}`);
  }
}
