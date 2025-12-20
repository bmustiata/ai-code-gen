import re
from typing import List, Any, Dict, Optional, Tuple

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
                 agent_file: str,
                 tools: List[Any]=[],
                 output_type: type[Any] | AgentOutputSchemaBase | None = None,
                 data: Optional[Dict[str, str]] = None):
        """
        This creates an agent definition from a file. The agent file is divided in two parts divided by at least
        one empty line:
        1. metadata - a key/value pair set at the beginning
        2. instructions - the rest of the file that makes the system prompt

        :param agent_file:
        :param tools:
        :param output_type:
        :param data:
        """

        with open(agent_file, encoding="UTF-8") as f:
            agent_file_content = f.read()

        if data:
            agent_file_content = replace_values(agent_file_content, data)

        agent_file_lines = agent_file_content.splitlines()

        metadata, instruction_lines = extract_metadata(agent_file_lines)

        self.title = metadata['title']
        self.model_name = metadata['model']

        self.instructions = "\n".join(instruction_lines)
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


def extract_metadata(agent_lines: List[str]) -> Tuple[Dict[str, str], List[str]]:
    """
    Extracts the agent metadata (title, model, etc) and puts it in the
    metadata dictionary. The instructions are then returned.

    :param agent_lines:
    :return:
    """
    metadata: Dict[str, str] = dict()
    instruction_lines: List[str]

    metadata_finished = False

    for i in range(0, len(agent_lines)):
        line = agent_lines[i]

        # we finished metadata, and we have a line that's not empty? we started the instructions, we can return
        if metadata_finished and line.strip():
            return metadata, agent_lines[i:]

        # we finished metadata, but the line is still empty. next line.
        if metadata_finished:
            continue

        # IN METADATA
        # we haven't finished metadata, we're still reading:

        # we found an empty line? we're done reading the metadata
        if line.strip() == "":
            metadata_finished = True
            continue

        # comment line in metadata, ignore it
        if line.startswith("#"):
            continue

        kv = line.split('=', 1)
        if len(kv) < 2:
            raise Exception(f"unable to parse agent metadata: {line}")

        metadata[kv[0]] = kv[1]

    raise Exception("unable to find any instructions, for ended normally")

def replace_values(template: str, values: Dict[str, str]) -> str:
    """
    Replaces `{var_name}` values from the template, to the values passed in the
    dictionary. If a variable is missing, it is ignored, and the unchanged
    `{missing_var}` is left in the original code. Empty `{}` are also allowed
    in the template.
    """
    def replace_match(match):
        key = match.group(1)
        if key in values:
            return values[key]
        return match.group(0)

    return re.sub(r'\{([^}]+)\}', replace_match, template)