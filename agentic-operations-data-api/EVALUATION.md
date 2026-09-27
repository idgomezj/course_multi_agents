# Evaluation Guide — Data API and Case 0 Demo

This document defines how the public/development evaluator scores a run. It is the authoritative description of the score cards shown in the UI.

The evaluator reports three different kinds of information:

1. **Operational performance** — whether the plan actually works and how expensive it is.
2. **RAG quality** — whether the agent retrieved the business evidence expected for the scenario.
3. **Skills / Tools quality** — whether the agent used procedural Skills and operational tools in a disciplined way.

These are intentionally separated. A plan can be operationally feasible while still showing weak agent behavior, and a strong RAG score does not guarantee a good plan.

## 1. Operational score

### Feasibility

- Feasible plan: **100**
- Any critical feasibility violation: **0**

Feasibility is a gate. If the simulator reports the plan as infeasible, the final operational score is 0 regardless of service or cost.

### Service

    service_score = min(100, 100 × realized_service_level / service_level_target)

### Cost

    cost_gap = (student_cost - benchmark_cost) / benchmark_cost

| Cost gap vs benchmark | Cost score |
|---|---:|
| <= 5% | 100 |
| <= 10% | 90 |
| <= 20% | 75 |
| <= 30% | 60 |
| > 30% | decreases linearly from 60, with a minimum of 10 |

If the plan is infeasible, cost score is forced to 0.

### Final operational formula

For a feasible plan:

    Operational =
        35% Feasibility
      + 25% Service
      + 40% Cost

If the plan is infeasible:

    Operational = 0

The API response exposes the exact weighted contributions under evaluation_breakdown.operational.

## 2. RAG score

RAG is evaluated independently from operational performance.

Each public scenario can declare expected evidence sources under public_expectations.rag_expected_sources.

The score is source coverage:

    RAG score =
    100 × expected sources successfully retrieved / expected sources

The evaluator records sources touched by search_knowledge.

The response exposes:

- expected sources;
- expected sources actually retrieved;
- missing sources;
- all sources retrieved.

See evaluation_breakdown.rag.

Important: search_knowledge is scored here and is not double-counted as an operational-tool point in Skills / Tools.

## 3. Skills / Tools score

The previous evaluator mostly measured required tool names and could show 0% Skills/Tools even when Skills were actually used. It also penalized normal repeated use of a tool across different products.

The score is now explicitly decomposed into four parts.

### A. Skill usage — 25 points

| Behavior | Points |
|---|---:|
| list_skills called | 5 |
| At least one Skill loaded through load_skill | 20 |

This directly rewards use of the procedural Skill system.

### B. Expected operational tool coverage — 45 points

Each scenario can declare tools expected for that business problem.

Examples include forecast_pytorch, predict_supplier_delay, get_inventory, get_open_purchase_orders, calculate_bom_requirements, and get_supplier_options.

Coverage is proportional:

    45 × expected operational tools used / expected operational tools

The following are excluded from this 45-point bucket because they have their own scoring responsibility:

- list_skills
- load_skill
- search_knowledge
- calculate_plan_cost
- validate_plan

### C. Cost + validation discipline — 20 points

| Behavior | Points |
|---|---:|
| calculate_plan_cost called | 10 |
| validate_plan called | 10 |

### D. Efficiency — 10 points

A non-empty tool workflow starts with 10 efficiency points.

| Behavior | Penalty |
|---|---:|
| Each discouraged tool call | -5 |
| Exact duplicate call: same tool + same inputs | -2 |

Efficiency cannot go below 0.

Repeated calls with different inputs are not penalized. For example, forecasting FG01, FG02, and FG03 separately is normal.

An empty tool trace receives 0 efficiency points.

### Total

    Skills / Tools =
        Skill usage                 max 25
      + Expected operational tools max 45
      + Cost + validation          max 20
      + Efficiency                 max 10
                                    -------
                                    max 100

Detailed evidence is exposed under evaluation_breakdown.skills_tools, including:

- whether list_skills was called;
- exactly which Skills were loaded;
- expected, used, and missing operational tools;
- whether calculate_plan_cost was called;
- whether validate_plan was called;
- discouraged calls;
- exact duplicate-call count;
- component scores.

## 4. What is and is not included in Operational

RAG and Skills / Tools are diagnostic learning scores. They do not currently modify the operational score.

    Operational = what happened to the business.
    RAG = did the agent retrieve the right organizational evidence?
    Skills / Tools = did the agent follow a disciplined agentic workflow?

This allows the instructor to distinguish a feasible but expensive plan from a well-executed agent workflow.

## 5. Trace and transparency

Every tool call is captured in the run trace with:

- tool name;
- inputs;
- output.

The UI shows both the trace and the score breakdown.

The API returns the top-level scores plus an evaluation_breakdown object containing operational, rag, and skills_tools details.

## 6. Published reference versus AI Manager

### Published reference

The reference button runs a known reference plan through the deterministic simulator.

It evaluates:

- feasibility;
- realized service;
- realized cost;
- violations.

It does not score RAG or Skills / Tools because no AI Manager executes.

### AI Manager end-to-end

The AI Manager path executes:

    LLM Manager
    → Skills
    → RAG
    → PyTorch
    → deterministic tools
    → structured plan
    → simulator
    → evaluator

This path receives operational, RAG, and Skills / Tools scores plus the complete tool trace and detailed evaluation breakdown.

## 7. Public development evaluation versus final course evaluation

The public/development evaluator exists so students can improve their systems and understand failure modes.

The final course evaluation may use private:

- scenarios;
- realized outcomes;
- PyTorch holdouts;
- RAG queries;
- benchmark/oracle information;
- seeds.

Students must not have access to those hidden final assets. The scoring contract can remain the same while the final evidence stays private.

## 8. Course grade versus runtime scores

Do not confuse the runtime evaluator with the final academic grade.

The runtime evaluator measures one scenario execution.

If the course rubric separately awards points for PyTorch methodology, RAG design, Skill design, experiments, report, or defense, those academic rubric components are applied separately by the instructor.

## 9. Example interpretation

Example:

    Feasibility:  YES
    Service:      100%
    Cost Score:   10%
    RAG:          100%
    Skills/Tools: 65%

Interpretation:

- the plan can physically operate;
- customer service was achieved;
- the plan is far too expensive;
- the correct organizational evidence was retrieved;
- the agent followed only part of the intended planning workflow.


## 10. Case 0 T0-P01 expectations

For the fully solved reference scenario T0-P01, the benchmark stored with the scenario should match the current simulator result for the published reference plan.

The AI Manager does not need to reproduce the exact reference quantities, but a strong run should:

- remain feasible;
- meet the 99% service target;
- stay reasonably close to the reference benchmark;
- retrieve the expected RAG sources;
- load relevant Skills;
- use the expected operational tools;
- calculate candidate cost;
- validate the candidate before finalizing it.

The detailed score breakdown in the Case 0 UI is the preferred way to diagnose why a run earned a particular Skills / Tools score.
