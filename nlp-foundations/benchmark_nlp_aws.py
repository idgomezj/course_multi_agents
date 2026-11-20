#!/usr/bin/env python3
"""Benchmark de los tres casos NLP y proyección mensual AWS en HTML.

Los tiempos se miden en el equipo que ejecuta este script, NO en EC2
salvo que se ejecute allí. Las tarifas EC2 son una instantánea 2026-11-20.
"""
import argparse
import csv
from datetime import datetime, timezone
from html import escape
import importlib.util
import math
from pathlib import Path
import platform
import statistics
import time

BASE=Path(__file__).resolve().parent
TARIFAS={"m7i.large":0.1008,"c7i.xlarge":0.1785,"g5.xlarge":1.006}
MAPEO={
 "problemas de facturación y cobros":"FACTURACION",
 "problemas de envíos o entregas":"ENVIOS",
 "problemas para acceder a la cuenta":"ACCESO",
 "problemas técnicos de una aplicación":"SOPORTE_TECNICO",
}
VALIDAS=set(MAPEO.values())
SOURCES=[
 ("AWS EC2 oficial","https://aws.amazon.com/ec2/pricing/on-demand/"),
 ("m7i.large","https://instances.usage.ai/aws/ec2/m7i.large"),
 ("c7i.xlarge","https://instances.usage.ai/aws/ec2/c7i.xlarge"),
 ("g5.xlarge","https://instances.usage.ai/aws/ec2/g5.xlarge"),
]

def importar(nombre, archivo):
    spec=importlib.util.spec_from_file_location(nombre, BASE/archivo)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def corpus():
    with (BASE/"datos/mensajes.csv").open(encoding="utf-8-sig",newline="") as f:
        mensajes=list(csv.DictReader(f))
    with (BASE/"datos/referencia_docente.csv").open(encoding="utf-8-sig",newline="") as f:
        respuestas={r["id"]:r["intenciones"] for r in csv.DictReader(f)
                    if r["intenciones"] in VALIDAS}
    return ([x["mensaje"] for x in mensajes],
            [(x["mensaje"],respuestas[x["id"]]) for x in mensajes if x["id"] in respuestas])

def pctl(x,p):
    x=sorted(x)
    k=(len(x)-1)*p
    i=int(k)
    return x[i]*(1-(k-i))+x[min(i+1,len(x)-1)]*(k-i)

def medir(nombre,instancia,preparar,predecir,frases,referencia,n,warmups=2):
    r={"nombre":nombre,"instancia":instancia,"precio":TARIFAS[instancia],
       "estado":"no medido","muestras":0,"motivo":""}
    try:
        start=time.perf_counter()
        ctx=preparar()
        load=time.perf_counter()-start
        for i in range(warmups):
            predecir(ctx,frases[i%len(frases)])
        ms=[]
        for i in range(n):
            t=time.perf_counter_ns()
            predecir(ctx,frases[i%len(frases)])
            ms.append((time.perf_counter_ns()-t)/1e6)
        ok=0
        for frase,correcta in referencia:
            pred=predecir(ctx,frase)
            if isinstance(pred,(list,tuple,set)):
                pred=list(pred)[0] if len(pred)==1 else None
            ok+=(pred==correcta)
        r.update(estado="medido",muestras=n,carga_s=load,
                 p50_ms=pctl(ms,.50),p95_ms=pctl(ms,.95),
                 media_ms=statistics.mean(ms),rps=n/(sum(ms)/1000),
                 coincidencia=ok/len(referencia),n_referencia=len(referencia))
    except (Exception,SystemExit) as e:
        r["motivo"]=str(e)
    return r

def proyeccion(r,demanda,horas,utilizacion):
    if r["estado"]!="medido":
        return None
    n=max(1,math.ceil(demanda/(r["rps"]*utilizacion)))
    return (n,n*r["precio"]*horas,n*r["precio"]*730)

def moneda(n):
    return "Sin medición" if n is None else "US$ "+format(n,",.2f")

def numero(n,d=2):
    return "—" if n is None else format(n,f",.{d}f")

