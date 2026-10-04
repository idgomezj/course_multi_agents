# Case design requirements — harder cases without requiring programming

This document defines the instructor-side requirements for every Team 1–5 case.

The challenge should be difficult because students must understand a realistic business, reconcile imperfect evidence and configure a multi-agent system. It should **not** be difficult because critical facts are missing or because students must write advanced Python.

## 1. Start-context must describe a real operating company

Every team `start-context` should contain enough information to reason about the case without revealing an answer.

At minimum provide:

- company/industry description;
- products and product roles;
- customer/channel mix and any priority customers;
- how demand/orders/production/supply normally work;
- meaning and reliability of confirmed orders or equivalent signals;
- inventory/storage context;
- production capacity and extraordinary capacity;
- suppliers, lead times, reliability/quality and commercial differences;
- BOM/material context where applicable;
- open purchase-order context;
- service policies;
- finance/budget constraints;
- overtime/expedite/inventory/approval policies when relevant;
- cost structure relevant to trade-offs;
- known operational risks;
- which information sources may contain delays/noise/inconsistency;
- available RAG document types and how authority/effective dates work;
- the business objective and the trade-offs management cares about.

Do not state the optimal weights, thresholds, supplier allocation, production plan or model hyperparameters.

## 2. Raw historical evidence must be imperfect but solvable

Each team's `training-source.json` should include several realistic data-quality issues while still containing enough signal to build useful models.

Use a controlled mix such as:

- missing observations;
- duplicate uploads;
- inconsistent case/spacing in identifiers;
- late-arriving observations;
- plausible extreme values;
- one or more suspicious unsupported outliers;
- source-system fields;
- planner/operator notes;
- cancelled or changed commercial events;
- corrected orders;
- regime or concept drift;
- different quality across sources.

Important rules:

- preserve chronology;
- never make the only valid answer depend on guessing an undocumented corruption;
- include enough neighboring evidence to analyze suspicious observations;
- hidden holdouts must follow the same business universe even when combinations differ.

## 3. Signals should sometimes disagree

Cases should intentionally produce situations where specialist models and business signals disagree.

Examples:

- Model A forecast > confirmed orders > moving average;
- confirmed orders rise while a promotion is at risk of cancellation;
- supplier historical reliability is good while recent late-rate worsens;
- low-cost supplier has elevated quality risk;
- nominal capacity looks sufficient while downtime/maintenance risk is high.

Students should have enough contextual evidence to decide *how to investigate and balance* those signals, but not enough to simply copy one rule.

## 4. Trade-offs must be real

At least three material objectives/constraints should pull in different directions.

Possible hard constraints:

- minimum service level;
- monthly operating budget;
- purchase-spend cap;
- warehouse/FG inventory limit;
- monthly overtime cap;
- per-line overtime cap;
- expedite-unit cap;
- supplier authorization/MOQ;
- supplier capacity;
- approval thresholds;
- customer/product priority rule;
- JIT inventory ceiling;
- minimum/maximum buffer;
- line compatibility;
- quality restriction.

Hard constraints belong to the case and evaluator/simulator. Student configuration can express preferences but cannot weaken them.

## 5. Budgets must matter

Each case should have a financially meaningful limit or pressure, for example:

- monthly operating budget;
- procurement budget;
- working-capital pressure;
- overtime authorization limit;
- emergency/expedite cap.

The budget should be tight enough that "buy/produce extra just in case" is not a universally safe strategy.

## 6. RAG should include useful noise

Each case knowledge set should contain a balanced mixture of:

- current official policy;
- contract/current supplier terms;
- older superseded policy;
- draft document;
- advisory meeting notes;
- partially relevant operating guidance;
- at least two completely irrelevant but plausible company documents.

Example irrelevant documents:

- travel reimbursement;
- parking/office access;
- holiday calendar;
- branding guidelines.

Students should use `document_priorities.yaml` and RAG configuration to improve retrieval. Do not hide required facts exclusively in an unlabeled obsolete document.

## 7. Public vs hidden scenario design

Public scenarios should teach individual concepts and a few simple combinations.

Hidden scenarios should recombine known concepts:

```text
public: promotion
public: supplier delay
public: capacity pressure

hidden: promotion + supplier delay
hidden: supplier delay + capacity pressure
hidden: promotion + supplier delay + capacity pressure
```

Hidden scenarios may change magnitudes and timing, but should not introduce an entirely new rule that students had no way to learn from start-context, history or RAG.

## 8. Team-specific difficulty

### Team 1 — Volatile Demand

Must include:

- imperfect demand/promotion/order history;
- promotion lift that varies rather than one fixed multiplier;
- at least one promotion cancellation/change pattern;
- confirmed orders that are informative but not perfectly reliable;
- scenarios where Model A/statistical/confirmed-order signals disagree;
- budget/inventory/service trade-offs;
- irrelevant/obsolete promotion or inventory documents.

### Team 2 — Stable Make-to-Stock

Must include:

- mostly stable demand with occasional structural decline/change;
- excess-inventory pressure;
- open POs;
- MOQ/discount temptation;
- warehouse and/or working-capital constraint;
- scenarios where cheap bulk buying conflicts with inventory economics;
- current vs obsolete inventory/finance guidance.

### Team 3 — JIT

Must include:

- supplier-order history with missing/noisy timing observations;
- cheap/variable vs expensive/reliable supplier choices;
- moved production/need dates;
- delay-risk and arrival-time signals that can disagree;
- low inventory tolerance plus line-stop exposure;
- limited expedite/budget;
- current contracts plus irrelevant operational documents.

### Team 4 — Unreliable Supply

Must include:

- delay and quality outcomes;
- suppliers that are not uniformly best/worst;
- recent process/quality changes;
- long-lead/cheap vs short-lead/expensive trade-offs;
- material criticality;
- contract/authorization restrictions;
- budget/expedite limits;
- conflicting current/draft/old supplier documents.

### Team 5 — Capacity Constrained

Must include:

- downtime/maintenance/utilization history with imperfections;
- line compatibility;
- changeovers;
- labor/overtime constraints;
- capacity loss and customer urgency;
- cases where all demand cannot be satisfied simultaneously;
- budget/overtime/service trade-offs;
- current maintenance/overtime policy plus irrelevant company documents.

## 9. Student-configurable surfaces

Each team package exposes these controls:

```text
training/training_config.yaml
training/feature_config.yaml
rag/config.yaml
rag/document_priorities.yaml
skills/*.md
config/forecast_policy.yaml
config/risk_policy.yaml
config/planning_objectives.yaml
config/tool_policy.yaml
config/manager_llm.yaml
assumptions/business_assumptions.yaml
```

These are the areas students may tune.

The platform/evaluator/runtime implementation remains locked.

## 10. Evaluation strategy is NOT student editable

Students cannot modify:

- score formula;
- weights;
- benchmark/oracle;
- hidden scenarios;
- hidden holdouts;
- evaluation attempt policy;
- evaluator implementation.

Those remain instructor-controlled.

## 11. Readiness checklist before publishing a case

For every team verify:

- start-context alone gives enough business understanding to begin;
- the training source contains imperfections but remains analyzable;
- no single signal is always dominant;
- there are at least three meaningful business trade-offs;
- budget/financial pressure changes decisions;
- RAG contains relevant + irrelevant + obsolete/draft information;
- generic baseline configs run but are not optimal;
- changing at least three student-controlled surfaces can measurably improve results;
- a good solution generalizes across public scenarios;
- public scenario hardcoding performs poorly on hidden combinations;
- no hidden test depends on a rule never represented in accessible evidence.
