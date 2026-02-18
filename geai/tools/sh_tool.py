import os
import subprocess

from agents import function_tool
from pydantic import BaseModel

from geai.tools import workspace


class RunShResult(BaseModel):
    """Result of a shell command execution"""
    stdout: str
    stderr: str
    return_code: int
    success: bool


def run_sh_command_impl(command: str) -> RunShResult:
    """
    Internal implementation of running a shell command within the workspace.py directory.
    
    This function contains the actual logic for executing shell commands and should be
    tested directly. The public `run_sh_command` function is a delegate wrapper.
    
    :param command: The shell command to execute
    :return: RunShResult containing stdout, stderr, return_code, and success status
    """
    try:
        # Get the absolute path of the workspace.py folder
        workspace_path = os.path.abspath(workspace.folder)
        
        # Run the command within the workspace.py directory
        result = subprocess.run(
            command,
            shell=True,
            cwd=workspace_path,
            capture_output=True,
            text=True
        )
        
        return RunShResult(
            stdout=result.stdout,
            stderr=result.stderr,
            return_code=result.returncode,
            success=result.returncode == 0
        )
        
    except Exception as e:
        return RunShResult(
            stdout="",
            stderr=f"Error executing command: {str(e)}",
            return_code=-1,
            success=False
        )


@function_tool
def execute(command: str) -> RunShResult:
    """
    Run a shell command within the workspace.py directory.
    
    :param command: The shell command to execute
    :return: RunShResult containing stdout, stderr, return_code, and success status
    """
    return run_sh_command_impl(command)