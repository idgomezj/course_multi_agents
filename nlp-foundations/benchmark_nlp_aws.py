#!/usr/bin/env python3
"""Measured NLP inference benchmark + capacity *scenarios* for EC2.

Measures all three models unless --skip-pretrained. No benchmarks are fabricated.
No EC2 results are claimed unless actually executed on EC2 and --ec2-verified.
Cloud prices are an explicit dated snapshot, not live billing rates.
"""
from __future__ import annotations

import argparse
from concurrent.futures import ThreadPoolExecutor
import csv
from datetime import datetime, timezone
from html import escape
import importlib.util
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
import platform
import statistics
import sys
import threading
import time
from typing import Any

BASE = Path(__file__).resolve().parent
TIMESTAMP = "2026-11-20"
EC2 = {
    "m7i.large": {"rate": 0.1008, "vcpus": 2, "memory_gib": 8},
    "c7i.xlarge": {"rate": 0.1785, "vcpus": 4, "memory_gib": 8},
    "g5.xlarge": {"rate": 1.006, "vcpus": 4, "memory_gib": 16},
}
CANDIDATES = {
    "rules": "m7i.large", "ml": "m7i.large", "pretrained_cpu": "c7i.xlarge",
    "pretrained_cuda": "g5.xlarge",
}
LABEL_MAP = {
    "problemas de facturación y cobros": "FACTURACION",
    "problemas de envíos o entregas": "ENVIOS",
    "problemas para acceder a la cuenta": "ACCESO",
    "problemas técnicos de una aplicación": "SOPORTE_TECNICO",
}
SOURCE_LINKS = [
    ("Amazon EC2 On-Demand", "https://aws.amazon.com/ec2/pricing/on-demand/"),
    ("EBS gp3 pricing", "https://aws.amazon.com/ebs/pricing/"),
    ("EC2 instance price reference", "https://instances.usage.ai/aws/ec2/region/us-east-1"),
    ("Pretrained model", "https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli"),
]


def load_script(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, BASE / filename)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {filename}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def percentile(values: list[float], q: float) -> float | None:
    if not values:
        return None
    sorted_values = sorted(values)
    pos = (len(sorted_values) - 1) * q
    i = int(pos)
    return sorted_values[i] * (1 - (pos - i)) + sorted_values[min(i + 1, len(sorted_values) - 1)] * (pos - i)


def get_data() -> list[str]:
    with (BASE / "datos" / "mensajes.csv").open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    messages = [str(row.get("mensaje", "")).strip() for row in rows]
    if not messages or any(not x for x in messages):
        raise ValueError("Missing/empty mensajes.csv")
    return messages


try:
    import psutil
except ImportError:
    psutil = None


class ProcessMeter:
    """Peak RSS sampler; CPU from process time. Network from *host* counters only.

    Host network counters can contain OTHER programs' traffic and are not model
    bytes. Include this in metadata rather than misleading attribution.
    """
    def __init__(self, interval: float = .025):
        self.interval = interval
        self.process = psutil.Process(os.getpid()) if psutil else None
        self.stop_event = threading.Event()
        self.thread = None
        self.peak_rss = None
        self.start_cpu = None
        self.start_time = None
        self.net_start = None
        self.io_start = None
        self.gpu_start = None

    def _cpu_time(self):
        t = self.process.cpu_times()
        return t.user + t.system

    def _gpu(self):
        try:
            torch = sys.modules.get("torch")
            if torch is not None and torch.cuda.is_available():
                return int(torch.cuda.memory_allocated())
        except Exception:
            pass
        return None

    def _sample(self):
        while not self.stop_event.is_set():
            try:
                value = self.process.memory_info().rss
                self.peak_rss = value if self.peak_rss is None else max(self.peak_rss, value)
            except (psutil.Error, AttributeError):
                break
            self.stop_event.wait(self.interval)

    def __enter__(self):
        self.start_time = time.perf_counter()
        if self.process:
            self.start_cpu = self._cpu_time()
            self.peak_rss = self.process.memory_info().rss
            self.io_start = self.process.io_counters() if hasattr(self.process, "io_counters") else None
            self.net_start = psutil.net_io_counters()
            self.gpu_start = self._gpu()
            self.thread = threading.Thread(target=self._sample, daemon=True)
            self.thread.start()
        return self

    def __exit__(self, *_):
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=1)
        elapsed = time.perf_counter() - self.start_time
        self.wall_s = elapsed
        if not self.process:
            self.cpu_core_pct = self.cpu_s = self.peak_mib = self.net_recv_bytes = self.net_sent_bytes = self.disk_written_bytes = None
            self.gpu_peak_mib = None
            return
        self.peak_rss = max(self.peak_rss, self.process.memory_info().rss)
        self.peak_mib = round(self.peak_rss / 1048576, 2)
        self.cpu_s = round(max(0, self._cpu_time() - self.start_cpu), 4)
        self.cpu_core_pct = round(100 * self.cpu_s / elapsed, 2) if elapsed else None
        try:
            end = psutil.net_io_counters()
            self.net_recv_bytes = max(0, end.bytes_recv - self.net_start.bytes_recv)
            self.net_sent_bytes = max(0, end.bytes_sent - self.net_start.bytes_sent)
        except Exception:
            self.net_recv_bytes = self.net_sent_bytes = None
        try:
            endio = self.process.io_counters()
            self.disk_written_bytes = max(0, endio.write_bytes - self.io_start.write_bytes) if self.io_start else None
        except Exception:
            self.disk_written_bytes = None
        try:
            torch = sys.modules.get("torch")
            self.gpu_peak_mib = round(torch.cuda.max_memory_allocated() / 1048576, 2) if torch is not None and torch.cuda.is_available() else None
        except Exception:
            self.gpu_peak_mib = None

    def data(self):
        return {
            "wall_s": round(self.wall_s, 4), "cpu_time_s": self.cpu_s,
            "process_cpu_pct_of_one_core": self.cpu_core_pct,
            "peak_process_rss_mib": self.peak_mib,
            "host_network_rx_bytes": self.net_recv_bytes,
            "host_network_tx_bytes": self.net_sent_bytes,
            "process_disk_written_bytes": self.disk_written_bytes,
            "gpu_peak_allocated_mib": self.gpu_peak_mib,
        }


