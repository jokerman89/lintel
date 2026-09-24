/* component: public-theme-switcher
 * intent: ../README.md
 * constraints: local preference only; no telemetry; demo result apps stay unchanged
 * last_intent_review: 2026-09-22 */
(() => {
 'use strict';
 const root=document.documentElement,key='lintel-theme';
 let saved;try{saved=localStorage.getItem(key)}catch{}
 let theme=new URLSearchParams(location.search).get('theme')||saved||'neon';
 if(!['neon','paper'].includes(theme))theme='neon';
 root.dataset.theme=theme;
 const semantic=hex=>{
  let h=hex.slice(1);if(h.length===3||h.length===4)h=[...h].map(x=>x+x).join('');
  const rgb=[0,2,4].map(i=>parseInt(h.slice(i,i+2),16)),[r,g,b]=rgb,a=h.length===8?h.slice(6):'';
  const max=Math.max(...rgb),min=Math.min(...rgb),d=max-min;
  let col='#262522';
  if(d>25){if(r>g*1.16&&b>g*1.12)col='#69467b';else if(g>r*1.12&&g>b*1.14)col='#415a28';else if(r>g*1.2&&r>b*1.15)col='#922e38';else if(b>r*1.13&&b>g*1.08)col='#345974';else if(r>110&&g>100&&b<g*.73)col='#526123';else col='#47434b';}
  else if(max<70)col='#373630';else col='#514f49';
  return col+a;
 };
 const paperValue=(value,prop)=>{
  if(prop==='text-shadow'||prop==='box-shadow')return 'none';
  let v=value;
  if(prop.includes('background')){
   v=v.replace(/#[\da-f]{3,8}\b/gi,h=>{let x=h.slice(1);if(x.length===3||x.length===4)x=[...x].map(c=>c+c).join('');return '#f4f2ed'+(x.length===8?x.slice(6):'');});
   v=v.replace(/rgba?\([^)]*\)/gi,c=>{const n=c.match(/[\d.]+/g);return n?.length===4?'rgba(244,242,237,'+n[3]+')':'rgb(244,242,237)';});
   v=v.replaceAll('var(--paper)','var(--ink)').replaceAll('var(--lime)','#e1e7d7').replaceAll('var(--purple)','#e9e0ed');
  }else if(prop.startsWith('border')||prop==='outline-color'){
   v=v.replace(/#[\da-f]{3,8}\b/gi,'#b6b0a7');
  }else {
   v=v.replace(/#[\da-f]{3,8}\b/gi,semantic).replaceAll('var(--ink)','#262522');
   v=v.replace(/rgba?\([^)]*\)/gi,'#514f49');
  }
  return v;
 };
 function legacyPaper(){
  if(document.querySelector('.portal'))return;
  const wanted=p=>p==='color'||p.startsWith('background')||p==='border'||/^border-(top|right|bottom|left)(-color)?$/.test(p)||p==='border-color'||p==='box-shadow'||p==='text-shadow'||p==='outline-color';
  const walk=rules=>Array.from(rules).map(rule=>{
   if(rule.type===CSSRule.STYLE_RULE){
    if(rule.selectorText.includes('[data-theme')||rule.selectorText.includes(':root'))return '';
    const ds=Array.from(new Set([...rule.style,'background','border','border-top','border-right','border-bottom','border-left'])).filter(p=>wanted(p)&&rule.style.getPropertyValue(p)).map(p=>p+':'+paperValue(rule.style.getPropertyValue(p),p)+(rule.style.getPropertyPriority(p)?' !important':'')+';').join('');
    if(!ds)return '';
    const selectors=rule.selectorText.split(',').map(s=>':root[data-theme="paper"] '+s.trim().replace(/^html\b/,'')).join(',');
    return selectors+'{'+ds+'}';
   }
   if(rule.type===CSSRule.MEDIA_RULE)return '@media '+rule.conditionText+'{'+walk(rule.cssRules)+'}';
   if(rule.type===CSSRule.SUPPORTS_RULE)return '@supports '+rule.conditionText+'{'+walk(rule.cssRules)+'}';
   return '';
  }).join('\n');
  const style=document.createElement('style');style.id='paper-legacy';
  style.textContent=Array.from(document.styleSheets).filter(s=>!s.href||!s.href.includes('/site/theme.css')).map(s=>{try{return walk(s.cssRules)}catch{return ''}}).join('\n');
  // Theme-specific typography and controls remain last in the cascade.
  const own=document.querySelector('link[href$="site/theme.css"]');document.head.insertBefore(style,own||null);
 }
 function apply(t,persist=true){
  theme=t;root.dataset.theme=t;
  if(persist)try{localStorage.setItem(key,t)}catch{}
  document.querySelectorAll('[data-theme-choice]').forEach(b=>b.setAttribute('aria-pressed',String(b.dataset.themeChoice===t)));
 }
 addEventListener('DOMContentLoaded',()=>{
  legacyPaper();
  const mount=document.querySelector('[data-theme-mount]')||document.querySelector('.toolbar nav')||document.querySelector('header .nav')||document.querySelector('header');
  if(mount){const c=document.createElement('div');c.className='theme-picker';c.setAttribute('role','group');c.setAttribute('aria-label','Colour theme');c.innerHTML='<button type="button" data-theme-choice="neon" title="Neon theme">✦ Neon</button><button type="button" data-theme-choice="paper" title="Paper theme">Aa Paper</button>';mount.append(c);}
  apply(theme,false);
  document.addEventListener('click',e=>{const b=e.target.closest('[data-theme-choice]');if(b)apply(b.dataset.themeChoice)});
 });
 addEventListener('storage',e=>{if(e.key===key&&['neon','paper'].includes(e.newValue))apply(e.newValue,false)});
})();
