"""Add a measurement-derived, interactive 1000-RPS cost projection to the original
informe_benchmark_real.html. Uses original benchmark JSON; does not run models.

No dependencies beyond Python's standard library. Report carries the raw measured
CPU / RAM / throughput and separates assumed EC2 pricing from host measurement.
"""
from __future__ import annotations

import argparse
from html import escape
import json
import math
from pathlib import Path
import re

BASE = Path(__file__).resolve().parent
MODEL_NAMES = {"rules": "Rules", "ml": "Supervised ML", "pretrained": "Pretrained NLP"}
RATES = {"m7i.large": (2, 8.0), "c7i.xlarge": (4, 8.0), "g5.xlarge": (4, 16.0)}


def project(source: dict, *, target_rps: float = 1000, hours_day: float = 8,
            days: int = 30, capacity_fraction: float = .7) -> dict:
    """Scale measured *host* CPU-time/inference + throughput into hypothetical EC2.

    Use the more conservative replica count from sequential RPS or process CPU
    seconds per request. The latter is noisy for very short microbenchmarks, so
    include both counts in data and clearly state the limitation.
    """
    if not (target_rps > 0 and 0 < hours_day <= 24 and 1 <= days <= 31 and
            0 < capacity_fraction <= 1):
        raise ValueError("target_rps>0, 0<hours_day<=24, 1<=days<=31, 0<capacity_fraction<=1 required")
    cfg = source["config"]
    hours = hours_day * days
    messages = round(target_rps * 3600 * hours)
    items = []
    for record in source["results"]:
        key = record["id"]
        measured = record.get("status") == "MEASURED"
        instance = record.get("instance") or ("c7i.xlarge" if key == "pretrained" else "m7i.large")
        vcpu, memory_gib = RATES[instance]
        hourly = float(cfg["price_" + instance.replace(".", "_")])
        startup = record.get("startup") or {}
        inf = record.get("inference") or {}
        load = record.get("load_test") or {}
        cpu = record.get("load_resources") or {}
        avg_out_bytes = float(inf.get("avg_response_body_bytes") or 0)
        avg_in_bytes = float((record.get("inputs") or {}).get("avg_request_body_bytes") or 0)
        peak_rss_mib = max(float(x.get("peak_process_rss_mib") or 0)
                           for x in (startup, inf, cpu))
        observed_rps = float(inf.get("sequential_rps") or 0)
        n_sequential = float(inf.get("requests") or 0)
        inference_cpu_seconds = float(inf.get("cpu_time_s") or 0)
        cpu_sec_per_request = inference_cpu_seconds / n_sequential if n_sequential and inference_cpu_seconds > 0 else None
        # A few hundred very fast calls may be shorter than CPU timer resolution;
        # in such cases a reliable CPU-only lower bound is not available.
        rps_replicas = max(1, math.ceil(target_rps / (observed_rps * capacity_fraction))) if measured and observed_rps > 0 else None
        cpu_replicas = max(1, math.ceil(target_rps * cpu_sec_per_request / (vcpu * capacity_fraction))) if measured and cpu_sec_per_request else None
        count = max(rps_replicas, cpu_replicas or 1) if rps_replicas else None
        memory_pass = peak_rss_mib < memory_gib * 1024 * .8
        if count is not None and not memory_pass:
            count = None
        storage_gb = float(cfg["ebs_gb_pretrained"] if key == "pretrained" else cfg["ebs_gb"])
        egress_gb = messages * avg_out_bytes / 1e9
        ingress_gb = messages * avg_in_bytes / 1e9
        # Account-level free allowance is SHARED; per-model stand-alone scenario
        # assumption, never charge a full allowance separately if deployed together.
        egress_fee = (max(0, egress_gb - float(cfg["free_egress_gb"])) *
                      float(cfg["egress_price_per_gb"]))
        compute = count * hours * hourly if count is not None else None
        storage = count * storage_gb * float(cfg["ebs_price_gb_month"]) if count is not None else None
        active_total = compute + storage + egress_fee if compute is not None else None
        always_total = count * float(cfg["month_hours"]) * hourly + storage + egress_fee if count is not None else None
        tokens = (record.get("inputs") or {}).get("tokens_per_message_avg")
        tokens_total = messages * tokens if tokens is not None else None
        items.append({
            "id": key, "name": MODEL_NAMES[key], "status": record.get("status"),
            "instance": instance, "vcpu_per_instance": vcpu, "memory_gib_per_instance": memory_gib,
            "instance_hourly_usd": hourly, "replicas_throughput_only": rps_replicas,
            "replicas_cpu_bound": cpu_replicas, "replicas_recommended_proxy": count,
            "host_sequential_rps": observed_rps, "observed_host_cores": source.get("hardware", {}).get("cpu_logical"),
            "load_test_target_rps": load.get("target_rps"), "load_test_completed": load.get("completed"),
            "load_test_rejected": load.get("rejected"), "measured_p95_ms": inf.get("p95_ms"),
            "measured_p99_ms": inf.get("p99_ms"), "measured_peak_process_ram_mib": round(peak_rss_mib, 2),
            "cpu_time_s_per_request": cpu_sec_per_request,
            "observed_load_cpu_pct_one_core": cpu.get("process_cpu_pct_of_one_core"),
            "memory_fit_under_80pct": memory_pass,
            "total_vcpu_provisioned": count * vcpu if count is not None else None,
            "total_ram_gib_provisioned": count * memory_gib if count is not None else None,
            "compute_active_usd": compute, "storage_month_usd": storage,
            "internet_egress_gb_payload_only": egress_gb, "internet_ingress_gb_payload_only": ingress_gb,
            "internet_egress_usd": egress_fee, "total_active_usd": active_total,
            "total_always_on_usd": always_total,
            "cost_per_million_requests_usd": active_total/(messages/1e6) if active_total is not None else None,
            "tokens_per_request": tokens, "model_input_tokens_month": tokens_total,
            "infra_per_million_nli_tokens_usd": active_total/(tokens_total/1e6) if active_total is not None and tokens_total else None,
            "provider_token_api_cost_usd": 0,
        })
    return {
        "based_on_benchmark_utc": source.get("generated_utc"),
        "measurement_host": source.get("hardware", {}),
        "ec2_measurements": False,
        "scenario": {"rps": target_rps, "hours_day": hours_day, "days": days, "hours_month": hours,
                     "monthly_requests": messages, "capacity_fraction": capacity_fraction,
                     "always_on_hours": cfg["month_hours"]},
        "pricing": {"region": "us-east-1", "reference_date": source.get("price_snapshot_utc_date"),
                    "egress_price_per_gb": cfg["egress_price_per_gb"],
                    "free_egress_gb": cfg["free_egress_gb"],
                    "ebs_price_gb_month": cfg["ebs_price_gb_month"],
                    "storage_gb": cfg["ebs_gb"], "storage_gb_pretrained": cfg["ebs_gb_pretrained"]},
        "models": items,
        "limits": ["Extrapolated from GitHub Actions non-EC2 CPU host, not EC2 measurements",
                   "CPU accounting from 200/12 sequential inferences is noisy",
                   "One model process per EC2 assumption; no HTTP/TLS/LB, autoscaling, HA, NAT or logs",
                   "Host network RX/TX includes unrelated processes; service payload estimates only",
                   "Egress free tier is account-level and shared across any deployed models",
                   "240 active hours/month requires stopping compute outside work hours; EBS billed full month"],
    }


