import structs
import workspace_tools
from ge_agent import GeAgent


async def generate_file(file: structs.FileInfo) -> str:
    """
    Meat and butter of the generation.
    :param file:
    :return:
    """
    coder = GeAgent(get_coder_template(file, "code_gen.txt"),
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


async def check_generated_file(file: structs.FileInfo) -> structs.SpecCheckResult:
    coder = GeAgent(get_coder_template(file, "code_check.txt"),
                    data={
                        "file_name": file.filename,
                        "file_description": file.description,
                        "spec": workspace_tools.read_file_impl("/SPEC.md"),
                        "file_content": workspace_tools.read_file_impl(file.filename),
                    },
                    tools=[
                        workspace_tools.read_api,
                    ],
                    )

    try:
        result = await coder.run(f"Check the {file.filename}")
    except Exception as e:
        print(f"WARNING: unable to figure out if the result is VALID or INVALID: {e}.")
        return structs.SpecCheckResult(valid=True, reason="")

    if "INVALID" in result:
        reason = result.split("INVALID")[1]

        return structs.SpecCheckResult(
            valid=False,
            reason=reason
        )

    if "VALID" in result:
        return structs.SpecCheckResult(valid=True, reason="")

    print(f"WARNING: unable to figure out if the result is VALID or INVALID: {result}.")
    return structs.SpecCheckResult(valid=True, reason="")


async def fix_failed_code(file: structs.FileInfo, check: structs.SpecCheckResult) -> None:
    coder = GeAgent(get_coder_template(file, "code_fix.txt"),
                    data={
                        "file_name": file.filename,
                        "file_description": file.description,
                        "spec": workspace_tools.read_file_impl("/SPEC.md"),
                        "file_content": workspace_tools.read_file_impl(file.filename),
                        "rejection_reason": check.reason,
                    },
                    tools=[
                        workspace_tools.write_file,
                        workspace_tools.read_api,
                    ],
                    )

    await coder.run(f"Write the {file.filename}")


def get_coder_template(file: structs.FileInfo, name: str) -> str:
    if file.filename.endswith('.py'):
        return f"instructions/coder/py/{name}"

    return f"instructions/coder/py/{name}"
