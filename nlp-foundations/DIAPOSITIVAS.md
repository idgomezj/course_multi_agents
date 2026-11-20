# Diapositivas — Introducción a NLP (75 min)

> Guion para proyectar o convertir a presentación; no reemplaza `GUIA_DOCENTE.md`.

## 1. El problema ya no es solamente clasificar
- Antes: un mensaje → un departamento.
- Ahora: un mensaje puede pedir dos acciones.
- Pregunta: ¿qué información necesita realmente una organización?

## 2. ¿Qué es NLP?
- Área de IA y computación que estudia técnicas para procesar el lenguaje humano.
- No equivale a LLM; existen métodos basados en reglas, estadísticos y neuronales.
- Ejemplos: correo, atención al cliente, informes, contratos.

## 3. Varias tareas sobre un único texto
«Me cobraron dos veces el pedido 4582, todavía no llega y necesito solución urgente».
- Intenciones: facturación + envíos.
- Entidad: pedido 4582.
- Urgencia: explícita.
- Resumen: cobro duplicado y entrega pendiente.

## 4. Clasificación simple frente a clasificación multilabel
- Un departamento obligatorio puede perder información.
- Dos departamentos pueden corresponder al mismo caso.
- Pregunta: ¿cómo enviamos una solicitud a más de un equipo?

## 5. Extracción de entidades
- La entidad debe aparecer en el mensaje.
- `pedido_id = 4582`, no adivinar identificadores.
- Diferenciar extracción de interpretación.

## 6. Ambigüedad
- «El banco no funciona».
- «Mi problema es con el sistema».
- Diferenciar evidencia insuficiente de un mensaje claramente fuera de dominio.

## 7. El diseño de etiquetas es parte del problema
- Definiciones claras y casos límite.
- `ACCESO`, `FACTURACION`, `SOPORTE_TECNICO`, `ENVIOS`.
- `OTRO` y `REVISAR` son distintos.
- Dos personas pueden discrepar: hace falta consenso.

## 8. ¿Qué medimos?
- Exact match: todas las intenciones correctas.
- Precision: ¿qué proporción de etiquetas predichas era pertinente?
- Recall: ¿qué proporción de etiquetas reales detectamos?
- F1: balance entre precision y recall.

## 9. Ejercicio en parejas
- Anotar los 20 mensajes del CSV.
- Comparar dos decisiones discutibles.
- Ejecutar el evaluador y comentar los errores.

## 10. Transición a llm-lab
- Sabemos qué tareas buscamos resolver y cómo evaluar.
- Aún no hemos construido un modelo de lenguaje.
- Pregunta final: ¿cómo aprende un modelo a producir predicciones a partir de texto?
