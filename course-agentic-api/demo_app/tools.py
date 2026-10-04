import math
from statistics import mean, pstdev
from typing import Any

from pydantic_ai import RunContext

from .cost_engine import estimate_plan_cost, supplier_unit_cost
from .runtime import RuntimeDeps
from .schemas import MonthlyOperationsPlan
from .simulator import simulate_month


def _model_key_for_task(ctx: RunContext[RuntimeDeps], task: str) -> str | None:
    for key, spec in ctx.deps.models.spec.get("models", {}).items():
        if spec.get("task") == task:
            return key
    return None


def _predict_or_none(ctx: RunContext[RuntimeDeps], task: str, features: dict[str, float]) -> list[float] | None:
    key = _model_key_for_task(ctx, task)
    if not key or not ctx.deps.models.has_model(key):
        return None
    return ctx.deps.models.predict(key, features)


def _supplier_options(case: dict[str, Any], material_id: str) -> list[dict[str, Any]]:
    out = []
    for sid, supplier in case["suppliers"].items():
        if material_id in supplier.get("materials", []):
            out.append({
                "supplier_id": sid,
                "unit_cost": supplier["unit_cost"][material_id],
                "lead_time_days": supplier["lead_time_days"],
                "reliability": supplier["reliability"],
                "quality_score": supplier["quality_score"],
                "moq": supplier.get("moq", {}).get(material_id, 0),
            })
    return out


def _downtime_features(ctx: RunContext[RuntimeDeps], line_id: str) -> dict[str, float]:
    line = ctx.deps.case["lines"][line_id]
    visible = ctx.deps.scenario.get("visible", {})
    return {
        "recent_downtime": float(visible.get("recent_downtime", {}).get(line_id, line.get("recent_downtime", 4))),
        "maintenance_age_days": float(visible.get("maintenance_age_days", {}).get(line_id, line.get("maintenance_age_days", 30))),
        "utilization": float(visible.get("utilization", {}).get(line_id, line.get("utilization", 0.8))),
        "runtime_hours": float(line["weekly_hours"]),
        "overload": float(visible.get("overload", {}).get(line_id, 0.0)),
    }


def _downtime_probability(ctx: RunContext[RuntimeDeps], line_id: str) -> float:
    features = _downtime_features(ctx, line_id)
    pred = _predict_or_none(ctx, "downtime_risk", features)
    if pred:
        return max(0.0, min(1.0, float(pred[0])))
    return max(0.0, min(1.0, features["recent_downtime"] / 25 + max(0, features["utilization"] - 0.8)))


def list_skills(ctx: RunContext[RuntimeDeps]) -> list[dict[str, str]]:
    """List the procedural Skills available to the Manager for this operation."""
    return ctx.deps.record("list_skills", {}, ctx.deps.skills.list())


def load_skill(ctx: RunContext[RuntimeDeps], name: str) -> str:
    """Load one procedural Skill when it is relevant to the current problem."""
    out = ctx.deps.skills.load(name)
    return ctx.deps.record("load_skill", {"name": name}, out)


def search_knowledge(ctx: RunContext[RuntimeDeps], query: str, top_k: int | None = None) -> list[dict]:
    """Retrieve company policies, contracts and operational knowledge through RAG."""
    out = ctx.deps.rag.search(query, top_k)
    for item in out:
        ctx.deps.rag_hits.add(item["source"])
    return ctx.deps.record("search_knowledge", {"query": query, "top_k": top_k}, out)


def get_business_constraints(ctx: RunContext[RuntimeDeps]) -> dict[str, Any]:
    """Return authoritative company constraints and solved planning preferences."""
    out = {
        "hard_policies": ctx.deps.case.get("policies", {}),
        "hard_constraints": ctx.deps.case.get("constraints", {}),
        "customer_priorities": ctx.deps.case.get("customer_priorities", {}),
        "planning_objectives": ctx.deps.student_config.get("planning_objectives", {}),
    }
    return ctx.deps.record("get_business_constraints", {}, out)


