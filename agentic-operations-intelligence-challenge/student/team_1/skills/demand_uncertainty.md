# Demand uncertainty handling

Use this skill whenever demand is volatile, a promotion/event is active, confirmed
orders disagree with recent history, or the forecast tools disagree.

## Evidence first

Retrieve the organizational evidence that can change the decision. Prefer focused
queries rather than one vague query:

- `service level policy safety stock stockout`
- `promotion policy forecast override cancellation`
- `forecast override rules confirmed orders`
- `customer priority agreements service`
- `safety stock policy demand uncertainty`

Do not invent policy thresholds.

## Forecast workflow

For every product affected by the scenario:

1. Call `forecast_pytorch(product_id)` as the primary four-week forecast.
2. Call `estimate_forecast_uncertainty(product_id)`.
3. If uncertainty is moderate/high, promotion is active, confirmed orders conflict
   with history, or the scenario explicitly describes a spike/drop/cancellation,
   compare with `forecast_exponential_smoothing`, `forecast_seasonal`, and when
   useful `forecast_moving_average`.
4. Do not mechanically average forecasts. Use the policy evidence, confirmed orders,
   promotion state, and uncertainty to decide which signal deserves more weight.

Interpret the trained uncertainty score as a bounded forecast-error risk:
- below about 0.10: relatively low;
- around 0.10–0.18: material uncertainty;
- above about 0.18: high uncertainty and a strong reason to protect service.

These are planning heuristics, not policy limits.

## Buffer discipline

Lost sales are expensive in Team 1, but excess inventory still has a cost.

- Use `calculate_safety_stock` when uncertainty is material.
- Prefer a targeted buffer for the exposed product/week instead of inflating all
  four weeks.
- For a confirmed promotion/spike, protect the early weeks first.
- For promotion cancellation or a sudden drop, remove obsolete buffer quickly and
  avoid carrying the old peak forecast through the month.
- When confirmed orders are already strong, treat them as a demand floor unless
  policy evidence says otherwise.

Always pass the final candidate through `calculate_plan_cost` and `validate_plan`.
Revise critical violations before returning the plan.
