# Guía docente — NLP mediante comparación humana y automática

## Agenda: 75 minutos

| Tiempo | Profesor | Estudiantes |
|---|---|---|
| 0–10 min | Define NLP y muestra un mensaje | Enumeran las posibles tareas |
| 10–25 min | Muestra mensaje #6 sin respuesta | Identifican intenciones, urgencia, pedido |
| 25–45 min | Ejecuta el programa con `--ejemplos --pausa` | Votan antes de cada resultado y debaten |
| 45–55 min | Contrasta `OTRO` frente a `REVISAR` | Defienden decisiones |
| 55–70 min | Prueba mensajes propuestos por el grupo | Detectan aciertos y fallos |
| 70–75 min | Explica límites y abre transición a llm-lab | Reflexionan sobre generalización |

## Antes de la clase

```bash
python3 -m pip install -r nlp-foundations/requirements.txt
python3 nlp-foundations/demo_nlp.py --id 6
```

## Durante la clase

```bash
python3 nlp-foundations/demo_nlp.py --ejemplos --pausa
```

La pantalla enseña el mensaje; **no aparece el análisis hasta pulsar Enter**. Esa pausa es esencial: permite preguntar primero a los alumnos.

También puede ejecutar:

```bash
python3 nlp-foundations/demo_nlp.py --mensaje "La compra desapareció de mi historial"
```

## Respuestas orientativas para el debate

- #5: ACCESO + FACTURACION.
- #6: FACTURACION + ENVIOS, urgencia SI, pedido 4582.
- #7: REVISAR («banco» es ambiguo).
- #11: ACCESO, urgencia SI por «hoy mismo».
- #12: OTRO (horario de atención).
- #13: FACTURACION + SOPORTE_TECNICO.
- #15: ENVIOS + SOPORTE_TECNICO, pedido 8821.
- #20: FACTURACION + SOPORTE_TECNICO, pedido 9715.

Estas respuestas no son verdades lingüísticas universales. Invite a discutir propuestas razonables, especialmente en casos ambiguos.

## Mensaje técnico honesto

La implementación usa el analizador básico de español de **spaCy**, coincidencias de expresiones y regex; es **NLP basado en reglas**, no un modelo de ML/LLM entrenado. Los ejemplos del CSV son conocidos al diseñar los patrones. Pruebe con frases nuevas para evidenciar límites y diferencias.

## No explicar en este módulo

Bigram, tokens para modelado de lenguaje, embeddings, redes neuronales, attention, Transformers o fine-tuning: corresponde a `llm-lab`.

**Pregunta puente:** ¿cómo desarrollar modelos que aprendan a reconocer expresiones que el programador no previó?
