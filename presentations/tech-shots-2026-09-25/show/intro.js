/* component: presentation-holding-intro
 * intent: ../README.md
 * constraints: silent decorative media; pause/reduced-motion/failure fallback; no timed-story progress
 * last_intent_review: 2026-09-24 */
(() => {
 'use strict';
 const motion=matchMedia('(prefers-reduced-motion: reduce)');
 let wantsPlayback=!motion.matches,active=null,control=null,status=null,failed=false;
 function sync(){
  if(!active||!control)return;
  const playing=!active.paused;
  control.textContent=failed?'Still image':playing?'Pause motion':'Play motion';
  control.disabled=failed;
  status.textContent=failed?'Video unavailable. Still image shown.':playing?'Silent loop': 'Motion paused';
 }
 async function play(){
  const video=active;
  if(!video||!wantsPlayback||document.hidden||failed)return;
  if(!video.getAttribute('src'))video.src=video.dataset.src;
  try{await video.play();}
  catch{if(active===video&&!document.hidden&&!failed){wantsPlayback=false;sync();}}
 }
 function unmount(){
  const video=active;active=null;control=null;status=null;
  if(video){video.onplaying=null;video.onpause=null;video.onerror=null;video.pause();video.removeAttribute('src');video.load();}
 }
 function mount(){
  active=document.querySelector('#introVideo');
  if(!active)return;
  const video=active;failed=false;
  control=document.querySelector('#introMotion');status=document.querySelector('#introStatus');
  video.muted=true;
  video.onplaying=()=>{if(active===video)sync()};video.onpause=()=>{if(active===video)sync()};
  video.onerror=()=>{if(active!==video)return;failed=true;wantsPlayback=false;video.hidden=true;sync()};
  control.addEventListener('click',()=>{wantsPlayback=video.paused;if(wantsPlayback)play();else video.pause();sync()});
  // Space activates this control without also advancing the deck's global shortcuts.
  control.addEventListener('keydown',event=>{if(event.key===' '||event.key==='Enter')event.stopPropagation()});
  sync();play();
 }
 document.addEventListener('visibilitychange',()=>{if(!active)return;if(document.hidden)active.pause();else play()});
 motion.addEventListener('change',event=>{wantsPlayback=!event.matches;if(active){if(wantsPlayback)play();else active.pause();sync()}});
 window.LINTEL_INTRO={mount,unmount,render:()=>`<section class="slide holding-intro"><h1 class="intro-title">The portal is open. Welcome to Lintel.</h1><img class="intro-poster" src="../assets/intro/lintel-living-portal-poster.jpg" alt="A luminous Lintel portal between the beasts of context rot and AI slop."><video id="introVideo" class="intro-video" data-src="../assets/intro/lintel-living-portal.mp4" poster="../assets/intro/lintel-living-portal-poster.jpg" muted loop playsinline preload="none" aria-hidden="true"></video><div class="intro-welcome"><span>WELCOME TO LINTEL</span><p>We begin shortly.</p></div><div class="intro-controls"><button type="button" id="introMotion">Play motion</button><span id="introStatus" aria-live="polite">Motion paused</span></div></section>`};
})();
