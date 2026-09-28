# Case 0 clean training datasets

Case 0 is the instructor validation case. Unlike Teams 1–5, its model-training data is intentionally **clean, deterministic and ready for training**.

These files are the canonical inputs for validating the complete model pipeline:

```text
training/
├── model_a_training.csv
└── model_b_training.csv
```

## model_a_training.csv

Task: four-week demand forecast regression.

- Rows: 3,000
- Missing model values: 0
- Exact duplicate rows: 0
- Features:
  - `last4_mean`
  - `last4_std`
  - `trend`
  - `promotion`
  - `price_index`
  - `confirmed_orders`
  - `seasonal_index`
- Targets:
  - `target_w1`
  - `target_w2`
  - `target_w3`
  - `target_w4`

## model_b_training.csv

Task: supplier-delay classification.

- Rows: 3,000
- Missing model values: 0
- Exact duplicate rows: 0
- Class distribution in the committed dataset:
  - delay = 1: 1,768
  - delay = 0: 1,232
- Features:
  - `reliability`
  - `recent_late_rate`
  - `lead_time_days`
  - `order_qty_ratio`
  - `urgency`
  - `season_risk`
- Target:
  - `target_delay`

## Why Case 0 is different

Case 0 exists to validate that the platform itself works:

```text
clean training data
→ PyTorch training
→ .pt2 export
→ model loading
→ tool inference
→ Manager
→ simulator/evaluator
```

Because it is a reference/diagnostic case, data preparation ambiguity is intentionally removed.

Teams 1–5 are the exam cases. They receive raw historical JSON and must perform data selection, cleaning, feature engineering and target construction themselves.

## Train

From `agentic-operations-data-api/`:

```bash
python demo_case_0_solution/train_models.py
```

The script reads these CSV files directly and writes:

```text
demo_case_0_solution/models/model_a.pt2
demo_case_0_solution/models/model_b.pt2
```
