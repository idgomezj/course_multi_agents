# Catálogo común de Tools

Todos los equipos reciben la misma toolbox. **Que una tool exista no significa que sea apropiada para su caso.** Parte del reto consiste en enseñar al Manager a seleccionar las capacidades correctas.

## Forecasting
- `forecast_moving_average()`
- `forecast_exponential_smoothing()`
- `forecast_seasonal()`
- `forecast_pytorch()`
- `estimate_forecast_uncertainty()`

## Inventory
- `get_inventory()`
- `get_open_purchase_orders()`
- `calculate_inventory_projection()`
- `calculate_safety_stock()`
- `calculate_reorder_point()`
- `calculate_jit_requirement()`

## Materials
- `get_bom()`
- `calculate_bom_requirements()`
- `validate_material_availability()`

## Supply
- `get_supplier_options()`
- `predict_supplier_delay()`
- `predict_supplier_quality()`
- `predict_arrival_time()`
- `find_alternative_supplier()`
- `calculate_expedite_option()`

## Production
- `get_production_capacity()`
- `predict_downtime()`
- `predict_production_feasibility()`
- `calculate_changeover_cost()`
- `calculate_overtime_option()`
- `optimize_production_plan()`

## Cost
- `calculate_purchase_cost()`
- `calculate_holding_cost()`
- `calculate_stockout_cost()`
- `calculate_working_capital_cost()`
- `calculate_plan_cost()`

## Validation
- `validate_capacity()`
- `validate_inventory_policy()`
- `validate_supplier_policy()`
- `validate_approvals()`
- `validate_plan()`

## Regla de diseño

Una Skill que llama todas las tools no es una buena Skill. Los tests pueden penalizar llamadas irrelevantes o repetidas. La selección debe estar justificada por el contexto operacional.
