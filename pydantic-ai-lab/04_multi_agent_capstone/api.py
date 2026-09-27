from fastapi import FastAPI

from pydantic import BaseModel

from capstone import run_capstone


app = FastAPI(
    title="Local Multi-Agent Capstone"
)


class Request(BaseModel):

    goal: str


@app.get(
    "/health"
)
def health():

    return {
        "status": "ok"
    }


@app.post(
    "/run"
)
async def run(
    request: Request
):

    state = await run_capstone(
        request.goal
    )

    return state.model_dump()
