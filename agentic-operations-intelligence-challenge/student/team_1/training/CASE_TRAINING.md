# Team 1 training brief — Volatile Demand

## What this file is

This is the **raw historical evidence for your assigned business case**. It is intentionally not a training-ready ML table.

You must build the supervised learning dataset yourself. That means deciding how historical rows become examples, deriving the required model inputs from the raw observations, constructing defensible targets from later outcomes, handling missing/noisy observations, choosing train/validation splits, and documenting your assumptions.

The runtime model interface is fixed by `model_contract.json`. You may change the neural-network architecture, preprocessing inside the model, optimizer, loss, sampling, regularization, validation strategy, and training procedure, but the exported model must accept the feature columns and produce the target shape declared in the contract.

Do not hardcode public scenario IDs or benchmark answers into the training data. Your construction should generalize to unseen scenarios.

Your workflow should produce:

```text
student/team_X/training/model_a_training.csv
student/team_X/training/model_b_training.csv
student/team_X/models/model_a.pt2
student/team_X/models/model_b.pt2
```

The starter trainer refuses to create the supervised rows for you; it only trains after you create the model-specific CSV.


## Raw file

`raw_case_history.csv` contains weekly product demand history with promotion, price, confirmed-order, seasonality and commercial-event observations.

The case tells you demand is volatile and promotion-sensitive. Use the chronological history to construct rolling forecast examples. The model contract expects rolling statistics and four future weekly demand targets. Do not use future rows when computing features.

For the uncertainty model, construct a target that represents **how unreliable the forecast proved to be** using subsequent realized demand versus a forecast available at the prediction date. Your definition must be numeric, bounded/normalized in a defensible way, and documented. The raw file intentionally does not give you `target_uncertainty`.

Recommended validation: preserve time order so later weeks are validation/test-like observations rather than randomly leaking future patterns into training.
