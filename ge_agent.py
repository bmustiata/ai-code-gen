from typing import List, Any

from agents import Agent, Runner, OpenAIChatCompletionsModel, AgentOutputSchemaBase
from openai import AsyncOpenAI

local_client = AsyncOpenAI(
    base_url="http://gmktek:11434/v1/",
    api_key="EMPTY",
)


local_model = OpenAIChatCompletionsModel(
    model="qwen3-coder:30b",
    openai_client=local_client,
)


class GeAgent:
    """
    Very basic wrapper over OpenAI to simplify chain creation.
    """
    def __init__(self,
                 instructions_file: str,
                 tools: List[Any]=[],
                 output_type: type[Any] | AgentOutputSchemaBase | None = None):

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
            output_type=output_type,
        )

    async def run(self, user_input: str) -> Any:
        result = await Runner.run(self.agent, input=user_input)
        return result.final_output

