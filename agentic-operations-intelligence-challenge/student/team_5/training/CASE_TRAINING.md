# Team 5 training brief — Capacity-Constrained Plant

## What this file is

This is the **raw historical evidence for your assigned business case**. It is intentionally not a training-ready ML table.

Retrieve the raw historical evidence as JSON from `GET /v1/teams/team_5/training-source.json` using Team 5's assigned token. Treat that API response and `model_contract.json` as read-only assignment inputs. You may save the response locally as `raw_source.json` for analysis, but create new derived files rather than editing the source evidence or contract.

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

The JSON returned by `/v1/teams/team_5/training-source.json` contains historical line runs with utilization, maintenance age, recent downtime, planned/available hours, overload, changeovers, labor availability, overtime availability and realized completion/downtime outcomes.

For downtime risk, derive the classification target from a documented realized-downtime rule. Actual downtime is an outcome and cannot be included as an input.

For production feasibility, derive `required_hours_ratio` from the planned workload and available line hours, use an estimated/predicted downtime-risk input rather than the realized future downtime, and derive the target from the actual completion outcome.

Use validation that tests whether the model generalizes across later runs and different lines/products.

## How to solve the complete Team 5 case

Team 5 is capacity constrained. The models help estimate risk, but the final decision must reconcile capacity, downtime, overtime, line compatibility, materials and service.

After building the datasets:

1. tune Model A (downtime risk) and Model B (production feasibility);
2. test feature choices such as utilization, maintenance age, overload, labor ratio and changeovers;
3. configure risk thresholds for when downtime/feasibility signals require replanning;
4. use planning priorities to balance service, overtime cost, inventory and plan stability without overriding hard capacity limits;
5. review RAG for maintenance, overtime, customer-priority and line policies;
6. improve Skills for capacity checks, line selection, changeovers, overtime and replanning;
7. always validate candidate plans because a plausible production quantity can still be infeasible;
8. test combined downtime, labor shortage, urgent-customer and line-compatibility conditions.

The case may intentionally create situations where producing everything requested is impossible. The student must configure the system to make defensible trade-offs rather than pretending all objectives can be satisfied.

