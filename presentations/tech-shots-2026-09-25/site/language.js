/* component: presentation-language
 * implements: none — bounded presentation UI addition
 * intent: ../README.md
 * constraints: local catalogues only; preserve code, identifiers and original evidence
 * last_intent_review: 2026-09-28 */
(() => {
 'use strict';
 const root=document.documentElement,key='lintel-language',supported=['en','sv'];
 const requested=new URLSearchParams(location.search).get('lang');
 let stored;try{stored=localStorage.getItem(key)}catch{}
 let language=supported.includes(requested)?requested:requested?'en':supported.includes(stored)?stored:'en';
 const catalogue=window.LINTEL_SWEDISH||{};
 const sources=new WeakMap(),attributes=new WeakMap();
 const skip='script,style,pre,code,kbd,samp,svg,textarea,[data-no-translate]';
 const attributeNames=['title','alt','aria-label','placeholder'];
 let observer=null,scheduled=false,titleSource=document.title,titleRendered=document.title;
 root.lang=language;
 if(supported.includes(requested))try{localStorage.setItem(key,language)}catch{}
 function text(value){
  if(language==='en'||!value)return value;
  const source=value.trim();let translated=catalogue[source];
  // Counter values and the next-slide title change independently of slide text.
  if(translated===undefined){
   const position=source.match(/^SLIDE (\d+)( \/ \d+)?$/);
   const announcement=source.match(/^Slide (\d+) of (\d+): (.*)$/);
   const title=source.match(/^(\d+) · (.*) · Lintel$/);
   if(position)translated='SLIDE '+position[1]+(position[2]||'');
   else if(announcement)translated='Slide '+announcement[1]+' av '+announcement[2]+': '+text(announcement[3]);
   else if(title)translated=title[1]+' · '+text(title[2])+' · Lintel';
   else return value;
  }
  return value.slice(0,value.indexOf(source))+translated+value.slice(value.indexOf(source)+source.length);
 }
 function update(node){
  const current=node.data,record=sources.get(node);
  const source=record&&current===record.rendered?record.source:current;
  const rendered=text(source);sources.set(node,{source,rendered});
  if(current!==rendered)node.data=rendered;
 }
 function refresh(){
  if(!document.body)return;
  observer?.disconnect();
  const walker=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let node;
  while(node=walker.nextNode())if(node.parentElement&&!node.parentElement.closest(skip))update(node);
  for(const element of document.querySelectorAll('[title],[alt],[aria-label],[placeholder]')){
   if(element.closest(skip))continue;
   let records=attributes.get(element);if(!records){records={};attributes.set(element,records);}
   for(const name of attributeNames){
    const current=element.getAttribute(name);if(current===null)continue;
    const previous=records[name],source=previous&&current===previous.rendered?previous.source:current;
    const rendered=text(source);records[name]={source,rendered};if(current!==rendered)element.setAttribute(name,rendered);
   }
  }
  if(document.title!==titleRendered)titleSource=document.title;
  titleRendered=text(titleSource);if(document.title!==titleRendered)document.title=titleRendered;
  document.querySelectorAll('[data-language]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.language===language)));
  observer?.observe(document.body,{subtree:true,childList:true,characterData:true,attributes:true,attributeFilter:attributeNames});
 }
 function setLanguage(next,persist=true){
  if(!supported.includes(next))return;
  const changed=language!==next;language=next;root.lang=next;
  if(persist){const url=new URL(location.href);url.searchParams.set('lang',next);history.replaceState(null,'',url);try{localStorage.setItem(key,next)}catch{}}
  refresh();if(changed)window.dispatchEvent(new CustomEvent('lintel:language',{detail:{language}}));
 }
 const flags={
  en:'<svg viewBox="0 0 60 40" aria-hidden="true" focusable="false"><path fill="#18356b" d="M0 0h60v40H0z"/><path stroke="#fff" stroke-width="8" d="m0 0 60 40m0-40L0 40"/><path stroke="#c63543" stroke-width="3" d="m0 0 60 40m0-40L0 40"/><path stroke="#fff" stroke-width="13" d="M30 0v40M0 20h60"/><path stroke="#c63543" stroke-width="7" d="M30 0v40M0 20h60"/></svg>',
  sv:'<svg viewBox="0 0 60 40" aria-hidden="true" focusable="false"><path fill="#17669a" d="M0 0h60v40H0z"/><path fill="#f4cf46" d="M18 0h8v40h-8zM0 16h60v8H0z"/></svg>'
 };
 function start(){
  const mount=document.querySelector('.toolbar nav')||document.querySelector('.site-header [data-theme-mount]');
  if(mount){const picker=document.createElement('div');picker.className='language-picker';picker.setAttribute('role','group');picker.setAttribute('aria-label','Language');picker.innerHTML=supported.map(lang=>'<button type="button" data-language="'+lang+'" lang="'+lang+'" aria-label="'+(lang==='en'?'English':'Svenska')+'" title="'+(lang==='en'?'English':'Svenska')+'" data-no-translate>'+flags[lang]+'</button>').join('');mount.append(picker);}
  observer=new MutationObserver(()=>{if(!scheduled){scheduled=true;queueMicrotask(()=>{scheduled=false;refresh();});}});
  refresh();
 }
 window.LINTEL_LANGUAGE={text,refresh,setLanguage,get language(){return language;}};
 document.addEventListener('click',event=>{const button=event.target.closest('[data-language]');if(button)setLanguage(button.dataset.language);});
 addEventListener('storage',event=>{if(event.key===key&&supported.includes(event.newValue))setLanguage(event.newValue,false);});
 if(document.readyState==='loading')addEventListener('DOMContentLoaded',start,{once:true});else start();
})();
