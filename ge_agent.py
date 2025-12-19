from typing import List, Any, Dict, Optional

from agents import Agent, Runner, OpenAIChatCompletionsModel, AgentOutputSchemaBase, ModelSettings
from openai import AsyncOpenAI

local_client = AsyncOpenAI(
    base_url="http://gmktek:11434/v1/",
    api_key="EMPTY",
)


class GeAgent:
    """
    Very basic wrapper over OpenAI to simplify chain creation.
    """
    def __init__(self,
                 instructions_file: str,
                 tools: List[Any]=[],
                 output_type: type[Any] | AgentOutputSchemaBase | None = None,
                 data: Optional[Dict[str, str]] = None):

        with open(instructions_file, encoding="UTF-8") as f:
            instructions = f.read()

        if data:
            instructions = instructions.format(**data)

        instruction_lines = instructions.splitlines()

        self.title = instruction_lines[0]
        self.model_name = instruction_lines[1].split('=')[1]

        # FIXME: find the first line non-empty
        # FIXME: read the model from here
        self.instructions = "\n".join(instruction_lines[2:])

        self.tools = tools

        local_model = OpenAIChatCompletionsModel(
            model=self.model_name,
            openai_client=local_client,
        )

        self.agent = Agent(
            name=self.title,
            instructions=self.instructions,
            tools=tools,
            model=local_model,
            output_type=output_type,
            model_settings=ModelSettings(top_p=0.1),
        )

    async def run(self, user_input: str) -> Any:
        result = await Runner.run(self.agent, input=user_input)
        return result.final_output

