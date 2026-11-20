# Guía del docente — Módulo 0

## Mensaje didáctico

**La revolución no consiste en que los algoritmos desaparezcan.** Consiste en combinar reglas y cálculo explícito con modelos capaces de generalizar patrones, interpretar lenguaje e interactuar con herramientas. Ese cambio permite automatizar tareas antes difíciles de formalizar, pero introduce errores, costos, privacidad y control que debemos administrar.

Evitar afirmaciones absolutas del tipo «la IA piensa como una persona», «siempre es más precisa», «se enseña sola» o «un LLM es un agente».

## Preparación (antes de clase)

1. Tener Python 3.10+.
2. La práctica de reglas funciona con la biblioteca estándar.
3. Instalar scikit-learn solo si se va a ejecutar ML.
4. Los embeddings descargan un modelo la primera vez y el LLM requiere Ollama y un modelo local; preparar antes de clase o usar captura.
5. Abrir la presentación en PowerPoint para ver efectos de transición. PDF y visores web pueden eliminar esos efectos.

## Guion del instructor

**0–10 min:** abrir con «¿Podemos clasificar mensajes si no sabemos todas las formas de pedir ayuda?». Enseñar cuatro categorías y ocultar el código.

**10–25 min:** grupos crean reglas. La dinámica debe exhibir el costo de mantener condiciones cuando cambia el lenguaje.

**25–40 min:** ejecutar reglas.py, comparar sobre la misma prueba, señalar fallos y cómo mejoraría un sistema de reglas.

**40–55 min:** explicar «entrenamiento vs inferencia» usando tarjetas. Un ejemplo etiquetado produce evidencia para un patrón, no una instrucción individual; ejecutar ml_supervisado.py.

**55–70 min (opcional):** embeddings convierten textos a vectores reutilizables; similitud no equivale a veracidad. Atención a la descarga y al idioma.

**70–85 min (opcional):** LLM preentrenado permite clasificar a partir de instrucciones y ejemplos. No tiene acceso automático a cuentas reales. Mostrar salida estructurada y validación de categoría.

**85–100 min:** agente.py: una decisión se conecta con una acción simulada, con política de autorización y registro. **No se envía ningún ticket real**.

**100–120 min:** reunir predicciones, latencia, costo, mantenimiento, sesgos, privacidad y necesidad de un humano. Cierre: reconocer cuándo usar reglas, IA y flujos híbridos.

## Distinciones cruciales

- **Todo modelo ML ejecuta algoritmos;** la oposición es entre **reglas codificadas manualmente** y **parámetros aprendidos de datos**.
- TF-IDF + regresión logística es un modelo de ML, aunque no un LLM.
- Embeddings y LLM son alternativas basadas en modelos preentrenados y tienen costos distintos.
- Un **modelo** predice; un **agente** observa, decide y puede ejecutar herramientas bajo reglas.
- Un **sistema multiagente** agrega coordinación entre agentes; no surge por tener varios prompts.
- Medir sobre un conjunto pequeño solo sirve para la clase; no sacar conclusiones científicas amplias.

## Preguntas que suelen activar la discusión

- ¿Qué pasa si alguien escribe «No me entregaron la factura»? Hay señales de dos categorías.
- ¿Qué es peor: equivocarse al clasificar o ejecutar una acción sin autorización?
- Si cambiamos la palabra «contraseña» por «credenciales», ¿cómo afecta a cada método?
- ¿Cuándo sería más responsable una solución híbrida?
- ¿Por qué los modelos pueden producir respuestas convincentes e incorrectas?

## Conexión con módulo 1

La práctica muestra un ciclo **observar → decidir → validar → actuar**. El módulo siguiente formaliza roles, objetivos, estado, capacidades, políticas, memoria, herramientas y orquestación de agentes.