def get_student_configuration(ctx: RunContext[RuntimeDeps]) -> dict[str, Any]:
    """Return the solved Case 0 configuration currently loaded by the demo."""
    cfg = ctx.deps.student_config
    out = {
        "forecast_policy": cfg.get("forecast_policy", {}),
        "risk_policy": cfg.get("risk_policy", {}),
        "planning_objectives": cfg.get("planning_objectives", {}),
        "tool_policy": cfg.get("tool_policy", {}),
        "manager_llm": cfg.get("manager_llm", {}),
        "business_assumptions": cfg.get("business_assumptions", {}),
        "feature_config": cfg.get("feature_config", {}),
    }
    return ctx.deps.record("get_student_configuration", {}, out)


def get_inventory(ctx: RunContext[RuntimeDeps]) -> dict[str, Any]:
    """Return current raw-material and finished-goods inventory."""
    out = {
        "materials": {k: v["initial_inventory"] for k, v in ctx.deps.case["materials"].items()},
        "finished_goods": {k: v.get("initial_fg", 0) for k, v in ctx.deps.case["products"].items()},
    }
    return ctx.deps.record("get_inventory", {}, out)


def get_open_purchase_orders(ctx: RunContext[RuntimeDeps]) -> list[dict]:
    """Return purchase orders already placed and their expected arrival week."""
    return ctx.deps.record("get_open_purchase_orders", {}, ctx.deps.case.get("open_purchase_orders", []))


def get_bom(ctx: RunContext[RuntimeDeps], product_id: str) -> dict[str, float]:
    """Return the bill of materials for one finished product."""
    out = ctx.deps.case["bom"].get(product_id, {})
    return ctx.deps.record("get_bom", {"product_id": product_id}, out)


def calculate_bom_requirements(ctx: RunContext[RuntimeDeps], product_id: str, quantity: float) -> dict[str, float]:
    """Explode a product quantity into raw-material gross requirements."""
    out = {m: round(float(q) * quantity, 3) for m, q in ctx.deps.case["bom"][product_id].items()}
    return ctx.deps.record("calculate_bom_requirements", {"product_id": product_id, "quantity": quantity}, out)


def get_supplier_options(ctx: RunContext[RuntimeDeps], material_id: str) -> list[dict]:
    """Return authorized supplier options and commercial parameters for a material."""
    out = _supplier_options(ctx.deps.case, material_id)
    return ctx.deps.record("get_supplier_options", {"material_id": material_id}, out)


def get_production_capacity(ctx: RunContext[RuntimeDeps]) -> dict[str, Any]:
    """Return nominal weekly line capacity and product compatibility."""
    return ctx.deps.record("get_production_capacity", {}, ctx.deps.case["lines"])


def forecast_moving_average(ctx: RunContext[RuntimeDeps], product_id: str, window: int = 4) -> list[float]:
    """Low-variance moving-average demand forecast; often suitable for stable demand."""
    history = ctx.deps.case["products"][product_id]["demand_history"]
    value = mean(history[-max(1, min(window, len(history))):])
    out = [round(value, 2)] * 4
    return ctx.deps.record("forecast_moving_average", {"product_id": product_id, "window": window}, out)


def forecast_exponential_smoothing(ctx: RunContext[RuntimeDeps], product_id: str, alpha: float = 0.35) -> list[float]:
    """Exponentially weighted forecast emphasizing recent observations."""
    history = ctx.deps.case["products"][product_id]["demand_history"]
    level = float(history[0])
    for x in history[1:]:
        level = alpha * float(x) + (1 - alpha) * level
    out = [round(level, 2)] * 4
    return ctx.deps.record("forecast_exponential_smoothing", {"product_id": product_id, "alpha": alpha}, out)


def forecast_seasonal(ctx: RunContext[RuntimeDeps], product_id: str) -> list[float]:
    """Seasonal forecast using business-provided seasonal indices."""
    product = ctx.deps.case["products"][product_id]
    base = mean(product["demand_history"][-4:])
    out = [round(base * float(i), 2) for i in product.get("seasonal_indices", [1, 1, 1, 1])]
    return ctx.deps.record("forecast_seasonal", {"product_id": product_id}, out)


