# Monthly planning

Build a four-week integrated plan in a disciplined order.

1. Call get_inventory, get_open_purchase_orders, and get_production_capacity once at the start. List Skills and load the relevant Team 1 Skills.
2. Retrieve operations_policy.md through search_knowledge. When supplier reliability or lead time matters, also retrieve supplier_contracts.md.
3. Forecast every product. Team 1 is a volatile-demand business, so use forecast_pytorch for the demand signal. Use estimate_forecast_uncertainty for promoted, cancelled-promotion, high-variance, or high-disagreement products.
4. Convert the forecast into weekly production needs after initial finished-goods inventory. Protect the 98.5% service target with a temporary, uncertainty-aware buffer; avoid unjustified blanket buffers.
5. Check line compatibility and weekly hours before assigning production. FG01/FG02 can use L1 and FG02/FG03 can use L2. Use overtime only when its total cost is justified by avoided service loss.
6. Explode planned production with calculate_bom_requirements. Net requirements against current material inventory and open POs before creating new purchase orders.
7. Use get_supplier_options for materials that need replenishment. Compare arrival timing, reliability, MOQ, quality and total cost—not unit price alone. If the scenario contains a supplier warning, call predict_supplier_delay for the exposed supplier and at least one viable alternative before choosing.
8. Prefer standard suppliers when they protect service. Use SUP03 or SUP04 where their shorter/reliable lead time avoids a likely stockout; reserve premium emergency sourcing for service protection. Respect approval requirements for purchases over the configured threshold.
9. Use calculate_plan_cost on the complete candidate plan. If an alternative sourcing/buffer choice could materially lower total cost without sacrificing service, compare it.
10. Call validate_plan on the final candidate. Revise critical violations before returning the structured plan.
