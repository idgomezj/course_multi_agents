const scenarioEl=document.querySelector('#scenario');
const managerModelEl=document.querySelector('#managerModel');
const referenceBtn=document.querySelector('#referenceBtn');
const agentBtn=document.querySelector('#agentBtn');
const statusText=document.querySelector('#statusText');
const helpDialog=document.querySelector('#helpDialog');
const helpOpen=document.querySelector('#helpOpen');
const helpClose=document.querySelector('#helpClose');

async function getJson(url,options){
  const r=await fetch(url,options);
  const d=await r.json();
  if(!r.ok) throw new Error(d.detail||JSON.stringify(d));
  return d;
}
function money(v){return v==null?'—':new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(v)}
function pct(v){return v==null?'—':Number(v).toFixed(1)+'%'}
function escapeHtml(s){return String(s).replace(/[&<>'"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c]))}

async function init(){
  const [status,scenarios,config]=await Promise.all([
    getJson('/demo/api/status'),
    getJson('/demo/api/scenarios'),
    getJson('/demo/api/config')
  ]);
  scenarioEl.innerHTML=scenarios.map(x=>'<option value="'+x.id+'">'+x.id+' — '+x.title+'</option>').join('');
  managerModelEl.innerHTML=status.manager_models.map(x=>{
    const state=x.configured?'ready':'API key missing';
    return '<option value="'+x.id+'">'+x.label+' — '+x.model+' ('+state+')</option>';
  }).join('');
  managerModelEl.value=status.manager_model_id;
  document.querySelector('#runtimeStatus').innerHTML=[
    '<span class="pill">Data: '+(status.case_loaded?'READY':'MISSING')+'</span>',
    '<span class="pill">RAG: '+(status.rag_ready?'READY':'MISSING')+'</span>',
    '<span class="pill">Skills: '+status.skill_count+'</span>',
    '<span class="pill">'+status.models.model_a.artifact+': '+(status.models.model_a.ready?'READY':'NOT TRAINED')+'</span>',
    '<span class="pill">'+status.models.model_b.artifact+': '+(status.models.model_b.ready?'READY':'NOT TRAINED')+'</span>',
    ...Object.entries(status.solved_config_files||{}).map(([k,v])=>'<span class="pill">'+escapeHtml(k)+': '+(v?'READY':'MISSING')+'</span>'),
    ...status.manager_models.map(x=>'<span class="pill">'+x.label+': '+(x.configured?'READY':'KEY MISSING')+'</span>')
  ].join('');
  document.querySelector('#solvedConfig').innerHTML=
    '<b>Hard constraints:</b><pre>'+escapeHtml(JSON.stringify(status.hard_constraints||{},null,2))+'</pre>'+
    '<b>Forecast policy:</b><pre>'+escapeHtml(JSON.stringify(config.runtime.forecast_policy||{},null,2))+'</pre>'+
    '<b>Risk policy:</b><pre>'+escapeHtml(JSON.stringify(config.runtime.risk_policy||{},null,2))+'</pre>'+
    '<b>Planning objectives:</b><pre>'+escapeHtml(JSON.stringify(config.runtime.planning_objectives||{},null,2))+'</pre>'+
    '<b>Document authority:</b><pre>'+escapeHtml(JSON.stringify(config.runtime.document_priorities||{},null,2))+'</pre>';
  statusText.textContent='Ready. Review the solved configuration, then use Reference and AI Manager.';
}

function resetTrace(){document.querySelector('#trace').innerHTML='';}

function renderEvaluationBreakdown(data){
  const b=data.evaluation_breakdown||{};
  const op=b.operational||{};
  const rag=b.rag||{};
  const st=b.skills_tools||{};
  const components=st.components||{};
  const tools=st.operational_tools||{};
  const discipline=st.discipline||{};
  const efficiency=st.efficiency||{};

  document.querySelector('#evaluationBreakdown').innerHTML=
    '<b>Operational:</b> '+pct(op.total_score)+' — 35% feasibility + 25% service + 40% cost'+
    (op.feasible_gate===false?' <span class="bad">(critical-feasibility gate forced score to 0)</span>':'')+
    '<br><br><b>RAG:</b> '+pct(rag.total_score)+
    ' — expected sources: '+escapeHtml(JSON.stringify(rag.expected_sources||[]))+
    '; retrieved expected: '+escapeHtml(JSON.stringify(rag.retrieved_expected_sources||[]))+
    '<br><br><b>Skills / Tools:</b> '+pct(st.total_score)+
    '<br>• Skill usage: '+Number(components.skill_usage||0).toFixed(1)+' / 25'+
    '<br>• Expected operational tools: '+Number(components.expected_operational_tools||0).toFixed(1)+' / 45'+
    '<br>• Cost + validation: '+Number(components.cost_and_validation||0).toFixed(1)+' / 20'+
    '<br>• Efficiency: '+Number(components.efficiency||0).toFixed(1)+' / 10'+
    '<br>• Missing expected operational tools: '+escapeHtml(JSON.stringify(tools.missing||[]))+
    '<br>• calculate_plan_cost: '+(discipline.calculate_plan_cost_called?'YES':'NO')+
    '; validate_plan: '+(discipline.validate_plan_called?'YES':'NO')+
    '<br>• Discouraged calls: '+escapeHtml(JSON.stringify(efficiency.discouraged_calls||[]))+
    '; exact duplicate calls: '+Number(efficiency.exact_duplicate_calls||0);
}
function renderSimulation(sim,benchmark){
  document.querySelector('#feasibility').textContent=sim.feasible?'YES':'NO';
  document.querySelector('#feasibility').className=sim.feasible?'good':'bad';
  document.querySelector('#service').textContent=pct(sim.service_level*100);
  document.querySelector('#totalCost').textContent=money(sim.total_cost);
  document.querySelector('#costBreakdown').innerHTML=Object.entries(sim.cost_breakdown||{}).map(([k,v])=>'<div><b>'+escapeHtml(k)+'</b>: '+money(v)+'</div>').join('');
  document.querySelector('#violations').innerHTML=(sim.violations||[]).length
    ? sim.violations.map(v=>'<div class="'+(v.critical?'bad':'')+'">'+escapeHtml(v.code)+': '+escapeHtml(v.message)+'</div>').join('')
    : '<span class="good">No violations</span>';
  if(benchmark!=null){
    const gap=(sim.total_cost-benchmark)/benchmark;
    document.querySelector('#costScore').textContent=(gap<=.05?'100':gap<=.10?'90':gap<=.20?'75':gap<=.30?'60':'<60')+'%';
  } else document.querySelector('#costScore').textContent='—';
}

function renderReference(data){
  renderSimulation(data.simulation,data.benchmark_cost);
  document.querySelector('#ragScore').textContent='N/A';
  document.querySelector('#skillScore').textContent='N/A';
  resetTrace();
  document.querySelector('#plan').textContent=JSON.stringify(data.plan,null,2);
  document.querySelector('#evaluationBreakdown').innerHTML='Published-reference mode evaluates the deterministic plan/simulator result. RAG and Skills/Tools are not scored because no AI Manager ran.';
}

function renderAgent(data){
  document.querySelector('#feasibility').textContent=data.feasibility_score===100?'YES':'NO';
  document.querySelector('#feasibility').className=data.feasibility_score===100?'good':'bad';
  document.querySelector('#service').textContent=pct(data.service_score);
  document.querySelector('#totalCost').textContent=money(data.total_cost);
  document.querySelector('#costScore').textContent=pct(data.cost_score);
  document.querySelector('#ragScore').textContent=pct(data.rag_score);
  document.querySelector('#skillScore').textContent=pct(data.skill_tool_score);
  document.querySelector('#violations').innerHTML=data.violations.length
    ? data.violations.map(v=>'<div class="'+(v.critical?'bad':'')+'">'+escapeHtml(v.code)+': '+escapeHtml(v.message)+'</div>').join('')
    : '<span class="good">No violations</span>';
  document.querySelector('#costBreakdown').innerHTML='<div>Benchmark: <b>'+money(data.benchmark_cost)+'</b></div><div>Gap: <b>'+((data.cost_gap||0)*100).toFixed(2)+'%</b></div>';
  document.querySelector('#trace').innerHTML=data.trace.map((t,i)=>'<tr><td>'+(i+1)+'</td><td><b>'+escapeHtml(t.tool)+'</b></td><td><pre>'+escapeHtml(JSON.stringify(t.inputs,null,2))+'</pre></td><td><pre>'+escapeHtml(JSON.stringify(t.output,null,2))+'</pre></td></tr>').join('');
  document.querySelector('#plan').textContent=JSON.stringify(data.plan,null,2);
  renderEvaluationBreakdown(data);
}

referenceBtn.addEventListener('click',async()=>{
  statusText.textContent='Evaluating published reference through simulator/cost engine...';
  referenceBtn.disabled=true;agentBtn.disabled=true;
  try{
    const data=await getJson('/demo/api/reference/'+scenarioEl.value);
    renderReference(data);
    statusText.textContent='Reference evaluation complete.';
  }catch(e){statusText.textContent='Error: '+e.message}
  finally{referenceBtn.disabled=false;agentBtn.disabled=false}
});

agentBtn.addEventListener('click',async()=>{
  statusText.textContent='Running '+managerModelEl.options[managerModelEl.selectedIndex].text+' + RAG + Skills + PyTorch + tools...';
  referenceBtn.disabled=true;agentBtn.disabled=true;
  try{
    const selected=managerModelEl.value;
    const data=await getJson('/demo/api/run/'+scenarioEl.value+'?model_id='+encodeURIComponent(selected),{method:'POST'});
    renderAgent(data);
    statusText.textContent='Full AI evaluation complete with '+data.manager_model+'.';
  }catch(e){statusText.textContent='Error: '+e.message}
  finally{referenceBtn.disabled=false;agentBtn.disabled=false}
});

init().catch(e=>statusText.textContent='Startup error: '+e.message);


helpOpen.addEventListener('click',()=>{
  helpDialog.showModal();
});

helpClose.addEventListener('click',()=>{
  helpDialog.close();
});

helpDialog.addEventListener('click',(event)=>{
  if(event.target===helpDialog) helpDialog.close();
});