def forecast_pytorch(ctx: RunContext[RuntimeDeps], product_id: str) -> list[float]:
    """Use the team's trained PyTorch demand model."""
    product = ctx.deps.case["products"][product_id]
    history = [float(x) for x in product["demand_history"][-4:]]
    visible = ctx.deps.scenario.get("visible", {})
    avg = mean(history)
    features = {
        "last4_mean": avg,
        "last4_std": pstdev(history) if len(history) > 1 else 0.0,
        "trend": (history[-1] - history[0]) / max(1.0, history[0]),
        "promotion": 1.0 if product_id in visible.get("promotion_products", []) else 0.0,
        "price_index": float(visible.get("price_index", {}).get(product_id, 1.0)),
        "confirmed_orders": float(visible.get("confirmed_orders", {}).get(product_id, avg)),
        "seasonal_index": float(product.get("seasonal_indices", [1.0])[0]),
    }
    pred = _predict_or_none(ctx, "demand_forecast", features)
    if pred is None:
        level = avg
        out = [round(level, 2)] * 4
    else:
        out = [round(max(0.0, x), 2) for x in pred[:4]]
    return ctx.deps.record("forecast_pytorch", {"product_id": product_id}, out)


def estimate_forecast_uncertainty(ctx: RunContext[RuntimeDeps], product_id: str) -> float:
    """Estimate forecast uncertainty using the team's trained uncertainty model."""
    product = ctx.deps.case["products"][product_id]
    history = [float(x) for x in product["demand_history"][-4:]]
    visible = ctx.deps.scenario.get("visible", {})
    avg = mean(history)
    features = {
        "last4_std": pstdev(history) if len(history) > 1 else 0.0,
        "promotion": 1.0 if product_id in visible.get("promotion_products", []) else 0.0,
        "trend_abs": abs((history[-1] - history[0]) / max(1.0, history[0])),
        "forecast_disagreement": float(visible.get("forecast_disagreement", {}).get(product_id, 0.1)),
        "confirmed_ratio": float(visible.get("confirmed_orders", {}).get(product_id, avg)) / max(1.0, avg),
    }
    pred = _predict_or_none(ctx, "demand_uncertainty", features)
    value = float(pred[0]) if pred else min(1.0, features["last4_std"] / max(1.0, avg))
    out = round(max(0.0, min(1.0, value)), 4)
    return ctx.deps.record("estimate_forecast_uncertainty", {"product_id": product_id}, out)


def forecast_consensus(ctx: RunContext[RuntimeDeps], product_id: str) -> dict[str, Any]:
    """Combine demand signals using the solved Case 0 forecast policy."""
    product = ctx.deps.case["products"][product_id]
    visible = ctx.deps.scenario.get("visible", {})
    history = [float(x) for x in product["demand_history"]]
    avg = mean(history[-4:])

    moving = [mean(history[-4:])] * 4
    level = float(history[0])
    for x in history[1:]:
        level = 0.35 * float(x) + 0.65 * level
    exponential = [level] * 4
    seasonal = [avg * float(i) for i in product.get("seasonal_indices", [1, 1, 1, 1])[:4]]

    confirmed_raw = visible.get("confirmed_orders", {}).get(product_id, avg)
    if isinstance(confirmed_raw, list):
        confirmed = [float(confirmed_raw[min(i, len(confirmed_raw) - 1)]) for i in range(4)]
    else:
        confirmed = [float(confirmed_raw)] * 4

    model_pred = _predict_or_none(
        ctx,
        "demand_forecast",
        {
            "last4_mean": avg,
            "last4_std": pstdev(history[-4:]) if len(history[-4:]) > 1 else 0.0,
            "trend": (history[-1] - history[-4]) / max(1.0, history[-4]),
            "promotion": 1.0 if product_id in visible.get("promotion_products", []) else 0.0,
            "price_index": float(visible.get("price_index", {}).get(product_id, 1.0)),
            "confirmed_orders": confirmed[0],
            "seasonal_index": float(product.get("seasonal_indices", [1.0])[0]),
        },
    )
    model_values = [max(0.0, float(x)) for x in (model_pred[:4] if model_pred else [avg] * 4)]

    # Case 0 does not train a demand-uncertainty specialist, so use observable
    # history/disagreement as a transparent uncertainty proxy for the worked example.
    historical_ratio = (pstdev(history[-4:]) / max(1.0, avg)) if len(history[-4:]) > 1 else 0.0
    visible_disagreement = float(visible.get("forecast_disagreement", {}).get(product_id, historical_ratio))
    uncertainty = max(0.0, min(1.0, max(historical_ratio, visible_disagreement)))

    policy = ctx.deps.student_config.get("forecast_policy", {})
    weights = dict(policy.get("weights", {}))
    high = uncertainty >= float(policy.get("high_uncertainty_threshold", 0.30))
    if high:
        weights["model_a"] = float(weights.get("model_a", 0.0)) * float(policy.get("high_uncertainty_model_multiplier", 0.80))
        weights["confirmed_orders"] = float(weights.get("confirmed_orders", 0.0)) * float(policy.get("high_uncertainty_confirmed_multiplier", 1.15))
    total_weight = sum(max(0.0, float(v)) for v in weights.values()) or 1.0
    weights = {k: max(0.0, float(v)) / total_weight for k, v in weights.items()}

    components = {
        "model_a": model_values,
        "confirmed_orders": confirmed,
        "moving_average": moving,
        "exponential_smoothing": exponential,
        "seasonal": seasonal,
    }
    consensus = [
        round(max(0.0, sum(weights.get(name, 0.0) * values[week] for name, values in components.items())), 2)
        for week in range(4)
    ]
    out = {
        "product_id": product_id,
        "consensus": consensus,
        "uncertainty": round(uncertainty, 4),
        "high_uncertainty": high,
        "weights": {k: round(v, 4) for k, v in weights.items()},
        "components": {k: [round(float(x), 2) for x in v] for k, v in components.items()},
    }
    return ctx.deps.record("forecast_consensus", {"product_id": product_id}, out)


