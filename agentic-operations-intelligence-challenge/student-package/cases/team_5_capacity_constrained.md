# Equipo 5 — Capacity-Constrained Plant

## Contexto

La planta tiene demanda razonablemente predecible y materiales disponibles, pero opera cerca de su capacidad. Downtime, changeovers y overtime determinan la viabilidad.

## Objetivo

Construir un plan mensual factible que cumpla servicio minimizando overtime, changeovers, outsourcing y pérdidas por downtime.

## Modelos PyTorch

### A. Downtime Risk
Predice probabilidad/riesgo de falla por equipo o línea.

### B. Production Feasibility
Predice probabilidad de completar un plan propuesto dentro de la ventana disponible.

## Estructura de costos dominante

- downtime: **muy alto**;
- late delivery: **muy alto**;
- overtime: **alto**;
- changeover: **alto**;
- outsourcing: **medio/alto**;
- holding inventory: **bajo**.

## RAG

- maintenance rules;
- line/product compatibility;
- overtime policy;
- labor constraints;
- customer priority;
- outsourcing policy.

## Skills

- capacity shortage;
- line reallocation;
- maintenance disruption;
- production replanning;
- overtime vs outsourcing.

## Familias de escenarios

- machine downtime;
- capacity overload;
- overtime;
- changeover;
- line incompatibility;
- labor shortage;
- preventive maintenance;
- simultaneous failures.

## Qué hace este caso distinto

Tener material no garantiza servicio. La decisión dominante es cómo usar capacidad escasa y costosa.

## Evidencia para entrenamiento

El equipo obtiene mediante `GET /v1/teams/team_5/training-source.json` datos crudos **en JSON** con corridas históricas de línea, utilización, mantenimiento, carga planificada, capacidad, changeovers, disponibilidad de overtime/labor y resultados reales de downtime/completitud. Este endpoint requiere el token asignado a Team 5; no existe un `raw_case_history.csv` local suministrado.

El equipo debe derivar los targets de downtime y production feasibility, y construir los features requeridos sin usar outcomes futuros como inputs.