def prepare_model(key: str, device: str):
    if key == "rules":
        mod = load_script("nlp_bench_rules", "01_reglas.py")
        return (lambda text: mod.clasificar(text)), None
    if key == "ml":
        mod = load_script("nlp_bench_ml", "02_ml_supervisado.py")
        model, count = mod.entrenar()
        return (lambda text: model.predict([text])[0]), {"training_examples": count}
    if key == "pretrained":
        mod = load_script("nlp_bench_pretrained", "03_preentrenado.py")
        from transformers import pipeline
        import torch
        try:
            torch.set_num_threads(int(os.environ.get("NLP_BENCH_TORCH_THREADS", "2")))
        except RuntimeError:
            pass
        pipeline_device = 0 if device == "cuda" else -1
        if device == "cuda" and not torch.cuda.is_available():
            raise RuntimeError("CUDA requested but torch.cuda.is_available() is False")
        # Do not re-initialize the model for every request.
        pipe = pipeline("zero-shot-classification", model=mod.MODELO, device=pipeline_device)
        def predict(text):
            output = pipe(text, candidate_labels=mod.ETIQUETAS,
                          hypothesis_template="Este mensaje trata sobre {}.", multi_label=False)
            return LABEL_MAP[output["labels"][0]]
        return predict, {"huggingface_model": mod.MODELO, "candidate_labels": len(mod.ETIQUETAS), "tokenizer": pipe.tokenizer}
    raise ValueError(key)


def measure_tokens(ctx: dict | None, messages: list[str]) -> dict:
    if not ctx or "tokenizer" not in ctx:
        return {"tokens_per_message_avg": None, "token_type": "no billable API tokens"}
    tokenizer = ctx["tokenizer"]
    labels = ["Este mensaje trata sobre " + x + "." for x in LABEL_MAP]
    lengths = []
    for message in messages:
        counts = [len(tokenizer(message, text_pair=hypothesis, truncation=True)["input_ids"])
                  for hypothesis in labels]
        lengths.append(sum(counts))
    return {"tokens_per_message_avg": round(statistics.mean(lengths), 1),
            "token_type": "input tokens across 4 NLI text pairs (NOT provider billing)"}


def stress(predict, messages: list[str], *, target_rps: float, duration: float,
           workers: int, backlog: int) -> dict:
    """Bounded, open-loop task arrival test. Does not model HTTP/LB overhead.

    A request is rejected if there is not enough client-side capacity. Only
    completed tasks are counted. Offered rate is not mislabeled throughput.
    """
    limit = max(workers, backlog)
    max_offered = int(target_rps * duration)
    completed_latencies = []
    queued = []
    completed = rejected = failed = offered = 0
    pending = []
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for i in range(max_offered):
            due = start + i / target_rps
            remaining = due - time.perf_counter()
            if remaining > 0:
                time.sleep(remaining)
            pending_next = []
            for future in pending:
                if future.done():
                    try:
                        compute_ms, queue_ms = future.result()
                        completed_latencies.append(compute_ms)
                        queued.append(queue_ms)
                        completed += 1
                    except Exception:
                        failed += 1
                else:
                    pending_next.append(future)
            pending = pending_next
            offered += 1
            if len(pending) >= limit:
                rejected += 1
                continue
            text = messages[i % len(messages)]
            submitted_at = time.perf_counter()
            def invoke(message=text, submit= submitted_at):
                started = time.perf_counter()
                predict(message)
                done = time.perf_counter()
                return ((done - started) * 1000, (started - submit) * 1000)
            pending.append(pool.submit(invoke))
        for future in pending:
            try:
                compute_ms, queue_ms = future.result()
                completed += 1
                completed_latencies.append(compute_ms)
                queued.append(queue_ms)
            except Exception:
                failed += 1
    total_wall = time.perf_counter() - start
    return {
        "target_rps": target_rps, "duration_s_requested": duration,
        "workers": workers, "max_in_flight": limit,
        "offered": offered, "accepted": offered - rejected,
        "completed": completed, "rejected": rejected, "failed": failed,
        "wall_s_including_drain": round(total_wall, 4),
        "achieved_rps_including_drain": round(completed / total_wall, 2) if total_wall else None,
        "completion_ratio": round(completed / offered, 4) if offered else None,
        "inference_p95_ms": percentile(completed_latencies, .95),
        "queue_p95_ms": percentile(queued, .95),
        "end_to_end_p95_ms": percentile([a + b for a, b in zip(completed_latencies, queued)], .95),
        "passed_100rps_test": (rejected == 0 and failed == 0 and completed == offered and
                               total_wall <= duration * 1.10) if offered else False,
        "note": "in-process load; no HTTP/TLS/load balancer. Throughput includes drain time.",
    }


