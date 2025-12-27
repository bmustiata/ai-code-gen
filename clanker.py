import asyncio

import click

import workspace_tools
from codegen import generate_file, check_generated_file, fix_failed_code
from ge_agent import GeAgent
from structs import FileResult, SpecCheckResult, FileList
from workspace_tools import read_file_impl, write_file_impl


@click.command()
@click.option("--user-spec",
              help="User specification file. What do you want to be generated?")
@click.option("--workspace", "-w",
              help="Workspace folder where to create the files.",
              default="workspace")
def event_loop_main(user_spec: str, workspace: str) -> None:
   asyncio.run(main(user_spec, workspace))


async def main(user_spec: str, workspace: str) -> None:
    workspace_tools.workspace_folder = workspace

    if user_spec:
        with open(user_spec, "rt", encoding="utf-8") as f:
            user_input = f.read()
    else:
        user_input = read_multiline_message("> ")

    #
    print("⚙️ designing a spec ... ")
    spec_result = await create_specification(user_input)
    spec_result = read_file_impl("/SPEC.md")

    while True:
        print("⚙️ (re-)checking the specification ... ")
        check_spec = await check_generated_specification(user_input, spec_result)

        if check_spec.valid:
            break

        print(f"  ❌ spec was not valid:\n{check_spec.reason}")

        print("⚙️ fixing the specification ... ")
        spec_result = await fix_failed_specification(user_input, spec_result, check_spec)
        print(spec_result)

    print("⚙️ making a list of the files to be created ... ")
    file_list = await extract_file_list()

    for file in file_list.files:
        print(f"⚙️ generating {file.filename} ... ")
        await generate_file(file)

    for file in file_list.files:
        print(f"⚙️ re-checking the code for {file.filename} ... ")
        check = await check_generated_file(file)

        if check.valid:
            continue

        print(f"  ❌ code was not valid:\n{check.reason}")

        print(f"⚙️ fixing the code for {file.filename} ... ")
        await fix_failed_code(file, check)


def read_multiline_message(prompt: str) -> str:
    print(prompt, end="")

    message = ""
    last_message = input()

    while last_message != '\t':  # a single tab marks the end of input
        message += last_message + "\n"
        last_message = input()

    return message


async def create_specification(user_input: str) -> str:
    specgen = GeAgent("instructions/spec/spec_gen.txt",
                      output_type=FileResult,
                      data={
                          "requirements": user_input
                      })

    spec_file: FileResult = await specgen.run("Write the SPEC.md")
    write_file_impl("/SPEC.md", spec_file.content)

    return spec_file.content


async def check_generated_specification(user_input: str, spec: str) -> SpecCheckResult:
    spec_check = GeAgent("instructions/spec/spec_check.txt",
                         output_type=SpecCheckResult,
                         data={
                          "requirements": user_input,
                          "spec": spec,
                      })

    return await spec_check.run("Validate the current specification against the user requirements. Be concise.")


async def fix_failed_specification(user_input: str, spec_result: str, check_spec: SpecCheckResult) -> str:
    specgen = GeAgent("instructions/spec/spec_gen.txt",
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
    file_lister = GeAgent("instructions/spec/file_lister.txt",
                          data={
                              "spec": read_file_impl("/SPEC.md"),
                          },
                          output_type=FileList)
    return await file_lister.run("Read the list of files")


if __name__ == "__main__":
   event_loop_main()
