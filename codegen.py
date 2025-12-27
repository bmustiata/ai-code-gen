import workspace_tools
from ge_agent import GeAgent
from structs import FileInfo


async def generate_file(file: FileInfo) -> str:
    """
    Meat and butter of the generation.
    :param file:
    :return:
    """
    coder = GeAgent("instructions/coder/code_gen.txt",
                    data={
                        "file_name": file.filename,
                        "file_description": file.description,
                        "spec": workspace_tools.read_file_impl("/SPEC.md"),
                    },
                    tools=[
                        workspace_tools.write_file,
                        workspace_tools.read_api,
                    ],
                    )

    await coder.run(f"Write the {file.filename}")
    return workspace_tools.read_file_impl(file.filename)
