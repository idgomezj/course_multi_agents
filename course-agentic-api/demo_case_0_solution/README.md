# Case 0 — Complete Worked Example

Case 0 is the only fully worked example. It exists so students can see the expected level of analysis before beginning Teams 1–5.

The example demonstrates:
- training the assigned PyTorch demand and supplier-risk models;
- configuring retrieval for the Case 0 company documents;
- designing planning, sourcing and cost-comparison procedures;
- producing four-week production and purchasing plans;
- validating feasibility and comparing total operating cost;
- adapting the plan to different operational scenarios.

## Clean model-training data

Case 0 deliberately includes **clean, ready-to-train, deterministic datasets** so it can validate the platform rather than test data preparation:

```text
demo_case_0_solution/training/
├── README.md
├── model_a_training.csv   # 3,000 clean demand-forecast rows
└── model_b_training.csv   # 3,000 clean supplier-delay rows
```

`train_models.py` reads these committed files directly. It does not generate training examples at runtime.

This is intentionally different from Teams 1–5, where students receive raw historical JSON and must construct the supervised datasets themselves.

## Published reference scenarios

Every Case 0 public scenario now has its own published reference plan under:

```text
demo_case_0_solution/reference_plans/
├── T0-P01.json
├── T0-P02.json
└── T0-P03.json
```

The **Evaluate published reference** button works for all three scenarios.

### T0-P01 — Balanced month

The plan targets full service without overtime. Weekly production is:

- FG01: 950
- FG02: 762.5
- FG03: 570

Existing RM03 and RM05 purchase orders are used before new purchases are added.

Reference result:

```text
Feasible:       YES
Service:        100%
Reference cost: 79,249.05
```

### T0-P02 — Supplier trade-off

The reference deliberately demonstrates the supplier-risk trade-off.

For RM01 it:
- uses high-reliability SUP04 for the earlier 2,500-unit tranche;
- uses lower-cost SUP02 for a later 2,500-unit tranche;
- places the SUP02 order early enough that the scenario's realized four-day delay is absorbed before the material is needed.

This shows that the correct choice is not always "cheapest supplier" or "most reliable supplier"; timing slack and total cost matter.

Reference result:

```text
Feasible:       YES
Service:        100%
Reference cost: 77,827.30
```

### T0-P03 — Demand increase

The reference increases FG02 production to respond to the promotion-driven demand change:

```text
Week 1 FG02: 762.5
Week 2 FG02: 850
Week 3 FG02: 920
Week 4 FG02: 877.5
```

Small fast SUP04 orders supplement RM02, RM05 and RM06 so the higher production plan remains material-feasible without unnecessarily increasing all purchase quantities.

Reference result:

```text
Feasible:       YES
Service:        100%
Reference cost: 82,983.90
```

## Reference mode versus AI mode

**Evaluate published reference** loads the selected scenario's known worked plan and runs it through the deterministic simulator.

**Run AI Manager end-to-end** does not load the reference plan. The LLM Manager must independently solve the scenario using Skills, RAG, PyTorch, tools, cost analysis and validation.

The published plans therefore serve as:
- a teaching example;
- a simulator regression target;
- a benchmark reference for public development.

They are not hardcoded into the AI Manager.

This is a teaching example, not a reusable answer. Teams 1–5 have different model tasks, data distributions, constraints and cost structures.
