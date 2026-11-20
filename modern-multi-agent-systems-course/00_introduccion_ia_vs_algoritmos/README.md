# Módulo 0 — De algoritmos a inteligencia artificial

**Público:** estudiantes sin formación profunda en IA. **Duración sugerida:** 100–120 min.

## Pregunta central

> Si podemos escribir un algoritmo para resolver un problema, ¿qué aporta una IA?

El mismo problema se aborda mediante reglas, aprendizaje automático, representaciones semánticas (embeddings) y un modelo generativo. Después conectamos la decisión con una acción controlada para introducir el concepto de agente.

## Objetivos

1. Diferenciar algoritmo, aprendizaje automático, LLM y agente.
2. Distinguir entre codificar instrucciones y aprender patrones a partir de ejemplos.
3. Identificar casos donde es mejor NO usar IA.
4. Comparar calidad, costo, latencia, privacidad, explicación y necesidad de datos.
5. Entender que **LLM ≠ agente** y **un agente ≠ necesariamente varios agentes**.

## Secuencia de clase

| Minutos | Actividad |
|---|---|
| 0–10 | Presentar el reto sin revelar las soluciones |
| 10–25 | Equipos escriben reglas en pseudocódigo |
| 25–40 | Ejecutar reglas y descubrir excepciones |
| 40–55 | Entrenar clasificador supervisado |
| 55–70 | Mostrar embeddings y similitud semántica (opcional) |
| 70–85 | Probar un LLM local (opcional) y discutir límites |
| 85–100 | Convertir clasificación en una acción con validación |
| 100–120 | Comparación, debate y conexión con sistemas multiagentes |

## Archivos

- [ENUNCIADO_ESTUDIANTES.md](ENUNCIADO_ESTUDIANTES.md): tarea previa a la solución.
- [GUIA_DOCENTE.md](GUIA_DOCENTE.md): tiempos, preguntas y resultados esperados.
- [datos.py](datos.py): 40 mensajes de entrenamiento y 16 de prueba, separados.
- [reglas.py](reglas.py): solución programada explícitamente, sin IA.
- [ml_supervisado.py](ml_supervisado.py): TF-IDF + regresión logística.
- [embeddings.py](embeddings.py): representaciones semánticas preentrenadas.
- [llm_local.py](llm_local.py): clasificación mediante un LLM opcional en Ollama.
- [agente.py](agente.py): usa una decisión para ejecutar una herramienta simulada con control.
- [comparar.py](comparar.py): mismo conjunto de evaluación.
- [test_basico.py](test_basico.py): comprobaciones sin modelos externos.
- [presentacion_intro_ia.pptx](presentacion_intro_ia.pptx): presentación animada en español.
- [build_slides.py](build_slides.py): fuente reproducible de la presentación.

## Ejecutar (desde esta carpeta)

Sin instalar nada:

    python reglas.py
    python comparar.py --metodos reglas
    python agente.py --texto "No puedo entrar a mi cuenta"

Con aprendizaje supervisado (rápido y local):

    python -m pip install -r requirements.txt
    python ml_supervisado.py
    python comparar.py --metodos reglas ml

Con embeddings reales, de forma opcional:

    python -m pip install sentence-transformers
    python embeddings.py
    python comparar.py --metodos reglas ml embeddings

La primera ejecución de embeddings descarga un modelo multilingüe; después se puede usar desde caché. No es necesario enseñar sus matemáticas durante el primer encuentro.

Con un LLM local opcional: instalar Ollama por separado, ejecutar el servicio y descargar previamente un modelo de instrucciones (por ejemplo, **qwen2.5:1.5b**):

    ollama pull qwen2.5:1.5b
    python llm_local.py --texto "Me cobraron dos veces"

Se requiere hardware apropiado para el modelo. No se necesita una API de pago. Ollama no está incluido en requirements.txt.

Ejecutar pruebas básicas:

    python -m unittest test_basico.py -v

## Criterios de comparación

**Exactitud en 16 ejemplos no vistos** es una señal didáctica, no un benchmark representativo. También deben medirse errores por categoría, cobertura, latencia y carga operativa. No se garantiza que el método de IA obtenga mayor exactitud; esa es precisamente una hipótesis para contrastar.

## Enlace con el resto del curso

**Algoritmo → Modelo ML → LLM → Agente (objetivos + estado + herramientas + políticas) → Sistemas multiagentes (coordinación entre agentes).**

Continuar con ../01_agent_foundations_and_llm_integration/README.md.

## Presentación

Las diapositivas tienen transiciones de PowerPoint (fundidos y desplazamientos) y revelaciones progresivas construidas mediante diapositivas sucesivas; funcionan sin macros. Para regenerar:

    python -m pip install python-pptx
    python build_slides.py

Nota: una transición entre diapositivas no es lo mismo que una animación independiente de objetos. Esta versión se centra en efectos reproducibles y compatibles.
