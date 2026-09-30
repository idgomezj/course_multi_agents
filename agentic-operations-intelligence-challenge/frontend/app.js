const team = document.querySelector('#team');
const scenario = document.querySelector('#scenario');
const managerModel = document.querySelector('#managerModel');
const run = document.querySelector('#run');
const statusEl = document.querySelector('#status');
const runtimeStatus = document.querySelector('#runtimeStatus');
const helpDialog = document.querySelector('#helpDialog');
const helpOpen = document.querySelector('#helpOpen');
const helpClose = document.querySelector('#helpClose');

let scenarioItems = [];

async function json(url, options) {
  const r = await fetch(url, options);
  const data = await r.json();
  if (!r.ok) throw new Error(data.detail || JSON.stringify(data));
  return data;
}

function pct(v) {
  return v == null ? '—' : Number(v).toFixed(1) + '%';
}

function money(v) {
  return v == null
    ? '—'
    : new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD' }).format(v);
}

function escapeHtml(s) {
  return String(s).replace(/[&<>'"]/g, function(c) {
    return {'&':'&amp;','<':'&lt;','>':'&gt;',"'":'&#39;','"':'&quot;'}[c];
  });
}

function currentScenario() {
  return scenarioItems.find(function(x) { return x.id === scenario.value; }) || null;
}

function resetEvaluation() {
  ['#m-operational','#m-feasible','#m-service','#m-total-cost','#m-cost-gap','#m-cost','#m-rag','#m-skills']
    .forEach(function(selector) {
      document.querySelector(selector).textContent = '—';
    });
  document.querySelector('#violations').innerHTML = '—';
  document.querySelector('#cost-breakdown').innerHTML =
    '<span class="subtle">Run an evaluation to see realized cost components.</span>';
  document.querySelector('#evaluation-breakdown').innerHTML =
    'Run an evaluation to see exactly how each available score is calculated.';
  document.querySelector('#trace').innerHTML = '';
  document.querySelector('#plan').textContent = '—';
}

function renderScenarioContext(result) {
  const item = currentScenario();
  if (!item) {
    document.querySelector('#m-objective').textContent = '—';
    document.querySelector('#summary').innerHTML = 'No scenario is available.';
    return;
  }

  const benchmark = result && result.benchmark_cost != null
    ? result.benchmark_cost
    : item.benchmark_cost;

  document.querySelector('#m-objective').textContent =
    benchmark == null ? 'Not disclosed' : money(benchmark);

  let html =
    '<b>' + escapeHtml(item.id) + ' — ' + escapeHtml(item.title) + '</b>' +
    (item.description ? '<br>' + escapeHtml(item.description) : '') +
    '<br><br><b>Objective / benchmark:</b> ' +
    (benchmark == null ? 'Not disclosed for this scenario scope' : money(benchmark));

  const visible = item.visible || {};
  if (Object.keys(visible).length) {
    html += '<br><b>Visible conditions:</b><pre>' +
      escapeHtml(JSON.stringify(visible, null, 2)) + '</pre>';
  }

  if (result) {
    html +=
      '<b>Total realized cost:</b> ' + money(result.total_cost) + '<br>' +
      '<b>Cost gap:</b> ' +
      (result.cost_gap == null ? '—' : (Number(result.cost_gap) * 100).toFixed(2) + '%');
  }

  document.querySelector('#summary').innerHTML = html;
}

async function loadManagerModels() {
  const payload = await json('/api/manager-models');
  managerModel.innerHTML = payload.models.map(function(x) {
    const state = x.configured ? 'ready' : 'API key missing';
    return '<option value="' + escapeHtml(x.id) + '">' +
      escapeHtml(x.label) + ' — ' + escapeHtml(x.model) + ' (' + state + ')</option>';
  }).join('');
  managerModel.value = payload.default_model_id;
}

