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


## Contrato de anotación

CSV: `id,intenciones,urgente,revision,pedido_id`. Consultar [ACTIVIDAD.md](ACTIVIDAD.md) para criterios y ejemplos.

- `intenciones`: `ACCESO`, `FACTURACION`, `SOPORTE_TECNICO`, `ENVIOS`, `OTRO` o `REVISAR`.
- Para varias intenciones justificadas, unir con `|` (ejemplo: `FACTURACION|ENVIOS`). El orden no influye en la evaluación.
- `REVISAR`: mensaje demasiado ambiguo para asignar una intención; **no combinarlo** con otra etiqueta.
- `urgente`: `SI` solamente si existe una petición explícita de prioridad o plazo inmediato; `NO` en otro caso.
- `revision`: `SI` cuando no hay contexto suficiente para asignar una intención; `NO` en los demás casos.
- `pedido_id`: identificador numérico de pedido mencionado explícitamente, o vacío.

No se busca adivinar sentimientos, inferir departamentos a partir de cualquier palabra aislada ni crear anotaciones infalibles: hay decisiones discutibles. El objetivo es **documentar acuerdos**.


