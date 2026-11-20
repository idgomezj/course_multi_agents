# Fundamentos de NLP — del texto al problema de IA

**Duración sugerida:** 75 minutos · **Idioma:** español · **Requisitos:** actividad de [clasificación de mensajes](../introduction/actividad.md) y Python básico.

## Pregunta guía

> Antes de elegir un algoritmo o un LLM, ¿cómo definimos exactamente qué queremos comprender de un mensaje y cómo sabemos si lo resolvimos bien?

Este módulo **no construye modelos de lenguaje**. Trabaja la formulación de problemas de Procesamiento del Lenguaje Natural (NLP), el diseño de etiquetas y la evaluación de resultados, utilizando el mismo caso de atención al cliente para no aumentar la carga cognitiva.

## Resultados de aprendizaje

Al terminar, el estudiante podrá:

1. Distinguir clasificación de intenciones, extracción de entidades, sentimiento, resumen y detección de urgencia.
2. Explicar casos ambiguos, fuera de dominio y solicitudes con **más de una intención**.
3. Diseñar reglas de anotación consistentes y justificar cuándo solicitar revisión humana.
4. Separar datos de referencia (verdad de terreno) de predicciones y comparar ambos mediante métricas.
5. Interpretar **exact match, precision, recall y F1** sin confundir desempeño en una muestra pequeña con generalización.

## Contenidos y tiempos

| Bloque | Tiempo | Actividad |
|---|---:|---|
| Panorama de tareas NLP | 10 min | Un mensaje, varias preguntas |
| Intenciones, entidades y urgencia | 15 min | Descomponer una solicitud |
| Ambigüedad y revisión humana | 15 min | Resolver casos discutibles |
| Diseño de etiquetas y referencia | 15 min | Anotar mensajes y acordar criterios |
| Medición y discusión de errores | 20 min | Ejecutar evaluador, revisar desacuerdos |
| **Total** | **75 min** | |

## Materiales

- [Guía docente](GUIA_DOCENTE.md): secuencia, preguntas y criterios de corrección.
- [Actividad para estudiantes](ACTIVIDAD.md): enunciado y entregable.
- [Presentación en Markdown](DIAPOSITIVAS.md): guion de 10 diapositivas sin contenido redundante con llm-lab.
- [Datos de mensajes](datos/mensajes.csv): 20 mensajes para anotar.
- [Referencia docente](datos/referencia_docente.csv): decisión consensuada para cada caso, **visible en el repositorio; no es una prueba oculta**.
- [Predicciones de demostración](datos/predicciones_demo.csv): errores intencionales para aprender métricas.
- [Evaluador](evaluar.py) y [generador de plantilla](crear_plantilla.py): Python estándar, sin paquetes externos.

## Práctica paso a paso

Desde la raíz del repositorio:

```bash
python3 nlp-foundations/crear_plantilla.py
# Editar nlp-foundations/datos/respuestas_estudiante.csv
python3 nlp-foundations/evaluar.py --respuestas nlp-foundations/datos/respuestas_estudiante.csv
```

Para comenzar con una evaluación que ya contiene algunos errores:

```bash
python3 nlp-foundations/evaluar.py --respuestas nlp-foundations/datos/predicciones_demo.csv
```

La plantilla puede dejarse incompleta durante el trabajo. Para la evaluación final, anotar todas las filas.

## Contrato de anotación

CSV: `id,intenciones,urgente,revision,pedido_id`. Consultar [ACTIVIDAD.md](ACTIVIDAD.md) para criterios y ejemplos.

- `intenciones`: `ACCESO`, `FACTURACION`, `SOPORTE_TECNICO`, `ENVIOS`, `OTRO` o `REVISAR`.
- Para varias intenciones justificadas, unir con `|` (ejemplo: `FACTURACION|ENVIOS`). El orden no influye en la evaluación.
- `REVISAR`: mensaje demasiado ambiguo para asignar una intención; **no combinarlo** con otra etiqueta.
- `urgente`: `SI` solamente si existe una petición explícita de prioridad o plazo inmediato; `NO` en otro caso.
- `revision`: `SI` cuando no hay contexto suficiente para asignar una intención; `NO` en los demás casos.
- `pedido_id`: identificador numérico de pedido mencionado explícitamente, o vacío.

No se busca adivinar sentimientos, inferir departamentos a partir de cualquier palabra aislada ni crear anotaciones infalibles: hay decisiones discutibles. El objetivo es **documentar acuerdos**.

## Qué se deja expresamente para llm-lab

Bigram, predicción del siguiente token, construcción de tokenizadores y vocabularios para LLM, embeddings de modelos generativos, ventanas de contexto, PyTorch, attention, Transformers, inferencia con Qwen y ajuste fino (Full/LoRA/QLoRA). Véase [llm-lab](../llm-lab/).

**Siguiente etapa:** en llm-lab se estudia cómo aprende un modelo de lenguaje; este módulo prepara la necesidad de representaciones y modelos más expresivos sin adelantarse a su implementación.
