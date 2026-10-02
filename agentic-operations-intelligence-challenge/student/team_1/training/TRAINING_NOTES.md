# Team 1 model-development notes

## Cleaning
- Normalize product identifiers by trimming whitespace and upper-casing.
- Collapse duplicate product/week rows by keeping the first non-null value for each field.
- Keep the time order within each product.
- Forward-fill only planning variables that are observable at the forecast origin (price index, confirmed orders, seasonal index).
- For a missing historical demand value used only inside a lag window, use the mean of the previous four observed values. Never impute target demand.
- Skip any supervised example whose four future target weeks contain missing realized demand.

## Model A dataset
Each example is formed at the end of week t. Features use demand from t-3..t plus planning information available for t+1. Targets are actual demand for t+1..t+4. No future realized demand is used as an input.

Features follow the fixed model contract:
- last4_mean and population last4_std over t-3..t
- trend = (demand_t - demand_t-3) / max(1, abs(demand_t-3))
- promotion, price_index, confirmed_orders, seasonal_index from the next planning week
- four future realized-demand targets

## Model B dataset
Features are available at the same forecast origin:
- last4_std and absolute trend
- next-week promotion flag
- forecast_disagreement = abs(confirmed_orders - last4_mean * seasonal_index) / last4_mean, clipped to [0,1]
- confirmed_ratio = confirmed_orders / last4_mean

The uncertainty target is the mean absolute percentage error of a seasonal baseline (last4_mean times each known seasonal index) versus the next four realized weeks, clipped to [0,1]. This directly measures how unreliable an origin-available forecast proved to be without leaking future demand into features.

## Validation
The supplied trainer preserves row order and uses the final 20% as validation. The two historical product streams remain chronological, and the artifacts must preserve the fixed model_contract.json interface.
