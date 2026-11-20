# Benchmark real de NLP + CPU, RAM, red, latencia y AWS

Este script ejecuta de verdad los tres programas del curso:

1. `01_reglas.py` — coincidencias escritas a mano.
2. `02_ml_supervisado.py` — entrena un clasificador TF-IDF y regresión logística **una sola vez antes de la inferencia**.
3. `03_preentrenado.py` — descarga/carga **MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli** y ejecuta clasificaciones NLI *zero-shot* con cuatro hipótesis por mensaje. **No crea otra instancia del modelo por cada mensaje.**

La ejecución ocurre **en tres procesos Python separados**, para no contaminar las mediciones de RAM. Los datos provienen de los 20 mensajes docentes, repetidos cuando se requieren más solicitudes. No constituye una evaluación de precisión en producción.

## Instalación

Desde la raíz de `course_multi_agents`, con Python 3.11–3.12 recomendado:

```bash
python3 -m pip install -r nlp-foundations/requirements_benchmark.txt
```

Para registrar la tercera alternativa **debe estar instalado Transformers y el modelo debe poder descargarse de Hugging Face o estar en caché**. No se sustituyen fallas por números inventados.

## Ejecutar los tres enfoques (requiere Internet para el primer modelo preentrenado)

```bash
python3 nlp-foundations/benchmark_nlp_aws.py \
  --target-rps 100 --duration-s 15 \
  --workers 4 --max-in-flight 12 \
  --samples 300 --samples-pretrained 30
```

Salidas:

- `nlp-foundations/informe_benchmark_real.html` — informe visual autocontenido.
- `nlp-foundations/benchmark_mediciones.json` — mediciones brutas y supuestos, listo para análisis.

Si falla al ejecutar uno de los tres enfoques, **el script devuelve código de salida 2** y genera igualmente el HTML y el JSON con `NOT_MEASURED` y el error. Esto impide presentar falsamente una comparativa completa.

Si únicamente quieres una vista **incompleta**, claramente marcada:

```bash
python3 nlp-foundations/benchmark_nlp_aws.py --skip-pretrained --allow-partial
```

Para macOS, usa `--device cpu` (predeterminado). `--device cuda` es para hosts compatibles con NVIDIA CUDA; no presupone compatibilidad con Metal/MPS.

## Qué mide realmente

| Métrica | Método |
|---|---|
| Inicialización y entrenamiento | Segundos de reloj, una vez por proceso |
| Latencia de inferencia | p50, p95, p99 en ms; cientos de frases secuenciales |
| Throughput secuencial | Frases completadas / segundos reales |
| RPS bajo carga | Solicitudes completadas / tiempo total, incluyendo el tiempo de vaciado de cola |
| Prueba a 100 req/s | Llegadas temporizadas, cola limitada, solicitudes rechazadas y completadas |
| CPU | Tiempo de CPU del proceso / tiempo de reloj (100 % equivale a un núcleo lógico) |
| RAM | Pico de RSS del proceso, en MiB; cada enfoque aislado |
| GPU | Máximo de memoria CUDA asignada, si existe |
| Red | Diferencias de bytes RX/TX de interfaces de **todo el host** durante cada fase: **no son atribuibles exclusivamente al modelo** |
| Disco | Bytes escritos por el proceso cuando están disponibles |
| Tokens | Para el preentrenado, longitud del tokenizer en las cuatro hipótesis NLI por frase; **no es una tarifa por token** |
| Volumen | 100/s × 8 horas/mes = 2.880.000; y 100/s × 8 horas/día × 30 días = 86.400.000 |

**Crítica importante:** el generador de carga ejecuta llamadas Python *in-process* con varios hilos. No incluye API HTTP, TLS, serialización real por la red, balanceador, autoscaling, colas de producción, disponibilidad ni pruebas repetidas en distintas horas. Para validar el volumen en AWS, ejecutar **dentro** de cada instancia de destino y hacer pruebas HTTP independientes.

## Costos: precio por token vs. infraestructura

Los tres scripts son **locales/self-hosted**. Sus inferencias no tienen factura de proveedor de tokens: **US$0 por token API**, incluso para el modelo preentrenado que usa un tokenizer internamente. Se paga **hardware** mientras la VM está activa, más almacenamiento y transferencia de salida.

Tarifas de referencia **20-nov-2026**, us-east-1, Linux On-Demand (consulta siempre [EC2 oficial](https://aws.amazon.com/ec2/pricing/on-demand/)):

| Instancia hipotética | CPU | RAM | USD/h |
|---|---:|---:|---:|
| `m7i.large` | 2 vCPU | 8 GiB | 0.1008 |
| `c7i.xlarge` | 4 vCPU | 8 GiB | 0.1785 |
| `g5.xlarge` | 4 vCPU + GPU NVIDIA | 16 GiB | 1.0060 |

El cálculo de escenarios usa EBS gp3 **US$0,08/GB-mes** (30 GB para reglas y ML, 50 GB para preentrenado), y salida de datos **US$0,09/GB después de 100 GB gratuitos** como supuestos editables, sin incluir HTTP/TLS ni alta disponibilidad. Esos beneficios/tarifas pueden cambiar; valida en AWS Pricing Calculator. Para un entorno corporativo añade balanceador, CloudWatch, snapshots, IPv4 pública, NAT Gateway, fallos/reintentos, impuestos y soporte.

**No es medición EC2** a menos que ejecutes el benchmark allí. La cantidad de réplicas propuesta en el HTML deriva de throughput de **tu host**, con una reserva de capacidad de 30 %. Esa extrapolación **no es garantía** de capacidad de EC2. Un informe con modelo ausente no muestra precio inferido para ese modelo.

Opciones útiles:

```bash
python3 nlp-foundations/benchmark_nlp_aws.py --help
python3 nlp-foundations/benchmark_nlp_aws.py --target-rps 100 --duration-s 30 --workers 4
python3 nlp-foundations/benchmark_nlp_aws.py --price-m7i-large 0.1008 --ebs-price-gb-month 0.08
```

## GitHub Actions: ejecutar sin preparar tu Mac

Ve a **Actions → Full NLP benchmark (all 3) → Run workflow**. Ese job instala las dependencias, intenta descargar realmente el modelo preentrenado y produce los archivos `informe_benchmark_real.html` y `benchmark_mediciones.json` como *artifact*. Un modelo no medido hace **fallar el job**, en vez de simular un resultado.

Esas mediciones son del **runner de GitHub**, no de EC2. Si la descarga falla por conectividad, el reporte indica claramente cuál alternativa no pudo ejecutarse.

## Fuentes

- [AWS EC2 On-Demand](https://aws.amazon.com/ec2/pricing/on-demand/)
- [AWS EBS gp3](https://aws.amazon.com/ebs/pricing/)
- [AWS pricing calculator](https://calculator.aws/)
- [Pretrained MiniLM multilingual zero-shot NLI](https://huggingface.co/MoritzLaurer/multilingual-MiniLMv2-L6-mnli-xnli)