def benchmark_one(key: str, device: str, corpus: list[str], args) -> dict:
    row = {"id": key, "status": "NOT_MEASURED", "reason": None,
           "instance": CANDIDATES[key if key != "pretrained" else "pretrained_" + device],
           "samples": args.samples_pretrained if key == "pretrained" else args.samples}
    if key == "pretrained" and args.skip_pretrained:
        row["reason"] = "explicit --skip-pretrained"
        return row
    try:
        with ProcessMeter() as meter:
            predict, context = prepare_model(key, device)
        row["startup"] = meter.data()
        row.update({"status": "MEASURED", "model_info": {k:v for k,v in (context or {}).items() if k != "tokenizer"}})
        for phrase in corpus[:max(1, args.warmups)]:
            predict(phrase)
        timings_ms = []
        with ProcessMeter() as infer_meter:
            for i in range(row["samples"]):
                phrase = corpus[i % len(corpus)]
                t0 = time.perf_counter_ns()
                predict(phrase)
                timings_ms.append((time.perf_counter_ns() - t0) / 1e6)
        row["inference"] = infer_meter.data()
        elapsed = row["inference"]["wall_s"]
        row["inference"].update({
            "requests": len(timings_ms),
            "mean_ms": round(statistics.mean(timings_ms), 4),
            "p50_ms": round(percentile(timings_ms, .5), 4),
            "p95_ms": round(percentile(timings_ms, .95), 4),
            "p99_ms": round(percentile(timings_ms, .99), 4),
            "sequential_rps": round(len(timings_ms) / elapsed, 2) if elapsed else None,
            "avg_response_body_bytes": round(statistics.mean(
                len(json.dumps({"intent": str(predict(x))}, ensure_ascii=False).encode("utf-8"))
                for x in corpus[:min(10, len(corpus))]), 1),
        })
        row["inputs"] = {
            "avg_request_body_bytes": round(statistics.mean(
                len(json.dumps({"message": x}, ensure_ascii=False).encode("utf-8")) for x in corpus), 1),
            **measure_tokens(context, corpus),
        }
        if not args.skip_stress:
            with ProcessMeter() as load_meter:
                row["load_test"] = stress(predict, corpus, target_rps=args.target_rps,
                                           duration=args.duration_s, workers=args.workers,
                                           backlog=args.max_in_flight)
            row["load_resources"] = load_meter.data()
        del predict
        if key == "pretrained":
            try:
                import torch
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
            except Exception:
                pass
    except Exception as exc:
        row["status"] = "NOT_MEASURED"
        row["reason"] = f"{type(exc).__name__}: {exc}"
        row.pop("inference", None)
        row.pop("load_test", None)
    return row


