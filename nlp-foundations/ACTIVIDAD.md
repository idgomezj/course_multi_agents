# Actividad de NLP: primero interpreta la persona, después el programa

**Modalidad:** participación en parejas y discusión guiada. **Sin calificaciones automáticas.**

## El problema

Una empresa recibe mensajes de clientes. Una sola solicitud puede contener **varios problemas**. Queremos distinguir intenciones, información concreta, urgencia e incertidumbre antes de elegir una tecnología de IA.

## Paso 1 — clasificación manual

Lee el mensaje proyectado. Antes de que el profesor muestre el programa, escribe:

| Campo | Qué debes indicar |
|---|---|
| Intenciones | ACCESO, FACTURACION, SOPORTE_TECNICO, ENVIOS; pueden ser varias |
| Pedido | El identificador explícito tras «pedido» u «orden», o vacío |
| Urgencia | SI solo si la urgencia o plazo inmediato se expresa claramente |
| Revisión | SI cuando no hay datos suficientes para decidir |
| OTRO | Tema claramente fuera de los cuatro departamentos |

**Ejemplo para discutir:**

> «Me cobraron dos veces el pedido 4582, todavía no llega y necesito solución urgente».

## Paso 2 — prueba en clase

El profesor mostrará el resultado de `demo_nlp.py`. Antes de cada revelación, voten y justifiquen sus respuestas.

**Casos recomendados:**

- «No puedo iniciar sesión y tampoco puedo ver mis facturas».
- «El banco no funciona».
- «La página falla y no puedo completar el pago».
- «Quiero conocer el horario de atención».
- «El enlace de seguimiento no carga y mi pedido 8821 no aparece».

## Paso 3 — desafiar al programa

Propongan en parejas mensajes **nuevos**, que no aparezcan en los veinte casos del archivo. El profesor los enviará a `demo_nlp.py --mensaje "..." `. ¿El programa identifica lo mismo que el grupo? ¿Qué información omitió? ¿Cuándo conviene pedir aclaración?

## Debate final

1. ¿Por qué podría haber más de una intención?
2. ¿Cuál es la diferencia entre `OTRO` y `REVISAR`?
3. ¿Una frase molesta es necesariamente urgente?
4. ¿El programa interpreta el significado o encuentra expresiones previstas?
5. ¿Qué tecnología usaríamos para aprender patrones a partir de ejemplos?

**Material:** `datos/mensajes.csv` y, opcionalmente, `crear_plantilla.py` para tener los mensajes en una tabla que el estudiante completa a mano. No se utiliza `evaluar.py` ni se califica automáticamente.

**Entregable opcional:** una lista de dos casos donde el programa coincidió con los estudiantes y uno donde su respuesta fue discutible, con explicación de por qué.
