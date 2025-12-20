import os.path
from typing import Optional

from agents import function_tool

from ge_agent import GeAgent

workspace_folder: str = "/tmp/x"


@function_tool
def write_file(file_name: str, content: str) -> str:
    """
    Writes the content into the file as UTF-8. Characters are written
    as they are, no escaping is necessary.

    :param file_name:
    :param content:
    :return:
    """
    return write_file_impl(file_name, content)


@function_tool
def read_file(file_name: str) -> str:
    """
    Reads the content of the file.
    :param file_name:
    :return:
    """
    return read_file_impl(file_name)


@function_tool
async def extract_api(file_name: str) -> str:
    """
    Get the API definitions from the given filename.
    :param file_name:
    :return:
    """
    print("EXTRACTING API!!")

    # Create an API extractor agent
    api_extractor = GeAgent("instructions/api_extractor.txt",
                           output_type=str,
                           data={
                               "file_name": file_name,
                               "file_content": read_file_impl(file_name)
                           })

    # Run the agent to extract the API
    api_content = await api_extractor.run(f"Extract the API for {file_name}")

    return api_content


def write_file_impl(file_name: str, content: str) -> str:
    full_file_name = ensure_file_path(file_name)

    if not full_file_name:
        return f"{file_name} was written!"

    try:
        with open(full_file_name, "wt", encoding="utf-8") as f:
            f.write(content)
        print(f":file: :checkmark: {full_file_name} written")
    except Exception as e:
        print(f"unable to write {full_file_name}")
        print(e)

    return f"{file_name} was written!"


def read_file_impl(file_name: str) -> str:
    try:
        full_file_name = ensure_file_path(file_name)

        if not full_file_name:
            print(f"unable to read file: {full_file_name}")
            return "FILE DOES NOT EXISTS"

        with open(full_file_name, "rt", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"unable to read file: {file_name}")
        print(e)
        return "FILE DOES NOT EXISTS"


def ensure_file_path(workspace_file_name: str) -> Optional[str]:
    """
    Ensures all the folders to that file exist. Ensures also the
    folder is inside the workspace.
    """
    try:
        if workspace_file_name and workspace_file_name.startswith("/"):
            workspace_file_name = "." + workspace_file_name

        full_file_name = os.path.abspath(os.path.join(workspace_folder, workspace_file_name))
        full_dir_name = os.path.dirname(full_file_name)
        os.makedirs(full_dir_name, exist_ok=True)

        return full_file_name
    except Exception as e:
        print(f"unable to create file {workspace_file_name}")
        print(e)
        return None
