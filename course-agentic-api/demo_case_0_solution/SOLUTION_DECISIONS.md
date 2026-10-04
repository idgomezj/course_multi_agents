# Case 0 — Fully worked configuration decisions

Case 0 is the reference implementation for the **process**, not a set of values to copy into Teams 1–5.

The same solved configuration is used across T0-P01, T0-P02 and T0-P03. Scenario-specific reference plans differ because the visible business conditions differ; the configuration is not rewritten per scenario.

## 1. Company and hard constraints

The case defines the authoritative constraints:

- 99% strategic-retailer service target;
- monthly operating budget: $85,000;
- monthly overtime cap: 72 hours;
- expedited-unit cap: 600 units;
- peak finished-goods inventory cap: 4,200 units;
- supplier authorization/MOQ;
- purchase approval threshold.

These limits live in the company case, not student YAML. The solved configuration cannot weaken them.

## 2. Training configuration

`training/training_config.yaml` uses:

- custom [64, 32] hidden layers;
- ReLU;
- 0.08 dropout;
- AdamW;
- learning rate 0.002;
- 240 epoch ceiling with early stopping;
- chronological 82/18 train/validation split;
- MSE for demand regression;
- BCE for supplier-delay classification.

The choice is deliberately moderate: enough capacity to learn nonlinear behavior without making the reference model unnecessarily large.

## 3. Feature selection

`training/feature_config.yaml` keeps all fixed-contract features.

This is a positive result, not a requirement for other teams. A student team should disable a feature only after testing whether removing it improves generalization or robustness.

## 4. RAG configuration and authority

The knowledge set contains:

- current operations policy;
- current supplier contracts;
- current company facts;
- obsolete legacy policy;
- unapproved planning draft;
- travel reimbursement policy;
- office parking rules.

`rag/document_priorities.yaml` marks current policy/contracts as authoritative, the old policy as obsolete, the draft as draft, and the travel/parking documents as irrelevant.

The source text is never edited to make retrieval easier.

## 5. Forecast policy

`config/forecast_policy.yaml` uses a blended signal:

- Model A: 50%;
- confirmed orders: 25%;
- moving average: 10%;
- exponential smoothing: 5%;
- seasonal signal: 10%.

The purpose is to avoid treating either the neural model or confirmed orders as infallible.

When observable uncertainty/disagreement is high, the model weight is reduced and confirmed-order weight is increased modestly.

## 6. Risk policy

The reference thresholds are:

- medium risk: 0.20;
- high risk: 0.45;
- safety-stock factor: 1.40;
- forecast-disagreement review threshold: 0.20.

These are decision thresholds used by the Manager/tools. They do not change evaluator rules.

## 7. Planning priorities

The solved preference weights are:

- service: 45%;
- total cost: 35%;
- ending inventory: 10%;
- plan stability: 10%.

Again, these are preferences. A hard $85,000 budget or 99% service policy remains binding independently.

## 8. Tool policy

The reference process requires:

- relevant Skill review;
- policy/contract retrieval;
- inventory/open-PO review before new procurement;
- demand-signal comparison;
- supplier-delay analysis when timing matters;
- `calculate_plan_cost`;
- `validate_plan`;
- no pointless exact duplicate calls.

## 9. Manager LLM settings

The solved demo uses a low temperature (0.10), a 3,500-token budget and at most five RAG documents per retrieval context.

The provider remains selectable because the purpose is to compare orchestration across supported LLMs without changing the rest of the solution.

## 10. Business assumptions

The assumption file explicitly records interpretations that are supported by current policy:

- confirmed orders are strong evidence, not the entire forecast;
- supplier choice is based on total operational consequence;
- inventory is allowed but carries economic cost;
- current official/contract sources outrank obsolete/draft/irrelevant documents.

## 11. Scenario application

### T0-P01 — balanced month

The reference plan uses existing inventory/open POs first, avoids unnecessary overtime/expedite and achieves full service under the budget.

### T0-P02 — supplier trade-off

The case intentionally makes unit price and delivery risk conflict. The published plan uses timing slack and supplier risk to split sourcing rather than applying a "cheapest always" or "most reliable always" rule.

### T0-P03 — demand increase

Promotion/confirmed-order evidence changes production and procurement. The same planning/RAG/risk configuration is used; only the scenario evidence changes.

## 12. What students should learn

A complete solution is not one model or one Skill.

```text
company context
+ imperfect evidence
+ training settings
+ feature choices
+ two specialist models
+ RAG configuration
+ document authority
+ Skills
+ forecast/risk/planning/tool policies
+ LLM settings
+ explicit assumptions
+ cost/constraint validation
= operational decision system
```

Teams 1–5 must derive their own settings from their own company, data and scenarios.
