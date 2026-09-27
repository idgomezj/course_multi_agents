# Supplier Selection — Lowest Total-Cost Feasible Source

## First determine whether a purchase is actually needed

Do not select a supplier before calculating the material's **net shortage**.

For each material:

1. determine planned production and gross BOM usage;
2. subtract beginning raw-material inventory;
3. subtract existing PO quantities that arrive before the material is needed;
4. purchase only the remaining shortage, subject to MOQ.

If inventory plus usable inbound POs already cover the requirement, do not place a new PO.

## Determine the required receipt date

Identify when the material must be available for production. Supplier selection must be tied to that need date.

A supplier is feasible when its lead time plus reasonable delay risk still allows the material to arrive before it is needed.

## Compare suppliers economically

Use `get_supplier_options` and supplier-delay evidence.

Do **not** automatically choose:

- the supplier with the shortest lead time;
- the supplier with the highest reliability;
- the most expensive low-risk supplier.

Instead, among suppliers that can meet the required timing/risk constraint, prefer the lower total-cost option.

A premium supplier is justified only when the premium prevents a larger expected cost such as:

- service failure;
- stockout/lost sales;
- material-driven line stop;
- emergency expedite;
- otherwise unavoidable disruption.

## Order timing

Once a supplier is chosen, place the PO as late as reasonably possible while preserving acceptable arrival confidence. This reduces holding and working-capital cost.

When useful, stagger purchases into tranches rather than buying the whole horizon at once. Split orders only when the timing/risk/cost benefit justifies it and MOQ rules are respected.

## Validate supplier choices in the whole plan

A supplier decision is not complete until the full candidate plan is checked with:

1. `calculate_plan_cost`;
2. `validate_plan`.

Compare `estimated_realized_cost` against at least one feasible alternative when supplier choice materially changes cost. Keep the cheaper feasible choice rather than the merely safest-looking choice.
