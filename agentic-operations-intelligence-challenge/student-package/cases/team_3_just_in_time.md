# Equipo 3 — Just-in-Time

## Contexto

La planta opera con inventarios extremadamente bajos y entregas frecuentes. El inventario excesivo es costoso, pero una entrega tardía puede detener la línea.

## Objetivo

Sincronizar abastecimiento y producción para minimizar inventario sin aumentar de forma inaceptable el riesgo de line stop.

## Modelos PyTorch

### A. Supplier Delay
Predice probabilidad de retraso para una orden/proveedor/material.

### B. Arrival-Time Prediction
Predice tiempo/fecha probable de llegada.

La media del lead time no es suficiente: la variabilidad es esencial.

## Estructura de costos dominante

- excess inventory: **muy alto**;
- holding: **muy alto**;
- line stop: **extremadamente alto**;
- late material: **extremadamente alto**;
- expedited freight: **alto**.

## RAG

- JIT inventory policy;
- delivery windows;
- supplier service agreements;
- line-stop escalation;
- emergency sourcing;
- production synchronization rules.

## Skills

- JIT replenishment;
- delivery-risk handling;
- micro-buffer decision;
- production/material synchronization.

## Familias de escenarios

- entrega temprana;
- entrega tardía;
- PO en tránsito;
- proveedor barato pero variable;
- cambio de fecha de producción;
- micro-buffer vs line-stop risk;
- múltiples entregas pequeñas.

## Qué hace este caso distinto

La decisión óptima depende fuertemente del timing. “Comprar más por seguridad” y “elegir el proveedor más barato” suelen ser malas heurísticas.

## Evidencia para entrenamiento

El equipo recibe `student/team_3/training/raw_case_history.csv`, con órdenes históricas, cantidades, cantidades típicas, fechas de orden/necesidad, lead time nominal y realizado, confiabilidad, tardanzas recientes y riesgo estacional.

El equipo debe derivar variables como `order_qty_ratio` y urgencia, y construir los targets de retraso y tiempo de llegada usando los resultados realizados. El lead time realizado es outcome y no puede filtrarse como input del mismo ejemplo.

