from __future__ import annotations

import argparse
import json
import os
from dataclasses import asdict, dataclass
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"


@dataclass(frozen=True)
class DisruptionScenario:
    product: str
    baseline_weekly_demand: int
    demand_increase_pct: float
    on_hand_inventory: int
    inbound_units: int
    inbound_delay_days: int
    extra_production_capacity: int


@dataclass(frozen=True)
class AgentReport:
    agent: str
    facts: dict[str, float | int | str | bool]
    recommendation: str


@dataclass(frozen=True)
class IntegratedPlan:
    forecast_demand: int
    required_replenishment: int
    extra_production: int
    expedited_procurement: int
    projected_supply: int
    service_gap: int
    risk_level: str
    actions: list[str]


@dataclass(frozen=True)
class ValidationResult:
    passed: bool
    checks: dict[str, bool]
    issues: list[str]


class DemandAgent:
    def analyze(self, scenario: DisruptionScenario) -> AgentReport:
        forecast = round(
            scenario.baseline_weekly_demand
            * (1 + scenario.demand_increase_pct)
        )

        return AgentReport(
            agent="demand-agent",
            facts={
                "baseline_demand": scenario.baseline_weekly_demand,
                "demand_increase_pct": scenario.demand_increase_pct,
                "forecast_demand": forecast,
            },
            recommendation=(
                f"Plan against forecast demand of {forecast} units."
            ),
        )


class InventoryAgent:
    def analyze(
        self,
        scenario: DisruptionScenario,
        forecast_demand: int,
    ) -> AgentReport:
        available_with_inbound = (
            scenario.on_hand_inventory
            + scenario.inbound_units
        )

        replenishment = max(
            forecast_demand - available_with_inbound,
            0,
        )

        return AgentReport(
            agent="inventory-agent",
            facts={
                "on_hand_inventory": scenario.on_hand_inventory,
                "inbound_units": scenario.inbound_units,
                "available_with_inbound": available_with_inbound,
                "required_replenishment": replenishment,
            },
            recommendation=(
                f"Secure {replenishment} additional units "
                "to cover the forecast."
            ),
        )


class ProductionAgent:
    def analyze(
        self,
        scenario: DisruptionScenario,
        required_replenishment: int,
    ) -> AgentReport:
        feasible_extra = min(
            required_replenishment,
            scenario.extra_production_capacity,
        )

        return AgentReport(
            agent="production-agent",
            facts={
                "extra_capacity": scenario.extra_production_capacity,
                "feasible_extra_production": feasible_extra,
            },
            recommendation=(
                f"Produce up to {feasible_extra} extra units."
            ),
        )


class LogisticsAgent:
    def analyze(self, scenario: DisruptionScenario) -> AgentReport:
        high_delay = scenario.inbound_delay_days >= 3

        risk = (
            "high"
            if high_delay
            else "moderate"
            if scenario.inbound_delay_days > 0
            else "low"
        )

        return AgentReport(
            agent="logistics-agent",
            facts={
                "inbound_units": scenario.inbound_units,
                "inbound_delay_days": scenario.inbound_delay_days,
                "delay_risk": risk,
            },
            recommendation=(
                "Treat inbound supply as at-risk and prepare "
                "an expedited contingency."
                if high_delay
                else
                "Monitor inbound supply under the normal plan."
            ),
        )


class Coordinator:
    def integrate(
        self,
        scenario: DisruptionScenario,
        demand: AgentReport,
        inventory: AgentReport,
        production: AgentReport,
        logistics: AgentReport,
    ) -> IntegratedPlan:
        forecast = int(
            demand.facts["forecast_demand"]
        )

        required = int(
            inventory.facts["required_replenishment"]
        )

        extra_production = int(
            production.facts["feasible_extra_production"]
        )

        residual = max(
            required - extra_production,
            0,
        )

        delay_risk = str(
            logistics.facts["delay_risk"]
        )

        expedited = (
            residual
            if delay_risk == "high"
            else 0
        )

        projected_supply = (
            scenario.on_hand_inventory
            + scenario.inbound_units
            + extra_production
            + expedited
        )

        service_gap = max(
            forecast - projected_supply,
            0,
        )

        risk_level = (
            "high"
            if service_gap > 0
            else "moderate"
            if delay_risk == "high"
            else "low"
        )

        actions = [
            f"Increase production by {extra_production} units.",
        ]

        if expedited > 0:
            actions.append(
                f"Expedite {expedited} units from an alternate source."
            )

        if delay_risk == "high":
            actions.append(
                "Monitor the delayed inbound shipment daily."
            )

        if service_gap > 0:
            actions.append(
                f"Escalate unresolved service gap of {service_gap} units."
            )

        return IntegratedPlan(
            forecast_demand=forecast,
            required_replenishment=required,
            extra_production=extra_production,
            expedited_procurement=expedited,
            projected_supply=projected_supply,
            service_gap=service_gap,
            risk_level=risk_level,
            actions=actions,
        )


