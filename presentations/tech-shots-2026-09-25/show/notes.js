/* component: detachable-speaker-notes
 * intent: ../README.md
 * constraints: same-origin opener only; getPresenterNotes is defined once in app.js
 * last_intent_review: 2026-09-24 */
(() => {
'use strict';
const $=id=>document.getElementById(id);
let api=null,registeredApi=null,lastId=null,lastHtml='',fontSize=20;
const connection=message=>{if($('connection').textContent!==message)$('connection').textContent=message;$('connection').classList.toggle('disconnected',!api);};
function sync(){
 try{
  const owner=window.opener;
  api=owner&&!owner.closed&&owner.location.origin===location.origin?owner.DECK_API:null;
  if(!api?.getPresenterNotes)throw new Error('Presentation unavailable');
  if(api!==registeredApi){api.registerPresenter(window);registeredApi=api;}
  const note=api.getPresenterNotes();
  connection('Connected · follows your presentation');
  $('position').textContent='SLIDE '+String(note.index+1).padStart(2,'0')+' / '+note.total;
  $('timing').textContent=note.timing;
  $('nextTitle').textContent=note.nextTitle;
  $('previous').disabled=note.index===0;$('next').disabled=note.index===note.total-1;
  if(note.html!==lastHtml){$('script').innerHTML=note.html;lastHtml=note.html;}
  if(note.id!==lastId){$('slideAnnouncement').textContent='Slide '+(note.index+1)+' of '+note.total+': '+note.title;window.scrollTo(0,0);lastId=note.id;}
  document.title=(note.index+1)+' · Speaker notes · Lintel';
 }catch{
  api=null;$('previous').disabled=true;$('next').disabled=true;
  connection(location.protocol==='file:'?'For offline notes sync, serve the extracted folder locally (python -m http.server 8000), open http://127.0.0.1:8000, then choose Notes.':'Not connected. Open or reopen Notes from the presentation window.');
 }
}
function move(delta){if(!api)return;try{api.go(api.getPresenterNotes().index+delta);sync();}catch{sync();}}
$('previous').onclick=()=>move(-1);$('next').onclick=()=>move(1);
function resize(delta){fontSize=Math.max(16,Math.min(30,fontSize+delta));document.documentElement.style.setProperty('--notes-size',fontSize+'px');$('smaller').disabled=fontSize===16;$('larger').disabled=fontSize===30;}
$('smaller').onclick=()=>resize(-2);$('larger').onclick=()=>resize(2);
addEventListener('keydown',e=>{if(e.ctrlKey||e.altKey||e.metaKey||e.target.closest('input,textarea,select'))return;if(e.key==='ArrowRight'||e.key==='PageDown'){e.preventDefault();move(1);}if(e.key==='ArrowLeft'||e.key==='PageUp'){e.preventDefault();move(-1);}});
// A small pull keeps reloads, overview jumps and browser history in sync without
// broadcasting notes or coupling independent presentation tabs together.
sync();setInterval(sync,200);
})();
