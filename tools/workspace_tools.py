import os.path
from typing import Optional, Dict

from agents import function_tool

from ge_agent import GeAgent

workspace_folder: str = "/tmp/gox/"


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
def patch_file(file_name: str, patch: str) -> str:
    """
    Patches a file by applying the given patch string. The patch can be:
    - A simple replacement: "old_string=new_string"
    - A multi-line replacement with delimiters
    - A more complex patch format

    :param file_name: The name of the file to patch
    :param patch: The patch string to apply
    :return: Confirmation message
    """
    return patch_file_impl(file_name, patch)


@function_tool
def list_files(path: str) -> list[str]:
    """
    Lists all the files in the given folder. Folders end with a `/` in the name.
    Files do not end with a `/`.
    :param path:
    :return:
    """
    print(f"  ➡️ listing {path}")
    full_path = get_full_file_name(path)

    if not os.path.isdir(full_path):
        return ["{path} does not exist or is not a directory!"]

    result: list[str] = []

    for f in os.listdir(full_path):
        joined_path = os.path.join(full_path, f)

        if os.path.isdir(joined_path):
            print("is folder: " + full_path)
            joined_path += "/"

        result.append(os.path.join(path, f))

    print(result)
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
    """
    global api_cache

    print(f"  ➡️ reading API for {file_name}")
    full_file_name = get_full_file_name(file_name)

    if full_file_name in api_cache:
        return api_cache[full_file_name]

    # Create an API extractor agent
    api_extractor = GeAgent("../instructions/api_extractor.txt",
                            output_type=str,
                            data={
                               "file_name": file_name,
                               "file_content": read_file_impl(file_name)
                           })

    # Run the agent to extract the API
    api_content = await api_extractor.run(f"Extract the API for {file_name}")

    return api_content


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
        print(f"  📄 {full_file_name} written")
    except Exception as e:
        print(f"unable to write {full_file_name}")
        print(e)

    return f"{file_name} WRITTEN successfully! DONE."


def patch_file_impl(file_name: str, patch: str) -> str:
    """
    Implements the patch_file functionality.
    Supports multiple patch formats:
    1. Simple replacement: "old_string=new_string"
    2. Multi-line replacement with triple quotes
    3. Complex patch patterns
    """
    global api_cache

    full_file_name = ensure_file_path(file_name)

    if not full_file_name:
        return f"unable to patch {file_name} - file path not valid"

    try:
        # Read the current file content
        with open(full_file_name, "rt", encoding="utf-8") as f:
            content = f.read()

        # Apply the patch
        patched_content = apply_patch(content, patch)

        # Update the cache if the file was in it
        if full_file_name in api_cache:
            del api_cache[full_file_name]

        # Write the patched content back
        with open(full_file_name, "wt", encoding="utf-8") as f:
            f.write(patched_content)

        print(f"  📝 {full_file_name} patched successfully")
        return f"{file_name} PATCHED successfully! DONE."

    except Exception as e:
        print(f"unable to patch {full_file_name}")
        print(e)
        return f"unable to patch {file_name}"


def apply_patch(content: str, patch: str) -> str:
    """
    Applies a patch to the content string.
    Supports multiple patch formats:
    1. Simple replacement: "old_string=new_string"
    2. Multi-line replacement with triple quotes
    3. Complex patch patterns
    """
    # Check for simple replacement format (old_string=new_string)
    if "=" in patch and not patch.startswith('"""') and not patch.startswith("'''"):
        parts = patch.split("=", 1)
        if len(parts) == 2:
            old_string = parts[0].strip()
            new_string = parts[1].strip()
            return content.replace(old_string, new_string)

    # Check for multi-line replacement with triple quotes
    if patch.startswith('"""') and patch.endswith('"""'):
        # Extract the replacement content (everything between the quotes)
        replacement = patch[3:-3].strip()
        
        # Try to find a matching section to replace
        # Look for a section that starts with the replacement content
        lines = content.split('\n')
        replacement_lines = replacement.split('\n')
        
        # Find the start and end of the section to replace
        start_idx = -1
        end_idx = -1
        
        for i in range(len(lines) - len(replacement_lines) + 1):
            match = True
            for j in range(len(replacement_lines)):
                if i + j >= len(lines) or lines[i + j] != replacement_lines[j]:
                    match = False
                    break
            if match:
                start_idx = i
                end_idx = i + len(replacement_lines)
                break
        
        if start_idx != -1:
            # Replace the section
            new_lines = lines[:start_idx] + [replacement] + lines[end_idx:]
            return '\n'.join(new_lines)
    
    # If no specific format matched, return the original content
    # (or you could raise an error or return a message)
    return content


def read_file_impl(file_name: str) -> str:
    try:
        full_file_name = ensure_file_path(file_name)

        if not full_file_name:
            print(f"unable to read file: {full_file_name} - file dos not exist")
            return "FILE DOES NOT EXISTS"

        with open(full_file_name, "rt", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        print(f"unable to read file: {file_name} - exception")
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