class PlanValidator:
    def validate(
        self,
        scenario: DisruptionScenario,
        plan: IntegratedPlan,
    ) -> ValidationResult:
        checks = {
            "production_within_capacity":
                plan.extra_production
                <= scenario.extra_production_capacity,
            "non_negative_procurement":
                plan.expedited_procurement >= 0,
            "service_gap_non_negative":
                plan.service_gap >= 0,
            "supply_arithmetic":
                plan.projected_supply
                == (
                    scenario.on_hand_inventory
                    + scenario.inbound_units
                    + plan.extra_production
                    + plan.expedited_procurement
                ),
        }

        issues = [
            name
            for name, passed in checks.items()
            if not passed
        ]

        return ValidationResult(
            passed=not issues,
            checks=checks,
            issues=issues,
        )


def build_local_solution(
    scenario: DisruptionScenario,
) -> dict:
    demand_agent = DemandAgent()
    inventory_agent = InventoryAgent()
    production_agent = ProductionAgent()
    logistics_agent = LogisticsAgent()

    demand = demand_agent.analyze(
        scenario
    )

    inventory = inventory_agent.analyze(
        scenario,
        int(demand.facts["forecast_demand"]),
    )

    production = production_agent.analyze(
        scenario,
        int(inventory.facts["required_replenishment"]),
    )

    logistics = logistics_agent.analyze(
        scenario
    )

    plan = Coordinator().integrate(
        scenario,
        demand,
        inventory,
        production,
        logistics,
    )

    validation = PlanValidator().validate(
        scenario,
        plan,
    )

    return {
        "scenario": asdict(scenario),
        "agent_reports": [
            asdict(demand),
            asdict(inventory),
            asdict(production),
            asdict(logistics),
        ],
        "integrated_plan": asdict(plan),
        "validation": asdict(validation),
    }


def llm_supervisor(
    local_state: dict,
) -> dict:
    try:
        from dotenv import load_dotenv
        from pydantic import BaseModel, Field
        from pydantic_ai import Agent
    except ImportError as exc:
        raise RuntimeError(
            "LLM mode requires: "
            "python -m pip install -r requirements.txt"
        ) from exc

    load_dotenv(
        BASE_DIR / ".env"
    )

    model = os.getenv(
        "LLM_MODEL"
    )

    if not model:
        raise RuntimeError(
            "Set LLM_MODEL in .env before using --llm."
        )

    class ExecutiveDecision(BaseModel):
        summary: str
        priorities: list[str] = Field(
            min_length=2,
            max_length=4,
        )
        risks: list[str] = Field(
            min_length=1,
            max_length=4,
        )
        approved: bool

    supervisor = Agent(
        model,
        output_type=ExecutiveDecision,
        instructions=(
            "You are a supervisor agent. "
            "Use only the supplied deterministic agent reports. "
            "Do not invent operational facts. "
            "Approve only if validation passed."
        ),
    )

    result = supervisor.run_sync(
        json.dumps(
            local_state,
            indent=2,
        )
    )

    return {
        "model": model,
        "decision": result.output.model_dump(),
        "usage": str(result.usage),
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Multi-agent operational disruption capstone."
        )
    )

    parser.add_argument(
        "--llm",
        action="store_true",
        help=(
            "Add an optional external-LLM supervisor "
            "after the local SMA has produced and validated its plan."
        ),
    )

    args = parser.parse_args()

    scenario = DisruptionScenario(
        product="PUMP-X",
        baseline_weekly_demand=100,
        demand_increase_pct=0.35,
        on_hand_inventory=70,
        inbound_units=20,
        inbound_delay_days=4,
        extra_production_capacity=35,
    )

    state = build_local_solution(
        scenario
    )

    if args.llm:
        state["llm_supervisor"] = llm_supervisor(
            state
        )

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_file = (
        OUTPUT_DIR
        / "capstone_result.json"
    )

    output_file.write_text(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    print(
        json.dumps(
            state,
            indent=2,
            ensure_ascii=False,
        )
    )

    print(
        f"\nSaved: {output_file}"
    )


if __name__ == "__main__":
    main()
