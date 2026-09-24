
window.LINTEL_OPENING = ({shell,icon,state}) => ({
  systemcover:s=>shell(s,
    '<div class="cover-art" role="img" aria-label="Lintel portal surrounded by the beasts of context rot and AI slop"></div>'+
    '<div class="cover-intro"><span>JOHANNES ÅKERMAN</span><span>CAIP SE + CSA</span></div>'+
    '<div class="cover-exchange"><div><span>09:12 · YOU</span><p>One dashboard, please.</p></div><i aria-hidden="true">→</i><div><span>12:12 · AGENT</span><p>I built you <strong>a platform.</strong></p></div></div>'+
    '<div class="cover-prompt">A quick show of hands. Teams, you too.</div>', 'system-cover'),
  systemmap:s=>shell(s,
    '<div class="system-map" aria-label="Lintel architecture: client runs the method, skills and roles; event hooks check selected actions; project records feed future tasks">'+
    '<div class="map-client">'+icon('terminal')+'<strong>Your coding client</strong><span>CLI / editor / desktop</span><b>You set the outcome.</b></div>'+
    '<div class="map-pack"><span class="map-kicker">TEAM PACK</span>'+icon('building')+'<h2>Your context</h2><p>Standards<br>Knowledge<br>Voice + brand</p><span class="pack-feed">informs the work →</span></div>'+
    '<div class="map-core"><div class="map-core-title"><b>LINTEL</b><span>Reusable workflows + local helpers</span></div>'+
    '<div class="map-method">'+icon('route')+'<strong>Method</strong><span>Understand · plan · build · verify · capture</span></div>'+
    '<div class="map-invokes">agent loads workflows and delegates roles</div><div class="map-executors"><div>'+icon('book')+'<strong>Skills</strong><span>Reusable recipes</span></div><div>'+icon('person')+'<strong>Agent roles</strong><span>Focused work + review</span></div><div class="map-hooks">'+icon('check')+'<strong>Hooks</strong><span>Checks on host events</span></div></div>'+
    '<div class="map-write"><span>agents + helpers write and maintain</span><b aria-hidden="true">↓</b></div>'+
    '<div class="map-records">'+icon('folder')+'<div><h2>Project scaffolding</h2><p>Plans + scope <i>·</i> Decisions + lessons <i>·</i> Handoff + next action</p></div></div>'+
    '<div class="map-storage"><span>Reviewed records travel with Git</span><span>Runtime state stays Git-ignored</span></div></div>'+
    '<div class="map-return"><span class="return-line" aria-hidden="true"></span>'+icon('git')+'<span class="map-kicker">COMPOUNDING</span><h2>The next task<br>starts wiser.</h2><p>Retrieve relevant<br>decisions and lessons.</p></div>'+
    '<div class="map-platform">'+icon('lock')+'<strong>Platform controls</strong><span>Permissions · sandbox · CI · deployment gates</span></div></div>', 'system-map-slide'),
  buildingblocks:s=>shell(s,
    '<div class="blocks-grid">'+[
      ['folder','Scaffolding','Where the project remembers.','Plans, decisions, lessons, handoffs.'],
      ['route','Method','How the work moves forward.','Clarify, plan, build, review, capture.'],
      ['book','Skills','Recipes you stop rewriting.','Architecture, testing, design, review.'],
      ['person','Agent roles','A focused job description.','Specialist work and independent review.'],
      ['check','Hooks','Checks at the right event.','Surface context, warn or block.'],
      ['git','Compounding','Useful learning comes back.','Retrieve it. Apply it. Check the result.']
    ].map(([i,h,p,d],n)=>'<article><div class="block-heading">'+icon(i)+'<span>0'+(n+1)+'</span></div><h2>'+h+'</h2><p>'+p+'</p><small>'+d+'</small></article>').join('')+'</div>', 'building-blocks'),
  stateflow:s=>{
    const step=state.trail??0;
    const moments=[
      {name:'1 · Clarify',kicker:'A SKILL SURFACES AMBIGUITY',headline:'“Which time zone defines export dates?”',copy:'The agent asks. You decide: UTC or local time?',label:'DECISION NEEDED',record:'date_basis: unresolved',task:'next: ask the operator',resume:'The missing answer stays visible.'},
      {name:'2 · Record',kicker:'THE ANSWER CHANGES THE WORK',headline:'“Use UTC, including offsets.”',copy:'The agent records the decision and updates the plan.',label:'TRAIL UPDATED',record:'decision: UTC boundaries',task:'next: add the boundary test',resume:'Decision + next action now exist outside the chat.'},
      {name:'3 · Restart',kicker:'A FRESH SESSION READS THE TRAIL',headline:'“UTC is decided. The test is next.”',copy:'Load the handoff. Check the files. Continue the task.',label:'CONTEXT RESTORED',record:'read: plan + decision + handoff',task:'resume: add the boundary test',resume:'No need to ask the same question again.'}
    ];const m=moments[step];const events=[['Prompt event','surface current step','agent sees open work'],['Tool event','run selected check','warn / block if configured'],['Session start','surface a digest','agent reads the records']][step];
    return shell(s,
      '<div class="trail-path"><div>'+icon('route')+'<b>Method</b><span>Requires the trail</span></div><i>→</i><div>'+icon('book')+'<b>Skills + agents</b><span>Ask, act and write</span></div><i>→</i><div>'+icon('folder')+'<b>Project records</b><span>Keep decisions + state</span></div><i>→</i><div>'+icon('handoff')+'<b>Next session</b><span>Read, verify, resume</span></div></div>'+
      '<div class="trail-example"><div class="trail-narrative"><nav aria-label="Walk through the example">'+moments.map((x,i)=>'<button data-trail="'+i+'" aria-pressed="'+(step===i)+'" class="'+(step===i?'selected':'')+'">'+x.name+'</button>').join('')+'</nav><span class="trail-kicker">'+m.kicker+'</span><h2>'+m.headline+'</h2><p>'+m.copy+'</p></div><div class="trail-record" aria-live="polite"><span class="record-top">PROJECT / SCAFFOLDING <b>'+m.label+'</b></span><pre>'+m.record+'\n'+m.task+'</pre><div class="record-outcome">'+icon(step===0?'bubble':'check')+m.resume+'</div></div></div>'+
      '<div class="trail-hooks">'+icon('check')+'<b>Registered hooks</b><span>'+events[0]+'</span><i>→</i><span>'+events[1]+'</span><i>→</i><span>'+events[2]+'</span><small>They support the workflow.<br>The agent asks the question.</small></div>', 'state-flow');
  }
});