def predict_excess_inventory_risk(ctx: RunContext[RuntimeDeps], product_id: str, planned_production: float, forecast_total: float) -> float:
    """Predict risk of ending the horizon with economically excessive finished inventory."""
    product = ctx.deps.case["products"][product_id]
    incoming = 0.0
    features = {
        "on_hand": float(product.get("initial_fg", 0.0)),
        "incoming": incoming + planned_production,
        "forecast_total": forecast_total,
        "holding_cost": float(ctx.deps.case["costs"].get("holding_per_unit_week", 0.0)),
        "trend": (float(product["demand_history"][-1]) - float(product["demand_history"][-4])) / max(1.0, float(product["demand_history"][-4])),
    }
    pred = _predict_or_none(ctx, "excess_inventory_risk", features)
    value = float(pred[0]) if pred else (1.0 if features["on_hand"] + planned_production > forecast_total * 1.2 else 0.0)
    out = round(max(0.0, min(1.0, value)), 4)
    return ctx.deps.record("predict_excess_inventory_risk", {"product_id": product_id, "planned_production": planned_production, "forecast_total": forecast_total}, out)


def calculate_safety_stock(ctx: RunContext[RuntimeDeps], average_weekly_demand: float, uncertainty_ratio: float, lead_time_weeks: float = 1.0) -> float:
    """Calculate demand-uncertainty safety stock using the solved Case 0 factor."""
    factor = float(ctx.deps.student_config.get("risk_policy", {}).get("safety_stock_factor", 1.40))
    qty = average_weekly_demand * uncertainty_ratio * math.sqrt(max(0.1, lead_time_weeks)) * factor
    out = round(max(0.0, qty), 2)
    return ctx.deps.record(
        "calculate_safety_stock",
        {"average_weekly_demand": average_weekly_demand, "uncertainty_ratio": uncertainty_ratio, "lead_time_weeks": lead_time_weeks, "safety_stock_factor": factor},
        out,
    )


def classify_risk(ctx: RunContext[RuntimeDeps], risk_value: float, label: str = "risk") -> dict[str, Any]:
    """Classify a 0-1 risk value using the solved risk thresholds."""
    policy = ctx.deps.student_config.get("risk_policy", {})
    medium = float(policy.get("medium_threshold", 0.20))
    high = float(policy.get("high_threshold", 0.45))
    value = max(0.0, min(1.0, float(risk_value)))
    level = "high" if value >= high else ("medium" if value >= medium else "low")
    out = {"label": label, "value": round(value, 4), "level": level, "medium_threshold": medium, "high_threshold": high}
    return ctx.deps.record("classify_risk", {"risk_value": risk_value, "label": label}, out)


def calculate_reorder_point(ctx: RunContext[RuntimeDeps], average_daily_usage: float, lead_time_days: float, safety_stock: float) -> float:
    """Calculate reorder point from usage, lead time and safety stock."""
    out = round(average_daily_usage * lead_time_days + safety_stock, 2)
    return ctx.deps.record("calculate_reorder_point", {"average_daily_usage": average_daily_usage, "lead_time_days": lead_time_days, "safety_stock": safety_stock}, out)


