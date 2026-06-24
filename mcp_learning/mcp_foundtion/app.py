import asyncio
import os
from dotenv import load_dotenv
from agents.mcp import MCPServerStdio
from agents import Agent, Runner, trace

load_dotenv(override=True)

import os

os.makedirs("sandbox", exist_ok=True)
fetch_path = {"command": "uvx", "args": ["mcp-server-fetch"]}
sandbox_path = os.path.abspath(os.path.join(os.getcwd(), "sandbox"))
playwright_params = {"command": "npx","args": [ "@playwright/mcp@latest"]}
files_params = {"command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", sandbox_path]}

async def main():

    instructions = """
    You browse the internet to accomplish your instructions.
    You are highly capable at browsing the internet independently to accomplish your task, 
    including accepting all cookies and clicking 'not now' as
    appropriate to get to the content you need. If one website isn't fruitful, try another. 
    Be persistent until you have solved your assignment,
    trying different options and sites as needed.
    When you need to write files, you do that inside the sandbox folder only.
    """

    async with MCPServerStdio(params=files_params, client_session_timeout_seconds=60) as mcp_server_files:
        async with MCPServerStdio(params=playwright_params, client_session_timeout_seconds=60) as mcp_server_browser:
            agent = Agent(
                name="investigator",
                instructions=instructions,
                model="gpt-4.1-mini",
                mcp_servers=[mcp_server_files, mcp_server_browser]
            )
            with trace("investigate"):
                result = await Runner.run(agent,
                                          "Find a great recipe for Banoffee Pie, then summarize it in markdown to banoffee.md",
                                          max_turns=30
                                          )
                print(result.final_output)


asyncio.run(main())