async function loadTeamStatus() {
  if (!team.value) return;
  runtimeStatus.innerHTML = 'Loading runtime status...';

  const s = await json('/api/status/' + encodeURIComponent(team.value));
  const modelPills = Object.entries(s.models || {}).map(function(entry) {
    const model = entry[1];
    return '<span class="pill">' + escapeHtml(model.artifact) + ': ' +
      (model.ready ? 'READY' : 'NOT TRAINED') + '</span>';
  });

  const providerPills = (s.manager_models || []).map(function(x) {
    return '<span class="pill">' + escapeHtml(x.label) + ': ' +
      (x.configured ? 'READY' : 'KEY MISSING') + '</span>';
  });

  runtimeStatus.innerHTML = [
    '<span class="pill">Data: ' + (s.case_loaded ? 'READY' : 'MISSING') + '</span>',
    '<span class="pill">RAG: ' + (s.rag_ready ? 'READY' : 'MISSING') + '</span>',
    '<span class="pill">Knowledge docs: ' + Number(s.knowledge_documents || 0) + '</span>',
    '<span class="pill">Skills: ' + Number(s.skill_count || 0) + '</span>',
    '<span class="pill">Service target: ' +
      (s.service_level_target == null ? '—' : (Number(s.service_level_target) * 100).toFixed(1) + '%') +
      '</span>'
  ].concat(modelPills, providerPills).join('');

  if (s.objective) {
    runtimeStatus.innerHTML +=
      '<div class="subtle" style="margin-top:8px"><b>Case objective:</b> ' +
      escapeHtml(s.objective) + '</div>';
  }
}

async function loadTeams() {
  const teams = await json('/api/teams');
  team.innerHTML = teams.map(function(x) {
    return '<option value="' + escapeHtml(x.team_id) + '">' +
      escapeHtml(x.team_id) + ': ' + escapeHtml(x.name) + '</option>';
  }).join('');

  if (!teams.length) {
    scenario.innerHTML = '';
    statusEl.textContent = 'No authorized teams.';
    return;
  }

  await refreshTeam();
}

async function loadScenarios() {
  scenarioItems = await json('/api/scenarios/' + encodeURIComponent(team.value));
  scenario.innerHTML = scenarioItems.map(function(x) {
    return '<option value="' + escapeHtml(x.id) + '">' +
      escapeHtml(x.id) + ' — ' + escapeHtml(x.title) + '</option>';
  }).join('');

  resetEvaluation();
  renderScenarioContext();
}

async function refreshTeam() {
  statusEl.textContent = 'Loading team context...';
  await Promise.all([loadScenarios(), loadTeamStatus()]);
  statusEl.textContent = 'Ready.';
}

function renderEvaluationBreakdown(data) {
  const b = data.evaluation_breakdown;
  if (!b) {
    document.querySelector('#evaluation-breakdown').innerHTML =
      '<span class="subtle">Detailed evaluation breakdown is not returned for this scenario scope.</span>';
    return;
  }

  const op = b.operational || {};
  const rag = b.rag || {};
  const st = b.skills_tools || {};
  const components = st.components || {};
  const ops = st.operational_tools || {};
  const discipline = st.discipline || {};
  const efficiency = st.efficiency || {};

  document.querySelector('#evaluation-breakdown').innerHTML =
    '<b>Operational score:</b> ' + pct(op.total_score) +
    ' — 35% feasibility + 25% service + 40% cost' +
    (op.feasible_gate === false
      ? ' <span class="bad">(critical-feasibility gate forced score to 0)</span>'
      : '') +
    '<br><br><b>RAG:</b> ' + pct(rag.total_score) +
    ' — expected sources: ' + escapeHtml(JSON.stringify(rag.expected_sources || [])) +
    '; retrieved expected: ' + escapeHtml(JSON.stringify(rag.retrieved_expected_sources || [])) +
    '<br><br><b>Skills / Tools:</b> ' + pct(st.total_score) +
    '<br>• Skill usage: ' + Number(components.skill_usage || 0).toFixed(1) + ' / 25' +
    '<br>• Expected operational tools: ' +
      Number(components.expected_operational_tools || 0).toFixed(1) + ' / 45' +
    '<br>• Cost + validation discipline: ' +
      Number(components.cost_and_validation || 0).toFixed(1) + ' / 20' +
    '<br>• Efficiency: ' + Number(components.efficiency || 0).toFixed(1) + ' / 10' +
    '<br>• Missing expected operational tools: ' +
      escapeHtml(JSON.stringify(ops.missing || [])) +
    '<br>• calculate_plan_cost: ' +
      (discipline.calculate_plan_cost_called ? 'YES' : 'NO') +
    '; validate_plan: ' +
      (discipline.validate_plan_called ? 'YES' : 'NO') +
    '<br>• Discouraged calls: ' +
      escapeHtml(JSON.stringify(efficiency.discouraged_calls || [])) +
    '; exact duplicate calls: ' + Number(efficiency.exact_duplicate_calls || 0);
}

