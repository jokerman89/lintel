/* component: techshots-technical-module
 * intent: https://github.com/jokerman89/lintel/blob/80002ed4/docs/architecture.md
 * constraints: merged source facts; observed host acceptance remains separate
 * last_intent_review: 2026-09-25 */
window.LINTEL_TECHNICAL=({shell,icon,state,viewButton})=>{
const ref=(anchor,label='Open the technical reference')=>viewButton(label,'technical-reference.html#'+anchor,'Lintel · technical reference');
const kicker=t=>'<span class="t-k">'+t+'</span>';
const foot=(t,a='overview',label)=>'<div class="t-foot"><span>'+t+'</span>'+ref(a,label)+'</div>';
const wrap=(s,h,c='')=>shell(s,h,'technical '+c);
const line=(i,h,p)=>'<div class="t-line">'+icon(i)+'<div><h2>'+h+'</h2><p>'+p+'</p></div></div>';
const phaseNames=['SENSE','SCOPE','DEFINE','DISCOVER','PLAN','BUILD','REVIEW','SHIP','CAPTURE'];
const phases=[
 [
  "Select work and context",
  "Runtime · state/00-state.md",
  "Cycle · selected map · verified profile",
  "Configured home · sessions/profiles/",
  "Pinned generation and content digest",
  "Routing selects the work. It grants no new authority."
 ],
 [
  "Agree size and depth",
  "Runtime · state/scope.md",
  "Or jobs/&lt;id&gt;/scope.md for an active job",
  "Runtime · state/00-state.md",
  "Scope decision + its exact path",
  "Keep bounded work proportionate; resolve material ambiguity first."
 ],
 [
  "Make the design explicit",
  "Repo · engineering/design-archive/",
  "Design document when that archive exists",
  "Otherwise · runtime/state/",
  "Selected design + private lens notes if needed",
  "The approved design supplies requirements; its destination determines what travels."
 ],
 [
  "Find relevant knowledge",
  "Runtime · state/discover-report-&lt;time&gt;.md",
  "Sources · constraints · decisions · gaps",
  "Runtime · state/00-state.md",
  "Selected report path + cycle identity",
  "Read the knowledge this task needs, including relevant lessons."
 ],
 [
  "Map the original work",
  "Committed intent · plans/&lt;initiative&gt;/work.json",
  "Original spec · plan · tasks · handoff",
  "Runtime · state/",
  "Planner checkpoint + selected analysis report",
  "Spec Kit keeps its own artifacts and task IDs. One map, one task authority."
 ],
 [
  "Build one bounded package",
  "Project · declared work paths",
  "One owner · acceptance evidence per leaf",
  "Runtime · state/build-log.md",
  "Results + package review pointers",
  "A failing leaf keeps its package open. Recheck affected work after repair."
 ],
 [
  "Review the actual result",
  "Runtime · reviews/&lt;record&gt;.json",
  "Decision bound to content and acceptance",
  "Selected evidence paths",
  "QA · reviewer corroboration · readable findings",
  "Required review stays open until independent evidence exists."
 ],
 [
  "Deliver within authority",
  "Git / platform · selected delivery path",
  "Commit · PR · release as authorized",
  "Runtime · state/00-state.md",
  "Delivery result + evidence pointers",
  "A later relevant rejection blocks an older pass. Deployment still needs authorization."
 ],
 [
  "Keep the next session useful",
  "Committed knowledge · memory/ + decisions/",
  "Lessons · working state · warranted ADRs",
  "Committed handoff · mapped prompt",
  "Verified progress + unresolved next action",
  "Capture preserves the rule and evidence. Its future use shows whether it helped."
 ]
];
const clients=[
 {
  "name": "Claude",
  "entry": ".claude/skills/li-*/SKILL.md",
  "native": ".github/lintel/ · shared source",
  "detail": "Code CLI and Desktop Code local routes.",
  "hook": "Optional Claude hooks",
  "hpath": "Code plugin: hooks/hooks.json",
  "note": "Repository kit installs no hooks. Check actual registration and firing."
 },
 {
  "name": "Copilot",
  "entry": ".github/skills/li-*/SKILL.md",
  "native": ".github/agents/*.agent.md",
  "detail": "CLI · App · VS Code · cloud; 3 role profiles.",
  "hook": "No Lintel hooks installed",
  "hpath": ".github/lintel/ · shared source",
  "note": "14 starter workflows. Discovery and execution need surface-specific evidence."
 },
 {
  "name": "Codex / Cursor",
  "entry": ".agents/skills/li-*/SKILL.md\n.cursor/skills/li-*/SKILL.md",
  "native": ".github/lintel/ · shared source",
  "detail": "Codex CLI/App/IDE · Cursor CLI/IDE/cloud.",
  "hook": "Actual tools decide",
  "hpath": "Codex cloud: manual route",
  "note": "Plugin routes remain. Delegation and isolation need observed host support."
 },
 {
  "name": "Gemini / OpenCode",
  "entry": ".gemini/skills/li-*/SKILL.md\n.opencode/skills/li-*/SKILL.md",
  "native": ".github/lintel/ · shared source",
  "detail": "Native-format CLI routes; existing routes remain.",
  "hook": "No Lintel hooks installed",
  "hpath": "OpenCode desktop/IDE: manual",
  "note": "Delivered wrapper files do not prove live discovery or execution."
 },
 {
  "name": "More surfaces",
  "entry": "Selected native skill roots\nor .github/lintel/START.md",
  "native": "Factory · Kiro · Antigravity · more",
  "detail": "Exact CLI, IDE, desktop and cloud records.",
  "hook": "Explicit manual fallback",
  "hpath": "Use the exact surface record",
  "note": "Continue, Aider and selected cloud/IDE surfaces use the manual route."
 }
];
return {
techkit:s=>wrap(s,'<div class="t-toolbox"><div class="t-library">'+kicker('UNIVERSAL 0.11.0 · SOURCE LIBRARY')+'<div class="t-counts"><div><strong>127</strong><span>skills</span></div><div><strong>69</strong><span>agent roles</span></div><div><strong>33</strong><span>hook scripts</span></div></div><p>Reusable methods. Scoped roles.<br>Hooks where registered.</p></div><div class="t-working">'+icon('compass')+kicker('THIS TASK’S WORKING SET')+'<h2>One intent.<br>Relevant context.<br>Enough verification.</h2><span class="t-aside">~80 skills planned through curation; 127 today.</span></div></div>'+foot('A separate 18-minute module · merged source 80002ed4','overview','Browse all inventories'),'t-kit'),
techskills:s=>wrap(s,'<div class="t-skill-loop">'+[['route','PLAN','Requirements → cards'],['terminal','BUILD','Packages → evidence'],['check','REVIEW','Bound evidence → verdict'],['bulb','CAPTURE','Corrections → lessons']].map(([i,h,p])=>'<article>'+icon(i)+'<h2>'+h+'</h2><p>'+p+'</p></article>').join('')+'</div><div class="t-skill-depth">'+line('compass','Route & recover','cycle · scope · discover · resume')+line('layers','Add engineering depth','ta · da · sc · dh · tq')+line('flask','Create & inspect','Design · browser · documents¹')+'</div>'+foot('¹ Document-format capabilities remain staged.','skills','Search all 127 skills'),'t-skills'),
techagents:s=>wrap(s,'<div class="t-agent-chain"><article>'+kicker('PREPARE')+icon('compass')+'<h2>Planner<br>Architect</h2><p>Intent · alternatives<br>Acceptance · dependencies</p></article><i>→</i><article>'+kicker('IMPLEMENT')+icon('terminal')+'<h2>build<br>+ scoped worker</h2><p>Declared files<br>Attributable changes</p></article><i>→</i><article>'+kicker('CHALLENGE')+icon('check')+'<h2>CodeReviewer<br>TestRunner</h2><p>SecurityAuditor when relevant<br>Findings + limitations</p></article></div><div class="t-coordinator">'+icon('git')+'<strong>Swarm: one coordinator</strong><span>One work map · isolated lanes · reviewed integration</span></div>'+foot('Missing independent review? Substantive work stays open.','agents','Search all 69 agents'),'t-agents'),
techstorage:s=>{const kit=state.techHome==='kit';return wrap(s,'<div class="t-storage-grid"><article>'+kicker('01 / INSTALLED SOURCE')+icon('layers')+'<h2>The reusable library</h2><code>skills/ · agents/ · '+(kit?'docs/':'hooks/')+'<br>lib/ · bin/ · scaffolding/</code><p>'+(kit?'Shared source: <b>.github/lintel/</b> · no hooks':'Plugin / bare-install source bundle')+'</p></article><article class="t-home">'+kicker('02 / CONFIGURATION HOME')+'<div class="t-tabs"><button data-tech-home="default" aria-pressed="'+!kit+'">Bare install</button><button data-tech-home="kit" aria-pressed="'+kit+'">Repo kit</button></div><h2>'+(kit?'Local by default':'Personal by default')+'</h2><code>'+(kit?'.claude/runtime/lintel-home/':'~/.lintel/')+'</code><p>Explicit <b>LINTEL_HOME</b> overrides the default.</p></article><article class="t-durable">'+kicker('03 / PROJECT · COMMIT INTENTIONALLY')+icon('git')+'<h2>Knowledge that travels</h2><code>.claude/memory/<br>.claude/decisions/ · .claude/plans/</code><p>Plan · decision · lesson · handoff</p></article><article class="t-runtime">'+kicker('04 / PROJECT · GIT-IGNORED')+icon('clock')+'<h2>Local working state</h2><code>.claude/runtime/<br>state/ · reviews/ · sessions/ · audit/</code><p>Local evidence does not travel with a clone.</p></article></div>'+foot('Source · preferences · durable knowledge · local evidence.','artifacts','Inspect all output families'),'t-storage');},
techcycle:s=>{const n=state.techPhase??4,p=phases[n];return wrap(s,'<div class="t-phase-tabs" role="group" aria-label="Choose a cycle phase">'+phaseNames.map((x,i)=>'<button data-tech-phase="'+i+'" aria-pressed="'+(i===n)+'"><small>0'+(i+1)+'</small>'+x+'</button>').join('')+'</div><div class="t-phase-result" aria-live="polite"><div class="t-phase-purpose">'+kicker(phaseNames[n])+'<h2>'+p[0]+'</h2>'+icon(n===8?'bulb':n===4?'route':'file')+'</div><div class="t-phase-files"><div>'+kicker(p[1])+'<p>'+p[2]+'</p></div><div>'+kicker(p[3])+'<p>'+p[4]+'</p></div></div></div><div class="t-callout">'+p[5]+'</div>'+foot('Paths below .claude/ unless a different root is shown.','artifacts','Phase-by-phase inventory'),'t-cycle');},
techresume:s=>wrap(s,'<div class="t-resume-layout"><div class="t-resume-map"><div>'+kicker('SELECT THE INITIATIVE')+'<code>plans/todo.md<br>memory/working-state.md</code></div><b>↓</b><div class="t-map-focus">'+kicker('COMMITTED INDEX')+'<code>plans/&lt;initiative&gt;/work.json</code></div><b>↓</b><div>'+kicker('FOLLOW THE ORIGINAL ARTIFACTS')+'<code>spec · plan · tasks · prompt<br>+ swarm coordination when used</code></div></div><div class="t-resume-truth">'+icon('handoff')+'<h2>Same work.<br>Verified context.</h2><p>Original cycle + profile.<br>Resume the unmet step.</p><div class="t-missing">Missing runtime: recover intent.<br>Missing review: work stays open.</div></div></div>'+foot('Profile drift needs reconciliation. Spec Kit keeps its original tasks.','recovery','Read the recovery contract'),'t-resume'),
techhooks:s=>{const opt=state.techHooks==='optional';const rows=opt?[['15','ENGINEERING','Architecture · data · security · deployment · testing','Advisory scripts; several inspect the existing file before an edit.'],['6','CROSS-CUTTING','Context · design · freeze · merge · production · DOM text','Not activated by the core manifest.'],['3','JOB LIFECYCLE','job-begin · job-end · job-stale-warn','Explicit helper contracts; begin/end can mutate files.']]:[['1','SessionStart','session-digest','Adds compact startup context.'],['2','UserPromptSubmit','cycle-position-inject · no-customer-data-in-message','Context reminder + prompt warning.'],['4','PreToolUse','Edit warning · git secret/data blockers · main-push warning','Two git scanners deny; unavailable checks cannot pass.'],['1','PostToolUse','memory-budget-warn','Warns about budgets; does not rewrite memory.'],['1','Stop','cycle-incomplete-warn','Emits advice; no forced continuation or checkpoint.']];return wrap(s,'<div class="t-hook-heading"><div class="t-tabs"><button data-tech-hooks="core" aria-pressed="'+!opt+'">9 registered core</button><button data-tech-hooks="optional" aria-pressed="'+opt+'">24 optional / manual</button></div><span>Claude plugin route · repo kit installs none</span></div><div class="t-hook-list '+(opt?'is-optional':'')+'">'+rows.map(([n,h,p,d])=>'<div><b>'+n+'</b><section><h2>'+h+'</h2><p>'+p+'</p></section><small>'+d+'</small></div>').join('')+'</div>'+foot('A receipt records an observation. No record means unobserved.','hooks','Inspect all 33 hook scripts'),'t-hooks');},
techclients:s=>{const n=state.techClient??1,c=clients[n];return wrap(s,'<div class="t-tabs t-client-tabs">'+clients.map((x,i)=>'<button data-tech-client="'+i+'" aria-pressed="'+(i===n)+'">'+x.name+'</button>').join('')+'</div><div class="t-client-content" aria-live="polite"><article>'+kicker('DISCOVERY / ENTRY')+'<h2>'+c.name+'</h2><pre>'+c.entry+'</pre><code>'+c.native+'</code><p>'+c.detail+'</p></article><article>'+kicker('LINTEL EXECUTION BOUNDARY')+icon('lock')+'<h2>'+c.hook+'</h2><code>'+c.hpath+'</code><p>'+c.note+'</p></article></div><div class="t-client-common">'+icon('folder')+'<b>Shared project knowledge</b><code>.claude/memory/ · decisions/ · plans/</code></div>'+foot('37 named surfaces + manual fallback. Validate the actual client.','clients','Full client and path matrix'),'t-clients');},
techpacks:s=>wrap(s,'<div class="t-pack-path"><article>'+kicker('REQUIRE')+icon('person')+'<h2>Your requirements</h2><code>Required pack + policy</code><p>Team standards<br>Explicit task authority</p></article><b>→</b><article>'+kicker('RESOLVE')+icon('building')+'<h2>Effective profile</h2><code>context · generation · digest</code><p>Exact sources<br>Explicit changes</p></article><b>→</b><article>'+kicker('VERIFY')+icon('file')+'<h2>This work</h2><code>Acceptance + bound evidence</code><p>Original requirements<br>Current review + QA</p></article></div><div class="t-policy-rail">'+icon('lock')+'<strong>Platform permissions + CI</strong><span>Configured and verified separately.</span></div>'+foot('Required pack missing or changed? Stop the dependent action.','packs','Pack resolution and trust'),'t-packs'),
techmaintenance:s=>wrap(s,'<div class="t-maintain">'+[['book','CAPTURE','Save the rule<br>and its reason.','A correction becomes a reviewed lesson.'],['route','RETRIEVE','Load what<br>this task needs.','Select relevant knowledge.'],['archive','PRESERVE','Retain evidence.<br>Dispose explicitly.','Owned snapshots; scoped cleanup.']].map(([i,k,h,p])=>'<article>'+icon(i)+kicker(k)+'<h2>'+h+'</h2><p>'+p+'</p></article>').join('')+'</div><div class="t-maintain-bottom"><div><b>A lesson preserves a correction</b><span>Its next use shows whether it helped.</span></div><div><b>A receipt preserves an observation</b><span>It does not certify quality or control.</span></div></div>'+foot('Keep the next session useful; preserve evidence before disposal.','maintenance','What maintenance actually does'),'t-maintenance'),
techproof:s=>wrap(s,'<div class="t-proof-grid">'+[['01','DISCOVERY','Which copy actually loaded?','file'],['02','REAL TASK','Does the evidence match the work?','check'],['03','COLD RESTART','Same work, profile and next step?','handoff'],['04','NEGATIVE CASE','Does failed acceptance stay blocked?','flask']].map(([n,k,h,i])=>'<article><span>'+n+'</span>'+icon(i)+kicker(k)+'<h2>'+h+'</h2></article>').join('')+'</div><div class="t-proof-end"><p>Verify the exact client.<br><b>Measure accepted outcomes and overhead.</b></p><div>'+ref('rollout','Take the pilot checklist')+'<a class="action" href="#three-hours">Back to the main story ↗</a></div></div>','t-proof')
};
};
