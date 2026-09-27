import asyncio

from capstone import run_capstone


async def main():

    state = await run_capstone(
        (
            "Design a small teaching application "
            "that demonstrates a useful multi-agent "
            "system using only a remote LLM API and "
            "local application resources."
        )
    )

    print(
        state.final.model_dump_json(
            indent=2
        )
    )


if __name__ == "__main__":

    asyncio.run(
        main()
    )
