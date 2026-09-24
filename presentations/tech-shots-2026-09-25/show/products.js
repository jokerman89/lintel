/* Product family illustrations. Theme-specific art is separate from editable release states. */
const PRODUCT_ART=[
 {key:'lintel',id:'product-lintel',name:'Lintel',tagline:'The full harness',status:'Available',alt:'Nested architectural portal: the complete Lintel harness.'},
 {key:'caip',id:'product-caip',name:'CAIP Pack',tagline:'Your team context',status:'Link to follow',alt:'Layered translucent panels: the CAIP Pack brings team context.'},
 {key:'core',id:'product-core',name:'Core',tagline:'Build for your case',status:'Planned',alt:'An open frame with one floating insert: a focused Lintel Core workflow.'},
 {key:'benchmark',id:'product-benchmark',name:'Benchmark',tagline:'Test the value',status:'Planned',alt:'A precision calibration reticle: measure whether Lintel earns its place.'}
];
const productImagePath=key=>'../assets/products/'+key+'-'+(document.documentElement.dataset.theme==='paper'?'paper':'neon')+'.png';
// A theme change swaps the original artwork, not a filter over the Neon image.
new MutationObserver(()=>document.querySelectorAll('.product-art[data-art-id]').forEach(a=>{
 const src=productImagePath(a.dataset.artId);a.setAttribute('href',src);a.querySelector('img').setAttribute('src',src);
})).observe(document.documentElement,{attributes:true,attributeFilter:['data-theme']});
window.LINTEL_PRODUCTS=({shell,icon,viewButton})=>({
 productfamily:s=>shell(s,
  '<div class="product-gallery">'+PRODUCT_ART.map(({key,id,name,tagline,status,alt})=>{
   const src=productImagePath(key);
   return '<article class="product-portrait"><a class="product-art" data-art-id="'+key+'" href="'+src+'" target="_blank" rel="noopener" title="Open '+name+' artwork"><img src="'+src+'" width="1024" height="1024" alt="'+alt+'"></a><button class="product-caption" data-product="'+id+'"><span>'+name+' <i>↗</i></span><small>'+tagline+'</small><em>'+status+'</em></button></article>';
  }).join('')+'</div>',
  'product-slide product-reveal'),
 productpack:s=>shell(s,
  '<div class="pack-layout"><div class="pack-request"><span class="p-label">THE REQUEST</span><blockquote>“Prepare a customer<br>technical workshop.”</blockquote><p>Same agent.<br>A more relevant starting point.</p></div><div class="pack-context"><div class="pack-context-title"><span>THE TEAM CONTEXT</span><strong>CAIP</strong></div><div class="pack-context-lines"><div><b>Role</b><span>MS Employee in CAIP</span></div><div><b>Knowledge</b><span>Approved team material</span></div><div><b>Standards</b><span>How we prepare and review</span></div></div><div class="pack-result">'+icon('file')+'<div><span>THE INTENDED RESULT</span><strong>A workshop brief<br>that fits the team.</strong></div></div></div></div><div class="p-bottom"><p>Lintel carries the method. The pack carries the context.</p><span>Pack #1 · Distribution link to follow</span></div>',
  'product-slide product-pack'),
 productcore:s=>shell(s,
  '<div class="core-journey"><div class="core-client"><span class="p-label">YOUR EXISTING CODING APP</span>'+icon('terminal')+'<h2>Desktop or CLI</h2><p>Including GitHub Copilot</p></div><div class="core-workflow"><span class="p-label">A CASE-SPECIFIC CORE</span><div class="core-start"><b>YOU INVOKE IT</b><q>Run the architecture review.</q></div><div class="core-path"><div><span>01</span><b>Relevant context</b></div><i>→</i><div><span>02</span><b>Chosen workflow</b></div><i>→</i><div><span>03</span><b>Reviewed artifacts</b></div></div><p class="core-output">Review notes + decision brief + next action</p></div></div><div class="core-fit"><strong>A focused workflow.<br>Less to maintain.</strong><p>For work a person drives in the coding app.<br>Hosted services still suit unattended execution.</p></div>',
  'product-slide product-core'),
 productbenchmark:s=>shell(s,
  '<div class="benchmark-constant"><span class="p-label">HOLD CONSTANT</span><p>Model <i>·</i> Task <i>·</i> Project knowledge <i>·</i> Tests + permissions</p></div><div class="benchmark-arms"><div><span>A / COMPETENT BASELINE</span><h2>The agent +<br>a well-prepared repo</h2></div><div class="benchmark-versus">vs.</div><div><span>B / WORKFLOW TREATMENT</span><h2>The same setup<br>+ Lintel</h2></div></div><div class="benchmark-measures">'+[
   ['clock','Accepted change','How long until it is usable?'],['bubble','Interventions','How often did you step in?'],['handoff','Defects + recovery','What failed or got forgotten?'],['scales','Total cost','Including process overhead.']
  ].map(([i,h,p])=>'<div>'+icon(i)+'<h3>'+h+'</h3><p>'+p+'</p></div>').join('')+'</div><div class="p-bottom"><p>Measure outcomes. Include the overhead.</p>'+viewButton('Open the prepared comparison','../comparison/index.html','Prepared A/B exhibit · one run per arm')+'</div>',
  'product-slide product-benchmark')
});
