/* component: public-theme-switcher
 * intent: ../README.md
 * constraints: local preference only; no telemetry; demo result apps stay unchanged
 * last_intent_review: 2026-09-24 */
(() => {
 'use strict';
 const root=document.documentElement,key='lintel-theme',themes=['neon','paper','fluent'];
 let saved;try{saved=localStorage.getItem(key)}catch{}
 const requested=new URLSearchParams(location.search).get('theme');
 let theme=requested||saved||'neon';
 if(!themes.includes(theme))theme='neon';
 root.dataset.theme=theme;
 if(themes.includes(requested))try{localStorage.setItem(key,theme)}catch{}
 // CSSOM serializes most authored hex colours as rgb()/rgba(). Map both forms
 // through the same palette so highlights keep their meaning on a light surface.
 const channels=value=>{
  if(value.startsWith('#')){
   let h=value.slice(1);if(h.length===3||h.length===4)h=[...h].map(x=>x+x).join('');
   return [...[0,2,4].map(i=>parseInt(h.slice(i,i+2),16)),h.length===8?parseInt(h.slice(6),16)/255:1];
  }
  const n=value.match(/[\d.]+/g).map(Number);return [n[0],n[1],n[2],n[3]??1];
 };
 const family=([r,g,b])=>{
  if(Math.max(r,g,b)-Math.min(r,g,b)<25)return 'neutral';
  if(r>g*1.2&&r>b*1.1)return 'red';
  if(r>g*1.16&&b>g*1.12)return 'purple';
  if(g>r*1.12&&g>b*1.14)return 'green';
  if(b>r*1.13&&b>g*1.08)return 'blue';
  if(r>110&&g>100&&b<g*.73)return 'amber';
  return 'neutral';
 };
 const ink={neutral:'#57534b',green:'#345119',purple:'#693781',red:'#8b2935',blue:'#234f68',amber:'#6e4c12'};
 const surface={green:'#dce8c5',purple:'#e8dbee',red:'#f1d8da',blue:'#dce7ef',amber:'#eee2c2'};
 const edge={neutral:'#8d877c',green:'#6b8052',purple:'#91779e',red:'#a9747b',blue:'#748d9e',amber:'#9a885e'};
 // The same adapter serves both light themes. Fluent values come from its CSS tokens.
 const lightPalette=mode=>{
  if(mode==='paper')return {ink,surface,edge,text:'#292923',canvas:'#faf8f2',panel:'#e9e5dc',strong:'#ddd8ce'};
  const css=getComputedStyle(root),token=name=>css.getPropertyValue('--fluent-'+name).trim();
  const colors=kind=>Object.fromEntries(['neutral','green','purple','red','blue','amber'].map(role=>[role,token(kind+'-'+role)]));
  return {ink:colors('ink'),surface:colors('surface'),edge:colors('edge'),text:token('text'),canvas:token('surface'),panel:token('surface-alt'),strong:token('surface-strong')};
 };
 const lightColor=(value,kind,gradient=false,palette=lightPalette('paper'))=>{
  const rgba=channels(value),role=family(rgba),level=Math.max(...rgba.slice(0,3));
  if(kind==='ink')return role==='neutral'&&level<90?palette.text:palette.ink[role];
  if(kind==='edge')return palette.edge[role];
  const hex=(role!=='neutral'?palette.surface[role]:null)||(level<19?palette.canvas:level<45?palette.panel:palette.strong);
  // Flat panels need a visible surface. Preserve only gradient alpha/fades;
  // zero-alpha stops and transparent overlays must remain transparent.
  if(rgba[3]===0)return 'transparent';
  if(gradient&&rgba[3]<1){const rgb=channels(hex);return `rgba(${rgb[0]},${rgb[1]},${rgb[2]},${rgba[3]})`;}
  return hex;
 };
 const lightValue=(value,prop,palette)=>{
  if(prop==='text-shadow'||prop==='box-shadow')return 'none';
  const kind=prop.includes('background')?'surface':prop.startsWith('border')||prop==='outline-color'?'edge':'ink';
  let v=value.replace(/\b(white|black)\b/gi,c=>c.toLowerCase()==='white'?'#ffffff':'#000000').replace(/#[\da-f]{3,8}\b|rgba?\([^)]*\)/gi,c=>lightColor(c,kind,value.includes('gradient('),palette));
  if(kind==='surface')v=v.replaceAll('var(--paper)',palette.strong).replaceAll('var(--lime)',palette.surface.green).replaceAll('var(--purple)',palette.surface.purple);
  else if(kind==='ink')v=v.replaceAll('var(--ink)',palette.text);
  return v;
 };
 function legacyLight(mode){
  if(mode==='paper'&&document.querySelector('.portal'))return;
  const palette=lightPalette(mode);
  const wanted=p=>p==='color'||p.startsWith('background')||p==='border'||/^border-(top|right|bottom|left)(-color)?$/.test(p)||p==='border-color'||p==='box-shadow'||p==='text-shadow'||p==='outline-color';
  const walk=rules=>Array.from(rules).map(rule=>{
   if(rule.type===CSSRule.STYLE_RULE){
    if(rule.selectorText.includes('[data-theme')||rule.selectorText.includes(':root'))return '';
    const ds=Array.from(new Set([...rule.style,'background','border','border-top','border-right','border-bottom','border-left'])).filter(p=>wanted(p)&&rule.style.getPropertyValue(p)).map(p=>p+':'+lightValue(rule.style.getPropertyValue(p),p,palette)+(rule.style.getPropertyPriority(p)?' !important':'')+';').join('');
    if(!ds)return '';
    const selectors=rule.selectorText.split(',').map(s=>':root[data-theme="'+mode+'"] '+s.trim().replace(/^html\b/,'')).join(',');
    return selectors+'{'+ds+'}';
   }
   if(rule.type===CSSRule.MEDIA_RULE)return '@media '+rule.conditionText+'{'+walk(rule.cssRules)+'}';
   if(rule.type===CSSRule.SUPPORTS_RULE)return '@supports '+rule.conditionText+'{'+walk(rule.cssRules)+'}';
   return '';
  }).join('\n');
  const style=document.createElement('style');style.id=mode+'-legacy';
  style.textContent=Array.from(document.styleSheets).filter(s=>!s.href||!s.href.includes('/site/theme.css')).map(s=>{try{return walk(s.cssRules)}catch{return ''}}).join('\n');
  // Theme-specific typography and controls remain last in the cascade.
  const own=document.querySelector('link[href$="site/theme.css"]');document.head.insertBefore(style,own||null);
 }
 function syncThemeArtwork(){
  const cover=document.querySelector('.cover-art');
  if(cover)cover.setAttribute('aria-label',theme==='fluent'?'Sculpted violet and blue gateway supporting a luminous opening':'Lintel portal surrounded by the beasts of context rot and AI slop');
  const hero=document.querySelector('.hero-scene>img');
  if(hero){
   hero.dataset.originalSrc??=hero.getAttribute('src');hero.dataset.originalAlt??=hero.getAttribute('alt')||'';
   hero.setAttribute('src',theme==='fluent'?'assets/fluent-gateway.svg':hero.dataset.originalSrc);
   hero.setAttribute('alt',theme==='fluent'?'Sculpted Lintel gateway in violet and blue':hero.dataset.originalAlt);
  }
 }
 function apply(t,persist=true){
  if(!themes.includes(t))return;
  theme=t;root.dataset.theme=t;
  if(persist){const url=new URL(location.href);url.searchParams.set('theme',t);history.replaceState(null,'',url);}
  document.querySelector('meta[name="theme-color"]')?.setAttribute('content',t==='neon'?'#0b0b10':t==='paper'?'#f6f4ef':'#f5f5f5');
  syncThemeArtwork();
  if(persist)try{localStorage.setItem(key,t)}catch{}
  document.querySelectorAll('[data-theme-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.themeChoice===t)));
 }
 addEventListener('DOMContentLoaded',()=>{
  legacyLight('paper');legacyLight('fluent');
  const mount=document.querySelector('[data-theme-mount]')||document.querySelector('.toolbar nav')||document.querySelector('header .nav')||document.querySelector('header');
  if(mount){const c=document.createElement('div');c.className='theme-picker';c.setAttribute('role','group');c.setAttribute('aria-label','Colour theme');c.innerHTML='<button type="button" data-theme-choice="neon" title="Neon theme">✦ Neon</button><button type="button" data-theme-choice="paper" title="Paper theme">Aa Paper</button><button type="button" data-theme-choice="fluent" title="Fluent-inspired theme">◈ Fluent</button>';mount.append(c);}
  apply(theme,false);
  const stage=document.querySelector('#stage');if(stage)new MutationObserver(syncThemeArtwork).observe(stage,{childList:true});
  document.addEventListener('click',e=>{const b=e.target.closest('[data-theme-choice]');if(b)apply(b.dataset.themeChoice)});
 });
 addEventListener('storage',e=>{if(e.key===key&&themes.includes(e.newValue))apply(e.newValue,false)});
})();
