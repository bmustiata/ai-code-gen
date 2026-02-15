import os.path
from typing import Optional, Dict

from agents import function_tool

from geai.ge_openai.ge_agent import GeAgent

workspace_folder: str = os.getcwd()


@function_tool
def write_file(file_name: str, content: str) -> str:
    """
    Writes the content into the file as UTF-8. Characters are written
    as they are, no escaping is necessary. Use this ONLY if you want to
    create a new file, otherwise use the `patch_file` tool.

    :param file_name:
    :param content:
    :return:
    """
    return write_file_impl(file_name, content)


@function_tool
def list_files(path: str) -> list[str]:
    """
    Lists all the files in the given folder. Folders end with a `/` in the name.
    Files do not end with a `/`.
    :param path:
    :return:
    """
    full_path = get_full_file_name(path)

    if not os.path.isdir(full_path):
        return ["{path} does not exist or is not a directory!"]

    result: list[str] = []

    for f in os.listdir(full_path):
        joined_path = os.path.join(full_path, f)

        if os.path.isdir(joined_path):
            joined_path += "/"

        result.append(os.path.join(path, f))

    return result


@function_tool
def read_file(file_name: str) -> str:
    """
    Reads the full content of the file. Use only when needed, files can be large.
    If all you need are API signatures, just use the `read_api` tool.
    :param file_name:
    :return:
    """
    return read_file_impl(file_name)


api_cache: Dict[str, str] = dict()


@function_tool
async def read_api(file_name: str) -> str:
    """
    Read the API declarations (classes, functions, structs, etc) from the given filename.

    :param file_name: The name of the file to read
    """
    global api_cache

    full_file_name = get_full_file_name(file_name)

    if full_file_name in api_cache:
        return api_cache[full_file_name]

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


@function_tool
def patch_file(file_name: str, search_text: str, replace_text: str) -> str:
    """
    Patches a file by replacing the first occurrence of search_text with replace_text.

    :param file_name: The name of the file to patch
    :param search_text: The text to search for
    :param replace_text: The text to replace with
    :return: confirmation or error message
    """
    global api_cache

    full_file_name = ensure_file_path(file_name)

    if not full_file_name:
        return f"unable to patch {file_name} - file path not valid"

    try:
        # Read the current file content
        with open(full_file_name, "rt", encoding="utf-8") as f:
            content = f.read()

        # Check if search_text is found
        if search_text not in content:
            return f"Searched text not found in {file_name}"

        # Replace only the first occurrence
        patched_content = content.replace(search_text, replace_text, 1)

        # Update the cache if the file was in it
        if full_file_name in api_cache:
            del api_cache[full_file_name]

        # Write the patched content back
        with open(full_file_name, "wt", encoding="utf-8") as f:
            f.write(patched_content)

        return f"File {file_name} patched successfully"

    except Exception as e:
        return f"unable to patch {file_name}"


def write_file_impl(file_name: str, content: str) -> str:
    global api_cache

    full_file_name = ensure_file_path(file_name)

    if full_file_name in api_cache:
        del api_cache[full_file_name]

    if not full_file_name:
        return f"{file_name} was written!"

    try:
        with open(full_file_name, "wt", encoding="utf-8") as f:
            f.write(content)
    except Exception as e:
        return f"Failed to write {file_name}: {e}"

    return f"{file_name} WRITTEN successfully! DONE."


def read_file_impl(file_name: str) -> str:
    try:
        full_file_name = ensure_file_path(file_name)

        if not full_file_name:
            return "FILE DOES NOT EXISTS"

        with open(full_file_name, "rt", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"FAILED TO READ {file_name}: {e}"


def ensure_file_path(workspace_file_name: str) -> Optional[str]:
    """
    Ensures all the folders to that file exist. Ensures also the
    folder is inside the workspace.
    """
    if workspace_file_name and workspace_file_name.startswith("/"):
        workspace_file_name = "." + workspace_file_name

    full_file_name = os.path.abspath(os.path.join(workspace_folder, workspace_file_name))
    full_dir_name = os.path.dirname(full_file_name)
    os.makedirs(full_dir_name, exist_ok=True)

    return full_file_name


def get_full_file_name(workspace_file_name: str) -> str:
    """
    Computes the absolute path of a workspace file
    """
    if workspace_file_name and workspace_file_name.startswith("/"):
        workspace_file_name = "." + workspace_file_name

    full_file_name = os.path.abspath(os.path.join(workspace_folder, workspace_file_name))

    return full_file_name


def file_exists_in_workspace(workspace_file_name: str) -> bool:
    """
    Checks if a file exists in the workspace
    """
    full_file_name = get_full_file_name(workspace_file_name)

    return os.path.exists(full_file_name) and os.path.isfile(full_file_name)
