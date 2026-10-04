# Equipo 4 — Unreliable Supply Network

## Contexto

La planta compra materiales críticos a una red de proveedores con lead times largos, retrasos, problemas de calidad y riesgo de interrupción.

## Objetivo

Mantener continuidad de producción y servicio seleccionando proveedores y buffers económicamente razonables.

## Modelos PyTorch

### A. Supplier Delay
Predice probabilidad de retraso.

### B. Supplier Quality Risk
Predice probabilidad de rechazo/falla de calidad.

## Estructura de costos dominante

- supplier failure: **muy alto**;
- quality failure: **muy alto**;
- line shutdown: **extremadamente alto**;
- expedite: **alto**;
- holding: **bajo/medio**.

## RAG

- supplier contracts;
- approved supplier list;
- quality clauses;
- MOQ;
- dual-sourcing rules;
- emergency procurement;
- material criticality policy.

## Skills

- supplier disruption;
- alternative sourcing;
- supplier comparison;
- emergency procurement;
- risk-adjusted inventory.

## Familias de escenarios

- retraso;
- cancelación;
- calidad deficiente;
- proveedor alternativo caro;
- proveedor no autorizado;
- dual sourcing;
- expedite vs buffer;
- fallas simultáneas.

## Qué hace este caso distinto

Aquí mantener inventario puede ser racional: la ausencia de buffer puede costar mucho más que almacenarlo.

## Evidencia para entrenamiento

El equipo obtiene mediante `GET /v1/teams/team_4/training-source.json` datos crudos **en JSON** con historial de órdenes, entregas y resultados de inspección de calidad. Este endpoint requiere el token asignado a Team 4; no existe un `raw_case_history.csv` local suministrado.

El equipo debe construir por sí mismo los datasets de supplier-delay y supplier-quality, incluyendo labels derivados de resultados reales. Los outcomes de llegada/rechazo no pueden utilizarse como features conocidos antes de la recepción.

