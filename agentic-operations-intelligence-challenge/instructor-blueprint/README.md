# Instructor Blueprint

Este directorio define **su parte** del proyecto. No contiene hidden tests reales.

## Lo que usted construye y mantiene

### Plataforma compartida
- Manager Agent con Pydantic AI;
- conexión al LLM;
- frontend;
- backend;
- toolbox;
- wrappers que cargan modelos PyTorch del estudiante;
- motor RAG configurable;
- loader de Skills;
- optimizer/tooling determinístico;
- output estructurado;
- logging/tracing.

### Evaluación
- public evaluator;
- final evaluator privado;
- simulator;
- constraint validator;
- cost engine;
- benchmark/oracle;
- datasets de entrenamiento por caso;
- holdouts privados;
- documentos RAG por caso;
- scenario generators;
- hidden seeds;
- score aggregation.

### Diseño docente
- asignar un caso por grupo;
- equilibrar dificultad;
- establecer baseline de cada caso;
- verificar que ninguna familia tenga una solución trivial;
- revisar que las tools “distractoras” sean plausibles;
- realizar defensa oral y live challenge.

## Lo que construyen los estudiantes

Solo:
- PyTorch models;
- RAG;
- Skills.

## Recomendación

No implementar cinco aplicaciones. Implementar **una plataforma parametrizada por `team_id/case_id`**.

```text
same app
same Manager
same toolbox
same schemas
same simulator framework
        ↓
case configuration
        ↓
different data + documents + costs + scenario family
```
