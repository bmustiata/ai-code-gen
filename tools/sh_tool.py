import subprocess

from agents import function_tool


@function_tool
def run_sh_command(command: str) -> str:
    """
    Run a shell command and return the output.
    """

    subprocess.call(command, shell=True)
