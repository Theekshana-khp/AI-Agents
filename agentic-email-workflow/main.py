from dotenv import load_dotenv
import asyncio
from agents import Agent,Runner,trace

load_dotenv(override=True)

agent = Agent(
    name="pasindu",
    instructions="you are a helpful assistant that can answer questions and help with tasks",
    model="gpt-4o-mini"
)


async def main():
    with trace("agent"):
        result = await Runner.run(agent, "what is the capital of france?")
        print(result.final_output)

asyncio.run(main())