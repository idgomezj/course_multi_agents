import asyncio
import json

import httpx2

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIChatModel, OpenAIChatModelSettings
from pydantic_ai.providers.deepseek import DeepSeekProvider

from demo_app.schemas import MonthlyOperationsPlan


def test_deepseek_v4_chat_tool_round_and_structured_output():
    """Regression for the DeepSeek HTTP-200 -> output-processing failure."""

    requests: list[dict] = []

    def handler(request: httpx2.Request) -> httpx2.Response:
        body = json.loads(request.content)
        requests.append(body)

        if len(requests) == 1:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_inventory",
                        "type": "function",
                        "function": {
                            "name": "probe_inventory",
                            "arguments": "{}",
                        },
                    }
                ],
            }
        else:
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_final",
                        "type": "function",
                        "function": {
                            "name": "final_result",
                            "arguments": json.dumps(
                                {
                                    "team_id": "team_0",
                                    "scenario_id": "T0-P01",
                                    "production_plan": [],
                                    "purchase_orders": [],
                                    "actions": [],
                                    "assumptions": [],
                                    "explanation": "compatibility smoke",
                                }
                            ),
                        },
                    }
                ],
            }

        return httpx2.Response(
            200,
            json={
                "id": f"deepseek-test-{len(requests)}",
                "object": "chat.completion",
                "created": 1791154800,
                "model": "deepseek-v4-flash",
                "choices": [
                    {
                        "index": 0,
                        "message": message,
                        "finish_reason": "tool_calls",
                    }
                ],
                "usage": {
                    "prompt_tokens": 10,
                    "completion_tokens": 10,
                    "total_tokens": 20,
                },
            },
        )

    async def run() -> None:
        async with httpx2.AsyncClient(transport=httpx2.MockTransport(handler)) as client:
            model = OpenAIChatModel(
                "deepseek-v4-flash",
                provider=DeepSeekProvider(api_key="offline-test-key", http_client=client),
            )

            def probe_inventory() -> dict[str, int]:
                return {"inventory": 1}

            agent = Agent(
                model,
                output_type=MonthlyOperationsPlan,
                tools=[probe_inventory],
                model_settings=OpenAIChatModelSettings(thinking=False),
            )
            result = await agent.run("Build the test plan.")

        assert isinstance(result.output, MonthlyOperationsPlan)
        assert result.output.scenario_id == "T0-P01"
        assert len(requests) == 2
        assert requests[0]["tool_choice"] == "required"
        assert requests[0].get("reasoning_effort") == "none"
        assert requests[1]["messages"][-1]["role"] == "tool"

    asyncio.run(run())
