const teamEl = document.querySelector('#team');
const scenarioEl = document.querySelector('#scenario');
const managerModelEl = document.querySelector('#managerModel');
const agentBtn = document.querySelector('#agentBtn');
const statusText = document.querySelector('#statusText');
const runtimeStatus = document.querySelector('#runtimeStatus');
const scenarioSummary = document.querySelector('#scenarioSummary');
const helpDialog = document.querySelector('#helpDialog');
const helpOpen = document.querySelector('#helpOpen');
const helpClose = document.querySelector('#helpClose');

let scenarioItems = [];

async function getJson(url, options) {
  const r = await fetch(url, options);
  const d = await r.json();
  if (!r.ok) throw new Error(d.detail || JSON.stringify(d));
  return d;
}

function money(v) {
  return v == null
    ? '—'
    : new Intl.NumberFormat('en-US', {style:'currency', currency:'USD'}).format(v);
}

function pct(v) {
  return v == null ? '—' : Number(v).toFixed(1) + '%';
}

function escapeHtml(s) {
  return String(s).replace(/[&<>'"]/g, c => ({
    '&':'&amp;',
    '<':'&lt;',
    '>':'&gt;',
    "'":'&#39;',
    '"':'&quot;'
  }[c]));
}

function currentScenario() {
  return scenarioItems.find(x => x.id === scenarioEl.value) || null;
}

function resetRunResult() {
  document.querySelector('#feasibility').textContent = '—';
  document.querySelector('#feasibility').className = '';
  document.querySelector('#service').textContent = '—';
  document.querySelector('#totalCost').textContent = '—';
  document.querySelector('#ragScore').textContent = '—';
  document.querySelector('#skillScore').textContent = '—';
  document.querySelector('#costBreakdown').innerHTML = 'Run an evaluation.';
  document.querySelector('#violations').innerHTML = 'Run an evaluation.';
  document.querySelector('#evaluationBreakdown').innerHTML =
    'Run an AI evaluation to see exactly how each available score is calculated.';
  document.querySelector('#trace').innerHTML = '';
  document.querySelector('#plan').textContent = '—';
}

function renderScenarioSummary() {
  const item = currentScenario();
  if (!item) {
    document.querySelector('#expectedCost').textContent = '—';
    scenarioSummary.textContent = 'No public scenario is available.';
    return;
  }

  document.querySelector('#expectedCost').textContent =
    item.benchmark_cost == null ? '—' : money(item.benchmark_cost);

  let html =
    '<b>' + escapeHtml(item.id) + ' — ' + escapeHtml(item.title) + '</b>';

  if (item.description) {
    html += ' · ' + escapeHtml(item.description);
  }

  if (item.benchmark_cost != null) {
    html += ' · <b>Expected optimized cost:</b> ' + money(item.benchmark_cost);
  }

  const visible = item.visible || {};
  if (Object.keys(visible).length) {
    html += '<br><b>Visible conditions:</b> ' +
      escapeHtml(JSON.stringify(visible));
  }

  scenarioSummary.innerHTML = html;
}

async function loadManagerModels() {
  const payload = await getJson('/api/manager-models');
  managerModelEl.innerHTML = payload.models.map(x => {
    const state = x.configured ? 'ready' : 'API key missing';
    return '<option value="' + escapeHtml(x.id) + '">' +
      escapeHtml(x.label) + ' — ' + escapeHtml(x.model) +
      ' (' + state + ')</option>';
  }).join('');
  managerModelEl.value = payload.default_model_id;
}

async function loadRuntimeStatus() {
  if (!teamEl.value) {
    runtimeStatus.innerHTML = '';
    return;
  }

  const status = await getJson('/api/status/' + encodeURIComponent(teamEl.value));

  const modelPills = Object.values(status.models || {}).map(model => (
    '<span class="pill">' + escapeHtml(model.artifact) + ': ' +
    (model.ready ? 'READY' : 'NOT TRAINED') + '</span>'
  ));

  const providerPills = (status.manager_models || []).map(x => (
    '<span class="pill">' + escapeHtml(x.label) + ': ' +
    (x.configured ? 'READY' : 'KEY MISSING') + '</span>'
  ));

  runtimeStatus.innerHTML = [
    '<span class="pill">Data: ' + (status.case_loaded ? 'READY' : 'MISSING') + '</span>',
    '<span class="pill">RAG: ' + (status.rag_ready ? 'READY' : 'MISSING') + '</span>',
    '<span class="pill">Knowledge: ' + Number(status.knowledge_documents || 0) + '</span>',
    '<span class="pill">Skills: ' + Number(status.skill_count || 0) + '</span>',
    ...modelPills,
    ...providerPills
  ].join('');

  if (status.objective) {
    runtimeStatus.innerHTML +=
      '<div class="subtle" style="margin-top:8px"><b>Case objective:</b> ' +
      escapeHtml(status.objective) + '</div>';
  }
}

