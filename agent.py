import asyncio
import sys

import click

from ge_agent import GeAgent
from memory_session import InMemorySession
from tools import workspace_tools
from tools.user_tools import ask_the_user
from tools.workspace_tools import write_file, list_files, read_file, read_api


@click.command()
@click.option("--workspace", "-w",
              help="Workspace folder where to create the files.",
              default="workspace")
def event_loop_main(workspace: str) -> None:
   asyncio.run(agent_mode(workspace))


async def agent_mode(workspace: str) -> None:
    workspace_tools.workspace_folder = workspace
    session = InMemorySession("wut")

    while True:
        print("AGENT> ", end="", flush=True)
        user_input = sys.stdin.readline().strip()

        print("⚙️ running custom query ... ")
        await run_agent(session, user_input)


async def run_agent(session, user_input: str) -> str:
    local_agent = GeAgent(
        "instructions/agent/agent.txt",
        tools=[
            write_file,
            list_files,
            read_file,
            read_api,
            ask_the_user,
        ],
        session=session,
    )
    result = ""

    async for token in local_agent.async_run(user_input):
        result += token
        print(token, end="", flush=True)

    return result


if __name__ == "__main__":
    event_loop_main()

