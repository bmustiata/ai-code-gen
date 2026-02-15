import time

from agents import function_tool


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
