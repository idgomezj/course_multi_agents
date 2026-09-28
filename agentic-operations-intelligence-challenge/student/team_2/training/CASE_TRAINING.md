# Team 2 training brief — Stable Make-to-Stock

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

`raw_case_history.csv` contains weekly demand plus inventory position, receipts and holding-cost observations.

The business is intentionally stable. Build rolling demand-forecast examples from the chronological demand history rather than generating arbitrary high-volatility samples.

For excess-inventory risk, use historical inventory outcomes to define whether a starting inventory/incoming position ultimately proved economically excessive relative to subsequent demand. You must decide and document a reasonable label rule from the case objective; the raw file does not provide `target_risk`.

Avoid constructing labels that simply memorize one numerical threshold. The model should learn the relationship among on-hand inventory, incoming supply, expected demand, holding cost and trend.
