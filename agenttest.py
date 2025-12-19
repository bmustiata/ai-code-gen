import asyncio

from ge_agent import GeAgent
from workspace_tools import write_file


async def main():
    # user_input = read_multiline_message("> ")
    with open("ctest.txt", "rt", encoding="utf-8") as f:
        user_input = f.read()

    print(":brain: creating an execution plan ... ", end=None)
    plan_result = await create_execution_plan(user_input)
    print("DONE")
    print(plan_result)


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



if __name__ == "__main__":
    asyncio.run(main())
