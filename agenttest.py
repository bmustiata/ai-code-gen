import asyncio
from typing import List

import pydantic

from ge_agent import GeAgent
from workspace_tools import read_file_impl, write_file_impl, read_api, write_file


class FileInfo(pydantic.BaseModel):
    filename: str
    description: str


class FileResult(pydantic.BaseModel):
    filename: str
    content: str


class FileList(pydantic.BaseModel):
    files: List[FileInfo]


class SpecCheckResult(pydantic.BaseModel):
    valid: bool
    """
    True if the specification matches the requirements. False otherwise.
    """
    reason: str
    """
    If the specification isn't matching the requirements, here's in contained,
    why it isn't matching.
    """


async def main():
    # user_input = read_multiline_message("> ")
    with open("ctest.txt", "rt", encoding="utf-8") as f:
        user_input = f.read()
    #
    # print("⚙️ designing a spec ... ", end=None)
    # spec_result = await create_specification(user_input)
    spec_result = read_file_impl("/SPEC.md")

    while True:
        print("⚙️ (re-)checking the specification ... ", end=None)
        check_spec = await check_generated_specification(user_input, spec_result)

        if check_spec.valid:
            break

        print(f"  ❌ spec was not valid:\n{check_spec.reason}")

        print("⚙️ fixing the specification ... ", end=None)
        spec_result = await fix_failed_specification(user_input, spec_result, check_spec)
        print(spec_result)

    print("⚙️ making a list of the files to be created ... ", end=None)
    file_list = await extract_file_list()

    for file in file_list.files:
        # file = FileInfo(
        #     filename="/src/main/java/com/folderlist/Main.java",
        #     description="Entry point that processes arguments and invokes listing logic")
        print(f"⚙️ generating {file.filename} ... ", end=None)
        await generate_file(file)


def read_multiline_message(prompt: str) -> str:
    print(prompt, end="")

    message = ""
    last_message = input()

    while last_message != '\t':  # a single tab marks the end of input
        message += last_message + "\n"
        last_message = input()

    return message


async def create_specification(user_input: str) -> str:
    specgen = GeAgent("instructions/specgen.txt",
                      output_type=FileResult,
                      data={
                          "requirements": user_input
                      })

    spec_file: FileResult = await specgen.run("Write the SPEC.md")
    write_file_impl("/SPEC.md", spec_file.content)

    return spec_file.content


async def check_generated_specification(user_input: str, spec: str) -> SpecCheckResult:
    spec_check = GeAgent("instructions/spec_check.txt",
                      output_type=SpecCheckResult,
                      data={
                          "requirements": user_input,
                          "spec": spec,
                      })

    return await spec_check.run("Validate the current specification against the user requirements. Be concise.")


async def fix_failed_specification(user_input: str, spec_result: str, check_spec: SpecCheckResult) -> str:
    specgen = GeAgent("instructions/specgen.txt",
                      output_type=FileResult,
                      data={
                          "requirements": user_input,
                          "spec": spec_result,
                          "rejection_reason": check_spec.reason,
                      })

    spec_file: FileResult = await specgen.run("Fix the specification from SPEC.md")
    write_file_impl("/SPEC.md", spec_file.content)

    return spec_file.content


async def extract_file_list() -> FileList:
    file_lister = GeAgent("instructions/file_lister.txt",
                          data={
                              "spec": read_file_impl("/SPEC.md"),
                          },
                          output_type=FileList)
    return await file_lister.run("Read the list of files")


async def generate_file(file: FileInfo) -> None:
    coder = GeAgent("instructions/coder.txt",
                    data={
                        "file_name": file.filename,
                        "file_description": file.description,
                        "spec": read_file_impl("/SPEC.md"),
                    },
                    tools=[
                        write_file,
                        read_api,
                    ],
                    )

    await coder.run(f"Write the {file.filename}")

if __name__ == "__main__":
   asyncio.run(main())

