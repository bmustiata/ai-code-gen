import subprocess

from agents import function_tool

from geai.tools import workspace
from geai.tools.grep_tool import GrepResult, GrepLine


@function_tool
def git_grep(search_text: str, is_regex: bool = False) -> GrepResult:
    """
    Searches for text in files using git grep (searches in git tracked files within workspace).

    :param search_text: The text to search for
    :param is_regex: Whether to treat search_text as a regular expression
    :return: GrepResult containing matched lines or error information
    """
    return git_grep_impl(search_text, is_regex)


def git_grep_impl(search_text: str, is_regex: bool = False) -> GrepResult:
    """
    Internal implementation of git grep - searches for text in git tracked files within workspace.

    This function is used by the git_grep tool and can be tested independently.

    :param search_text: The text to search for
    :param is_regex: Whether to treat search_text as a regular expression
    :return: GrepResult containing matched lines or error information
    """
    try:
        # Check if we're in a git repository
        subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            cwd=workspace.folder,
            capture_output=True,
            check=True
        )

        # Build git grep command with workspace.py restriction
        git_grep_args = ["git", "grep"]

        if is_regex:
            git_grep_args.append("-E")
        else:
            git_grep_args.append("-F")

        git_grep_args.append("-n")  # Show line numbers
        git_grep_args.append("-H")  # Always print filenames
        git_grep_args.append(search_text)

        # Run git grep command
        result = subprocess.run(
            git_grep_args,
            cwd=workspace.folder,
            capture_output=True,
            text=True,
            check=True
        )

        # Parse git grep output and convert absolute paths to relative paths
        lines = []
        for line in result.stdout.splitlines():
            # Git grep output format: filename:line_number:matched_line
            if ':' in line:
                parts = line.split(':', 2)
                if len(parts) >= 3:
                    file_name = parts[0]
                    line_num = int(parts[1])
                    matched_line = parts[2]

                    # Convert absolute path to relative path to hide workspace.py location
                    if file_name.startswith(workspace.folder):
                        relative_path = file_name[len(workspace.folder):].lstrip('/')
                        lines.append(GrepLine(
                            file_name=relative_path,
                            line=line_num,
                            matched_line=matched_line
                        ))
                    else:
                        # Keep as-is if it's not in workspace.py (shouldn't happen with restriction)
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
        # git grep returns non-zero when no matches are found
        if e.returncode == 1 and not e.stdout:
            return GrepResult(
                lines=[],
                success=True,
                error_message="No matches found in git tracked files"
            )
        return GrepResult(
            lines=[],
            success=False,
            error_message=f"Git grep command failed: {e.stderr}"
        )
    except subprocess.CalledProcessError as e:
        # Not in a git repository
        return GrepResult(
            lines=[],
            success=False,
            error_message="Not in a git repository"
        )
    except Exception as e:
        return GrepResult(
            lines=[],
            success=False,
            error_message=f"Error during git grep: {str(e)}"
        )