ESTILO="""
:root{color-scheme:dark}*{box-sizing:border-box}
body{margin:0;background:#091624;color:#ebf7fc;font:15px/1.6 Inter,'Segoe UI',Arial,sans-serif}
main{max-width:1140px;margin:auto;padding:28px 24px 75px}
header{border:1px solid #35616b;border-radius:26px;padding:43px;
background:radial-gradient(circle at 95% 0,#216c70,transparent 38%),linear-gradient(120deg,#16334f,#091724)}
header small{letter-spacing:.17em;text-transform:uppercase;color:#6fe6d4;font-weight:800}
h1{font-size:clamp(34px,4.5vw,55px);letter-spacing:-.05em;line-height:1.12;margin:14px 0}
h2{font-size:25px;letter-spacing:-.025em;margin:44px 0 18px}
.muted{color:#afc6d7}.pills{display:flex;gap:8px;flex-wrap:wrap}
.pills span{border:1px solid #4e7583;border-radius:20px;padding:7px 12px;font-size:12px}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}
.card{background:#11263b;border-radius:18px;border:1px solid #29465c;border-top:4px solid var(--a);padding:22px}
.card h3{font-size:21px}.big{font-size:38px;font-weight:850;letter-spacing:-.045em}
.small{font-size:12px;color:#b5cadd}.line{display:flex;justify-content:space-between;gap:14px;
border-top:1px solid #2c465e;padding:10px 0;font-size:13px}.line b{text-align:right}
.cost{color:var(--a);font-weight:800;font-size:20px}
.panel{background:#12263b;border:1px solid #2d485e;border-radius:19px;padding:23px}
.scenarios{display:grid;grid-template-columns:1fr 1fr;gap:16px}.scenarios b{display:block;font-size:31px}
.barrow{display:grid;grid-template-columns:160px 1fr 90px;gap:15px;align-items:center;margin:18px 0}
.track{height:17px;background:#263b50;border-radius:20px;overflow:hidden}.bar{height:100%;border-radius:20px}
table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:13px 10px;border-bottom:1px solid #2c475c;text-align:left}
th{color:#90ccda;text-transform:uppercase;font-size:11px;letter-spacing:.07em}th:nth-child(n+3),td:nth-child(n+3){text-align:right;white-space:nowrap}
.scroll{overflow-x:auto}.note{border-left:4px solid #f2bd77;background:#353034;padding:18px;border-radius:11px;color:#ffe1b1}
a{color:#6ae3da}footer{color:#8facbd;font-size:12px;margin-top:38px}
@media(max-width:900px){.grid,.scenarios{grid-template-columns:1fr}main{padding:16px}header{padding:25px}.barrow{grid-template-columns:85px 1fr 65px}}
"""

