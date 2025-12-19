import os.path
from typing import Optional

from agents import function_tool

workspace_folder: str = "/tmp/x"


@function_tool
def write_file(file_name: str, content: str) -> str:
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


@function_tool
def read_file(file_name: str) -> str:
    return read_file_impl(file_name)


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

        full_file_name = os.path.join(workspace_folder, workspace_file_name)
        full_dir_name = os.path.dirname(full_file_name)
        os.makedirs(os.path.dirname(full_dir_name), exist_ok=True)

        return full_file_name
    except Exception as e:
        print(f"unable to create file {workspace_file_name}")
        print(e)
        return None
