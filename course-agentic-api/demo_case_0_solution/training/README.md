# Case 0 training reference

Case 0 teaches both parts of the new workflow:

1. **an imperfect raw-data review example** exposed by the Data API;
2. **clean deterministic supervised CSVs** used to validate the reference training/export pipeline.

See [RAW_DATA_WALKTHROUGH.md](./RAW_DATA_WALKTHROUGH.md) for the worked data-quality analysis.

## Configuration-driven training

The reference trainer reads:

```text
training_config.yaml
feature_config.yaml
```

It does not require editing `train_models.py` to experiment with the allowed architecture/hyperparameter/feature settings.

## Deterministic supervised reference datasets

```text
model_a_training.csv
model_b_training.csv
```

### Model A

Task: four-week demand forecast regression.

- rows: 3,000;
- no missing model values;
- no exact duplicate rows;
- fixed contract features:
  - `last4_mean`
  - `last4_std`
  - `trend`
  - `promotion`
  - `price_index`
  - `confirmed_orders`
  - `seasonal_index`
- targets: `target_w1..target_w4`.

### Model B

Task: supplier-delay classification.

- rows: 3,000;
- no missing model values;
- no exact duplicate rows;
- fixed contract features:
  - `reliability`
  - `recent_late_rate`
  - `lead_time_days`
  - `order_qty_ratio`
  - `urgency`
  - `season_risk`
- target: `target_delay`.

## Why keep clean committed CSVs in the solved case?

The raw sample teaches the reasoning. The committed CSVs make this pipeline deterministic:

```text
training_config + feature_config
→ PyTorch training
→ .pt2 export
→ runtime model loading
→ tool inference
→ Manager
→ simulator/evaluator
```

Teams 1–5 do not receive ready-made clean supervised tables. They must create their own from the team-scoped raw history.

## Train

From `course-agentic-api/`:

```bash
python demo_case_0_solution/train_models.py
```

The script reads the solved YAML configuration and writes:

```text
demo_case_0_solution/models/model_a.pt2
demo_case_0_solution/models/model_b.pt2
```
