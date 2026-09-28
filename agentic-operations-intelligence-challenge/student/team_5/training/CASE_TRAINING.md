# Team 5 training brief — Capacity-Constrained Plant

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

`raw_case_history.csv` contains historical line runs with utilization, maintenance age, recent downtime, planned/available hours, overload, changeovers, labor availability, overtime availability and realized completion/downtime outcomes.

For downtime risk, derive the classification target from a documented realized-downtime rule. Actual downtime is an outcome and cannot be included as an input.

For production feasibility, derive `required_hours_ratio` from the planned workload and available line hours, use an estimated/predicted downtime-risk input rather than the realized future downtime, and derive the target from the actual completion outcome.

Use validation that tests whether the model generalizes across later runs and different lines/products.
