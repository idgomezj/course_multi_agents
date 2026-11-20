# Benchmark de tres NLP y costos AWS

El script [benchmark_nlp_aws.py](benchmark_nlp_aws.py) cronometra los tres ejemplos existentes y genera un informe HTML elegante y autocontenido. No sustituye ninguna actividad.

## Instalación y ejecución desde la raíz del repositorio

```bash
python3 -m pip install -r nlp-foundations/requirements_ml.txt
python3 -m pip install -r nlp-foundations/requirements_preentrenado.txt
python3 nlp-foundations/benchmark_nlp_aws.py
```

El reporte queda en **nlp-foundations/informe_nlp_aws.html**. Ábrelo en Chrome/Safari.

Si todavía no descargaste el modelo preentrenado:

```bash
python3 nlp-foundations/benchmark_nlp_aws.py --omitir-preentrenado
```

La alternativa preentrenada se marcará como **no medida**. El script no inventa resultados.

## Escenarios y tarifas

Precios de referencia verificados el 20 de noviembre de 2026: región **us-east-1**, Linux **On-Demand**, sin impuestos ni compromisos:

| EC2 | USD/h | Referencia |
|---|---:|---|
| m7i.large | 0.1008 | Reglas, ML supervisado |
| c7i.xlarge | 0.1785 | Preentrenado en CPU |
| g5.xlarge | 1.0060 | Preentrenado en GPU CUDA (opcional) |

Fuentes: [AWS oficial](https://aws.amazon.com/ec2/pricing/on-demand/), [m7i.large](https://instances.usage.ai/aws/ec2/m7i.large), [c7i.xlarge](https://instances.usage.ai/aws/ec2/c7i.xlarge), [g5.xlarge](https://instances.usage.ai/aws/ec2/g5.xlarge).

El escenario principal supone **100 frases/segundo durante 8 horas en total al mes**: 2.880.000 frases. Se incluye además la interpretación alternativa de **8 horas cada día durante 30 días**: 86.400.000 frases.

Editar el escenario:

```bash
python3 nlp-foundations/benchmark_nlp_aws.py --rps 100 --horas-mes 8 --horas-dia 8 --dias 30 --utilizacion 0.70 --muestras 300
```

Las tarifas son una instantánea histórica, **NO se actualizan en tiempo real**. Parámetros para sustituirlas: `--precio-m7i`, `--precio-c7i`, `--precio-g5`. `--dispositivo cuda` permite usar GPU para el preentrenado si PyTorch/CUDA están disponibles.

## Interpretación

- El script mide preparación/entrenamiento una vez y luego cronometra inferencias con p50, p95 y throughput secuencial.
- **No es una prueba de carga concurrente de 100 req/s.** La capacidad por EC2 se estima con escalado lineal idealizado y utilización del 70%; debe validarse en hardware EC2 real.
- La coincidencia con referencias del curso se calcula solo sobre ejemplos sencillos de una intención. No es un benchmark independiente de exactitud.
- Los precios EC2 no incluyen EBS, tráfico, balanceadores, observabilidad, alta disponibilidad ni impuestos.

Para medir rendimiento **real AWS**, ejecute el script dentro de las instancias candidatas con la misma versión de Python/dependencias y haga pruebas adicionales de concurrencia.