def pricing(row: dict, args, hours: float) -> dict:
    messages = int(args.target_rps * hours * 3600)
    instance = EC2[row["instance"]]
    base = {"messages": messages, "hours": hours, "instance": row["instance"],
            "ec2_hourly_usd": instance["rate"], "status": "UNVERIFIED_HOST_PROJECTION"}
    if row["status"] != "MEASURED":
        return {**base, "status": "NO_BENCHMARK", "replicas_assumed": None,
                "estimated_cost_active_usd": None, "estimated_cost_730h_usd": None}
    peak = max((row.get("startup") or {}).get("peak_process_rss_mib") or 0,
               (row.get("inference") or {}).get("peak_process_rss_mib") or 0,
               (row.get("load_resources") or {}).get("peak_process_rss_mib") or 0)
    if peak and peak > instance["memory_gib"] * 1024 * .80:
        return {**base, "status": "EC2_RAM_MAY_BE_TOO_SMALL", "replicas_assumed": None,
                "estimated_cost_active_usd": None, "estimated_cost_730h_usd": None}
    # This is a CONDITIONAL projection, NOT an EC2 benchmark or verified capacity.
    # A paced test that offered 100/s and accepted all 100/s does NOT tell us
    # max capacity; use the unpaced (sequential) measurement for a proxy.
    # The load-test pass/fail result is a separate check.
    capacity = (row.get("inference") or {}).get("sequential_rps")
    if not capacity:
        return {**base, "status": "NO_CAPACITY", "replicas_assumed": None,
                "estimated_cost_active_usd": None, "estimated_cost_730h_usd": None}
    replicas = max(1, math.ceil(args.target_rps / (capacity * args.capacity_fraction)))
    storage_gb = args.ebs_gb_pretrained if row["id"] == "pretrained" else args.ebs_gb
    ebs = replicas * storage_gb * args.ebs_price_gb_month
    # Only response bytes are outbound, request is inbound (excluded); payload no TLS overhead.
    outbound_gb = messages * row["inference"]["avg_response_body_bytes"] / 1e9
    data_transfer = max(0, outbound_gb - args.free_egress_gb) * args.egress_price_per_gb
    # EBS billed monthly even if compute runs only 8 hours.
    active = replicas * instance["rate"] * hours + ebs + data_transfer
    on = replicas * instance["rate"] * args.month_hours + ebs + data_transfer
    status = "MEASURED_ON_EC2_PROXY" if args.ec2_verified else "UNVERIFIED_HOST_PROJECTION"
    infra_per_million_tokens = (active / (messages * row["inputs"]["tokens_per_message_avg"] / 1e6)
                                if row.get("inputs", {}).get("tokens_per_message_avg") else None)
    return {**base, "status": status, "replicas_assumed": replicas,
            "per_instance_measured_host_rps": capacity,
            "ram_fit_check_only": peak,
            "ec2_compute_active_usd": round(replicas * instance["rate"] * hours, 4),
            "ebs_usd": round(ebs, 4), "egress_gb_payload_est": round(outbound_gb, 4),
            "egress_usd": round(data_transfer, 4),
            "estimated_cost_active_usd": round(active, 4),
            "estimated_cost_730h_usd": round(on, 4),
            "per_million_messages_usd_active": round(active / (messages / 1e6), 5) if messages else None,
            "billable_model_tokens": 0,
            "provider_token_charge_usd": 0,
            "self_hosted_infrastructure_usd_per_million_nli_input_tokens": round(infra_per_million_tokens, 5) if infra_per_million_tokens is not None else None,
            "note": "conditional estimate; CPU/GPU host != EC2 unless benchmark executed there",
    }


def fmt(x, digits=2, unit=""):
    if x is None:
        return "—"
    return f"{x:,.{digits}f}{unit}" if isinstance(x, (int, float)) else escape(str(x))


def bar_chart(title: str, rows: list[dict], key: str, suffix: str):
    maximum = max([float((r.get("inference") or {}).get(key) or 0) for r in rows] + [1])
    colors = {"rules": "#3ad6c2", "ml": "#7298fa", "pretrained": "#f0b463"}
    bars = []
    for row in rows:
        value = (row.get("inference") or {}).get(key)
        val = float(value or 0)
        width = val / maximum * 100 if maximum else 0
        bars.append(f'<div class="chart-row"><span>{escape(row["id"])}</span><div class="track"><i style="width:{width:.2f}%;background:{colors[row["id"]]}"></i></div><b>{fmt(value)} {suffix}</b></div>')
    return f'<section class="chartbox"><h3>{escape(title)}</h3>{"".join(bars)}</section>'


CSS = """
:root{color-scheme:dark;font-family:Inter,'Segoe UI',Arial,sans-serif}*{box-sizing:border-box}
body{margin:0;background:#081421;color:#e8f3ff;line-height:1.52}main{max-width:1210px;margin:auto;padding:40px 26px 80px}
h1{font-size:clamp(36px,5vw,61px);line-height:1.08;letter-spacing:-.047em;margin:18px 0}
h2{margin:42px 0 15px;font-size:26px;letter-spacing:-.02em}h3{margin:0 0 15px;font-size:16px}
.hero{border:1px solid #285976;padding:42px;border-radius:25px;background:radial-gradient(ellipse at 92% 15%,#226b70,transparent 44%),linear-gradient(130deg,#162f52,#081421)}
.eyebrow{text-transform:uppercase;letter-spacing:.18em;color:#52dfd0;font-size:12px;font-weight:800}
.sub{color:#a3bcd0;max-width:760px}.chips{display:flex;flex-wrap:wrap;gap:9px;margin-top:22px}.chips span{padding:7px 11px;border:1px solid #4c7385;border-radius:25px;font-size:12px}
.metrics{display:grid;grid-template-columns:repeat(3,1fr);gap:15px}.metric{border:1px solid #2c4662;background:#102438;border-radius:17px;padding:20px;border-top:4px solid var(--accent)}
.metric h3{font-size:20px}.big{font-size:33px;font-weight:820;letter-spacing:-.03em}.small{font-size:12px;color:#a6bfd0}
.info{display:flex;justify-content:space-between;border-top:1px solid #2b4359;padding:9px 0;font-size:13px;gap:15px}.info strong{text-align:right}
.status{font-size:11px;letter-spacing:.08em;font-weight:800;text-transform:uppercase}.ok{color:#5ce4ca}.warn{color:#f1c074}
.panel,.chartbox{border:1px solid #2b465f;border-radius:17px;background:#112438;padding:22px}
.stats{display:grid;grid-template-columns:repeat(2,1fr);gap:15px}.number{font-size:31px;letter-spacing:-.025em;font-weight:800}
.chart-row{display:grid;grid-template-columns:112px 1fr 120px;align-items:center;gap:15px;margin:14px 0}
.track{height:14px;background:#243c53;border-radius:18px;overflow:hidden}.track i{display:block;height:100%;border-radius:16px}
.scroll{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:13px}th,td{text-align:left;padding:13px 10px;border-bottom:1px solid #2e4960}th{font-size:11px;text-transform:uppercase;color:#a4dcdf;letter-spacing:.06em}td.num,th.num{text-align:right}
.critical{border-left:4px solid #e9b468;background:#2b2c35;border-radius:12px;padding:17px 20px}.sources a,a{color:#75e5da}
footer{margin-top:44px;font-size:12px;color:#91aabf}.bullets{color:#b1c6d8;font-size:14px}.bullets li{margin:7px 0}
@media(max-width:850px){main{padding:16px}.hero{padding:25px}.metrics,.stats{grid-template-columns:1fr}.chart-row{grid-template-columns:70px 1fr 80px}}
"""


