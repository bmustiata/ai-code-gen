from agents import function_tool

import geai.tools.workspace_tools as workspace_tools
from pydantic import BaseModel


class ReadFileResult(BaseModel):
    """Result object for file reading operations."""
    content: str
    success: bool
    error_message: str = ""


@function_tool
def read_file(file_name: str) -> ReadFileResult:
    """
    Reads the full content of the file. Use only when needed, files can be large.
    If all you need are API signatures, just use the `read_api` tool.
    
    :param file_name: The name of the file to read
    :return: ReadFileResult containing content, success status, and optional error message
    """
    return read_file_impl(file_name)


def read_file_impl(file_name: str) -> ReadFileResult:
    """
    Implementation of file reading with error handling.
    
    :param file_name: The name of the file to read
    :return: ReadFileResult object with file content or error information
    """
    try:
        full_file_name = workspace_tools.ensure_file_path(file_name)

        if not full_file_name:
            return ReadFileResult(
                content="",
                success=False,
                error_message=f"FILE DOES NOT EXIST: {file_name}"
            )

        with open(full_file_name, "rt", encoding="utf-8") as f:
            content = f.read()
            return ReadFileResult(
                content=content,
                success=True,
                error_message=""
            )
    except Exception as e:
        return ReadFileResult(
            content="",
            success=False,
            error_message=f"FAILED TO READ {file_name}: {e}"
        )