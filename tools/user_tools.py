from agents import function_tool

import readinput
import time


@function_tool
def ask_the_user(question: str, options: list[str]) -> str:
    """
    Ask the user to select one of the available options in case you
    have questions about something.
    """

    return readinput.read_options("AGENT", question, options, color="red")


@function_tool
def sleep(seconds: float) -> str:
    """
    Wait for the specified number of seconds.
    
    Args:
        seconds: Number of seconds to wait (can be a float for fractional seconds)
    
    Returns:
        A confirmation message indicating the sleep is complete
    """
    time.sleep(seconds)
    return f"Successfully slept for {seconds} seconds"