function renderCostBreakdown(data) {
  const breakdown = data.cost_breakdown || {};
  const entries = Object.entries(breakdown);
  document.querySelector('#cost-breakdown').innerHTML = entries.length
    ? entries.map(function(entry) {
        return '<div><b>' + escapeHtml(entry[0]) + '</b>: ' + money(entry[1]) + '</div>';
      }).join('')
    : '<span class="subtle">Cost component breakdown is not returned for this scenario scope.</span>';
}

function render(data) {
  document.querySelector('#m-operational').textContent = pct(data.operational_score);
  document.querySelector('#m-feasible').textContent = pct(data.feasibility_score);
  document.querySelector('#m-service').textContent = pct(data.service_score);
  document.querySelector('#m-total-cost').textContent = money(data.total_cost);

  const benchmark = data.benchmark_cost != null
    ? data.benchmark_cost
    : (currentScenario() || {}).benchmark_cost;
  document.querySelector('#m-objective').textContent =
    benchmark == null ? 'Not disclosed' : money(benchmark);
  document.querySelector('#m-cost-gap').textContent =
    data.cost_gap == null ? '—' : (Number(data.cost_gap) * 100).toFixed(2) + '%';

  document.querySelector('#m-cost').textContent = pct(data.cost_score);
  document.querySelector('#m-rag').textContent = pct(data.rag_score);
  document.querySelector('#m-skills').textContent = pct(data.skill_tool_score);

  const violations = data.violations || [];
  document.querySelector('#violations').innerHTML = violations.length
    ? violations.map(function(v) {
        return '<div class="' + (v.critical ? 'bad' : '') + '">' +
          escapeHtml(v.code) + ': ' + escapeHtml(v.message) + '</div>';
      }).join('')
    : '<span class="ok">No violations.</span>';

  const trace = data.trace || [];
  document.querySelector('#trace').innerHTML = trace.length
    ? trace.map(function(t, i) {
        return '<tr><td>' + (i + 1) + '</td><td><b>' + escapeHtml(t.tool) +
          '</b></td><td><pre>' + escapeHtml(JSON.stringify(t.inputs, null, 2)) +
          '</pre></td><td><pre>' + escapeHtml(JSON.stringify(t.output, null, 2)) +
          '</pre></td></tr>';
      }).join('')
    : '<tr><td colspan="4" class="subtle">Trace is not returned for this scenario scope.</td></tr>';

  document.querySelector('#plan').textContent = data.plan
    ? JSON.stringify(data.plan, null, 2)
    : 'Plan details are not returned for this scenario scope.';

  renderScenarioContext(data);
  renderCostBreakdown(data);
  renderEvaluationBreakdown(data);
}

team.addEventListener('change', function() {
  refreshTeam().catch(function(e) {
    statusEl.textContent = 'Error: ' + e.message;
  });
});

scenario.addEventListener('change', function() {
  resetEvaluation();
  renderScenarioContext();
});

run.addEventListener('click', async function() {
  run.disabled = true;
  statusEl.textContent =
    'Running ' + managerModel.options[managerModel.selectedIndex].text +
    ' + RAG + Skills + PyTorch + tools + simulator...';

  try {
    const data = await json('/api/evaluate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        team_id: team.value,
        scenario_id: scenario.value,
        model_id: managerModel.value
      })
    });
    render(data);
    statusEl.textContent =
      'Evaluation complete' + (data.manager_model ? ' with ' + data.manager_model : '') + '.';
  } catch (e) {
    statusEl.textContent = 'Error: ' + e.message;
  } finally {
    run.disabled = false;
  }
});

Promise.all([loadManagerModels(), loadTeams()]).catch(function(e) {
  statusEl.textContent = 'Startup error: ' + e.message;
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
