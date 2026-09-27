const team = document.querySelector('#team');
const scenario = document.querySelector('#scenario');
const run = document.querySelector('#run');
const statusEl = document.querySelector('#status');
const helpDialog = document.querySelector('#helpDialog');
const helpOpen = document.querySelector('#helpOpen');
const helpClose = document.querySelector('#helpClose');

async function json(url, options) {
  const r = await fetch(url, options);
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}

async function loadTeams() {
  const teams = await json('/api/teams');
  team.innerHTML = teams.map(function(x) {
    return '<option value="' + x.team_id + '">' + x.team_id + ': ' + x.name + '</option>';
  }).join('');
  await loadScenarios();
}

async function loadScenarios() {
  const items = await json('/api/scenarios/' + team.value);
  scenario.innerHTML = items.map(function(x) {
    return '<option value="' + x.id + '">' + x.id + ' — ' + x.title + '</option>';
  }).join('');
}

function pct(v) { return v == null ? '—' : Number(v).toFixed(1) + '%'; }
function money(v) {
  return v == null ? '—' : new Intl.NumberFormat('en-US',{style:'currency',currency:'USD'}).format(v);
}
function escapeHtml(s) {
  return s.replace(/[&<>'"]/g, function(c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c];
  });
}

function render(data) {
  document.querySelector('#m-operational').textContent = pct(data.operational_score);
  document.querySelector('#m-feasible').textContent = pct(data.feasibility_score);
  document.querySelector('#m-service').textContent = pct(data.service_score);
  document.querySelector('#m-cost').textContent = pct(data.cost_score);
  document.querySelector('#m-rag').textContent = pct(data.rag_score);
  document.querySelector('#m-skills').textContent = pct(data.skill_tool_score);
  document.querySelector('#summary').innerHTML =
    '<b>Total realized cost:</b> ' + money(data.total_cost) + '<br>' +
    '<b>Benchmark:</b> ' + money(data.benchmark_cost) + '<br>' +
    '<b>Cost gap:</b> ' + (data.cost_gap == null ? '—' : (data.cost_gap * 100).toFixed(2) + '%');
  document.querySelector('#violations').innerHTML = data.violations.length
    ? data.violations.map(function(v) {
        return '<div class="' + (v.critical ? 'bad' : '') + '">' + v.code + ': ' + v.message + '</div>';
      }).join('')
    : '<span class="ok">No violations.</span>';
  document.querySelector('#trace').innerHTML = data.trace.map(function(t,i) {
    return '<tr><td>' + (i+1) + '</td><td><b>' + t.tool + '</b></td><td><pre>' +
      escapeHtml(JSON.stringify(t.inputs,null,2)) + '</pre></td><td><pre>' +
      escapeHtml(JSON.stringify(t.output,null,2)) + '</pre></td></tr>';
  }).join('');
  document.querySelector('#plan').textContent = JSON.stringify(data.plan, null, 2);
}

team.addEventListener('change', loadScenarios);
run.addEventListener('click', async function() {
  run.disabled = true;
  statusEl.textContent = 'Running Manager + tools + simulator...';
  try {
    const data = await json('/api/evaluate', {
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({team_id:team.value, scenario_id:scenario.value})
    });
    render(data);
    statusEl.textContent = 'Evaluation complete.';
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
  } finally {
    run.disabled = false;
  }
});

helpOpen.addEventListener('click', function() {
  helpDialog.showModal();
});

helpClose.addEventListener('click', function() {
  helpDialog.close();
});

helpDialog.addEventListener('click', function(event) {
  if (event.target === helpDialog) helpDialog.close();
});

loadTeams().catch(function(e) { statusEl.textContent = e.message; });
