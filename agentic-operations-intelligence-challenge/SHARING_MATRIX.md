# Qué compartir y qué NO compartir

Esta página es la fuente de verdad de la frontera profesor/estudiante.

## Compartir con estudiantes

### Plataforma
- frontend;
- cliente/backend necesario para ejecutar la solución;
- Manager Agent ya implementado;
- integración Pydantic AI;
- wrappers de tools;
- interfaces de los modelos PyTorch;
- loader de RAG;
- loader de Skills;
- schemas de entrada/salida;
- documentación completa de la toolbox.

### Por equipo
Cada equipo recibe **solo su paquete de caso**:
- descripción del negocio;
- objetivo operacional;
- datasets de entrenamiento;
- dataset de validación público, si aplica;
- documentos empresariales para RAG;
- Skills baseline deliberadamente incompletas;
- modelos/notebooks baseline;
- parámetros y reglas que el negocio realmente conocería;
- acceso al cost tool;
- escenarios públicos de desarrollo;
- resultados baseline;
- URL/credencial del evaluador público de su equipo.

### Evaluación visible
Se puede compartir:
- rúbrica;
- categorías evaluadas;
- restricciones duras conocidas;
- métricas de modelos;
- definición del costo total;
- forma general de calcular el score;
- ejemplos de errores y traces del servidor público.

## NO compartir con estudiantes

Nunca distribuir:
- hidden scenarios finales;
- seeds del generador hidden;
- holdout dataset final de PyTorch;
- hidden RAG queries;
- expected document/chunk IDs de hidden tests;
- secuencias esperadas de tools;
- respuestas de referencia;
- planes benchmark;
- costos benchmark por escenario;
- código del final evaluator si permite deducir los tests;
- realizaciones futuras usadas por el simulador final;
- team secret keys;
- credenciales del backend final;
- logs de evaluación de otros grupos;
- archivos de entrega de otros grupos.

## Qué puede estar en este repositorio público

Sí:
- especificaciones;
- contratos;
- casos públicos;
- tool catalog;
- templates;
- public evaluator client;
- starter notebooks;
- Skills baseline;
- documentos RAG que se entregarán a los alumnos.

No:
- cualquier activo que permita reconstruir la evaluación final.

## Recomendación operativa

Mantener dos superficies:

```text
PUBLIC / STUDENT
course_multi_agents/
  agentic-operations-intelligence-challenge/

PRIVATE / INSTRUCTOR
agentic-ops-evaluator-private/
  hidden/
  holdout/
  oracle/
  seeds/
  final_evaluator/
  credentials/
```

El repositorio privado puede ser un repo privado de GitHub o, preferiblemente, el código/data del backend final sin acceso directo de estudiantes.
