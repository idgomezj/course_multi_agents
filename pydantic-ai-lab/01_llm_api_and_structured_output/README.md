# 01 — External LLM API and Structured Output

## Goal

Learn the minimum application-level concepts needed to call an external LLM professionally with Pydantic AI.

This module compresses:

- provider abstraction
- model strings
- API authentication
- instructions/prompts
- agent runs
- output vs messages
- typed structured output
- Pydantic validation
- token/cost usage
- run IDs and conversation IDs
- multi-turn history

## Run

From this directory:

```bash
python 01_basic_call.py
python 02_structured_output.py
python 03_conversation_history.py
```

## Mental model

```text
Python application
      ↓
Pydantic AI Agent
      ↓
provider/model selected by LLM_MODEL
      ↓
external LLM API
      ↓
response
```

Pydantic AI lets the application keep the same high-level code while the configured provider/model changes.

## Structured output

Free-form text:

```text
LLM
 ↓
"some text"
 ↓
application parses manually
```

Typed output:

```text
LLM
 ↓
Pydantic schema
 ↓
validated Python object
```

That is especially useful for agents because downstream code should operate on known fields and types.

## Conversation history

The model does not automatically remember a prior Python call.

Pydantic AI lets the application pass:

```python
message_history=previous_result.all_messages()
```

A later run can therefore continue the conversation.

Key distinction:

```text
model memory
≠
application-managed message history
```

## Provider switching

Change only the environment variable:

```text
LLM_MODEL=openai:...
LLM_MODEL=anthropic:...
LLM_MODEL=google-gla:...
```

assuming you have the corresponding API key and model access.

## Concepts intentionally not expanded here

- fallbacks/routing: important in production, but not needed to teach the core flow
- streaming: same agent concept, different response-consumption pattern
- hosted observability: later we use local logging instead
