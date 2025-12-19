import asyncio
from typing import List

import pydantic

from ge_agent import GeAgent
from workspace_tools import write_file, read_file, read_file_impl


class FileInfo(pydantic.BaseModel):
    filename: str
    description: str


class FileList(pydantic.BaseModel):
    files: List[FileInfo]


async def main():
    # user_input = read_multiline_message("> ")
    # with open("ctest.txt", "rt", encoding="utf-8") as f:
    #     user_input = f.read()

    # print(":brain: creating an execution plan ... ", end=None)
    # plan_result = await create_execution_plan(user_input)
    # print("DONE")
    # print(plan_result)

    print(":brain: making a list of the files to be created ... ", end=None)
    file_list = await extract_file_list()
    print("DONE")
    print(file_list)

    for file in file_list.files:
        print(f":brain: writing {file.filename} ... ", end=None)
        await generate_file(file)
        print("DONE")

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


async def extract_file_list() -> FileList:
    file_lister = GeAgent("instructions/file_lister.txt",
                          tools=[read_file],
                          data={
                              "plan": read_file_impl("/PLAN.md"),
                          },
                          output_type=FileList)
    return await file_lister.run("Read the list of files")


async def generate_file(file: FileInfo) -> None:
    coder = GeAgent("instructions/coder.txt",
                    tools=[write_file],
                    data={
                        "file_name": file.filename,
                        "file_description": file.description,
                        "plan": read_file_impl("/PLAN.md"),
                    })

    return await coder.run(f"Write the {file.filename}")

if __name__ == "__main__":
    asyncio.run(main())
