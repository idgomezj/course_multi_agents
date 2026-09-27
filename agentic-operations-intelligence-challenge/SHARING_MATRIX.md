# Sharing boundary after Data API split

## Students receive

### Local application
- frontend;
- FastAPI challenge backend;
- Pydantic AI Manager;
- tool implementations;
- simulator/public evaluator code;
- schemas;
- training script;
- their editable `models/`, `rag/`, and `skills/` workspace.

### Credentials/configuration
- `DATA_API_URL`;
- one `DATA_API_TOKEN` authorized only for their assigned team;
- LLM credentials according to the course deployment model.

### Delivered through the Data API
Only for their authorized team:
- business case data;
- demand/inventory/BOM/supplier/capacity data;
- policies and known cost parameters;
- RAG source documents;
- PyTorch model contract;
- public training data;
- public scenarios.

## Do NOT put in the student application

Do not copy team data into:
- `cases/`;
- local JSON/YAML fixtures;
- notebooks committed with full datasets;
- local RAG document folders;
- model-spec files that duplicate the API contract.

The application must fail clearly if the Data API is unavailable rather than silently falling back to embedded data.

## Instructor-owned private assets

Never send through the student-facing Data API:
- final hidden scenarios;
- hidden scenario seeds;
- final PyTorch holdout data;
- hidden RAG queries/expected evidence;
- final benchmark plans/costs;
- hidden realized future events;
- final evaluator credentials;
- team-token mapping.

## Important repository warning

The repository `idgomezj/course_multi_agents` is public. A Git branch is **not** a security boundary. The service branch is architecturally independent, but its source/data can still be inspected on GitHub while the repo is public.

For the actual class, the recommended deployment is:

```text
PRIVATE instructor source/deployment
        ↓
Agentic Operations Data API
        ↓ team-scoped token
Student application
```

Keep the public service branch as development/reference code only, or move/copy it to a private repository before distributing credentials.
