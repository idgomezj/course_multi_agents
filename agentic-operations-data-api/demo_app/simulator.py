from __future__ import annotations

import math
import logging
from collections import defaultdict
from typing import Any

from .cost_engine import supplier_unit_cost
from .schemas import ConstraintViolation, MonthlyOperationsPlan, SimulationResult
from app.observability import log_event

logger = logging.getLogger(__name__)


def _week_from_day(day: int) -> int:
    return min(4, max(1, math.ceil(day / 7)))


def _actual_demand(case: dict[str, Any], scenario: dict[str, Any], product_id: str, week: int) -> float:
    base = float(case["products"][product_id]["base_demand"][week - 1])
    realized = scenario.get("realized", {})
    by_product = realized.get("demand_multiplier", {})
    value = by_product.get(product_id, 1.0)
    if isinstance(value, list):
        multiplier = float(value[week - 1])
    else:
        multiplier = float(value)
    return max(0.0, base * multiplier)


def simulate_month(case: dict[str, Any], scenario: dict[str, Any], plan: MonthlyOperationsPlan) -> SimulationResult:
    """Independent deterministic evaluator for a submitted plan.

    The hidden final evaluator can use the same contract with private scenario
    realizations. The Manager never receives scenario['realized'].
    """
    violations: list[ConstraintViolation] = []
    log_event(
        logger,
        "simulation.started",
        team_id=plan.team_id,
        scenario_id=plan.scenario_id,
        production_orders=len(plan.production_plan),
        purchase_orders=len(plan.purchase_orders),
        initial_material_inventory={k: float(v["initial_inventory"]) for k, v in case["materials"].items()},
        initial_finished_inventory={k: float(v.get("initial_fg", 0.0)) for k, v in case["products"].items()},
    )
    costs = case["costs"]
    policy = case.get("policies", {})
    realized = scenario.get("realized", {})

    material_inv = {k: float(v["initial_inventory"]) for k, v in case["materials"].items()}
    fg_inv = {k: float(v.get("initial_fg", 0.0)) for k, v in case["products"].items()}
    receipts: dict[int, list[tuple[str, float, str]]] = defaultdict(list)

    # Existing POs.
    for po in case.get("open_purchase_orders", []):
        receipts[int(po["arrival_week"])].append((po["material_id"], float(po["quantity"]), po["supplier_id"]))

    purchase_cost = 0.0
    expedite_cost = 0.0
    working_capital_cost = 0.0

    # Student POs.
    for po in plan.purchase_orders:
        supplier = case["suppliers"].get(po.supplier_id)
        if not supplier or po.material_id not in supplier.get("materials", []):
            violations.append(ConstraintViolation(code="SUPPLIER_NOT_AUTHORIZED", message=f"{po.supplier_id} cannot supply {po.material_id}"))
            continue
        moq = float(supplier.get("moq", {}).get(po.material_id, 0.0))
        if po.quantity < moq:
            violations.append(ConstraintViolation(code="MOQ", message=f"{po.material_id} order {po.quantity:.1f} is below MOQ {moq:.1f}"))
        unit_cost = supplier_unit_cost(case, po.supplier_id, po.material_id)
        po_cost = unit_cost * po.quantity
        purchase_cost += po_cost
        working_capital_cost += po_cost * float(costs.get("working_capital_rate", 0.0))
        if po.expedite:
            expedite_cost += po.quantity * float(costs.get("expedite_per_unit", 0.0))

        lead = float(supplier.get("lead_time_days", 7))
        delay = float(realized.get("supplier_delay_days", {}).get(po.supplier_id, 0.0))
        effective = max(1.0, lead * (0.55 if po.expedite else 1.0) + delay)
        arrival_day = po.order_day + effective
        arrival_week = min(4, max(1, math.ceil(arrival_day / 7)))

        reject_fraction = float(realized.get("supplier_reject_fraction", {}).get(po.supplier_id, 0.0))
        delivered_qty = po.quantity * max(0.0, 1.0 - reject_fraction)
        receipts[arrival_week].append((po.material_id, delivered_qty, po.supplier_id))
        log_event(
            logger,
            "simulation.purchase_order.scheduled",
            level=logging.DEBUG,
            material_id=po.material_id,
            supplier_id=po.supplier_id,
            quantity=po.quantity,
            order_day=po.order_day,
            expedite=po.expedite,
            arrival_week=arrival_week,
            delivered_quantity=delivered_qty,
            purchase_cost=po_cost,
        )

        threshold = float(policy.get("approval_threshold", math.inf))
        if po_cost > threshold and not any(a.requires_approval for a in plan.actions):
            violations.append(ConstraintViolation(code="APPROVAL_REQUIRED", message=f"PO {po.material_id}/{po.supplier_id} exceeds approval threshold"))

    line_capacity = {
        line: [float(cfg["weekly_hours"])] * 4
        for line, cfg in case["lines"].items()
    }
    for line, weekly_loss in realized.get("downtime_hours", {}).items():
        if line in line_capacity:
            if isinstance(weekly_loss, list):
                for i, value in enumerate(weekly_loss[:4]):
                    line_capacity[line][i] = max(0.0, line_capacity[line][i] - float(value))
            else:
                line_capacity[line][0] = max(0.0, line_capacity[line][0] - float(weekly_loss))

    plan_by_week: dict[int, list] = defaultdict(list)
    for item in plan.production_plan:
        plan_by_week[item.week].append(item)

    production_cost = 0.0
    overtime_cost = 0.0
    holding_cost = 0.0
    lost_sales_cost = 0.0
    stockout_cost = 0.0
    downtime_cost = 0.0
    changeover_cost = 0.0
    lost_units = 0.0
    line_stop_hours = 0.0
    total_demand = 0.0
    total_served = 0.0
    line_last_product: dict[str, str] = {}

    for week in range(1, 5):
        log_event(
            logger,
            "simulation.week.started",
            level=logging.DEBUG,
            week=week,
            material_inventory=dict(material_inv),
            finished_inventory=dict(fg_inv),
            receipts=[{"material_id": m, "quantity": q, "supplier_id": s} for m, q, s in receipts.get(week, [])],
        )
        week_demand: dict[str, float] = {}
        week_served: dict[str, float] = {}
        week_produced: dict[str, float] = {}
        for material_id, quantity, _supplier_id in receipts.get(week, []):
            material_inv[material_id] = material_inv.get(material_id, 0.0) + quantity

        used_hours = defaultdict(float)
        for order in plan_by_week.get(week, []):
            if order.product_id not in case["products"]:
                violations.append(ConstraintViolation(code="UNKNOWN_PRODUCT", message=order.product_id))
                continue
            product = case["products"][order.product_id]
            line = order.line_id or product.get("preferred_line")
            if line not in case["lines"]:
                violations.append(ConstraintViolation(code="UNKNOWN_LINE", message=str(line)))
                continue
            if order.product_id not in case["lines"][line]["products"]:
                violations.append(ConstraintViolation(code="LINE_INCOMPATIBLE", message=f"{order.product_id} cannot run on {line}"))
                continue

            hpu = float(product["hours_per_unit"])
            required_hours = order.quantity * hpu
            max_ot = float(policy.get("max_overtime_hours_per_line_week", 0.0))
            permitted_ot = min(float(order.overtime_hours), max_ot)
            available = max(0.0, line_capacity[line][week - 1] - used_hours[line]) + permitted_ot
            feasible_by_capacity = order.quantity if required_hours <= available else available / hpu
            if feasible_by_capacity + 1e-9 < order.quantity:
                violations.append(ConstraintViolation(code="CAPACITY", message=f"{line} week {week} cannot produce requested {order.quantity:.1f} {order.product_id}"))

            bom = case["bom"][order.product_id]
            feasible_by_material = feasible_by_capacity
            for material_id, per_unit in bom.items():
                if per_unit > 0:
                    feasible_by_material = min(feasible_by_material, material_inv.get(material_id, 0.0) / float(per_unit))

            actual_qty = max(0.0, feasible_by_material)
            if actual_qty + 1e-9 < feasible_by_capacity:
                missing_qty = feasible_by_capacity - actual_qty
                stop_hours = missing_qty * hpu
                line_stop_hours += stop_hours
                downtime_cost += stop_hours * float(costs.get("line_stop_per_hour", 0.0))
                violations.append(ConstraintViolation(code="MATERIAL_SHORTAGE", message=f"Week {week}: materials limit {order.product_id} to {actual_qty:.1f} units"))

            for material_id, per_unit in bom.items():
                material_inv[material_id] -= actual_qty * float(per_unit)

            base_hours = actual_qty * hpu
            used_hours[line] += min(base_hours, max(0.0, line_capacity[line][week - 1] - used_hours[line]))
            actual_ot = max(0.0, base_hours - line_capacity[line][week - 1])
            overtime_cost += actual_ot * float(costs.get("overtime_per_hour", 0.0))
            production_cost += actual_qty * float(product.get("production_cost", 0.0))
            fg_inv[order.product_id] += actual_qty
            week_produced[order.product_id] = week_produced.get(order.product_id, 0.0) + actual_qty

            log_event(
                logger,
                "simulation.production.executed",
                level=logging.DEBUG,
                week=week,
                product_id=order.product_id,
                line_id=line,
                requested_quantity=order.quantity,
                actual_quantity=actual_qty,
                required_hours=required_hours,
                overtime_hours=actual_ot,
                material_inventory_after=dict(material_inv),
            )

            if line in line_last_product and line_last_product[line] != order.product_id:
                changeover_cost += float(costs.get("changeover_cost", 0.0))
            line_last_product[line] = order.product_id

        for product_id in case["products"]:
            demand = _actual_demand(case, scenario, product_id, week)
            total_demand += demand
            served = min(fg_inv[product_id], demand)
            fg_inv[product_id] -= served
            total_served += served
            week_demand[product_id] = demand
            week_served[product_id] = served
            lost = demand - served
            lost_units += lost
            lost_sales_cost += lost * float(costs.get("lost_sale_per_unit", 0.0))
            stockout_cost += lost * float(costs.get("stockout_per_unit", 0.0))

        holding_rate = float(costs.get("holding_per_unit_week", 0.0))
        holding_cost += sum(max(0.0, q) for q in material_inv.values()) * holding_rate
        holding_cost += sum(max(0.0, q) for q in fg_inv.values()) * holding_rate
        log_event(
            logger,
            "simulation.week.completed",
            level=logging.DEBUG,
            week=week,
            demand=week_demand,
            served=week_served,
            produced=week_produced,
            material_inventory=dict(material_inv),
            finished_inventory=dict(fg_inv),
            used_hours=dict(used_hours),
            cumulative_holding_cost=holding_cost,
            cumulative_lost_units=lost_units,
        )

    service_level = 1.0 if total_demand <= 0 else total_served / total_demand
    target = float(policy.get("service_level_target", 0.0))
    if service_level + 1e-9 < target:
        violations.append(ConstraintViolation(code="SERVICE_LEVEL", message=f"Service {service_level:.3f} below target {target:.3f}", critical=False))

    # Negative inventory should never survive the production limiter.
    for material_id, qty in material_inv.items():
        if qty < -1e-6:
            violations.append(ConstraintViolation(code="NEGATIVE_INVENTORY", message=f"{material_id}: {qty:.2f}"))

    total = sum([
        purchase_cost, production_cost, overtime_cost, expedite_cost, working_capital_cost,
        holding_cost, lost_sales_cost, stockout_cost, downtime_cost, changeover_cost,
    ])
    breakdown = {
        "purchase": purchase_cost,
        "production": production_cost,
        "overtime": overtime_cost,
        "expedite": expedite_cost,
        "working_capital": working_capital_cost,
        "holding": holding_cost,
        "lost_sales": lost_sales_cost,
        "stockout": stockout_cost,
        "line_stop": downtime_cost,
        "changeover": changeover_cost,
    }
    critical = [v for v in violations if v.critical]
    log_event(
        logger,
        "simulation.completed",
        team_id=plan.team_id,
        scenario_id=plan.scenario_id,
        feasible=len(critical) == 0,
        service_level=service_level,
        total_demand=total_demand,
        total_served=total_served,
        lost_units=lost_units,
        line_stop_hours=line_stop_hours,
        total_cost=round(total, 2),
        cost_breakdown={k: round(v, 2) for k, v in breakdown.items()},
        ending_material_inventory={k: round(v, 3) for k, v in material_inv.items()},
        ending_finished_inventory={k: round(v, 3) for k, v in fg_inv.items()},
        violations=[v.model_dump() for v in violations],
    )
    return SimulationResult(
        feasible=len(critical) == 0,
        service_level=max(0.0, min(1.0, service_level)),
        total_cost=round(total, 2),
        cost_breakdown={k: round(v, 2) for k, v in breakdown.items()},
        violations=violations,
        ending_material_inventory={k: round(v, 3) for k, v in material_inv.items()},
        ending_finished_inventory={k: round(v, 3) for k, v in fg_inv.items()},
        line_stop_hours=round(line_stop_hours, 3),
        lost_units=round(lost_units, 3),
    )
