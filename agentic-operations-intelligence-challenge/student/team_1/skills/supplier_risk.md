# Supplier risk

Use this Skill when a scenario reports a supplier warning, recent late-rate increase, urgent demand spike, or other supply risk.

1. Retrieve supplier_contracts.md with search_knowledge and inspect existing purchase orders before ordering.
2. Use get_supplier_options for every material at risk. Do not assume the cheapest supplier is the lowest-cost choice.
3. Call predict_supplier_delay for the warned supplier with the planned quantity and realistic urgency, then compare at least one approved alternative when available.
4. Protect the 98.5% service target. A short/reliable supplier can be economically preferable when it avoids lost sales, stockout penalties, or emergency procurement.
5. Honor MOQ, lead time, quality, authorization, and approval thresholds. Avoid duplicate tool calls with identical inputs.
6. Include the sourcing choice in calculate_plan_cost and validate_plan before finalizing.
