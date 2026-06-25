from dotenv import load_dotenv
import asyncio
from agents import Agent, Runner, trace
from agents.mcp import MCPServerStdio

load_dotenv(override=True)

from accounts import Account


async def main():
    account = Account.get("Pasindu Theekshana")
    account.buy_shares("AMZN", 3, "Because this bookstore website looks promising")
    account.report()
    account.list_transactions()

    params = {"command":"uv", "args":["run" , "accounts_server.py"]}

    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
        mcp_tools = await server.list_tools()

    instructions = "You are able to manage an account for a client, and answer questions about the account."
    request = "My name is Pasindu Theekshana and my account is under the name Pasindu Theekshana. What's my balance and my holdings?"
    model = "gpt-4.1-mini"

    async with MCPServerStdio(params=params, client_session_timeout_seconds=30) as server:
        agent = Agent(name="Pasindu Theekshana", instructions=instructions, model=model, mcp_servers=[server])
        with trace("account_manager"):
            result = await Runner.run(agent, request)
        print(result.final_output)

    from accounts_client import get_accounts_tools_openai, read_accounts_resource, list_accounts_tools

    mcp_tools = await list_accounts_tools()
    print(mcp_tools)
    openai_tools = await get_accounts_tools_openai()
    print(openai_tools)

    request = "My name is Pasindu Theekshana and my account is under the name Pasindu Theekshana. What's my balance?"

    with trace("account_mcp_client"):
        agent = Agent(name="account_manager", instructions=instructions, model=model, tools=openai_tools)
        result = await Runner.run(agent, request)
        print(result.final_output)

    context = await read_accounts_resource("Pasindu Theekshana")
    print(context)

if __name__ == "__main__":
    asyncio.run(main())


