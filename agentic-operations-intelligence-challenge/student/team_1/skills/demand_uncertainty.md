# Demand uncertainty

Use this procedure whenever demand is volatile, a promotion starts or is cancelled, confirmed orders disagree with the statistical signal, or recent variance is high.

1. Retrieve the volatile-demand operations policy with search_knowledge before selecting a buffer.
2. Use forecast_pytorch for the affected product and estimate_forecast_uncertainty. Treat confirmed orders as evidence, not as the complete forecast.
3. Compare the trained forecast with a simple seasonal or moving-average reference only when it adds information; do not repeat identical tool calls.
4. If uncertainty is material, quantify a temporary safety buffer with calculate_safety_stock. Because lost sales and stockouts are expensive in this case, protect the 98.5% service target, but do not carry a permanent promotion buffer after the event.
5. For a promotion cancellation or weak confirmed-order signal, reduce production rather than mechanically extending the previous high-demand level.
6. Do not use calculate_jit_requirement for ordinary Team 1 demand planning; volatile demand needs an uncertainty-aware buffer rather than a zero-buffer JIT assumption.
7. Before finalizing, use calculate_plan_cost and validate_plan and revise any critical capacity, material, MOQ, supplier, or approval violation.