def calculate_jit_requirement(ctx: RunContext[RuntimeDeps], gross_requirement: float, on_hand: float, incoming_before_need: float) -> float:
    """Calculate the smallest JIT order after usable on-hand and incoming supply."""
    out = round(max(0.0, gross_requirement - on_hand - incoming_before_need), 2)
    return ctx.deps.record("calculate_jit_requirement", {"gross_requirement": gross_requirement, "on_hand": on_hand, "incoming_before_need": incoming_before_need}, out)


def calculate_inventory_projection(ctx: RunContext[RuntimeDeps], opening: float, receipts: list[float], requirements: list[float]) -> list[float]:
    """Project four weekly ending-inventory balances."""
    balance = opening
    out = []
    for week in range(4):
        balance += float(receipts[week] if week < len(receipts) else 0)
        balance -= float(requirements[week] if week < len(requirements) else 0)
        out.append(round(balance, 2))
    return ctx.deps.record("calculate_inventory_projection", {"opening": opening, "receipts": receipts, "requirements": requirements}, out)


def _supplier_features(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float, urgency: float) -> dict[str, float]:
    supplier = ctx.deps.case["suppliers"][supplier_id]
    visible = ctx.deps.scenario.get("visible", {})
    typical = float(ctx.deps.case["materials"][material_id].get("typical_order_qty", max(quantity, 1.0)))
    return {
        "reliability": float(supplier["reliability"]),
        "recent_late_rate": float(visible.get("supplier_recent_late_rate", {}).get(supplier_id, 1 - supplier["reliability"])),
        "lead_time_days": float(supplier["lead_time_days"]),
        "order_qty_ratio": quantity / max(1.0, typical),
        "urgency": urgency,
        "season_risk": float(visible.get("season_risk", 0.2)),
    }


def predict_supplier_delay(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float, urgency: float = 0.5) -> float:
    """Predict probability that a supplier order arrives late."""
    features = _supplier_features(ctx, supplier_id, material_id, quantity, urgency)
    pred = _predict_or_none(ctx, "supplier_delay", features)
    value = float(pred[0]) if pred else 1 - features["reliability"] + 0.4 * features["recent_late_rate"]
    out = round(max(0.0, min(1.0, value)), 4)
    return ctx.deps.record("predict_supplier_delay", {"supplier_id": supplier_id, "material_id": material_id, "quantity": quantity, "urgency": urgency}, out)


def predict_arrival_time(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float, urgency: float = 0.5) -> float:
    """Predict expected supplier lead time in days."""
    features = _supplier_features(ctx, supplier_id, material_id, quantity, urgency)
    pred = _predict_or_none(ctx, "arrival_time", features)
    value = float(pred[0]) if pred else features["lead_time_days"] * (1 + features["recent_late_rate"])
    out = round(max(0.5, value), 2)
    return ctx.deps.record("predict_arrival_time", {"supplier_id": supplier_id, "material_id": material_id, "quantity": quantity, "urgency": urgency}, out)


def predict_supplier_quality(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float) -> float:
    """Predict probability of supplier quality rejection."""
    supplier = ctx.deps.case["suppliers"][supplier_id]
    visible = ctx.deps.scenario.get("visible", {})
    typical = float(ctx.deps.case["materials"][material_id].get("typical_order_qty", max(quantity, 1.0)))
    features = {
        "quality_score": float(supplier["quality_score"]),
        "recent_reject_rate": float(visible.get("supplier_recent_reject_rate", {}).get(supplier_id, 1 - supplier["quality_score"])),
        "order_qty_ratio": quantity / max(1.0, typical),
        "criticality": 1.0 if ctx.deps.case["materials"][material_id].get("critical", False) else 0.0,
        "process_change": float(visible.get("supplier_process_change", {}).get(supplier_id, 0.0)),
    }
    pred = _predict_or_none(ctx, "supplier_quality", features)
    value = float(pred[0]) if pred else features["recent_reject_rate"]
    out = round(max(0.0, min(1.0, value)), 4)
    return ctx.deps.record("predict_supplier_quality", {"supplier_id": supplier_id, "material_id": material_id, "quantity": quantity}, out)


