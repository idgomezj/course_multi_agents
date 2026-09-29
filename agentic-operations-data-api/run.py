import uvicorn

from app.observability import log_event, setup_logging

logger = setup_logging("agentic-operations-data-api")

if __name__ == "__main__":
    log_event(logger, "server.starting", host="0.0.0.0", port=8100, reload=True)
    uvicorn.run("app.main:app", host="0.0.0.0", port=8100, reload=True, log_config=None)
