# Team 1 model-development notes

## Cleaning
- Normalize product identifiers by trimming whitespace and upper-casing.
- Collapse duplicate product/week rows by keeping the first non-null value for each field.
- Keep the time order within each product and interleave products by forecast-origin week before training.
- Forward-fill only planning variables observable at the forecast origin (price index, confirmed orders, seasonal index).
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

The uncertainty target is the mean absolute percentage error of a seasonal baseline (last4_mean times each known seasonal index) versus the next four realized weeks, clipped to [0,1]. This measures how unreliable an origin-available forecast proved to be without leaking future demand into features.

## Training and validation
`train_solution.py` uses PyTorch for deterministic ridge training on an engineered nonlinear basis while preserving the fixed model input/output contract. The first 80% of globally time-ordered examples are used for fitting and the final 20% for chronological validation.

Current validation results:
- Model A MAE by horizon: approximately 100, 136, 145 and 179 units for weeks 1-4.
- Model A RMSE by horizon: approximately 115, 169, 185 and 211 units.
- Model B uncertainty MAE: approximately 0.064.
- Model B uncertainty RMSE: approximately 0.076.

The exported `.pt2` files are compacted with standard ZIP deflate after `torch.export.save`; `torch.export.load` is run immediately afterward to validate that the artifact remains loadable.
