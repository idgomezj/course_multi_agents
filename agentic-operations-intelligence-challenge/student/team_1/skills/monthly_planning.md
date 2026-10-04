# Monthly volatile-demand planning

Use this skill to build the complete four-week Team 1 production and procurement
plan. The objective is high service at the lowest feasible total cost, not minimum
inventory in isolation.

## Required planning sequence

1. Inspect state once:
   - `get_inventory`
   - `get_open_purchase_orders`
   - `get_production_capacity`
2. Retrieve relevant policies with `search_knowledge`, especially service level,
   promotion/override, safety-stock, and customer-priority evidence.
3. For each product:
   - `forecast_pytorch`
   - `estimate_forecast_uncertainty`
   - compare classical forecasts only when volatility/uncertainty makes comparison useful.
4. Convert the chosen weekly demand plan into production quantities. Account for
   starting finished goods and avoid producing demand already covered by inventory.
5. Use `optimize_production_plan` as a feasibility helper when assigning line/week
   quantities. Do not treat it as the final business decision.
6. For planned production, explode requirements with
   `calculate_bom_requirements(product_id, quantity)`.
7. Net raw-material needs against:
   - current material inventory;
   - open purchase orders arriving before need;
   - projected weekly consumption/receipts (`calculate_inventory_projection`).
8. Only for remaining shortages, use `get_supplier_options`. Respect authorized
   suppliers, lead times and MOQ. Do not create a new PO for supply already covered
   by on-hand inventory or an open PO.
9. If uncertainty justifies a buffer, size it with `calculate_safety_stock` rather
   than arbitrary percentages.
10. Build one complete candidate `MonthlyOperationsPlan`, then call:
    - `calculate_plan_cost`
    - `validate_plan`
11. If validation reports a critical violation, revise only what is necessary and
    re-run cost/validation on the revised complete plan.

## Cost discipline

Team 1's dominant trade-off is stockout/lost-sales risk versus holding and
overproduction. Avoid emergency procurement when normal supply can arrive in time.
Do not choose a supplier from unit price alone when lead time or reliability would
create a service failure.

## Tool efficiency

Repeated calls with different product/material inputs are normal. Avoid exact
duplicate calls with the same inputs. Do not call unrelated JIT, downtime, quality,
or supplier-risk tools unless the scenario/evidence actually makes them relevant.
