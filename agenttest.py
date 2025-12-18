import asyncio
import os

from agents import Agent, Runner, function_tool, OpenAIChatCompletionsModel
from openai import AsyncOpenAI


@function_tool
def list_folder(folder_name) -> list[str]:
    return os.listdir(folder_name)


@function_tool
def write_file(file_name: str, content: str) -> None:
    with open("PLAN.md", "wt", encoding="utf-8") as f:
        f.write(content)


local_client = AsyncOpenAI(
    base_url="http://gmktek:11434/v1/",
    api_key="EMPTY",
)

local_model = OpenAIChatCompletionsModel(
    model="qwen3-coder:30b",
    openai_client=local_client,
)

async def main():
    user_input = read_multiline_message("> ")
    print(await create_execution_plan(user_input))


def read_multiline_message(prompt: str) -> str:
    print(prompt, end="")

    message = ""
    last_message = input()

    while last_message != '\t':  # a single tab marks the end of input
        message += last_message + "\n"
        last_message = input()

    return message


async def create_execution_plan(user_input: str) -> str:
    planner = GeAgent("instructions/planner.txt", tools=[write_file])
    return await planner.run(user_input)


class GeAgent:
    """
    Very basic wrapper over OpenAI to simplify chain creation.
    """
    def __init__(self,
                 instructions_file: str,
                 tools: list[any]=[]):

        with open(instructions_file, encoding="UTF-8") as f:
            instruction_lines = f.readlines()

        self.title = instruction_lines[0]
        self.instructions = "\n".join(instruction_lines[2:])  # FIXME: find the first line non-empty

        self.tools = tools

        self.agent = Agent(
            name=self.title,
            instructions=self.instructions,
            tools=tools,
            model=local_model,
        )

    async def run(self, user_input: str) -> str:
        result = await Runner.run(self.agent, input=user_input)
        return result.final_output


if __name__ == "__main__":
    asyncio.run(main())
