# Team 4 training brief — Unreliable Supply Network

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

`raw_case_history.csv` contains supplier-order history including delivery timing and quality-inspection outcomes.

For the delay model, derive the same operational features available at order time and construct the classification target from the realized delivery outcome.

For supplier-quality risk, derive the target from the inspection/rejection outcome. Inputs such as quality score, recent reject rate, criticality and process change are known before receipt; rejected quantity is an outcome and must not leak into inputs.

The case emphasizes long lead times, delay and quality disruption, so class balance and recall on costly failure events should be considered rather than relying only on accuracy.