def make_html(report: dict) -> str:
    args = report["config"]
    results = report["results"]
    names = {"rules": "Reglas", "ml": "ML supervisado", "pretrained": "Preentrenado"}
    colors = {"rules": "#3ad6c2", "ml": "#7298fa", "pretrained": "#f0b463"}
    cards = []
    for row in results:
        startup = row.get("startup", {})
        perf = row.get("inference", {})
        load = row.get("load_test", {})
        usage = row.get("load_resources", {})
        notes = escape(row.get("reason") or "")
        good = row["status"] == "MEASURED"
        cards.append(f'''<article class="metric" style="--accent:{colors[row['id']]}">
        <div class="status {'ok' if good else 'warn'}">{'MEASURED' if good else 'NOT MEASURED'}</div>
        <h3>{names[row['id']]}</h3><div class="big">{fmt(perf.get('sequential_rps'),1)}</div><div class="small">frases/s · secuencial</div>
        <div class="info"><span>Inferencia p95</span><strong>{fmt(perf.get('p95_ms'),3)} ms</strong></div>
        <div class="info"><span>CPU durante inferencia</span><strong>{fmt(usage.get('process_cpu_pct_of_one_core'),1)} % de 1 núcleo</strong></div>
        <div class="info"><span>RAM pico (inferencia)</span><strong>{fmt(perf.get('peak_process_rss_mib'),1)} MiB</strong></div>
        <div class="info"><span>Carga/entrenamiento</span><strong>{fmt(startup.get('wall_s'))} s</strong></div>
        <div class="info"><span>Prueba {args['target_rps']:g} req/s</span><strong>{fmt(load.get('achieved_rps_including_drain'),1)} req/s</strong></div>
        <div class="small">{notes}</div></article>''')
    table_rows = []
    for row in results:
        perf, load, startup = (row.get(x) or {} for x in ("inference", "load_test", "startup"))
        usage = row.get("load_resources") or {}
        data = [names[row["id"]],row["status"],fmt(startup.get("wall_s")), fmt(perf.get("p50_ms"),3),fmt(perf.get("p95_ms"),3),fmt(perf.get("p99_ms"),3),fmt(perf.get("peak_process_rss_mib")),fmt(usage.get("process_cpu_pct_of_one_core")),fmt(load.get("completed"),0),fmt(load.get("rejected"),0),fmt(load.get("achieved_rps_including_drain")),fmt(usage.get("host_network_rx_bytes"),0),fmt(usage.get("host_network_tx_bytes"),0)]
        table_rows.append("<tr>"+"".join(f'<td class="num">{v}</td>' if i>1 else f'<td>{v}</td>' for i,v in enumerate(data))+"</tr>")
    cost_rows=[]
    for scenario, days, hours in [("8 horas totales/mes",None,args["hours_month"]),("8 h/día × 30 días",args["days"],args["hours_day"]*args["days"])]:
        for row in results:
            cost=pricing(row, SimpleNamespace(**args), hours)
            cost_rows.append(f'''<tr><td>{scenario}</td><td>{names[row['id']]}</td>
            <td class="num">{cost['messages']:,}</td><td class="num">{cost.get('replicas_assumed') or '—'}</td>
            <td class="num">{fmt(cost.get('ec2_compute_active_usd'),2)}</td><td class="num">{fmt(cost.get('ebs_usd'),2)}</td>
            <td class="num">{fmt(cost.get('egress_usd'),2)}</td>
            <td class="num">{fmt(cost.get('estimated_cost_active_usd'),2)}</td>
            <td class="num">{fmt(cost.get('estimated_cost_730h_usd'),2)}</td>
            <td>{escape(cost['status'])}</td></tr>''')
    volume_a = int(args["target_rps"] * args["hours_month"] * 3600)
    volume_b = int(args["target_rps"] * args["hours_day"] * args["days"] * 3600)
    provenance = "AWS EC2 (self-reported)" if args["ec2_verified"] else "Non-EC2 / unverified host"
    sources = " · ".join(f'<a href="{escape(link,quote=True)}">{escape(label)}</a>' for label,link in SOURCE_LINKS)
    full = sum(r["status"]=="MEASURED" for r in results)
    note = 'ALL THREE models were measured.' if full == 3 else 'Only '+str(full)+' of 3 models measured. Missing models are NOT extrapolated or imputed.'
    return f'''<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>NLP | CPU, RAM, Network & AWS Cost Benchmark</title><style>{CSS}</style></head><body><main>
    <header class="hero"><div class="eyebrow">Measured performance · AWS scenarios · {escape(report['generated_utc'])}</div>
    <h1>Three NLP approaches.<br>One honest benchmark.</h1>
    <p class="sub">Real code execution where available. CPU, peak RAM, latency, attempted 100 requests/s, and host network I/O. Cloud costs are projections, not AWS invoices.</p>
    <div class="chips"><span>{full}/3 executed</span><span>{escape(provenance)}</span><span>{args['target_rps']:g} req/s target</span><span>us-east-1 On-Demand</span><span>USD · prices {TIMESTAMP}</span></div></header>
    <h2>Data provenance</h2><p class="critical"><strong>{note}</strong> Machine: {escape(report['hardware']['platform'])}, {report['hardware']['cpu_logical']} logical CPUs,
    {fmt(report['hardware']['ram_total_gib'])} GiB RAM. Never treat results from this host as measured on EC2. A hypothetical EC2 replica count is not a capacity guarantee.</p>
    <h2>Measured model performance</h2><div class="metrics">{''.join(cards)}</div>
    <h2>In-depth performance</h2><div class="stats">
    {bar_chart('Sequential inference: phrases/second', results, 'sequential_rps','rps')}
    {bar_chart('Peak process RAM (MiB)', results, 'peak_process_rss_mib','MiB')}
    </div>
    <h2>Time, CPU, memory and network</h2><div class="panel scroll"><table><thead><tr>
    <th>Approach</th><th>Status</th><th class="num">Init s</th><th class="num">p50 ms</th><th class="num">p95 ms</th><th class="num">p99 ms</th><th class="num">RSS MiB</th><th class="num">CPU %*</th><th class="num">Completed</th><th class="num">Rejected</th><th class="num">Load RPS</th><th class="num">Host RX B (load)</th><th class="num">Host TX B (load)</th></tr></thead><tbody>{''.join(table_rows)}</tbody></table></div>
    <p class="small">* Process CPU % and network RX/TX refer to the paced load test (the sequential loops are too short for reliable CPU sampling). Process CPU % is relative to one logical CPU (200% means about two cores). Network values use HOST counters, include unrelated traffic, and are NOT attributable to this model. Inference is local in-process, so there is no remote inference API call.</p>
    <h2>Demand and monthly infrastructure estimate</h2><div class="stats">
    <section class="panel"><span class="small">{args['target_rps']:g}/s × {args['hours_month']:g} total h/month</span><div class="number">{volume_a:,}</div><span class="small">messages per month</span></section>
    <section class="panel"><span class="small">{args['target_rps']:g}/s × {args['hours_day']:g} h/day × {args['days']} days</span><div class="number">{volume_b:,}</div><span class="small">messages per month</span></section></div>
    <div class="panel scroll" style="margin-top:16px"><table><thead><tr><th>Scenario</th><th>Method</th><th class="num">Messages</th><th class="num">EC2 replicas†</th><th class="num">Compute USD</th><th class="num">EBS USD</th><th class="num">Egress USD</th><th class="num">Active USD total</th><th class="num">Always-on 730h USD</th><th>Verification</th></tr></thead><tbody>{''.join(cost_rows)}</tbody></table></div>
    <p class="small">† Conditional scaling: ceil(target RPS / (HOST measured RPS × {args['capacity_fraction']:.0%})); no AWS performance validation. Also compare memory to EC2. Always-on (730h) costs are available in the JSON. Add data services, redundancy, load balancers, TLS/HTTP, cloud logs, support and taxes separately. EBS is billed for the full month.</p>
    <h2>Model tokens and cost attribution</h2>
    <div class="panel scroll"><table><thead><tr><th>Approach</th><th>Measured NLI tokens/message</th><th>Provider fee per token</th><th>Infrastructure USD / million model input tokens*</th></tr></thead><tbody>
    {''.join(f'<tr><td>{names[r["id"]]}</td><td>{fmt((r.get("inputs") or {}).get("tokens_per_message_avg"))}</td><td>USD 0</td><td>{fmt((pricing(r, SimpleNamespace(**args), args["hours_month"])).get("self_hosted_infrastructure_usd_per_million_nli_input_tokens"),5)}</td></tr>' for r in results)}
    </tbody></table><p class="small">* Model token counts only apply to the pretrained NLI model (four text-pairs per request). This is effective EC2 + EBS + egress cost divided by computational model tokens, NOT a model vendor's price. Input tokens may change with sentence length.</p></div>
    <h2>How token costs work here</h2><div class="panel"><p>All three examples use <strong>locally executed</strong> algorithms/models. There is <strong>no billable per-token provider charge</strong>, even for the pretrained model. Its tokenizer produces NLI input tokens; those are workload measurements, not AWS invoices. Per-message infrastructure cost depends on EC2 hours, memory fit, storage and egress. On Bedrock or an external paid model API, you must select that provider's specific model and pricing separately.</p>
    <ul class="bullets"><li>Approximate service request/response payload sizes are included in JSON; network transfer assumes JSON bodies and excludes HTTP/TLS headers.</li><li>Internet inbound is generally free; outbound price assumes {args['free_egress_gb']} GB free and USD {args['egress_price_per_gb']} / GB above that; these are editable assumptions.</li><li>EC2 rates: m7i.large ${EC2['m7i.large']['rate']}/h, c7i.xlarge ${EC2['c7i.xlarge']['rate']}/h, g5.xlarge ${EC2['g5.xlarge']['rate']}/h. gp3: USD {args['ebs_price_gb_month']}/GB-month.</li></ul></div>
    <h2>Limitations & reproducibility</h2><div class="critical">The stress test is an in-process, bounded-arrival experiment, NOT an HTTP server load test. Shared pipeline calls under threads may not scale like multiple independent workers. Repeating 20 classroom messages is not an independent accuracy benchmark. All AWS totals are scenarios until measured on the specific EC2 hardware under real networking.</div>
    <h2>Pricing/model sources</h2><section class="panel sources">{sources}</section>
    <footer>Generated at {escape(report['generated_utc'])}. Full raw measurements and assumptions: accompanying JSON. No fabricated measurements.</footer>
    </main></body></html>'''


