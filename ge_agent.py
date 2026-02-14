import re
from typing import List, Any, Dict, Optional, Tuple, AsyncIterable

from openai import AsyncOpenAI
from openai.types.responses import ResponseOutputItemAddedEvent, ResponseFunctionToolCall, ResponseOutputItemDoneEvent, \
    ResponseReasoningItem, ResponseTextDeltaEvent, ResponseReasoningTextDeltaEvent

from agent_output import AgentPrintout
from agents import Agent, Runner, OpenAIChatCompletionsModel, AgentOutputSchemaBase, ModelSettings, \
    RawResponsesStreamEvent

local_client = AsyncOpenAI(
    base_url="http://gmktek:11434/v1/",
    api_key="EMPTY",
)

agent_index = 1


class GeAgent:
    """
    Very basic wrapper over OpenAI to simplify chain creation.
    """
    def __init__(self,
                 agent_file: str,
                 agent_output: AgentPrintout | None = None,
                 tools: List[Any]=[],
                 output_type: type[Any] | AgentOutputSchemaBase | None = None,
                 data: Optional[Dict[str, str]] = None,
                 session: Optional[any] = None):
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

        try:
            with open(agent_file, encoding="UTF-8") as f:
                agent_file_content = f.read()
        except:
            print(f"unable to open agent file: {agent_file}")
            raise

        if data:
            agent_file_content = replace_values(agent_file_content, data)

        agent_file_lines = agent_file_content.splitlines()

        metadata, instruction_lines = extract_metadata(agent_file_lines)

        self.title = metadata['title']
        self.model_name = metadata['model']

        self.instructions = "\n".join(instruction_lines)
        self.tools = tools
        self.session = session
        self.agent_output = agent_output

        self._last_status = None
        self._last_printed = None

        local_model = OpenAIChatCompletionsModel(
            model=self.model_name,
            openai_client=local_client,
        )

        global agent_index
        agent_index += 1

        self.agent = Agent(
            name=self.title + f' #{agent_index}',
            instructions=self.instructions,
            tools=tools,
            model=local_model,
            output_type=output_type,
            model_settings=ModelSettings(top_p=0.1, max_tokens=202752),
        )

    async def run(self, user_input: str) -> Any:
        result = await Runner.run(
            self.agent,
            input=user_input,
            max_turns=200,  # how many tools to call
        )
        return result.final_output

    async def async_run(self, user_input: str) -> AsyncIterable[str]:
        result = Runner.run_streamed(
                self.agent,
                input=user_input,
                max_turns=200,
                session=self.session,
        )

        async for event in result.stream_events():
            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseOutputItemAddedEvent) and \
                    isinstance(event.data.item, ResponseFunctionToolCall):
                self.agent_output.set_status(f"🔧 {event.data.item.name}")
                self._last_status = "tool"
                continue

            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseOutputItemDoneEvent) and \
                    isinstance(event.data.item, ResponseFunctionToolCall):
                if self._last_status == "tool":
                    self.agent_output.set_status(f"")
                    self._last_status = None

                self.agent_output.print(f"\n🔧 calling {event.data.item.name}")
                self._last_printed = "tool"

                continue

            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseOutputItemAddedEvent) and \
                    isinstance(event.data.item, ResponseReasoningItem):
                self.agent_output.set_status(f"⚙️ thinking...")
                self._last_status = "think"

                continue

            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseOutputItemDoneEvent) and \
                    isinstance(event.data.item, ResponseReasoningItem):
                if self._last_status == "think":
                    self.agent_output.set_status(f"")
                    self._last_status = None

                continue

            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseReasoningTextDeltaEvent):
                if event.data.delta == "":
                    continue

                if self._last_printed != "think":
                    self._last_printed = "think"
                    self.agent_output.print("\n")

                # print as dimmed text
                self.agent_output.print(event.data.delta, ansi_before="\033[2m", ansi_after="\033[0m")

                continue

            if isinstance(event, RawResponsesStreamEvent) and \
                    isinstance(event.data, ResponseTextDeltaEvent):
                if event.data.delta == "":
                    continue

                if self._last_printed != "text":
                    self._last_printed = "text"
                    self.agent_output.print("\n")

                yield event.data.delta
            else:
                pass
                # print(f"--> unexpected event: {event}")


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
