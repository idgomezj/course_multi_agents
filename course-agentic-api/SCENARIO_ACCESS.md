# Scenario Access Control

This file documents the two-token scenario model used by the Data API.

The authoritative token/policy file is:

```text
agentic-operations-data-api/data/scenario_access.json
```

## Tokens

| Team | Public scenario token | Hidden scenario token |
|---|---|---|
| Team 1 | `scn_t1_pub_c7a64b9e0f2d4a1b8e5c79d3f06a21b4` | `scn_t1_hid_91e5c3a7b2d84f06a1c9e47b5d30f268` |
| Team 2 | `scn_t2_pub_4d8a1f73c6e209b5a8473d1e6c92f054` | `scn_t2_hid_b3f0751c8a6d42e99f3147c05e8a26bd` |
| Team 3 | `scn_t3_pub_85c1e7b402ad4936bf7051d9a63e28fc` | `scn_t3_hid_2a94d6f17cbe40858d31e7a64f09bc52` |
| Team 4 | `scn_t4_pub_f31a8c406e7b25d9940c1fa683bd572e` | `scn_t4_hid_6d0b24f9c18e437aa5f7031cb82e964d` |
| Team 5 | `scn_t5_pub_19e4c7a52d8b4306af91d3e705bc264f` | `scn_t5_hid_a6073f9d1c4e58b2d9306af17e45bc82` |

These checked-in values are development/course-control credentials. If this repository is visible to students, they are not secrets. For a real deployment, override only the token values with `SCENARIO_TOKENS_JSON` or store the access file outside the student-visible repository.

## Where scenarios live

Public scenarios are currently defined in:

```text
data/teams/team_1.yaml
data/teams/team_2.yaml
data/teams/team_3.yaml
data/teams/team_4.yaml
data/teams/team_5.yaml
```

under each file's `public_scenarios:` section.

Hidden scenarios are defined in:

```text
data/scenarios/team_1/hidden.json
data/scenarios/team_2/hidden.json
data/scenarios/team_3/hidden.json
data/scenarios/team_4/hidden.json
data/scenarios/team_5/hidden.json
```

The full stored scenario may contain fields such as `realized` and evaluator expectations. Those fields are internal and are not returned to the student token.

## Token-selected endpoints

Preferred endpoints:

```text
GET /v1/teams/{team_id}/scenarios
GET /v1/teams/{team_id}/scenarios/{scenario_id}
POST /v1/teams/{team_id}/scenarios/{scenario_id}/evaluate
```

Send either:

```text
X-Scenario-Token: <token>
```

or, for backward compatibility:

```text
X-Team-Token: <token>
```

The token decides the scenario scope. There is no request parameter a student can use to promote a public token to hidden access.

### Public token

- lists only public scenarios;
- scenario detail returns only fields configured in `public.detail_fields`;
- can evaluate only public scenarios.

### Hidden token

- lists only hidden scenarios;
- list response intentionally omits `visible` by default;
- scenario detail reveals the configured student-visible information;
- never returns `realized`, benchmark/oracle values, or private evaluator expectations;
- can evaluate only hidden scenarios.

## Controlling what is shared

Edit `data/scenario_access.json`.

For each team and scope you can independently change:

```json
{
  "token": "...",
  "list_fields": ["id", "title", "description"],
  "detail_fields": ["id", "title", "description", "visible"],
  "evaluation_fields": ["team_id", "scenario_id", "operational_score"]
}
```

The backend projects the internal scenario/evaluation object to exactly those configured fields.

## Important deployment note

If students can clone the branch containing `data/scenarios/**/hidden.json`, no HTTP token can make those files hidden. For a real hidden exam, deploy this service from an instructor-only/private repository or inject the hidden scenario directory into the server at deployment time. Give students the hidden token when you want them to access that hidden scenario set through the API, not repository access to the underlying files.

## Current hidden-set status

The access mechanism is operational and each graded team currently has three hidden scenario definitions (`H01`–`H03`) to exercise the flow. These are the initial hidden set, not the final 20-scenario suite described in the instructor blueprint. Their final benchmark costs still need calibration before they should be used for final cost-gap grading.


## Canonical public start context

The first context endpoint is intentionally easier to consume:

```text
GET /v1/teams/{team_id}/start-context
```

For the public context, no token and no client-identification header are required. A request with no AI-identifying signal is treated as a normal human/browser request.

Example:

```bash
curl http://localhost:8100/v1/teams/team_3/start-context
```

A valid hidden scenario token is still required to make this endpoint operate in hidden scope. An invalid token is rejected rather than silently downgraded to public.
