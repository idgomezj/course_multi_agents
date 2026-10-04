# Team 3 training brief — Just-in-Time Supply

## What this file is

This is the **raw historical evidence for your assigned business case**. It is intentionally not a training-ready ML table.

Retrieve the raw historical evidence as JSON from `GET /v1/teams/team_3/training-source.json` using Team 3's assigned token. Treat that API response and `model_contract.json` as read-only assignment inputs. You may save the response locally as `raw_source.json` for analysis, but create new derived files rather than editing the source evidence or contract.

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

The JSON returned by `/v1/teams/team_3/training-source.json` contains historical supplier orders with order size, normal order size, order/need dates, nominal lead time, realized lead time, reliability, recent late-rate and seasonal-risk observations.

Derive `order_qty_ratio` from order quantity versus typical quantity. Derive an urgency measure from the time available between order placement, expected arrival and the material need date. Define the delay classification target from the realized delivery outcome and define arrival-time regression from realized lead time.

Be careful about leakage: realized lead time is an outcome/target source and cannot be used as an input feature for the same example.
