const scenarioEl=document.querySelector('#scenario');
const referenceBtn=document.querySelector('#referenceBtn');
const agentBtn=document.querySelector('#agentBtn');
const statusText=document.querySelector('#statusText');

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
  const [status,scenarios]=await Promise.all([
    getJson('/demo/api/status'),
    getJson('/demo/api/scenarios')
  ]);
  scenarioEl.innerHTML=scenarios.map(x=>'<option value="'+x.id+'">'+x.id+' — '+x.title+'</option>').join('');
  document.querySelector('#runtimeStatus').innerHTML=[
    '<span class="pill">Data: '+(status.case_loaded?'READY':'MISSING')+'</span>',
    '<span class="pill">RAG: '+(status.rag_ready?'READY':'MISSING')+'</span>',
    '<span class="pill">Skills: '+status.skill_count+'</span>',
    '<span class="pill">'+status.models.model_a.artifact+': '+(status.models.model_a.ready?'READY':'NOT TRAINED')+'</span>',
    '<span class="pill">'+status.models.model_b.artifact+': '+(status.models.model_b.ready?'READY':'NOT TRAINED')+'</span>',
    '<span class="pill">LLM key: '+(status.llm_key_present?'READY':'MISSING')+'</span>'
  ].join('');
  statusText.textContent='Ready. Use Reference first, then AI Manager.';
}

function resetTrace(){document.querySelector('#trace').innerHTML='';}
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
  statusText.textContent='Running LLM Manager + RAG + Skills + PyTorch + tools...';
  referenceBtn.disabled=true;agentBtn.disabled=true;
  try{
    const data=await getJson('/demo/api/run/'+scenarioEl.value,{method:'POST'});
    renderAgent(data);
    statusText.textContent='Full AI evaluation complete.';
  }catch(e){statusText.textContent='Error: '+e.message}
  finally{referenceBtn.disabled=false;agentBtn.disabled=false}
});

init().catch(e=>statusText.textContent='Startup error: '+e.message);
