# Team 1 solution notes — Volatile Demand

This implementation keeps the fixed model contract and changes only Team 1-owned
training, RAG, Skills, and model artifacts.

## Data construction

The canonical raw input remains the hosted JSON endpoint:

`GET https://course-agentic-api.idgomezj.com/v1/teams/team_1/training-source.json`

with Team 1's token in `X-Team-Token`.

`build_dataset.py` normalizes product identifiers, collapses duplicate uploads,
imputes missing exogenous planning signals, excludes supervised windows that touch
missing realized demand, and applies a conservative rule for gross unsupported
data-entry spikes. It then builds leakage-safe rolling examples.

For each forecast example, the last four realized weeks end at the anchor week.
The four targets are strictly weeks +1 through +4. Promotion, price, confirmed
orders, and seasonal index are treated as planning-time signals for the first
forecast week.

The uncertainty label is bounded to [0,1] and is the four-week MAPE of a forecast
available at the anchor date. The historical `forecast_disagreement` feature is
the normalized disagreement among moving-average, exponential-smoothing, and
seasonal forecasts.

## Validation

Rows are sorted by anchor week and product, then split chronologically 80/20.

On the preserved Team 1 assignment chronology used for model development:

- demand model validation MAPE: about 12.2%
- four-week moving-average baseline MAPE: about 16.4%
- uncertainty model validation MAE: about 0.043

The public scenario/evaluation API should still be run before merging whenever the
hosted course API is reachable from the execution environment.
