# Cost Optimization — Compare and Revise Feasible Plans

## Core rule

**Feasible does not mean economical.** After feasibility and service are satisfied, continue reducing realized operating cost.

## Use both cost tools correctly

`calculate_plan_cost` estimates known decision-time costs such as purchases, production, overtime, expedite, and working capital.

`validate_plan` evaluates the candidate in the deterministic development simulator and returns `estimated_realized_cost`, which also reflects effects such as inventory holding, stockout/lost sales, line stops, and changeovers.

Therefore:

1. use `calculate_plan_cost` to understand direct/known cost;
2. use `validate_plan` to confirm feasibility/service and compare **realized total cost**;
3. do not select a plan only because its `known_total` looks low;
4. do not stop merely because `validate_plan` says `feasible: true`.

## Mandatory candidate comparison

Compare at least two **distinct** feasible candidate plans when possible.

Start with a feasible candidate, then deliberately create a leaner alternative. Revalidate after each material change.

Prefer the candidate with the lowest `estimated_realized_cost` that still meets the service target and has no critical violation.

## Highest-value cost reductions to investigate

In this order, inspect:

1. **Overproduction**
   - Credit beginning finished-goods inventory.
   - Produce only what is needed for service/timing.

2. **Over-purchasing**
   - Gross BOM is not purchase quantity.
   - Credit beginning raw-material inventory.
   - Credit existing inbound POs by arrival week.
   - Buy only the remaining net shortage, subject to MOQ.

3. **Purchasing too early**
   - Move receipts closer to the week of consumption when lead time/risk allows.
   - Avoid creating large early raw-material balances.

4. **Unnecessary supplier premium**
   - Do not default to the fastest or most reliable supplier.
   - Use the lowest-cost supplier that remains timing/risk feasible.

5. **Unnecessary expedite or overtime**
   - Use only when the avoided service/disruption cost is larger.

6. **Excess ending inventory**
   - Large ending RM or FG is a warning that production/purchasing may be too high or too early.

7. **Avoidable changeovers**
   - Preserve feasible production timing while avoiding unnecessary line/product switching.

## Economic discipline

Do not add arbitrary safety stock merely to make a plan "safer." Extra inventory has holding and working-capital cost. Add buffers only when forecast uncertainty, supplier risk, policy, or other evidence justifies them.

When two plans are both feasible with comparable service, choose the lower realized-cost plan.

Document in the final explanation which cost-saving changes were made and why they did not compromise service or feasibility.
