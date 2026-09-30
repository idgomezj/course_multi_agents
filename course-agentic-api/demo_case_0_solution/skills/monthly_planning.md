# Monthly Planning — Net Requirements and Low-Cost Procurement

## Objective

Create a four-week plan that is feasible and meets the service target **while minimizing realized total operating cost**. A feasible plan is only the starting point; do not stop optimizing just because validation says it is feasible.

## 1. Start from demand and existing finished goods

1. Inspect current finished-goods and raw-material inventory with `get_inventory`.
2. Inspect all existing inbound purchase orders with `get_open_purchase_orders`.
3. Forecast each product with the trained PyTorch demand model and compare the forecast with visible confirmed-order/scenario evidence.
4. Build a week-by-week finished-goods projection.
5. Use beginning finished-goods inventory to reduce required production. Do **not** automatically produce the full forecast/demand quantity every week.
6. Schedule only the production needed to keep projected service at or above target, subject to line/capacity constraints.

A useful cumulative check is:

```text
required cumulative production
= max(0, cumulative demand through week
         + desired ending FG buffer
         - beginning FG
         - prior planned production)
```

Keep buffers evidence-based and small. Do not add blanket safety quantities when the scenario does not justify them.

## 2. Convert production into gross BOM requirements

For the production quantities actually planned, use `calculate_bom_requirements`.

This result is **gross material usage**, not the quantity to purchase.

Never turn gross BOM requirements directly into purchase orders.

## 3. Compute material requirements NET of inventory and inbound POs

For every raw material, project inventory by week:

```text
projected material balance
= beginning raw-material inventory
+ existing PO receipts available by that week
+ new receipts available by that week
- cumulative material usage from planned production
```

Rules:

- Existing inventory is consumed before new purchasing.
- Existing purchase orders are inbound supply and must be credited before creating new POs.
- Create a new PO only when the projected balance would become insufficient before a production requirement.
- The economic new-order requirement is the **net shortage**, not the gross BOM requirement.
- Respect MOQ and supplier authorization, but do not inflate an order beyond what is economically necessary merely to create a large safety buffer.
- Avoid purchasing a material that is already sufficiently covered by on-hand inventory plus usable open POs.

## 4. Time purchases close to need

For each real net shortage:

1. determine the week/date by which the material must be available;
2. compare authorized suppliers;
3. account for nominal lead time and predicted delay risk;
4. place the order late enough to avoid unnecessary holding cost, but early enough to arrive with acceptable risk;
5. stagger orders/receipts when one large early purchase would create avoidable inventory.

Do not buy the whole month's requirements on day 1 unless timing/risk evidence makes that necessary.

## 5. Choose suppliers on total cost, not maximum reliability

A faster or more reliable supplier may be more expensive.

Choose the lowest-cost supplier that can satisfy the required receipt date and acceptable risk. Pay a reliability/expedite premium only when it prevents a larger expected operational cost such as stockout, line stop, lost sales, or service failure.

## 6. Bounded cost-improvement loop

Do not finalize the first feasible candidate, but keep the optimization bounded so the Manager can finish the run.

**Candidate budget:**
- Evaluate at most two candidates when candidate A is feasible.
- A third candidate is allowed only if both A and B are infeasible and one targeted correction is necessary.
- For each candidate, call `calculate_plan_cost` at most once and `validate_plan` at most once.
- Reuse earlier inventory, open-PO, RAG, model, BOM, and supplier results instead of calling the same tool again with identical inputs.
- Once two feasible candidates have been compared, choose the cheaper one and return the final plan. Do not keep searching for marginal improvements.

Start with candidate A.

For candidate A:

1. call `calculate_plan_cost`;
2. call `validate_plan`;
3. record feasibility, service level, and especially `estimated_realized_cost`.

If candidate A is feasible, create at least one distinct leaner candidate B. Typical improvements include:

- less production because beginning FG already covers part of demand;
- fewer raw-material purchases because inventory/open POs already cover requirements;
- smaller or later purchase orders;
- a lower-cost feasible supplier;
- removal of unnecessary expedite or overtime;
- lower ending FG/RM inventory;
- fewer avoidable changeovers.

Then call `calculate_plan_cost` and `validate_plan` for candidate B.

Choose the **lowest `estimated_realized_cost` candidate that remains feasible and meets the service target**. If a cheaper candidate fails feasibility/service, revert the specific change that caused the failure rather than returning to a broadly over-buffered plan.

Repeated cost/validation calls are allowed only for genuinely different candidates within the candidate budget above. Avoid exact duplicate calls and avoid reopening evidence that has already been retrieved unless the inputs changed.

## 7. Final pre-submission checks

Before returning the plan, verify:

- service target is met;
- no critical violations remain;
- beginning FG was credited;
- beginning RM inventory was credited;
- existing POs were credited by arrival timing;
- purchase quantities are net shortages rather than gross BOM;
- no unnecessary expedite/overtime exists;
- supplier premiums are justified by timing/risk;
- ending inventories are not economically excessive;
- the final validated realized cost is the lowest among the feasible candidates you compared.

Return the final structured plan only after this cost-improvement loop.
