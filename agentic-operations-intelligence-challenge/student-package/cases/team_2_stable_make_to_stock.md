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
