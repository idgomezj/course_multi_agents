# Equipo 2 — Stable Make-to-Stock

## Contexto

La planta produce referencias maduras con demanda estable. La empresa tiene costos elevados de almacenamiento y capital inmovilizado.

## Objetivo

Cumplir el servicio con un plan simple, estable y económico, evitando sobreproducción y compras innecesarias.

## Modelos PyTorch

### A. Stable Demand Forecast
Forecast de cuatro semanas. El reto no es usar el modelo más complejo, sino evitar sobreajuste al ruido.

### B. Excess Inventory Risk
Predice riesgo de terminar el horizonte con inventario excesivo.

## Estructura de costos dominante

- holding inventory: **alto**;
- working capital: **muy alto**;
- warehouse utilization: **alto**;
- stockout: **medio**;
- expedite: **bajo/medio**.

## RAG

- inventory targets;
- warehouse capacity;
- working-capital policy;
- reorder rules;
- purchasing agreements.

## Skills

- lean monthly planning;
- excess inventory prevention;
- economic replenishment;
- plan validation.

## Familias de escenarios

- demanda estable;
- ruido aleatorio;
- demanda ligeramente descendente;
- exceso de inventario;
- open PO innecesario;
- MOQ vs inventory cost;
- descuento por volumen vs working capital.

## Qué hace este caso distinto

Una arquitectura o Skill diseñada para “protegerse” comprando buffer puede ser económicamente muy mala.

## Evidencia para entrenamiento

El equipo obtiene mediante `GET /v1/teams/team_2/training-source.json` la historia cruda **en JSON** de demanda, posición de inventario, recibos y costo de almacenamiento. Este endpoint requiere el token asignado a Team 2.

No existe un dataset supervisado listo. El equipo debe crear ventanas de forecast y definir/documentar el target de riesgo de exceso de inventario a partir de los resultados reales posteriores. La construcción debe reflejar el contexto estable del caso y evitar fabricar volatilidad artificial que no existe en la operación.

