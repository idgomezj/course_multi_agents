# Logging and Observability

The challenge application has structured logs across the full execution path so instructors and students can see what the system is doing internally.

## What is logged

Each HTTP request receives a `trace_id`. The same trace is propagated to the standalone Data API through `X-Trace-Id`.

The logs cover:

- HTTP request start/completion/failure and latency;
- selected LLM provider/model;
- Manager runtime construction;
- Manager prompt using only scenario-visible information;
- Manager run start/completion/failure;
- every tool call with safe/redacted inputs and outputs;
- Skill discovery and Skill loading;
- RAG index creation, search query, returned sources/chunks/scores;
- PyTorch model availability, loading, features, and predictions;
- outbound Data API requests, status, payload size, and latency;
- simulator/evaluator result summaries;
- feasibility, service, cost, RAG, and Skills/Tools score breakdowns;
- PyTorch training configuration, dataset size, progress, validation metrics, and export artifact.

## Trace and span IDs

Every log record contains:

- `trace_id` — one end-to-end request/run;
- `span_id` — the current operation context;
- `event` — stable event name;
- `data` — structured event details.

Tool trace entries returned to the frontend also contain `trace_id` and `span_id`.

The main app sends its current `trace_id` to the Data API, making it possible to correlate logs from both processes.

## Secret protection

Logging automatically redacts fields whose names look like:

- token;
- authorization;
- API key;
- password;
- secret;
- cookie;
- credential.

The code intentionally logs whether an authentication mechanism exists or succeeded, but never the credential value.

Do not log or print real `.env` contents.

## Configuration

Use the following environment variables:

```text
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/challenge.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5
LOG_PAYLOADS=true
LOG_MAX_VALUE_CHARS=4000
LOG_MAX_COLLECTION_ITEMS=100
```

### LOG_LEVEL

- `DEBUG` — maximum detail, including every training epoch;
- `INFO` — recommended normal development mode;
- `WARNING` — warnings/errors only;
- `ERROR` — errors only.

### LOG_FORMAT

Use:

```text
LOG_FORMAT=json
```

for structured machine-readable logs, or:

```text
LOG_FORMAT=text
```

for compact terminal-readable lines.

### LOG_PAYLOADS

`true` logs sanitized inputs/outputs for tools, RAG, model inference, etc.

Set:

```text
LOG_PAYLOADS=false
```

when you want only event names/summary metadata.

## Where logs go

The server always logs to stdout.

When `LOG_FILE` is configured, it additionally writes rotating logs to:

```text
logs/challenge.log
```

Rotation defaults to 10 MB per file with five backups.

## Example

```json
{
  "timestamp": "2026-09-27T20:00:00+00:00",
  "level": "INFO",
  "service": "agentic-operations-challenge",
  "trace_id": "7fd...",
  "span_id": "41b...",
  "event": "tool.completed",
  "data": {
    "tool": "forecast_pytorch",
    "team_id": "team_3",
    "scenario_id": "T3-P01",
    "tool_inputs": {"product_id": "FG01"},
    "tool_output": [1012.3, 1008.4, 1021.7, 1015.0]
  }
}
```

## Following one run

For JSON logs with `jq`:

```bash
tail -f logs/challenge.log | jq .
```

Find a trace:

```bash
grep '<TRACE_ID>' logs/challenge.log
```

The HTTP response header `X-Trace-Id` gives the trace ID for the request.

## Evaluation logs

The runtime evaluation remains documented separately in [EVALUATION.md](./EVALUATION.md). Logging explains **how execution reached the result**; evaluation explains **how the result was scored**.


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
