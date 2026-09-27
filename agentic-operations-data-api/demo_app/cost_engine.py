from __future__ import annotations

import math
from typing import Any

from .schemas import MonthlyOperationsPlan


def supplier_unit_cost(case: dict[str, Any], supplier_id: str, material_id: str) -> float:
    supplier = case["suppliers"].get(supplier_id, {})
    return float(supplier.get("unit_cost", {}).get(material_id, 0.0))


def estimate_plan_cost(case: dict[str, Any], plan: MonthlyOperationsPlan) -> dict[str, float]:
    """Decision-time estimate using known costs, not hidden realized events."""
    costs = case["costs"]
    purchase = 0.0
    expedite = 0.0
    working_capital = 0.0
    overtime = 0.0
    production = 0.0

    for po in plan.purchase_orders:
        base = supplier_unit_cost(case, po.supplier_id, po.material_id) * po.quantity
        purchase += base
        working_capital += base * float(costs.get("working_capital_rate", 0.0))
        if po.expedite:
            expedite += po.quantity * float(costs.get("expedite_per_unit", 0.0))

    for order in plan.production_plan:
        product = case["products"].get(order.product_id, {})
        production += order.quantity * float(product.get("production_cost", 0.0))
        overtime += order.overtime_hours * float(costs.get("overtime_per_hour", 0.0))

    total = purchase + production + overtime + expedite + working_capital
    return {
        "purchase": round(purchase, 2),
        "production": round(production, 2),
        "overtime": round(overtime, 2),
        "expedite": round(expedite, 2),
        "working_capital": round(working_capital, 2),
        "known_total": round(total, 2),
    }


def cost_gap(student_cost: float, benchmark_cost: float | None) -> float | None:
    if benchmark_cost is None or benchmark_cost <= 0:
        return None
    return (student_cost - benchmark_cost) / benchmark_cost


def cost_score_from_gap(gap: float | None) -> float:
    if gap is None:
        return 100.0
    if gap <= 0.05:
        return 100.0
    if gap <= 0.10:
        return 90.0
    if gap <= 0.20:
        return 75.0
    if gap <= 0.30:
        return 60.0
    return max(10.0, 60.0 - (gap - 0.30) * 100.0)
