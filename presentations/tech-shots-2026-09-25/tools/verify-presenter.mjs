// component: presenter-window-integration-check
// intent: ../README.md
// constraints: tests the real presentation/notes windows together; no external service
// Run against a served build: LINTEL_PREVIEW_URL=http://127.0.0.1:8000/ node tools/verify-presenter.mjs
// Requires Playwright + Chromium. LINTEL_PLAYWRIGHT_MODULE can point to an existing installation.
import assert from 'node:assert/strict';
const {chromium}=await import(process.env.LINTEL_PLAYWRIGHT_MODULE||'playwright');
const base=process.env.LINTEL_PREVIEW_URL||'http://127.0.0.1:8000/';
const browser=await chromium.launch({headless:true});
let checks=0;const ok=(v,m)=>{assert.ok(v,m);checks++;};
const context=await browser.newContext({viewport:{width:1440,height:960}});
const errors=[];context.on('page',p=>p.on('pageerror',e=>errors.push(e.message)));
const p=await context.newPage();
const slide=i=>p.evaluate(i=>window.DECK_API.go(i),i);
const synced=async(n,i)=>{await n.waitForFunction(i=>document.querySelector('#position').textContent.startsWith('SLIDE '+String(i+1).padStart(2,'0')+' /'),i);const actual=await n.locator('#script').innerHTML();const expected=await p.evaluate(()=>window.DECK_API.getPresenterNotes().html);ok(actual===expected,'Popup receives exact current notes');ok((await n.locator('#slideAnnouncement').innerText()).startsWith('Slide '+(i+1)+' of'),'Slide change has a concise live announcement');};
const open=async()=>{const created=p.waitForEvent('popup');await p.locator('#notes').click();const n=await created;await n.waitForLoadState();return n;};
try{
 await p.goto(new URL('show/index.html?theme=fluent#welcome',base).href);
 const n=await open();await synced(n,0);
 ok(await p.locator('#notePanel').count()===0,'No audience notes overlay');
 await p.locator('#next').click();await synced(n,1);
 await n.locator('#next').click();await synced(n,2);ok(new URL(p.url()).hash!=='#three-hours','Popup navigates the presentation');
 await n.keyboard.press('ArrowLeft');await synced(n,1);
 await p.locator('#overview').click();await p.locator('[data-slide="8"]').click();await synced(n,8);
 await p.locator('#acts button[data-group="technical"]').click();const tech=await p.evaluate(()=>window.DECK_API.state.index);await synced(n,tech);
 await p.evaluate(()=>location.hash='#profile');const profile=await p.evaluate(()=>window.DECK_API.slides.findIndex(s=>s.id==='profile'));await synced(n,profile);
 await n.locator('#larger').click();ok(await n.evaluate(()=>getComputedStyle(document.documentElement).getPropertyValue('--notes-size').trim())==='22px','Reading size increases');
 await p.locator('#notes').click();await p.waitForTimeout(250);ok(context.pages().length===2,'Notes reuses its existing popup');
 await p.reload();await p.waitForFunction(()=>!!window.DECK_API);await synced(n,profile);await p.waitForTimeout(300);await p.locator('#notes').click();ok(context.pages().length===2,'Reload reconnects the same popup');
 await slide(2);await synced(n,2);await n.setViewportSize({width:390,height:720});ok(await n.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),'Narrow notes window fits');
 const other=await context.newPage();await other.goto(new URL('show/index.html?theme=paper#three-hours',base).href);const nextPop=other.waitForEvent('popup');await other.locator('#notes').click();const otherNotes=await nextPop;await otherNotes.waitForFunction(()=>document.querySelector('#position').textContent.startsWith('SLIDE 02'));
 await slide(4);await synced(n,4);ok((await otherNotes.locator('#position').innerText()).startsWith('SLIDE 02'),'Separate decks remain isolated');await otherNotes.close();await other.close();
 await n.close();const reopened=await open();await synced(reopened,4);
 const last=await p.evaluate(()=>window.DECK_API.slides.length-1);await slide(last);await synced(reopened,last);ok(await reopened.locator('#next').isDisabled(),'End boundary disables Next');await slide(0);await synced(reopened,0);ok(await reopened.locator('#previous').isDisabled(),'Start boundary disables Previous');
 await p.close();await reopened.waitForFunction(()=>document.querySelector('#connection').classList.contains('disconnected'));ok(await reopened.locator('#next').isDisabled(),'Closed presentation disables navigation');await reopened.close();
 const blocked=await context.newPage();await blocked.addInitScript(()=>{window.open=()=>null;});await blocked.goto(new URL('show/index.html#three-hours',base).href);await blocked.locator('#notes').click();ok(await blocked.locator('#notesStatus').isVisible(),'Popup blocking gives actionable feedback');ok((await blocked.locator('#notesStatus').innerText()).includes('Allow pop-ups'),'Blocked popup instruction');await blocked.locator('#next').click();ok((await blocked.locator('#counter').innerText()).startsWith('03'),'Slide navigation still works when popup blocked');await blocked.close();
 ok(errors.length===0,'No browser errors: '+errors.join('; '));console.log(JSON.stringify({result:'PASS',checks,browser:'Chromium',base}));
}finally{await browser.close();}