def find_alternative_supplier(ctx: RunContext[RuntimeDeps], material_id: str, exclude_supplier_id: str | None = None) -> list[dict]:
    """Find authorized alternatives sorted by known unit cost."""
    out = [x for x in _supplier_options(ctx.deps.case, material_id) if x["supplier_id"] != exclude_supplier_id]
    out.sort(key=lambda x: x["unit_cost"])
    return ctx.deps.record("find_alternative_supplier", {"material_id": material_id, "exclude_supplier_id": exclude_supplier_id}, out)


def calculate_expedite_option(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float) -> dict[str, float]:
    """Estimate expedite premium and shortened nominal lead time."""
    supplier = ctx.deps.case["suppliers"][supplier_id]
    out = {
        "expedite_premium": round(quantity * float(ctx.deps.case["costs"].get("expedite_per_unit", 0)), 2),
        "estimated_lead_time_days": round(max(1.0, float(supplier["lead_time_days"]) * 0.55), 2),
    }
    return ctx.deps.record("calculate_expedite_option", {"supplier_id": supplier_id, "material_id": material_id, "quantity": quantity}, out)


def predict_downtime(ctx: RunContext[RuntimeDeps], line_id: str) -> float:
    """Predict downtime risk for a production line."""
    out = round(_downtime_probability(ctx, line_id), 4)
    return ctx.deps.record("predict_downtime", {"line_id": line_id}, out)


def predict_production_feasibility(ctx: RunContext[RuntimeDeps], line_id: str, product_id: str, quantity: float, week: int) -> float:
    """Predict probability a proposed production order completes in its week."""
    product, line = ctx.deps.case["products"][product_id], ctx.deps.case["lines"][line_id]
    visible = ctx.deps.scenario.get("visible", {})
    downtime = _downtime_probability(ctx, line_id)
    features = {
        "required_hours_ratio": quantity * float(product["hours_per_unit"]) / max(1.0, float(line["weekly_hours"])),
        "downtime_risk": downtime,
        "changeovers": float(visible.get("expected_changeovers", {}).get(line_id, 2)),
        "overtime_available": float(ctx.deps.case.get("policies", {}).get("max_overtime_hours_per_line_week", 0)),
        "labor_ratio": float(visible.get("labor_ratio", {}).get(line_id, 1.0)),
    }
    pred = _predict_or_none(ctx, "production_feasibility", features)
    value = float(pred[0]) if pred else 1.2 - features["required_hours_ratio"] - 0.3 * downtime
    out = round(max(0.0, min(1.0, value)), 4)
    return ctx.deps.record("predict_production_feasibility", {"line_id": line_id, "product_id": product_id, "quantity": quantity, "week": week}, out)


def calculate_overtime_option(ctx: RunContext[RuntimeDeps], hours: float) -> dict[str, float]:
    """Calculate allowed overtime and direct overtime cost."""
    max_hours = float(ctx.deps.case.get("policies", {}).get("max_overtime_hours_per_line_week", 0))
    allowed = min(max(0.0, hours), max_hours)
    out = {"allowed_hours": allowed, "cost": round(allowed * float(ctx.deps.case["costs"].get("overtime_per_hour", 0)), 2)}
    return ctx.deps.record("calculate_overtime_option", {"hours": hours}, out)


def optimize_production_plan(ctx: RunContext[RuntimeDeps], week: int, demand_by_product: dict[str, float]) -> list[dict[str, Any]]:
    """Greedy deterministic capacity helper; it proposes a feasible line assignment, not the final plan."""
    remaining = {line: float(cfg["weekly_hours"]) for line, cfg in ctx.deps.case["lines"].items()}
    out = []
    for product_id, qty in sorted(demand_by_product.items(), key=lambda x: x[0]):
        product = ctx.deps.case["products"][product_id]
        compatible = [line for line, cfg in ctx.deps.case["lines"].items() if product_id in cfg["products"]]
        compatible.sort(key=lambda line: (line != product.get("preferred_line"), -remaining[line]))
        left = float(qty)
        for line in compatible:
            if left <= 0:
                break
            hpu = float(product["hours_per_unit"])
            capacity_qty = remaining[line] / hpu
            assigned = min(left, capacity_qty)
            if assigned > 0:
                out.append({"week": week, "product_id": product_id, "quantity": round(assigned, 2), "line_id": line})
                remaining[line] -= assigned * hpu
                left -= assigned
        if left > 0:
            out.append({"week": week, "product_id": product_id, "unassigned_quantity": round(left, 2)})
    return ctx.deps.record("optimize_production_plan", {"week": week, "demand_by_product": demand_by_product}, out)