def hacer_html(resultados,args):
    volumen_8=int(args.rps*3600*args.horas_mes)
    horas_diarias=args.horas_dia*args.dias
    volumen_diario=int(args.rps*3600*horas_diarias)
    nombres=["Reglas","Machine Learning","Preentrenado"]
    colores=["#35d6ba","#85aaff","#f4c17d"]
    tarjetas=[]
    rows=[]
    barras=[]
    mayor=max([r.get("rps",0) for r in resultados] or [0])
    for i,r in enumerate(resultados):
        c=colores[i]
        estim=proyeccion(r,args.rps,args.horas_mes,args.utilizacion)
        tarjetas.append(
            f'<article class="card" style="--a:{c}"><small>{escape(r["estado"].upper())}</small>'
            f'<h3>{nombres[i]}</h3><div class="big">{numero(r.get("rps"),1)}</div>'
            '<div class="small">frases/segundo · secuencial</div>'
            f'<div class="line"><span>Latencia p50</span><b>{numero(r.get("p50_ms"),3)} ms</b></div>'
            f'<div class="line"><span>Latencia p95</span><b>{numero(r.get("p95_ms"),3)} ms</b></div>'
            f'<div class="line"><span>Preparación</span><b>{numero(r.get("carga_s"))} s</b></div>'
            f'<div class="line"><span>Coincidencia docente*</span><b>{numero(r.get("coincidencia"))}</b></div>'
            f'<div class="line"><span>Instancia hipotética</span><b>{r["instancia"]} · USD {r["precio"]:.4f}/h</b></div>'
            f'<div class="line"><span>8 horas/mes</span><b class="cost">{moneda(estim[1] if estim else None)}</b></div>'
            f'<div class="small">{escape(r["motivo"]) if r["motivo"] else ""}</div></article>'
        )
        v=r.get("rps",0)
        anchura=100*v/mayor if mayor else 0
        barras.append(f'<div class="barrow"><span>{nombres[i]}</span><div class="track">'
                      f'<div class="bar" style="background:{c};width:{anchura:.2f}%"></div></div>'
                      f'<strong>{numero(r.get("rps"),1)}</strong></div>')
    for etiqueta,horas,volumen in [("8 h/mes",args.horas_mes,volumen_8),
                                  (f"{args.horas_dia:g} h/día x {args.dias} días",horas_diarias,volumen_diario)]:
        for i,r in enumerate(resultados):
            x=proyeccion(r,args.rps,horas,args.utilizacion)
            rows.append(f'<tr><td>{etiqueta}</td><td>{nombres[i]}</td><td>{volumen:,}</td>'
                        f'<td>{x[0] if x else "—"}</td><td>{moneda(x[1] if x else None)}</td>'
                        f'<td>{moneda(x[2] if x else None)}</td></tr>')
    enlaces=" · ".join(f'<a href="{escape(url,quote=True)}">{escape(n)}</a>' for n,url in SOURCES)
    fechahora=datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f'''<!doctype html><html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Benchmark NLP · Costos AWS</title><style>{ESTILO}</style></head><body><main>
<header><small>FinOps + IA · Informe de rendimiento</small><h1>NLP: rendimiento<br>y costos AWS</h1>
<p class="muted">Mediciones locales reales y proyecciones matemáticas de infraestructura EC2: NO son benchmarks de AWS salvo que ejecutes el script allí.</p>
<div class="pills"><span>100 frases/s (editable)</span><span>us-east-1, Linux On-Demand</span>
<span>Precios 20-nov-2026</span><span>{sum(r["estado"]=="medido" for r in resultados)}/3 medidos</span></div></header>
<h2>Volumen mensual</h2><section class="scenarios">
<div class="panel"><span class="muted">{args.horas_mes:g} horas totales/mes</span><b>{volumen_8:,}</b><span class="muted">mensajes</span></div>
<div class="panel"><span class="muted">{args.horas_dia:g} h/día x {args.dias} días</span><b>{volumen_diario:,}</b><span class="muted">mensajes</span></div></section>
<h2>Tres alternativas</h2><section class="grid">{''.join(tarjetas)}</section>
<h2>Velocidad de inferencia</h2><section class="panel"><p class="muted">Frases/s secuenciales, excluyendo carga del modelo y tiempo de red. Host: {escape(platform.platform())}</p>{''.join(barras)}</section>
<h2>Costo estimado mensual</h2><section class="panel scroll"><table><thead><tr><th>Escenario</th><th>Enfoque</th><th>Mensajes</th><th>EC2 necesarias*</th><th>Solo horas activas</th><th>Encendido 730 h</th></tr></thead>
<tbody>{''.join(rows)}</tbody></table></section>
<h2>Cómo leer correctamente el resultado</h2><div class="note">
Las instancias son una estimación <b>hipotética</b> con escalado lineal: ceil({args.rps:g} / (frases/s medidas x {args.utilizacion:.0%} de uso)).
No es una garantía de servicio a 100 solicitudes/s. Para estimar AWS realmente debes medir en la instancia EC2 propuesta y probar
concurrencia, batch, carga, p95 y memoria. La coincidencia docente compara una pequeña selección de mensajes con una sola
intención, no una prueba de calidad de producción. Si falta el modelo preentrenado, aparece como NO MEDIDO y no se inventan datos.
</div>
<p class="muted">Tiempo de carga/entrenamiento separado del de inferencia. Precios de referencia fijos, no se actualizan en vivo.
Se excluyen almacenamiento/EBS, redes, balanceadores, logs, alta disponibilidad, licencias e impuestos.</p>
<h2>Precios y fuentes</h2><section class="panel">{enlaces}<p class="muted">m7i.large: USD {TARIFAS["m7i.large"]:.4f}/h · c7i.xlarge: USD {TARIFAS["c7i.xlarge"]:.4f}/h · g5.xlarge: USD {TARIFAS["g5.xlarge"]:.4f}/h.</p></section>
<footer>Generado {fechahora} · {escape(platform.platform())} · Precios referencia 2026-11-20</footer>
</main></body></html>'''

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rps",type=float,default=100)
    p.add_argument("--horas-mes",type=float,default=8)
    p.add_argument("--horas-dia",type=float,default=8)
    p.add_argument("--dias",type=int,default=30)
    p.add_argument("--utilizacion",type=float,default=.70)
    p.add_argument("--muestras",type=int,default=300)
    p.add_argument("--muestras-preentrenado",type=int,default=10)
    p.add_argument("--omitir-preentrenado",action="store_true")
    p.add_argument("--dispositivo",choices=["cpu","cuda"],default="cpu")
    p.add_argument("--precio-m7i",type=float,default=TARIFAS["m7i.large"])
    p.add_argument("--precio-c7i",type=float,default=TARIFAS["c7i.xlarge"])
    p.add_argument("--precio-g5",type=float,default=TARIFAS["g5.xlarge"])
    p.add_argument("--salida",type=Path,default=BASE/"informe_nlp_aws.html")
    a=p.parse_args(argv)
    if a.rps<=0 or a.horas_mes<=0 or a.horas_dia<=0 or a.dias<=0 or a.muestras<2 or a.muestras_preentrenado<2 or not 0<a.utilizacion<=1:
        p.error("RPS, horas, días y muestras positivos. Utilización entre 0 y 1.")
    if min(a.precio_m7i,a.precio_c7i,a.precio_g5)<=0:
        p.error("Los precios deben ser positivos")
    TARIFAS.update({"m7i.large":a.precio_m7i,"c7i.xlarge":a.precio_c7i,"g5.xlarge":a.precio_g5})
    mensajes,referencia=corpus()
    resultados=[]
    reglas=importar("nlp_reglas", "01_reglas.py")
    resultados.append(medir("reglas","m7i.large",lambda:None,
                            lambda _,s:reglas.clasificar(s),mensajes,referencia,a.muestras))
    try:
        ml=importar("nlp_ml","02_ml_supervisado.py")
        resultados.append(medir("ml","m7i.large",lambda:ml.entrenar()[0],
                                lambda model,s:model.predict([s])[0],mensajes,referencia,a.muestras))
    except (Exception,SystemExit) as e:
        resultados.append(dict(nombre="ml",instancia="m7i.large",precio=TARIFAS["m7i.large"],
                               estado="no medido",motivo=str(e),muestras=0))
    instancia="g5.xlarge" if a.dispositivo=="cuda" else "c7i.xlarge"
    if a.omitir_preentrenado:
        resultados.append(dict(nombre="preentrenado",instancia=instancia,
                               precio=TARIFAS[instancia],estado="no medido",
                               motivo="Omitido a petición del usuario",muestras=0))
    else:
        def carga_pre():
            from transformers import pipeline
            cfg=importar("nlp_pre","03_preentrenado.py")
            pipe=pipeline("zero-shot-classification",model=cfg.MODELO,
                          device=0 if a.dispositivo=="cuda" else -1)
            return pipe,cfg
        def pred_pre(ctx,s):
            pipe,cfg=ctx
            pred=pipe(s,candidate_labels=cfg.ETIQUETAS,
                      hypothesis_template="Este mensaje trata sobre {}.",multi_label=False)
            return MAPEO[pred["labels"][0]]
        resultados.append(medir("preentrenado",instancia,carga_pre,pred_pre,
                                mensajes[:10],referencia,a.muestras_preentrenado,warmups=1))
    a.salida.parent.mkdir(parents=True,exist_ok=True)
    a.salida.write_text(hacer_html(resultados,a),encoding="utf-8")
    for r in resultados:
        print(r["nombre"],r["estado"],numero(r.get("rps")),"frases/s",r.get("motivo",""))
    print("Informe HTML:",a.salida.resolve())

if __name__=="__main__":
    main()
