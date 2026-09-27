# Logging and Observability

The Data API and Case 0 demo emit correlated structured logs for the full execution path.

Each HTTP request receives a trace_id. The same trace is used by the Case 0 Manager, tool calls, RAG, Skills, PyTorch inference, simulator, evaluator, and score calculation.

Logged areas include:
- HTTP request start/completion/failure and latency;
- team authorization decisions without credential values;
- Data API asset loading;
- selected LLM provider/model;
- Manager prompt, lifecycle, tool count, RAG sources, and final plan;
- every tool call with sanitized inputs/outputs;
- Skill listing/loading;
- RAG index/search/hits/scores;
- PyTorch model loading and predictions;
- Case 0 model training progress and metrics;
- simulation PO scheduling, production, weekly state, inventories, service, and cost;
- evaluation scores and breakdowns.

## Configuration

Use environment variables:

LOG_LEVEL=INFO
LOG_FORMAT=text
LOG_FILE=logs/data-api.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_PAYLOADS=true
LOG_MAX_VALUE_CHARS=4000
LOG_MAX_COLLECTION_ITEMS=100

Use LOG_LEVEL=DEBUG for the most detailed simulator and training logs.

LOG_FORMAT=text is the default and recommended format for local development because it is easy to read directly in the terminal. Set LOG_FORMAT=json only when structured machine-readable output is specifically needed.

JSON logs include `file`, `line`, and `function`. Text logs show the same source location as `[filename.py:line:function]`, for example `[manager.py:214:run]`. This makes it possible to jump directly from a runtime event to the code that emitted it.

## Trace IDs

Every structured record includes:
- file — source Python filename that emitted the log
- line — source line number
- function — source function name
- trace_id
- span_id
- event
- data

The HTTP response includes X-Trace-Id. Search that value in the log file to reconstruct one complete run.

Example:

grep '<TRACE_ID>' logs/data-api.log

For the default text logs:

```bash
tail -f logs/data-api.log
```

If you explicitly switch to `LOG_FORMAT=json`, you can use:

```bash
tail -f logs/data-api.log | jq .
```

## Secret protection

Fields whose names indicate tokens, authorization headers, API keys, passwords, secrets, cookies, or credentials are automatically redacted.

The system may log whether credentials are configured or authentication succeeded, but it must never log the secret value itself.

## Relationship to evaluation

See EVALUATION.md for how a run is scored. Logging explains how the system reached the plan and score; evaluation documentation explains the scoring formula.


## PyTorch Export inference mode

Exported `.pt2` inference modules must not be passed through `.eval()` or `.train()` after `torch.export.load(...).module()`. PyTorch intentionally rejects those calls on exported GraphModules. The training/export scripts put the source model in evaluation mode before export, so runtime loading executes the exported inference graph directly. Legacy TorchScript `.pt` artifacts still use `.eval()` after loading.

If a runtime reports `Calling eval() is not supported yet.`, make sure the loader is not calling `.eval()` on the `.pt2` module.

## PyTorch Export concurrency

PyTorch Export deserialization uses process-global state internally. If two `torch.export.load(...)` calls overlap in different threads, PyTorch can raise an error such as:

```text
_CURRENT_DESERIALIZER is already set
```

The application prevents this in two ways:

1. all `.pt2` deserialization is protected by one process-wide lock;
2. available models are warmed up serially before the LLM is allowed to make concurrent tool calls.

Loaded inference modules are cached by artifact path, modification time, and size. Retraining a model changes that signature, so the new artifact is loaded on the next run.

Relevant log events:

```text
models.load.started
models.load.completed
models.load.cache_hit
models.load.failed
models.warmup.completed
models.predict.completed
```

If you upgraded from an older checkout that already produced the deserializer error, fully stop and restart the Python/Uvicorn process after pulling the fix. The lock exists in process memory and cannot repair an already running old process.
