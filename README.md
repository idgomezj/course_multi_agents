# Curso de Inteligencia Artificial y Sistemas Multiagentes

Material docente organizado en rutas complementarias. No todas son requisitos secuenciales.

## Ruta recomendada (grupo que comienza en IA)

1. [Introducción: problema de clasificación](introduction/actividad.md) — reglas frente a aprendizaje supervisado.
2. [Fundamentos de NLP](nlp-foundations/README.md) ([tres ejemplos ejecutables](nlp-foundations/README_TRES_ENFOQUES.md)) — tareas, ambigüedad, clasificación manual, entidades y comparación en vivo con un programa (**sin entrenar un LLM**).
3. [Laboratorios de modelos de lenguaje](llm-lab/) — 01 Bigram, 02 Contexto, 03 Attention, 04 Transformer, 05 modelo preentrenado; 06–08 fine-tuning, LoRA y QLoRA como profundización opcional.
4. [Curso principal de sistemas multiagentes modernos](modern-multi-agent-systems-course/) — 4 módulos de fundamentos, herramientas, confiabilidad y colaboración entre agentes.
5. [Case 0 — ejemplo completo resuelto](course-agentic-api/demo_case_0_solution/).
6. [Reto final por equipos](agentic-operations-intelligence-challenge/student-package/README.md).

## Rutas complementarias

- [Sistemas multiagentes: fundamentos académicos](sistemas-multiagentes-course/) — IAD, arquitecturas, negociación/Contract Net y metodologías GAIA, MaSE y MAS-CommonKADS.
- [Pydantic AI Lab](pydantic-ai-lab/) — experimentos técnicos cortos sobre LLM, tools, RAG, workflows y multiagentes, parcialmente solapados con el curso moderno.

## Plataforma del proyecto final

- [Challenge](agentic-operations-intelligence-challenge/) — aplicación, espacio de estudiantes, simulación y evaluación pública.
- [Data API](course-agentic-api/) — datos, casos y escenarios servidos por FastAPI; incluye Case 0.
- [Validación técnica](scripts/) y [workflows](.github/workflows/) — automatización y mantenimiento, no módulos de clase.

**Separación curricular:** la introducción responde «¿cómo resolver/clasificar?», NLP responde «¿qué significa interpretar un texto y contrastarlo con un programa?», llm-lab responde «¿cómo funciona y se adapta un modelo de lenguaje?» y los módulos de SMA responden «¿cómo un agente decide, actúa y coopera?».

**Nota de seguridad docente:** no publicar datos privados de evaluación ni credenciales reales en un repositorio visible a los estudiantes.
