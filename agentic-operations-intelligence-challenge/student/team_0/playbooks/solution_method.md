# Case 0 Solution Method

The completed reference solution combines demand forecasting, supplier-delay prediction, company-document retrieval, inventory checks, BOM calculations, supplier comparison, production-capacity checks, total-cost comparison, and final plan validation.

Existing purchase orders are considered before new purchasing. New receipts are staggered when later delivery lowers carrying cost without reducing service. Supplier choices use timing and reliability as well as purchase price. Production remains within compatible-line capacity, and the final candidate is checked for feasibility and service before it is returned.
