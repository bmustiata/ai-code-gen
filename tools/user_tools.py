from agents import function_tool

import readinput


@function_tool
def ask_the_user(question: str, options: list[str]) -> str:
    """
    Ask the user to select one of the available options in case you
    have questions about something.
    """

    return readinput.read_options("AGENT", question, options, color="red")
