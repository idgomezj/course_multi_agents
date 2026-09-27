from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProductionOrder(BaseModel):
    week: int = Field(ge=1, le=4)
    product_id: str
    quantity: float = Field(ge=0)
    line_id: str | None = None
    overtime_hours: float = Field(default=0, ge=0)


class PurchaseOrder(BaseModel):
    material_id: str
    supplier_id: str
    quantity: float = Field(gt=0)
    order_day: int = Field(ge=1, le=31)
    expedite: bool = False


class PlanAction(BaseModel):
    action_type: str
    reason: str
    requires_approval: bool = False


class MonthlyOperationsPlan(BaseModel):
    team_id: str
    scenario_id: str
    production_plan: list[ProductionOrder]
    purchase_orders: list[PurchaseOrder]
    actions: list[PlanAction] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)
    explanation: str = ""


class ToolTraceEntry(BaseModel):
    tool: str
    inputs: dict[str, Any]
    output: Any


class ConstraintViolation(BaseModel):
    code: str
    message: str
    critical: bool = True


class SimulationResult(BaseModel):
    feasible: bool
    service_level: float = Field(ge=0, le=1)
    total_cost: float = Field(ge=0)
    cost_breakdown: dict[str, float]
    violations: list[ConstraintViolation]
    ending_material_inventory: dict[str, float]
    ending_finished_inventory: dict[str, float]
    line_stop_hours: float = 0
    lost_units: float = 0


class EvaluationResult(BaseModel):
    team_id: str
    scenario_id: str
    operational_score: float = Field(ge=0, le=100)
    feasibility_score: float = Field(ge=0, le=100)
    service_score: float = Field(ge=0, le=100)
    cost_score: float = Field(ge=0, le=100)
    skill_tool_score: float = Field(ge=0, le=100)
    rag_score: float = Field(ge=0, le=100)
    total_cost: float
    benchmark_cost: float | None = None
    cost_gap: float | None = None
    violations: list[ConstraintViolation]
    trace: list[ToolTraceEntry]
    plan: MonthlyOperationsPlan
    evaluation_breakdown: dict[str, Any] = Field(default_factory=dict)
