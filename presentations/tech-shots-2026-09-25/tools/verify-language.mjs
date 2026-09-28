// component: language-selector-integration-check
// implements: none — bounded presentation UI addition
// intent: ../README.md
// constraints: local catalogue; real presentation/notes communication; no external translation service
// last_intent_review: 2026-09-28
import assert from 'node:assert/strict';
const {chromium}=await import(process.env.LINTEL_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.LINTEL_PREVIEW_URL||'http://127.0.0.1:8000/';
const browser=await chromium.launch({headless:true});let checks=0;
const ok=(value,message)=>{assert.ok(value,message);checks++;};
try{
 const context=await browser.newContext({viewport:{width:1440,height:960},reducedMotion:'reduce'}),errors=[];
 context.on('page',page=>page.on('pageerror',e=>errors.push(e.message)));
 const p=await context.newPage();await p.goto(new URL('show/index.html?theme=neon#three-hours',base).href);
 await p.waitForFunction(()=>window.DECK_API&&window.LINTEL_LANGUAGE);
 ok(await p.locator('html').getAttribute('lang')==='en','Fresh browser defaults to English');
 ok(await p.locator('[data-language="en"]').getAttribute('aria-pressed')==='true','English flag exposes selection');
 const original=await p.locator('#stage').innerText();
 await p.locator('[data-language="sv"]').focus();await p.keyboard.press('Enter');
 ok(await p.locator('html').getAttribute('lang')==='sv','Swedish can be selected with keyboard');
 ok((await p.locator('#stage h1').innerText()).includes('Vi hade en plan'),'Swedish slide is real translated content');
 ok(new URL(p.url()).hash==='#three-hours'&&new URL(p.url()).searchParams.get('lang')==='sv','Choice preserves current slide and updates share URL');
 const popup=p.waitForEvent('popup');await p.locator('#notes').click();const n=await popup;
 await n.waitForFunction(()=>document.documentElement.lang==='sv'&&document.querySelector('#script h2')?.textContent.includes('Vi hade en plan'));
 ok(!(await n.locator('#script').innerText()).includes('I am Johannes'),'Speaker script translated too');
 await p.locator('#next').click();await n.waitForFunction(()=>document.querySelector('#position').textContent.startsWith('SLIDE 03'));
 ok(await n.locator('html').getAttribute('lang')==='sv','Notes follow slide changes in Swedish');
 await n.locator('#previous').click();await p.waitForFunction(()=>window.DECK_API.state.index===1);
 await p.locator('[data-language="en"]').click();await n.waitForFunction(()=>document.documentElement.lang==='en'&&document.querySelector('#script').textContent.includes('I am Johannes'));
 ok(await p.locator('#stage').innerText()===original,'English source restores exactly');
 await p.evaluate(()=>window.DECK_API.go(window.DECK_API.slides.findIndex(s=>s.id==='profile')));
 await p.locator('#stage [data-profile]').last().click();const state=await p.evaluate(()=>JSON.stringify(window.DECK_API.state));
 await p.locator('[data-language="sv"]').click();ok(await p.evaluate(()=>JSON.stringify(window.DECK_API.state))===state,'Language switch preserves interactive demo state');
 await p.reload();await p.waitForFunction(()=>window.DECK_API);ok(await p.locator('html').getAttribute('lang')==='sv','Language survives reload');
 await p.goto(new URL('index.html',base).href);await p.waitForFunction(()=>window.LINTEL_LANGUAGE);
 ok(await p.locator('html').getAttribute('lang')==='sv','Preference follows to homepage');
 ok(!(await p.locator('h1').innerText()).includes('Good work'),'Homepage is translated');
 await p.goto(new URL('show/index.html?lang=en#mars',base).href);await p.waitForFunction(()=>window.DECK_API);
 ok(await p.locator('html').getAttribute('lang')==='en','Explicit English link overrides remembered Swedish');
 await p.locator('[data-language="sv"]').click();await p.locator('[data-theme-choice="paper"]').click();
 ok(await p.locator('html').getAttribute('lang')==='sv'&&await p.locator('html').getAttribute('data-theme')==='paper','Theme change preserves language');
 await n.close();await context.close();
 const blocked=await browser.newContext();await blocked.addInitScript(()=>{Object.defineProperty(window,'localStorage',{get(){throw new DOMException('Storage unavailable','SecurityError');}});});const q=await blocked.newPage();
 await q.goto(new URL('show/index.html#three-hours',base).href);await q.waitForFunction(()=>window.DECK_API);
 ok(await q.locator('html').getAttribute('lang')==='en','Unavailable storage keeps English default');
 await q.locator('[data-language="sv"]').click();await q.reload();await q.waitForFunction(()=>window.DECK_API);
 ok(await q.locator('html').getAttribute('lang')==='sv','Share URL keeps language when storage is unavailable');
 await blocked.close();ok(errors.length===0,'No browser errors: '+errors.join('; '));
 console.log(JSON.stringify({result:'PASS',checks,base}));
}finally{await browser.close();}