# Avoid any third-party dependency for render-only helpers.
from types import SimpleNamespace


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--samples", type=int, default=180)
    parser.add_argument("--samples-pretrained", type=int, default=14)
    parser.add_argument("--warmups", type=int, default=2)
    parser.add_argument("--target-rps", type=float, default=100, help="Actual short load-test rate")
    parser.add_argument("--projection-rps", type=float, default=1000, help="Monthly infrastructure demand; independent of load test")
    parser.add_argument("--rebuild-from-json", type=Path, default=None, help="Use saved real measurements to recreate informe_benchmark_real.html without rerunning models")
    parser.add_argument("--duration-s", type=float, default=2.5)
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--max-in-flight", type=int, default=9)
    parser.add_argument("--skip-pretrained", action="store_true")
    parser.add_argument("--skip-stress", action="store_true")
    parser.add_argument("--allow-partial", action="store_true", help="Exit 0 if some model could not be executed; status in HTML remains NOT_MEASURED")
    parser.add_argument("--device", choices=("cpu", "cuda"), default="cpu")
    parser.add_argument("--torch-threads", type=int, default=2)
    parser.add_argument("--ec2-verified", action="store_true", help="Only use when this actually runs on EC2; avoids falsely claiming an AWS benchmark")
    parser.add_argument("--hours-month", type=float, default=8)
    parser.add_argument("--hours-day", type=float, default=8)
    parser.add_argument("--days", type=int, default=30)
    parser.add_argument("--month-hours", type=float, default=730)
    parser.add_argument("--capacity-fraction", type=float, default=.70)
    parser.add_argument("--ebs-gb", type=float, default=30)
    parser.add_argument("--ebs-gb-pretrained", type=float, default=50)
    parser.add_argument("--ebs-price-gb-month", type=float, default=.08)
    parser.add_argument("--egress-price-per-gb", type=float, default=.09)
    parser.add_argument("--free-egress-gb", type=float, default=100)
    for instance in EC2:
        parser.add_argument("--price-" + instance.replace(".", "-"), type=float, default=EC2[instance]["rate"])
    parser.add_argument("--html-out", type=Path, default=BASE / "informe_benchmark_real.html")
    parser.add_argument("--json-out", type=Path, default=BASE / "benchmark_mediciones.json")
    parser.add_argument("--_child-model", choices=("rules", "ml", "pretrained"), default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_child-config", type=Path, default=None, help=argparse.SUPPRESS)
    parser.add_argument("--_child-result", type=Path, default=None, help=argparse.SUPPRESS)
    a=parser.parse_args(argv)
    if min(a.samples, a.samples_pretrained, a.workers, a.max_in_flight, a.torch_threads, a.days) < 1:
        parser.error("Sample sizes, workers, inflight, threads and days must be positive")
    if min(a.target_rps,a.duration_s,a.hours_month,a.hours_day,a.month_hours,a.ebs_gb,a.ebs_gb_pretrained) <= 0:
        parser.error("Target rate, duration, hours, EBS sizes must be positive")
    if not 0 < a.capacity_fraction <= 1:
        parser.error("capacity-fraction must be in (0,1]")
    for instance in EC2:
        EC2[instance]["rate"] = getattr(a,"price_"+instance.replace(".","_"))
    return a


def run(argv=None):
    args=parse_args(argv)
    if args._child_model:
        # Subprocess isolation prevents previous models from contaminating RAM
        # measurements; the total executable load is measured within each child.
        child_config = json.loads(args._child_config.read_text(encoding="utf-8"))
        child_args = SimpleNamespace(**child_config)
        os.environ["NLP_BENCH_TORCH_THREADS"] = str(child_args.torch_threads)
        child_row = benchmark_one(args._child_model, child_args.device, get_data(), child_args)
        args._child_result.write_text(json.dumps(child_row, ensure_ascii=False,indent=2), encoding="utf-8")
        return 0

    if args.rebuild_from_json:
        from benchmark_capacity_report import enhance_html
        saved=json.loads(args.rebuild_from_json.read_text(encoding="utf-8"))
        html,projection=enhance_html(make_html(saved),saved,
            target_rps=args.projection_rps,hours_day=args.hours_day,
            days=args.days,capacity_fraction=args.capacity_fraction)
        args.html_out.parent.mkdir(parents=True,exist_ok=True)
        args.html_out.write_text(html,encoding="utf-8")
        projection_path=args.html_out.with_name("proyeccion_benchmark_1000_rps.json")
        projection_path.write_text(json.dumps(projection,ensure_ascii=False,indent=2),encoding="utf-8")
        print("Updated original HTML from recorded measurements:",args.html_out.resolve())
        return 0

    corpus=get_data()
    results=[]
    # Each model starts in a clean Python interpreter with its own process RSS.
    with tempfile.TemporaryDirectory(prefix="nlp-benchmark-") as td:
        tmp = Path(td)
        config_file = tmp / "config.json"
        config_file.write_text(json.dumps({k:v for k,v in vars(args).items()
                                           if k not in ("html_out", "json_out", "_child_model", "_child_config", "_child_result")}),encoding="utf-8")
        for name in ("rules", "ml", "pretrained"):
            print(f"Running real {name} benchmark in isolated subprocess...",flush=True)
            result_path = tmp / f"{name}.json"
            process = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                      "--_child-model",name,"--_child-config",str(config_file),
                                      "--_child-result",str(result_path)],
                                     capture_output=True,text=True, timeout=1200)
            if result_path.exists():
                row = json.loads(result_path.read_text(encoding="utf-8"))
            else:
                row={"id":name,"status":"NOT_MEASURED", "reason":f"child exit {process.returncode}: {process.stderr[-900:]}"}
            row["child_exit_code"] = process.returncode
            if process.stderr.strip() and row.get("reason"):
                row["child_stderr_tail"] = process.stderr[-1200:]
            results.append(row)
            print(f"  {row['status']}; {row.get('reason') or 'measured'}",flush=True)

    hardware={"platform":platform.platform(),"python":sys.version.split()[0],"cpu_logical":os.cpu_count(),
              "cpu_physical":psutil.cpu_count(logical=False) if psutil else None,
              "ram_total_gib":round(psutil.virtual_memory().total / (1024**3),2) if psutil else None,
              "host_network_is_system_wide":True,
              "model_runner":"GitHub Actions" if os.getenv("GITHUB_ACTIONS") else "local/container",
              "environment_is_ec2_verified":bool(args.ec2_verified)}
    data={"generated_utc":datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),
          "hardware":hardware,
          "config":{key:value for key,value in vars(args).items()
                    if key not in ("html_out", "json_out", "_child_model", "_child_config", "_child_result")},
          "results":results,
          "cost_scenarios":{
              name:{r["id"]:pricing(r,args,hours) for r in results}
              for name,hours in (("8h_month",args.hours_month),("8h_daily",args.hours_day*args.days))},
          "price_snapshot_utc_date":TIMESTAMP,"price_sources":SOURCE_LINKS,
          "all_three_measured":all(r["status"]=="MEASURED" for r in results),
          "network_notice":"psutil.net_io_counters is system-wide and may include other processes; local inference requires no per-token paid network API."}
    args.json_out.parent.mkdir(parents=True,exist_ok=True)
    args.html_out.parent.mkdir(parents=True,exist_ok=True)
    from benchmark_capacity_report import enhance_html
    html,projection=enhance_html(make_html(data),data,
        target_rps=args.projection_rps,hours_day=args.hours_day,
        days=args.days,capacity_fraction=args.capacity_fraction)
    data["monthly_capacity_projection"]=projection
    args.json_out.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding="utf-8")
    args.html_out.write_text(html,encoding="utf-8")
    print("JSON:",args.json_out.resolve())
    print("HTML:",args.html_out.resolve())
    if not data["all_three_measured"] and not args.allow_partial:
        print("INCOMPLETE: at least one model did not execute. Use --allow-partial for an intentionally partial report.", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(run())
