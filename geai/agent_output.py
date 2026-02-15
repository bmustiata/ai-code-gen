class NoOpAgentPrintout:
    """A class that does nothing. Used when no output is desired."""
    def set_status(self, status: str) -> None:
        pass

    def print(self, text: str, ansi_before: str = "", ansi_after: str = "") -> None:
        pass


class AgentPrintout:
    """
    A class for printing output to a 120-character terminal with a status line at the end.
    The cursor always stays at the bottom left after operations.

    It's designed to show thinking, and what happens in the agent currently.
    """
    # FIXME: in an ideal world, the terminal size should be read from the terminal itself
    #        where this is running.

    def __init__(self):
        """Initialize the AgentPrintout with a column tracker."""
        self.current_column = 0
        self._status = ""
    
    def set_status(self, status: str) -> None:
        """
        Set the status line on the bottom of the terminal.
        
        Args:
            status: The status string to display
        """
        self._status = status
        self._print_status()

    def print(self, text: str, ansi_before: str = "", ansi_after: str = "") -> None:
        """
        Print text with special cursor behavior.
        
        The cursor moves up one line, then prints each character at the current column.
        If the 120-character mark is reached, a newline is printed before the next character.
        If a newline is in the text, the column is reset to 0.
        
        Args:
            :param text: The text to print
            :param ansi_before:  ANSI control codes to print before the string. These characters
                  counted against the screen width for text wrapping.
            :param ansi_after: ANSI control codes to print after the string. These characters
                  counted against the screen width for text wrapping.
        """
        # Move cursor one line up
        print("\033[1A", end='')

        # move Cursor to the right column
        for i in range(self.current_column):
            print("\033[1C", end='', flush=False)

        print(ansi_before, end='', flush=False)

        for c in text:
            if c == "\n":
                print("\n\033[2K", end="", flush=False)
                self.current_column = 0
                continue

            self.current_column += 1

            if self.current_column == 120:
                print("\n\033[2K", end="", flush=False)
                self.current_column = 1  # the column will be 1, since we'll print the character

            print(c, end='')

        print(ansi_after, end='', flush=False)

        print()
        self._print_status()

    def _print_status(self):
        print(f" {self._status.ljust(119)}", end='')
        print("\r", end='')
