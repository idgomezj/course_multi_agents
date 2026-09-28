from __future__ import annotations

import math
import logging
from typing import Any

from .schemas import MonthlyOperationsPlan
from .observability import log_event

logger = logging.getLogger(__name__)


def supplier_unit_cost(case: dict[str, Any], supplier_id: str, material_id: str) -> float:
    supplier = case["suppliers"].get(supplier_id, {})
    value = float(supplier.get("unit_cost", {}).get(material_id, 0.0))
    log_event(logger, "cost.supplier_unit_cost", level=logging.DEBUG, supplier_id=supplier_id, material_id=material_id, unit_cost=value)
    return value


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
    result = {
        "purchase": round(purchase, 2),
        "production": round(production, 2),
        "overtime": round(overtime, 2),
        "expedite": round(expedite, 2),
        "working_capital": round(working_capital, 2),
        "known_total": round(total, 2),
    }
    log_event(
        logger,
        "cost.plan_estimated",
        team_id=plan.team_id,
        scenario_id=plan.scenario_id,
        purchase_orders=len(plan.purchase_orders),
        production_orders=len(plan.production_plan),
        breakdown=result,
    )
    return result


def cost_gap(student_cost: float, benchmark_cost: float | None) -> float | None:
    if benchmark_cost is None or benchmark_cost <= 0:
        log_event(logger, "cost.gap.unavailable", level=logging.DEBUG, student_cost=student_cost, benchmark_cost=benchmark_cost)
        return None
    gap = (student_cost - benchmark_cost) / benchmark_cost
    log_event(logger, "cost.gap.calculated", level=logging.DEBUG, student_cost=student_cost, benchmark_cost=benchmark_cost, gap=gap)
    return gap


def cost_score_from_gap(gap: float | None) -> float:
    if gap is None:
        score = 100.0
        log_event(logger, "cost.score.calculated", level=logging.DEBUG, gap=gap, score=score)
        return score
    if gap <= 0.05:
        score = 100.0
    elif gap <= 0.10:
        score = 90.0
    elif gap <= 0.20:
        score = 75.0
    elif gap <= 0.30:
        score = 60.0
    else:
        score = max(10.0, 60.0 - (gap - 0.30) * 100.0)
    log_event(logger, "cost.score.calculated", level=logging.DEBUG, gap=gap, score=score)
    return score
