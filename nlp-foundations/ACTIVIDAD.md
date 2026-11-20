# Actividad: un mensaje, múltiples problemas de NLP

**Duración:** 45–50 min dentro de la clase · **Modalidad:** grupos de 2–3 estudiantes · **No utilizar modelos generativos para hacer las anotaciones**.

## Contexto

La empresa del ejercicio anterior quiere automatizar la atención al cliente. Inicialmente solo enviaba cada mensaje a **un** departamento. Sin embargo, encuentra solicitudes con varias intenciones, datos relevantes y expresiones ambiguas.

> «Me cobraron dos veces el pedido 4582, todavía no llega y necesito solución urgente».

### Parte A. ¿Cuál es realmente la tarea?

Identificar, por separado:

1. **Intención o intenciones:** ¿qué departamentos deben participar? Un mensaje puede requerir dos.
2. **Entidades:** ¿qué número de pedido aparece expresamente?
3. **Urgencia:** ¿se solicita prioridad o una respuesta inmediata explícita?
4. **Incertidumbre:** ¿la información basta para decidir o debe revisarla una persona?
5. **Resumen:** redactar en una frase el problema del cliente (no se califica con el script).

Discutir en clase otras tareas NLP: sentimiento, traducción, resumen, búsqueda de respuestas y extracción de información. No todas son clasificación.

### Parte B. Crear un conjunto de anotaciones

Leer `datos/mensajes.csv`, que incluye 20 casos. Completar una fila por mensaje con las columnas:

| Columna | Valores permitidos | Regla |
|---|---|---|
| `id` | Identificador de fila | Mantenerlo sin cambios |
| `intenciones` | `ACCESO`, `FACTURACION`, `SOPORTE_TECNICO`, `ENVIOS`, `OTRO`, `REVISAR` | Usar `|` para varias intenciones; `OTRO` y `REVISAR` no se combinan |
| `urgente` | `SI` o `NO` | Se expresa urgencia explícita o un plazo inmediato |
| `revision` | `SI` o `NO` | Hace falta aclarar la intención con una persona |
| `pedido_id` | Dígitos o vacío | Solo el número de pedido que el cliente escribe |

Ejemplo de anotación:

```csv
id,intenciones,urgente,revision,pedido_id
6,FACTURACION|ENVIOS,SI,NO,4582
```

**Evitar:** deducir el número de pedido; etiquetar automáticamente como urgente todo mensaje negativo; seleccionar una sola categoría cuando hay dos solicitudes independientes; asignar departamento cuando solo se dice «el sistema no funciona» sin más contexto.

Generar el archivo a completar:

```bash
python3 nlp-foundations/crear_plantilla.py
```

### Parte C. Comparar y evaluar

Al terminar las anotaciones, comparar con la referencia consensuada del docente:

```bash
python3 nlp-foundations/evaluar.py --respuestas nlp-foundations/datos/respuestas_estudiante.csv
```

Revisar las métricas: coincidencia exacta de intenciones, precision/recall/F1 micro, accuracy de urgencia, revisión y pedido.

**Preguntas de reflexión:**

- ¿Por qué accuracy puede ocultar errores importantes de un departamento poco frecuente?
- ¿Qué consecuencias tiene perder una intención secundaria de un mensaje?
- ¿Cuál es el costo empresarial de una falsa urgencia frente a una urgencia omitida?
- Si dos anotadores discrepan, ¿quién determina la etiqueta de referencia?
- ¿Se puede evaluar confiablemente un modelo con 20 mensajes? ¿Qué falta?

### Entregable

`respuestas_estudiante.csv` completo y un texto de 150–250 palabras con al menos dos casos ambiguos, los desacuerdos, las métricas obtenidas y una propuesta de mejora de las reglas de anotación.
