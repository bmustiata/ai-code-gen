import asyncio
import sys

import click

from ge_agent import GeAgent
from memory_session import InMemorySession
from tools import workspace_tools
from tools.workspace_tools import write_file, list_files, read_file, read_api, patch_file, grep, git_grep


@click.command()
@click.option("--workspace", "-w",
              help="Workspace folder where to create the files.",
              default="workspace")
def event_loop_main(workspace: str) -> None:
   asyncio.run(agent_mode(workspace))


async def agent_mode(workspace: str) -> None:
    workspace_tools.workspace_folder = workspace
    session = InMemorySession("wut")

    try:
        while True:
            print("AGENT> ", end="", flush=True)
            user_input = sys.stdin.readline().strip()

            # Check if user wants to quit
            if user_input.lower() == "quit":
                exit_program()

            print("⚙️ running custom query ... ")
            await run_agent(session, user_input)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        exit_program()


async def run_agent(session, user_input: str) -> str:
    local_agent = GeAgent(
        "instructions/agent/agent.txt",
        tools=[
            write_file,
            list_files,
            read_file,
            read_api,
            patch_file,
            grep,
            git_grep,
        ],
        session=session,
    )
    result = ""

    async for token in local_agent.async_run(user_input):
        result += token
        print(token, end="", flush=True)

    return result


def exit_program() -> None:
    """Print goodbye message and exit the program."""
    print("\n👋 Goodbye!")
    sys.exit(0)



if __name__ == "__main__":
    event_loop_main()