async function loadScenarios() {
  scenarioItems = await getJson('/api/scenarios/' + encodeURIComponent(teamEl.value));

  scenarioEl.innerHTML = scenarioItems.map(x => (
    '<option value="' + escapeHtml(x.id) + '">' +
    escapeHtml(x.id) + ' — ' + escapeHtml(x.title) + '</option>'
  )).join('');

  resetRunResult();
  renderScenarioSummary();
}

async function loadTeams() {
  const teams = await getJson('/api/teams');

  teamEl.innerHTML = teams.map(x => (
    '<option value="' + escapeHtml(x.team_id) + '">' +
    escapeHtml(x.team_id) + ': ' + escapeHtml(x.name) + '</option>'
  )).join('');

  if (!teams.length) {
    statusText.textContent = 'No Team 1–5 workspace is available.';
    scenarioEl.innerHTML = '';
    return;
  }

  await refreshTeam();
}

async function refreshTeam() {
  statusText.textContent = 'Loading team context...';
  await Promise.all([
    loadScenarios(),
    loadRuntimeStatus()
  ]);
  statusText.textContent = 'Ready. Compare your run with the Expected Optimized Cost.';
}

function renderEvaluationBreakdown(data) {
  const b = data.evaluation_breakdown;
  if (!b) {
    document.querySelector('#evaluationBreakdown').innerHTML =
      '<span class="subtle">Detailed evaluation breakdown is not returned for this scenario scope.</span>';
    return;
  }

  const op = b.operational || {};
  const rag = b.rag || {};
  const st = b.skills_tools || {};
  const components = st.components || {};
  const tools = st.operational_tools || {};
  const discipline = st.discipline || {};
  const efficiency = st.efficiency || {};

  document.querySelector('#evaluationBreakdown').innerHTML =
    '<b>Operational:</b> ' + pct(op.total_score) +
    ' — 35% feasibility + 25% service + 40% cost' +
    (op.feasible_gate === false
      ? ' <span class="bad">(critical-feasibility gate forced score to 0)</span>'
      : '') +
    '<br><br><b>Cost Score:</b> ' + pct(data.cost_score) +
    (data.cost_gap == null
      ? ''
      : ' · <b>Cost gap:</b> ' + (Number(data.cost_gap) * 100).toFixed(2) + '%') +
    '<br><br><b>RAG:</b> ' + pct(rag.total_score) +
    ' — expected sources: ' + escapeHtml(JSON.stringify(rag.expected_sources || [])) +
    '; retrieved expected: ' + escapeHtml(JSON.stringify(rag.retrieved_expected_sources || [])) +
    '<br><br><b>Skills / Tools:</b> ' + pct(st.total_score) +
    '<br>• Skill usage: ' + Number(components.skill_usage || 0).toFixed(1) + ' / 25' +
    '<br>• Expected operational tools: ' +
      Number(components.expected_operational_tools || 0).toFixed(1) + ' / 45' +
    '<br>• Cost + validation: ' +
      Number(components.cost_and_validation || 0).toFixed(1) + ' / 20' +
    '<br>• Efficiency: ' + Number(components.efficiency || 0).toFixed(1) + ' / 10' +
    '<br>• Missing expected operational tools: ' +
      escapeHtml(JSON.stringify(tools.missing || [])) +
    '<br>• calculate_plan_cost: ' +
      (discipline.calculate_plan_cost_called ? 'YES' : 'NO') +
    '; validate_plan: ' +
      (discipline.validate_plan_called ? 'YES' : 'NO') +
    '<br>• Discouraged calls: ' +
      escapeHtml(JSON.stringify(efficiency.discouraged_calls || [])) +
    '; exact duplicate calls: ' +
      Number(efficiency.exact_duplicate_calls || 0);
}

