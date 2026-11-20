# Guía docente — Fundamentos de NLP

**Objetivo:** introducir problemas de lenguaje, calidad de datos y evaluación sin repetir la construcción o el entrenamiento de un LLM.

## Secuencia de 75 minutos

**0–10 min — ¿Qué es NLP?** Recuperar la tarea de clasificación de mensajes de `introduction/actividad.md`. A partir de un mensaje, mostrar que surgen objetivos distintos: intenciones, entidades, urgencia, resumen, sentimiento. No enseñar otra solución TF-IDF ni `fit()`.

**10–25 min — Un mensaje no equivale a una etiqueta.** Mostrar el caso con cobro duplicado, pedido 4582 y entrega pendiente: dos intenciones + identificador + urgencia. Preguntar qué equipo debería atenderlo. Distinguir el campo `intenciones` del campo `revision`.

**25–40 min — Ambigüedad.** Ejemplos: «El banco no funciona» (banco financiero, asiento u otra cosa), «Mi problema es con el sistema» (no sabemos qué sistema). El mensaje puede ser legítimo y, aun así, no dar evidencia para decidir. Definir `REVISAR` y discutir el costo de las decisiones forzadas.

**40–55 min — Etiquetado.** En parejas, anotar el CSV de 20 mensajes. Comparar desacuerdos entre dos equipos. Elaborar una «guía de anotación»: definición operacional de cada campo, tratamiento de casos multi-intención y de incertidumbre, cómo preservar identificadores de pedido.

**55–75 min — Evaluación.** Ejecutar primero `predicciones_demo.csv` (contiene errores intencionales) y después anotaciones de los estudiantes. Explicar que la referencia está **consensuada por el docente**, no descubierta matemáticamente. Revisar precision, recall y F1 y su relevancia para el negocio. Analizar unos pocos errores, sin confundir evaluación con entrenamiento.

## Puntos para reforzar

- NLP es un **campo de problemas y métodos**, no un sinónimo de LLM.
- Una clasificación multilabel requiere otra métrica además del porcentaje de mensajes totalmente correctos.
- Las entidades deben estar respaldadas por el texto.
- Revisar una solicitud es una decisión válida; es diferente de `OTRO` (fuera de las cuatro áreas).
- La referencia de 20 casos **no** es un benchmark real ni permite afirmar generalización.
- Separar `train`, `validation` y `test` sigue siendo esencial para modelos aprendidos; aquí solo evaluamos anotaciones/manuales contra la misma tabla docente.

## Preguntas para discusión

1. Un mensaje pide ayuda con factura y entrega: ¿una etiqueta o dos?
2. ¿El sentimiento negativo implica prioridad urgente?
3. ¿Cómo resolver desacuerdos entre anotadores?
4. ¿Qué grupos de usuarios podrían quedar poco representados en el dataset?
5. ¿Qué daños pueden causar errores al clasificar reclamaciones o datos privados?

## Evaluación de la clase (sugerida)

- 30 %: identificación de tareas y explicación conceptual.
- 30 %: consistencia de anotaciones y criterio para `REVISAR`.
- 25 %: interpretación de métricas y análisis de errores.
- 15 %: calidad del argumento sobre limitaciones, privacidad y mejoras.

## Transición

Cerrar con: «Ya sabemos **qué** debe entender un sistema y **cómo** evaluar sus respuestas. ¿Cómo aprende un modelo a producir predicciones de lenguaje?». Iniciar `llm-lab/01_bigram` allí, sin desarrollar Bigram en esta clase.
