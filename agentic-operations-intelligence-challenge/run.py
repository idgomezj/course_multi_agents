import uvicorn

from challenge.observability import log_event, setup_logging

logger = setup_logging("agentic-operations-challenge")

if __name__ == "__main__":
    log_event(logger, "server.starting", host="0.0.0.0", port=8000, reload=True)
    uvicorn.run("challenge.api:app", host="0.0.0.0", port=8000, reload=True)
