# Equipo 1 — Volatile Demand

## Contexto

La planta fabrica productos de consumo con demanda sensible a promociones, estacionalidad, precio y eventos comerciales. El costo de quedarse sin producto es alto.

## Objetivo

Crear un plan mensual que mantenga un alto nivel de servicio sin reaccionar de forma excesiva al ruido y sin generar inventario innecesario.

## Modelos PyTorch

### A. Demand Forecast
Predice demanda por producto para las próximas cuatro semanas.

Variables disponibles pueden incluir:
- historia de ventas;
- semana/mes;
- promociones;
- precio;
- órdenes confirmadas;
- tendencia reciente;
- variables comerciales proporcionadas.

### B. Demand Uncertainty
Estima el riesgo/incertidumbre asociado al forecast.

No basta con acertar el promedio: el Manager debe saber cuándo el forecast es poco confiable.

## Estructura de costos dominante

Prioridades relativas:
- lost sales / stockout: **muy alto**;
- emergency procurement: **alto**;
- holding inventory: **medio**;
- overproduction: **medio**.

Los valores concretos son accesibles mediante la cost tool.

## RAG

Documentos típicos:
- service-level policy;
- promotion policy;
- forecast override rules;
- safety-stock policy;
- customer-priority agreements.

## Skills a desarrollar

Ejemplos:
- demand-spike management;
- forecast uncertainty handling;
- monthly demand planning;
- production replanning.

## Familias de escenarios públicos

- estacionalidad;
- promoción;
- cancelación de promoción;
- spike inesperado;
- caída repentina;
- forecast vs confirmed orders;
- alta incertidumbre.

## Qué hace este caso distinto

Una solución que siempre minimiza inventario puede destruir nivel de servicio. El equipo debe aprender cuándo vale la pena pagar por buffer.

## Evidencia para entrenamiento

El equipo recibe `student/team_1/training/raw_case_history.csv`, un historial semanal **crudo** de demanda, promociones, precio, órdenes confirmadas, estacionalidad y eventos comerciales.

No se entregan filas listas para entrenamiento ni targets calculados. El equipo debe construir ventanas temporales, derivar los features exigidos por `model_contract.json`, crear los targets de las cuatro semanas futuras y definir/documentar una medida razonable de incertidumbre usando resultados posteriores. Debe evitar leakage temporal.