def _money(n):
    return "—" if n is None else "$" + f"{n:,.2f}"


def enhance_html(base_html: str, source: dict, *, target_rps: float = 1000,
                 hours_day: float = 8, days: int = 30,
                 capacity_fraction: float = .7) -> tuple[str, dict]:
    """Replace old scenarios INSIDE the original benchmark report, preserve its graphs."""
    result = project(source, target_rps=target_rps, hours_day=hours_day, days=days,
                     capacity_fraction=capacity_fraction)
    sc = result["scenario"]
    data = result["models"]
    colors = {"rules": "#3ad6c2", "ml": "#7298fa", "pretrained": "#f0b463"}
    cards = []
    for m in data:
        cards.append(f'''<article class="metric" style="--accent:{colors[m['id']]}">
          <div class="status ok">{escape(m['name'])} · calculated from measured execution</div>
          <div class="big" id="projection-total-{m['id']}">{_money(m['total_active_usd'])}</div>
          <div class="small">USD / month · EC2 + monthly EBS + estimated internet egress</div>
          <div class="info"><span>EC2 instances (proxy)</span><strong id="projection-count-{m['id']}">{m['replicas_recommended_proxy'] or '—'} × {m['instance']}</strong></div>
          <div class="info"><span>Observed host throughput</span><strong>{m['host_sequential_rps']:,.1f} req/s</strong></div>
          <div class="info"><span>Measured process RAM peak</span><strong>{m['measured_peak_process_ram_mib']:,.1f} MiB</strong></div>
          <div class="info"><span>Measured CPU during 100/s load</span><strong>{m['observed_load_cpu_pct_one_core']:.1f}% of 1 core</strong></div>
          <div class="info"><span>Compute only (240 h)</span><strong id="projection-compute-{m['id']}">{_money(m['compute_active_usd'])}</strong></div>
          <div class="info"><span>Storage for full month</span><strong id="projection-storage-{m['id']}">{_money(m['storage_month_usd'])}</strong></div>
        </article>''')
    rows = []
    for m in data:
        rows.append(f'''<tr><td>{m['name']}</td><td>{m['instance']}</td>
          <td class="num" id="projection-n-{m['id']}">{m['replicas_recommended_proxy'] or '—'}</td>
          <td class="num" id="projection-vcpu-{m['id']}">{m['total_vcpu_provisioned'] or '—'}</td>
          <td class="num" id="projection-ram-{m['id']}">{m['total_ram_gib_provisioned'] or '—'}</td>
          <td class="num" id="projection-compute-row-{m['id']}">{_money(m['compute_active_usd'])}</td>
          <td class="num" id="projection-ebs-{m['id']}">{_money(m['storage_month_usd'])}</td>
          <td class="num" id="projection-egress-{m['id']}">{_money(m['internet_egress_usd'])}</td>
          <td class="num" id="projection-total-row-{m['id']}">{_money(m['total_active_usd'])}</td>
          <td class="num" id="projection-always-{m['id']}">{_money(m['total_always_on_usd'])}</td>
          <td class="num" id="projection-million-{m['id']}">{_money(m['cost_per_million_requests_usd'])}</td></tr>''')
    resource_rows = []
    for m in data:
        resource_rows.append(f'''<tr><td>{m['name']}</td><td class="num">{m['host_sequential_rps']:,.1f}</td>
          <td class="num">{m['measured_p95_ms']:.3f}</td><td class="num">{m['measured_peak_process_ram_mib']:.1f}</td>
          <td class="num">{m['observed_load_cpu_pct_one_core']:.1f}%</td>
          <td class="num" id="proj-throughput-only-{m['id']}">{m['replicas_throughput_only'] or '—'}</td>
          <td class="num" id="proj-cpu-only-{m['id']}">{m['replicas_cpu_bound'] if m['replicas_cpu_bound'] is not None else 'Not reliable'}</td>
          <td class="num">{m['internet_ingress_gb_payload_only']:.2f} GB</td>
          <td class="num">{m['internet_egress_gb_payload_only']:.2f} GB</td></tr>''')
    tokenrow = data[2]
    # No source metrics are overwritten; only the old cost section is replaced.
    panel = f'''<h2>Demand and monthly infrastructure estimate</h2>
      <div class="critical" style="margin-bottom:16px"><strong>PRIMARY WORKLOAD: 1,000 requests/second × 8 hours/day × 30 days.</strong>
       These are projections using the measured GitHub Actions CPU, RAM and throughput figures below. The original load test offered <b>{source['config']['target_rps']:g} req/s for {source['config']['duration_s']:g} seconds</b>, not 1,000 req/s on EC2.</div>
      <section class="panel" style="margin-bottom:16px"><div class="capacity-inputs">
       <label>Requested RPS <input id="proj-rps" type="number" min="1" value="{target_rps:g}"></label>
       <label>Hours/day <input id="proj-hours" type="number" min="0.5" max="24" step="0.5" value="{hours_day:g}"></label>
       <label>Days/month <input id="proj-days" type="number" min="1" max="31" value="{days}"></label>
       <label>Capacity reserve <select id="proj-util"><option value="0.5">50% utilization</option><option value="0.7" selected>70% utilization</option><option value="0.8">80% utilization</option></select></label>
       </div><div class="number" id="projection-monthly-volume">{sc['monthly_requests']:,} requests/month</div>
       <p class="small">Change the inputs to recalculate all three monthly projections. The measured benchmark results do not change.</p></section>
      <div class="metrics">{''.join(cards)}</div>
      <h3 style="margin-top:26px">Full AWS infrastructure cost and provisioned resources</h3>
      <div class="panel scroll"><table><thead><tr><th>Model</th><th>EC2 type</th><th class="num">EC2 count</th><th class="num">vCPU total</th><th class="num">RAM GiB total</th><th class="num">Compute (active)</th><th class="num">EBS (monthly)</th><th class="num">Internet egress</th><th class="num">Total (active)</th><th class="num">730h always-on</th><th class="num">USD / 1M req</th></tr></thead>
       <tbody>{''.join(rows)}</tbody></table></div>
      <h3 style="margin-top:26px">Exact measurement basis and network payload estimates</h3>
      <div class="panel scroll"><table><thead><tr><th>Model</th><th class="num">Measured host req/s</th><th class="num">Measured p95 (ms)</th><th class="num">Peak process RSS (MiB)</th><th class="num">CPU load (% 1 core)</th><th class="num">Count from throughput</th><th class="num">Count from CPU seconds</th><th class="num">Request input/month*</th><th class="num">Response output/month*</th></tr></thead><tbody>{''.join(resource_rows)}</tbody></table></div>
      <p class="small">* Payload-size estimates use observed average input/output JSON body bytes (no HTTP/TLS headers). Measured host RX/TX counters are retained in the original table above and include other processes. Per-model monthly input/output volumes are NOT per-instance traffic.</p>
      <p class="small">Sizing proxy: <code>ceil(target RPS / (sequential host RPS × utilization))</code>, increased if <code>ceil(target RPS × measured CPU seconds/request / (EC2 vCPU × utilization))</code> is greater. The CPU measurement is short and noisy; this added conservative check increases ML from 1 to 2 instances. This still does not validate EC2 throughput, latency under sustained 1,000 RPS, or memory under multi-worker concurrency.</p>
      <div class="critical"><b>Not verified on AWS.</b> Reference prices: us-east-1 On-Demand Linux, {escape(str(result['pricing']['reference_date']))}. Instances are assumptions—not actual EC2 measurements. Stop EC2 outside the 240 active hours to achieve "active" compute costs; storage remains billed throughout the month. Internet egress pricing uses {result['pricing']['free_egress_gb']:g} GB free at the account level and ${result['pricing']['egress_price_per_gb']:.2f}/GB above that. Real-world costs also include HTTP/LB, TLS, public IPv4, NAT, logging, autoscaling, redundancy, support and taxes. Values use the *recorded* hourly price snapshot, not live billing.</div>
      '''
    tokens_panel = f'''<h2>Model tokens and cost attribution</h2><div class="panel">
      <p>The self-hosted scripts have <b>US$0 paid API token charges</b>. Their real expense is CPU/RAM, instance uptime, storage and network.</p>
      <div class="stats"><section><span class="small">Measured pretrained NLI input tokens per request</span><div class="number">{tokenrow['tokens_per_request']:,.0f}</div><p class="small">Includes the four candidate-label text pairs.</p></section>
      <section><span class="small">Projected monthly pretrained NLI tokens</span><div class="number" id="proj-monthly-tokens">{tokenrow['model_input_tokens_month']:,.0f}</div><p class="small" id="proj-per-million-tokens">Effective self-hosted infrastructure: {_money(tokenrow['infra_per_million_nli_tokens_usd'])} per 1M NLI input tokens; NOT an API token price.</p></section></div>
      </div>'''
    html = re.sub(r'<h2>Demand and monthly infrastructure estimate</h2>.*?(?=<h2>Model tokens and cost attribution</h2>)',
                  lambda _: panel, base_html, count=1, flags=re.S)
    html = re.sub(r'<h2>Model tokens and cost attribution</h2>.*?(?=<h2>How token costs work here</h2>)',
                  lambda _: tokens_panel, html, count=1, flags=re.S)
    if 'id="projection-monthly-volume"' not in html:
        raise ValueError('Unexpected base HTML: demand section not found')
    html = re.sub(r'<style id="capacity-style">.*?</style>', '', html, flags=re.S)
    html = re.sub(r'<script id="capacity-projection-js">.*?</script>', '', html, flags=re.S)
    css = '''<style id="capacity-style">
      .capacity-inputs{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:15px;margin-bottom:20px}
      .capacity-inputs label{color:#9fcbd0;font-size:12px;display:flex;flex-direction:column;gap:6px}
      .capacity-inputs input,.capacity-inputs select{background:#203b53;border:1px solid #457087;border-radius:9px;padding:11px;color:white;font-size:16px;width:100%}
      code{background:#1e384e;padding:2px 5px;border-radius:4px} .panel .stats{gap:22px}
      @media(max-width:850px){.capacity-inputs{grid-template-columns:repeat(2,1fr)}}
    </style>'''
    html = html.replace('</head>', css + '</head>', 1)
    # Small JSON payload for interactivity; JS recalculates the same Python formulas.
    simple = [{k:m[k] for k in ('id','instance_hourly_usd','vcpu_per_instance','memory_gib_per_instance','host_sequential_rps','cpu_time_s_per_request','memory_fit_under_80pct','tokens_per_request')}
              for m in data]
    jsdata = json.dumps({"models":simple,"price":result['pricing'],"always":sc['always_on_hours']}, separators=(',',':')).replace('</','<\\/')
    javascript = '''<script id="capacity-projection-js">(function(){const d=DATA;
       const by=id=>document.getElementById(id);const fmt=n=>Number(n).toLocaleString('en-US',{maximumFractionDigits:0});
       const usd=n=>n==null?'—':('$'+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2}));
       function go(){const rps=Number(by('proj-rps').value),hours=Number(by('proj-hours').value),days=Number(by('proj-days').value),util=Number(by('proj-util').value);
       if(!(rps>0&&hours>0&&hours<=24&&days>=1&&days<=31&&util>0&&util<=1)){return;}
       const month=rps*hours*days*3600;
       by('projection-monthly-volume').textContent=fmt(month)+' requests/month';
       d.models.forEach(m=>{const id=m.id;const bySpeed=Math.max(1,Math.ceil(rps/(m.host_sequential_rps*util)));
       const byCpu=m.cpu_time_s_per_request?Math.max(1,Math.ceil(rps*m.cpu_time_s_per_request/(m.vcpu_per_instance*util))):null;
       const n=m.memory_fit_under_80pct?Math.max(bySpeed,byCpu||1):null;
       const disk=m.id==='pretrained'?d.price.storage_gb_pretrained:d.price.storage_gb;
       const outbytes=OUTPUTS[id];const eg=Math.max(0,(month*outbytes/1e9)-d.price.free_egress_gb)*d.price.egress_price_per_gb;
       const compute=n==null?null:n*hours*days*m.instance_hourly_usd;
       const storage=n==null?null:n*disk*d.price.ebs_price_gb_month;
       const total=n==null?null:compute+storage+eg;
       const always=n==null?null:n*d.always*m.instance_hourly_usd+storage+eg;
       const million=total==null?null:total/(month/1e6);
       const write=(name,val)=>{const node=by(name+'-'+id);if(node)node.textContent=val;};
       write('projection-total',usd(total));write('projection-count',n==null?'—':(n+' × '+INSTANCES[id]));
       write('projection-compute',usd(compute));write('projection-storage',usd(storage));
       write('projection-n',n==null?'—':fmt(n));write('projection-vcpu',n==null?'—':fmt(n*m.vcpu_per_instance));
       write('projection-ram',n==null?'—':fmt(n*m.memory_gib_per_instance));
       write('projection-compute-row',usd(compute));write('projection-ebs',usd(storage));write('projection-egress',usd(n==null?null:eg));
       write('projection-total-row',usd(total));write('projection-always',usd(always));write('projection-million',usd(million));
       write('proj-throughput-only',fmt(bySpeed));write('proj-cpu-only',byCpu==null?'Not reliable':fmt(byCpu));
       if(id==='pretrained'){const tokens=month*(m.tokens_per_request||0);by('proj-monthly-tokens').textContent=fmt(tokens);
       by('proj-per-million-tokens').textContent='Effective self-hosted infrastructure: '+usd(total==null||!tokens?null:total/(tokens/1e6))+' per 1M NLI input tokens; NOT an API token price.';}
       });}
       ['proj-rps','proj-hours','proj-days','proj-util'].forEach(k=>by(k).addEventListener('input',go));go();
    })();</script>'''
    javascript = javascript.replace('DATA',jsdata).replace('OUTPUTS',json.dumps({m['id']: float(next(x for x in source['results'] if x['id']==m['id'])['inference']['avg_response_body_bytes']) for m in data})).replace('INSTANCES',json.dumps({m['id']:m['instance'] for m in data}))
    html=html.replace('</body>',javascript+'</body>',1)
    # Clarify that the hero describes the benchmark load not the extrapolation.
    html=html.replace(f"<span>{source['config']['target_rps']:g} req/s target</span>",f"<span>{source['config']['target_rps']:g} req/s measured load test</span><span>{target_rps:g} req/s cost projection</span>",1)
    html=html.replace('attempted 100 requests/s','measured 100 requests/s and projected 1,000 requests/s',1)
    return html,result


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--benchmark-json',type=Path,default=BASE/'datos'/'benchmark_three_models_20261120.json')
    p.add_argument('--base-html',type=Path,default=BASE/'informe_benchmark_real.html')
    p.add_argument('--out',type=Path,default=BASE/'informe_benchmark_real.html')
    p.add_argument('--projection-json',type=Path,default=BASE/'datos'/'proyeccion_benchmark_1000_rps.json')
    p.add_argument('--target-rps',type=float,default=1000)
    p.add_argument('--hours-day',type=float,default=8)
    p.add_argument('--days',type=int,default=30)
    p.add_argument('--capacity-fraction',type=float,default=.7)
    a=p.parse_args(argv)
    source=json.loads(a.benchmark_json.read_text(encoding='utf-8'))
    if not a.base_html.exists():
        raise SystemExit(f'Original HTML not found: {a.base_html}. Run benchmark_nlp_aws.py first, or provide --base-html.')
    html,projection=enhance_html(a.base_html.read_text(encoding='utf-8'),source,
        target_rps=a.target_rps,hours_day=a.hours_day,days=a.days,capacity_fraction=a.capacity_fraction)
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.projection_json.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(html,encoding='utf-8')
    a.projection_json.write_text(json.dumps(projection,indent=2,ensure_ascii=False),encoding='utf-8')
    print('Updated ORIGINAL HTML:',a.out.resolve())
    print('Projection JSON:',a.projection_json.resolve())
    for m in projection['models']:
        print(f" {m['name']}: {m['replicas_recommended_proxy']} x {m['instance']}; {_money(m['total_active_usd'])}/month")
    return 0


if __name__=='__main__':
    raise SystemExit(main())