def calculate_purchase_cost(ctx: RunContext[RuntimeDeps], supplier_id: str, material_id: str, quantity: float) -> float:
    """Calculate direct purchase cost."""
    out = round(supplier_unit_cost(ctx.deps.case, supplier_id, material_id) * quantity, 2)
    return ctx.deps.record("calculate_purchase_cost", {"supplier_id": supplier_id, "material_id": material_id, "quantity": quantity}, out)


def calculate_holding_cost(ctx: RunContext[RuntimeDeps], units: float, weeks: float = 1.0) -> float:
    """Calculate inventory holding cost."""
    out = round(max(0.0, units) * max(0.0, weeks) * float(ctx.deps.case["costs"].get("holding_per_unit_week", 0)), 2)
    return ctx.deps.record("calculate_holding_cost", {"units": units, "weeks": weeks}, out)


def calculate_stockout_cost(ctx: RunContext[RuntimeDeps], units: float) -> float:
    """Calculate stockout plus lost-sales penalty."""
    rate = float(ctx.deps.case["costs"].get("stockout_per_unit", 0)) + float(ctx.deps.case["costs"].get("lost_sale_per_unit", 0))
    out = round(max(0.0, units) * rate, 2)
    return ctx.deps.record("calculate_stockout_cost", {"units": units}, out)


def calculate_working_capital_cost(ctx: RunContext[RuntimeDeps], purchase_value: float) -> float:
    """Calculate working-capital charge associated with a purchase."""
    out = round(max(0.0, purchase_value) * float(ctx.deps.case["costs"].get("working_capital_rate", 0)), 2)
    return ctx.deps.record("calculate_working_capital_cost", {"purchase_value": purchase_value}, out)


def calculate_plan_cost(
    ctx: RunContext[RuntimeDeps],
    candidate_plan: MonthlyOperationsPlan,
) -> dict[str, float]:
    """Estimate known cost of a complete candidate MonthlyOperationsPlan before finalizing it."""
    plan = candidate_plan
    candidate_payload = plan.model_dump()
    out = estimate_plan_cost(ctx.deps.case, plan)
    return ctx.deps.record("calculate_plan_cost", {"candidate_plan": candidate_payload}, out)


def validate_plan(
    ctx: RunContext[RuntimeDeps],
    candidate_plan: MonthlyOperationsPlan,
) -> dict[str, Any]:
    """Validate a complete candidate MonthlyOperationsPlan in the deterministic simulator."""
    plan = candidate_plan
    candidate_payload = plan.model_dump()
    result = simulate_month(ctx.deps.case, ctx.deps.scenario, plan)
    out = {
        "feasible": result.feasible,
        "service_level": result.service_level,
        "violations": [v.model_dump() for v in result.violations],
        "estimated_realized_cost": result.total_cost,
    }
    return ctx.deps.record("validate_plan", {"candidate_plan": candidate_payload}, out)


ALL_TOOLS = [
    list_skills, load_skill, search_knowledge, get_business_constraints, get_student_configuration,
    get_inventory, get_open_purchase_orders, get_bom, calculate_bom_requirements,
    get_supplier_options, get_production_capacity,
    forecast_moving_average, forecast_exponential_smoothing, forecast_seasonal, forecast_pytorch, forecast_consensus,
    estimate_forecast_uncertainty, predict_excess_inventory_risk,
    calculate_safety_stock, classify_risk, calculate_reorder_point, calculate_jit_requirement, calculate_inventory_projection,
    predict_supplier_delay, predict_arrival_time, predict_supplier_quality,
    find_alternative_supplier, calculate_expedite_option,
    predict_downtime, predict_production_feasibility, calculate_overtime_option, optimize_production_plan,
    calculate_purchase_cost, calculate_holding_cost, calculate_stockout_cost, calculate_working_capital_cost,
    calculate_plan_cost, validate_plan,
]
