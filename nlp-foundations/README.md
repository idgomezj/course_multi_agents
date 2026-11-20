# Fundamentos de NLP — demostración participativa

**Duración:** 75 minutos · **Idioma:** español · **Nivel:** introductorio.

## Objetivo

Después del [ejercicio inicial de clasificación](../introduction/actividad.md), aprender que procesar lenguaje puede significar detectar **varias intenciones**, extraer identificadores, reconocer urgencia y solicitar aclaraciones cuando un mensaje resulta ambiguo.

**No hay una evaluación automatizada de estudiantes.** La comparación se hace con toda la clase.

## Dinámica

1. Proyectar un mensaje de `datos/mensajes.csv` sin mostrar ninguna respuesta.
2. Los estudiantes lo interpretan **manualmente** (intenciones, urgencia, pedido, revisión).
3. Votar y explicar la decisión.
4. El profesor ejecuta `demo_nlp.py`, que pausa antes de revelar la interpretación automática.
5. Pulsar **Enter** para revelar el resultado. Conversar sobre acuerdos y discrepancias.
6. Inventar mensajes que no estaban en el ejercicio y descubrir dónde falla el programa.

## Comandos desde la raíz del repositorio

Instalar una sola vez:

```bash
python3 -m pip install -r nlp-foundations/requirements.txt
```

**Demostración para toda la clase (recomendada):**

```bash
python3 nlp-foundations/demo_nlp.py --ejemplos --pausa
```

**Un caso concreto o un mensaje inventado:**

```bash
python3 nlp-foundations/demo_nlp.py --id 6
python3 nlp-foundations/demo_nlp.py --mensaje "Me debitaron dinero y todavía no recibí el paquete"
```

**Todos los mensajes, revelando uno a uno:**

```bash
python3 nlp-foundations/demo_nlp.py --todos --pausa
```

Para preparar una hoja de respuestas **manual** en CSV, opcionalmente:

```bash
python3 nlp-foundations/crear_plantilla.py
```

El archivo `datos/respuestas_estudiante.csv` contiene el texto del mensaje junto con columnas vacías.

## Tres enfoques comparativos de NLP

**[Ejecutar y comparar: reglas, ML entrenado y un modelo preentrenado](README_TRES_ENFOQUES.md).**

- [01_reglas.py](01_reglas.py) — reglas escritas por nosotros.
- [02_ml_supervisado.py](02_ml_supervisado.py) — clasificador que entrenamos con 40 ejemplos.
- [03_preentrenado.py](03_preentrenado.py) — modelo multilingüe que descargamos ya entrenado.

Son demostraciones opcionales; la actividad principal sigue siendo manual y participativa.

## Recursos

- [ACTIVIDAD.md](ACTIVIDAD.md): enunciado y preguntas para los estudiantes.
- [GUIA_DOCENTE.md](GUIA_DOCENTE.md): conducción y tiempos de clase.
- [DIAPOSITIVAS.md](DIAPOSITIVAS.md): guion visual de nueve diapositivas.
- [datos/mensajes.csv](datos/mensajes.csv): 20 mensajes que la clase puede analizar.
- [demo_nlp.py](demo_nlp.py): procesamiento automático en vivo.
- [datos/referencia_docente.csv](datos/referencia_docente.csv): referencia orientativa para el profesor (pública, no prueba privada).

## ¿Qué tecnología utiliza?

`demo_nlp.py` emplea **spaCy con reglas lingüísticas** (`PhraseMatcher`) y expresiones regulares para reconocer fragmentos, varias intenciones e identificadores. No descarga un modelo grande, ni entrena un clasificador ni utiliza un LLM. Puede equivocarse con sinónimos, ironía o mensajes no previstos. **No confundir coincidencia con comprensión semántica universal.**

## Límite curricular

**No repetir** Bigram, predicción del siguiente token, tokenizadores internos, embeddings, redes neuronales, attention, Transformers, Qwen, fine-tuning, LoRA o QLoRA. Esos contenidos pertenecen a [llm-lab](../llm-lab/).

**Pregunta de cierre:** si el programa funciona bien con ejemplos preparados, ¿cómo podemos conseguir que generalice mejor a textos desconocidos?

## Costos y rendimiento de los tres enfoques

[Benchmark técnico y generación de informe HTML de costos AWS](README_BENCHMARK_AWS.md). [Informe integrado (1.000 req/s, 8 h/día)](informe_benchmark_real.html).
