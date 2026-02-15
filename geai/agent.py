import asyncio
import sys

import click

from agent_output import AgentPrintout
from ge_agent import GeAgent
from memory_session import InMemorySession
from tools import workspace_tools
from tools.git_grep_tool import git_grep
from tools.grep_tool import grep
from tools.time_tools import sleep
from tools.workspace_tools import write_file, list_files, read_file, read_api, patch_file
from tools.sh_tool import run_sh_command


@click.command()
@click.option("--workspace", "-w",
              help="Workspace folder where to create the files.",
              default="workspace")
@click.option("--user-prompt", "-u",
              help="Default user prompt to start the conversation.",
              default=None)
def event_loop_main(workspace: str, user_prompt: str) -> None:
   asyncio.run(agent_mode(workspace, user_prompt))


async def agent_mode(workspace: str, user_prompt: str) -> None:
    workspace_tools.workspace_folder = workspace
    session = InMemorySession("wut")

    try:
        # Use default user prompt if provided, otherwise read from stdin
        if user_prompt:
            user_input = user_prompt
        else:
            print("🗑️ AGENT> ", end="", flush=True)
            user_input = sys.stdin.readline().strip()

        # Check if user wants to quit
        if user_input.lower() == "quit":
            exit_program()

        await run_agent(session, user_input)

        # Continue reading from stdin for subsequent messages
        while True:
            print("🗑️ AGENT> ", end="", flush=True)
            user_input = sys.stdin.readline().strip()

            # Check if user wants to quit
            if user_input.lower() == "quit":
                exit_program()

            await run_agent(session, user_input)
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        exit_program()


async def run_agent(session, user_input: str) -> str:
    agent_output = AgentPrintout()

    local_agent = GeAgent(
        "../instructions/agent/agent.txt",
        agent_output=agent_output,
        tools=[
            git_grep,
            grep,
            list_files,
            patch_file,
            read_api,
            read_file,
            run_sh_command,
            sleep,
            write_file,
        ],
        session=session,
        data={
            "user_input": user_input,
        }
    )
    result = ""

    async for token in local_agent.async_run(user_input):
        result += token

    return result


def exit_program() -> None:
    """Print goodbye message and exit the program."""
    print("\n👋 Goodbye!")
    sys.exit(0)



if __name__ == "__main__":
    event_loop_main()