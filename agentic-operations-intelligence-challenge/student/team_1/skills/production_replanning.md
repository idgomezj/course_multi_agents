# Production replanning after validation

Use only when the first candidate plan is infeasible or has an avoidable
service/cost problem.

- Read the `validate_plan` violations literally; do not rebuild unrelated parts.
- Capacity violation: use `get_production_capacity` and
  `optimize_production_plan` to move/split affected product quantities.
- Material shortage: recompute `calculate_bom_requirements`, inspect inventory and
  open POs, then source only the residual shortage.
- Service shortfall with feasible capacity/materials: revisit the affected
  product's forecast/uncertainty and add the smallest targeted buffer that closes
  the gap.
- Excess inventory/cost: reduce late-week production first, especially after
  promotion cancellation or demand drop.
- After every material revision, run `calculate_plan_cost` and `validate_plan`
  again on the complete candidate.

Stop once the plan is feasible and additional inventory or expedite cost does not
buy meaningful service protection.
