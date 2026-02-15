import os
import subprocess
from typing import List, Optional

from agents import function_tool
from pydantic import BaseModel

from geai.tools import workspace_tools


class GrepLine(BaseModel):
    """Represents a single line matched by grep"""
    file_name: str
    line: int
    matched_line: str


class GrepResult(BaseModel):
    """Result of a grep operation"""
    lines: List[GrepLine]
    success: bool
    error_message: Optional[str] = None


def grep_impl(search_text: str, is_regex: bool = False) -> GrepResult:
    """
    Internal implementation of grep - searches for text in files within the workspace directory.
    
    This function is used by the grep tool and can be tested independently.
    
    :param search_text: The text to search for
    :param is_regex: Whether to treat search_text as a regular expression
    :return: GrepResult containing matched lines or error information
    """
    try:
        full_workspace_path = os.path.abspath(workspace_tools.workspace_folder)
        
        if not os.path.isdir(full_workspace_path):
            return GrepResult(
                lines=[],
                success=False,
                error_message=f"Workspace directory does not exist: {full_workspace_path}"
            )
        
        # Build grep command
        grep_args = ["grep"]
        
        if is_regex:
            grep_args.append("-r")
            grep_args.append("-E")
        else:
            grep_args.append("-r")
            grep_args.append("-F")
        
        grep_args.append("-n")  # Show line numbers
        grep_args.append("-H")  # Always print filenames
        grep_args.append(search_text)
        grep_args.append(".")
        
        # Run grep command
        result = subprocess.run(
            grep_args,
            cwd=full_workspace_path,
            capture_output=True,
            text=True,
            check=True
        )
        
        # Parse grep output
        lines = []
        for line in result.stdout.splitlines():
            # Grep output format: filename:line_number:matched_line
            if ':' in line:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    file_name = parts[0]
                    line_num = int(parts[1])
                    matched_line = parts[2]
                    lines.append(GrepLine(
                        file_name=file_name,
                        line=line_num,
                        matched_line=matched_line
                    ))
        
        return GrepResult(
            lines=lines,
            success=True
        )
        
    except subprocess.CalledProcessError as e:
        # grep returns non-zero when no matches are found
        if e.returncode == 1 and not e.stdout:
            return GrepResult(
                lines=[],
                success=True,
                error_message="No matches found"
            )
        return GrepResult(
            lines=[],
            success=False,
            error_message=f"Grep command failed: {e.stderr}"
        )
    except Exception as e:
        return GrepResult(
            lines=[],
            success=False,
            error_message=f"Error during grep: {str(e)}"
        )


@function_tool
def grep(search_text: str, is_regex: bool = False) -> GrepResult:
    """
    Searches for text in files within the workspace directory.
    
    :param search_text: The text to search for
    :param is_regex: Whether to treat search_text as a regular expression
    :return: GrepResult containing matched lines or error information
    """
    return grep_impl(search_text, is_regex)