function renderCostBreakdown(data) {
  const benchmark = data.benchmark_cost != null
    ? data.benchmark_cost
    : (currentScenario() || {}).benchmark_cost;

  const summary = [
    ['Realized total cost', money(data.total_cost)],
    ['Expected optimized cost', money(benchmark)],
    ['Cost gap', data.cost_gap == null ? '—' : (Number(data.cost_gap) * 100).toFixed(2) + '%'],
    ['Cost score', pct(data.cost_score)],
    ['Operational score', pct(data.operational_score)]
  ];

  const detail = Object.entries(data.cost_breakdown || {});

  document.querySelector('#costBreakdown').innerHTML =
    summary.map(([label, value]) => (
      '<div class="cost-row"><span>' + escapeHtml(label) + '</span><span>' +
      escapeHtml(value) + '</span></div>'
    )).join('') +
    (detail.length
      ? '<div style="height:10px"></div>' +
        detail.map(([key, value]) => (
          '<div class="cost-row"><span>' + escapeHtml(key) + '</span><span>' +
          money(value) + '</span></div>'
        )).join('')
      : '<div class="subtle" style="margin-top:10px">Detailed cost components were not returned.</div>');
}

function renderAgent(data) {
  const feasible = Number(data.feasibility_score) === 100;
  document.querySelector('#feasibility').textContent = feasible ? 'YES' : 'NO';
  document.querySelector('#feasibility').className = feasible ? 'good' : 'bad';
  document.querySelector('#service').textContent = pct(data.service_score);
  document.querySelector('#totalCost').textContent = money(data.total_cost);
  document.querySelector('#ragScore').textContent = pct(data.rag_score);
  document.querySelector('#skillScore').textContent = pct(data.skill_tool_score);

  const benchmark = data.benchmark_cost != null
    ? data.benchmark_cost
    : (currentScenario() || {}).benchmark_cost;
  document.querySelector('#expectedCost').textContent = money(benchmark);

  const violations = data.violations || [];
  document.querySelector('#violations').innerHTML = violations.length
    ? violations.map(v => (
        '<div class="' + (v.critical ? 'bad' : '') + '">' +
        escapeHtml(v.code) + ': ' + escapeHtml(v.message) + '</div>'
      )).join('')
    : '<span class="good">No violations</span>';

  const trace = data.trace || [];
  document.querySelector('#trace').innerHTML = trace.length
    ? trace.map((t, i) => (
        '<tr><td>' + (i + 1) + '</td><td><b>' + escapeHtml(t.tool) +
        '</b></td><td><pre>' + escapeHtml(JSON.stringify(t.inputs, null, 2)) +
        '</pre></td><td><pre>' + escapeHtml(JSON.stringify(t.output, null, 2)) +
        '</pre></td></tr>'
      )).join('')
    : '<tr><td colspan="4" class="subtle">No trace was returned.</td></tr>';

  document.querySelector('#plan').textContent =
    data.plan ? JSON.stringify(data.plan, null, 2) : 'Plan details were not returned.';

  renderCostBreakdown(data);
  renderEvaluationBreakdown(data);
}

teamEl.addEventListener('change', () => {
  refreshTeam().catch(e => {
    statusText.textContent = 'Error: ' + e.message;
  });
});

scenarioEl.addEventListener('change', () => {
  resetRunResult();
  renderScenarioSummary();
  statusText.textContent = 'Ready. Compare your run with the Expected Optimized Cost.';
});

agentBtn.addEventListener('click', async () => {
  if (!teamEl.value || !scenarioEl.value) return;

  statusText.textContent =
    'Running ' + managerModelEl.options[managerModelEl.selectedIndex].text +
    ' + RAG + Skills + PyTorch + tools...';
  agentBtn.disabled = true;

  try {
    const data = await getJson('/api/evaluate', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        team_id: teamEl.value,
        scenario_id: scenarioEl.value,
        model_id: managerModelEl.value
      })
    });

    renderAgent(data);
    statusText.textContent =
      'Full AI evaluation complete' +
      (data.manager_model ? ' with ' + data.manager_model : '') + '.';
  } catch (e) {
    const msg = String(e.message || e);
    if (msg.includes('403') || msg.toLowerCase().includes('token')) {
      statusText.textContent =
        'Evaluation token error: verify DATA_API_TOKEN for your assigned team. ' + msg;
    } else {
      statusText.textContent = 'Error: ' + msg;
    }
  } finally {
    agentBtn.disabled = false;
  }
});

Promise.all([
  loadManagerModels(),
  loadTeams()
]).catch(e => {
  statusText.textContent = 'Startup error: ' + e.message;
});

helpOpen.addEventListener('click', () => {
  helpDialog.showModal();
});

helpClose.addEventListener('click', () => {
  helpDialog.close();
});

helpDialog.addEventListener('click', event => {
  if (event.target === helpDialog) helpDialog.close();
});
