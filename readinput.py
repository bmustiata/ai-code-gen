import sys
import select
import tty
import termios

# this was generated with clanker itself :)

# ANSI escape codes for styling
ANSI_CODES = {
    'black': '30',
    'red': '31',
    'green': '32',
    'yellow': '33',
    'blue': '34',
    'magenta': '35',
    'cyan': '36',
    'white': '37',
    'bright_black': '90',
    'bright_red': '91',
    'bright_green': '92',
    'bright_yellow': '93',
    'bright_blue': '94',
    'bright_magenta': '95',
    'bright_cyan': '96',
    'bright_white': '97',
}

ANSI_BG_CODES = {
    'black': '40',
    'red': '41',
    'green': '42',
    'yellow': '43',
    'blue': '44',
    'magenta': '45',
    'cyan': '46',
    'white': '47',
    'bright_black': '100',
    'bright_red': '101',
    'bright_green': '102',
    'bright_yellow': '103',
    'bright_blue': '104',
    'bright_magenta': '105',
    'bright_cyan': '106',
    'bright_white': '107',
}

# ANSI control sequences
ANSI_BOLD = '1'
ANSI_ITALIC = '3'
ANSI_RESET = '0'

def _apply_styling(text, color=None, bgcolor=None, bold=False, italic=False):
    """Apply ANSI styling to text."""
    codes = []

    # Add color codes
    if color and color in ANSI_CODES:
        codes.append(ANSI_CODES[color])
    if bgcolor and bgcolor in ANSI_BG_CODES:
        codes.append(ANSI_BG_CODES[bgcolor])

    # Add style codes
    if bold:
        codes.append(ANSI_BOLD)
    if italic:
        codes.append(ANSI_ITALIC)

    if codes:
        return f"\033[{';'.join(codes)}m{text}\033[{ANSI_RESET}m"
    return text

def _get_input():
    """Get input from stdin with non-blocking read."""
    # Save current terminal settings
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        # Set terminal to raw mode for non-blocking input
        tty.setraw(sys.stdin.fileno())
        # Check if input is available
        if select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], []):
            return sys.stdin.read(1)
        return None
    finally:
        # Restore terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

def read_single(prompt: str, color: str = None, bgcolor: str = None, bold: bool = False, italic: bool = False) -> str:
    """
    Reads a single line of input.

    Args:
        prompt: The prompt to display
        color: Text color
        bgcolor: Background color
        bold: Whether text should be bold
        italic: Whether text should be italic

    Returns:
        The input string after pressing Enter
    """
    # Apply styling to the prompt
    print_prompt(prompt, bgcolor, color, bold, italic)

    # Read input character by character until Enter
    input_buffer = []
    while True:
        char = _get_input()
        if char is None:
            continue

        if char == '\r' or char == '\n':  # Enter key
            print()  # New line after input
            break
        elif char == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif char == '\x7f':  # Backspace
            if input_buffer:
                input_buffer.pop()
                # Move cursor back, erase character, move cursor back again
                print('\b \b', end='', flush=True)
        else:
            input_buffer.append(char)
            print(char, end='', flush=True)

    return ''.join(input_buffer)

def read_multi(prompt: str, color: str = None, bgcolor: str = None, bold: bool = False, italic: bool = False) -> str:
    """
    Reads multi-line input.

    Args:
        prompt: The prompt to display
        color: Text color
        bgcolor: Background color
        bold: Whether text should be bold
        italic: Whether text should be italic

    Returns:
        The multi-line input as a string
    """
    print_prompt(prompt, bgcolor, color, bold, italic)

    input_lines = []
    current_line = []

    while True:
        char = _get_input()
        if char is None:
            continue

        if char == '\r' or char == '\n':  # Enter key
            input_lines.append(''.join(current_line))
            print()  # New line after input
            current_line = []
        elif char == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif char == '\x7f':  # Backspace
            if current_line:
                current_line.pop()
                print('\b \b', end='', flush=True)
        elif char == '\x04':  # Ctrl+D
            # If we're at the end of a line, finish input
            input_lines.append(''.join(current_line))
            print()  # New line after input
            break
        else:
            current_line.append(char)
            print(char, end='', flush=True)

    return '\n'.join(input_lines)

def read_options(prompt: str, title: str, options: list[str], color: str = None, bgcolor: str = None, bold: bool = False, italic: bool = False) -> str:
    """
    Reads input from a list of options.

    Args:
        prompt: The prompt to display
        title: The title to display (in bold)
        options: List of option strings
        color: Text color
        bgcolor: Background color
        bold: Whether text should be bold
        italic: Whether text should be italic

    Returns:
        The selected option text or the raw input if not a valid option number
    """

    # Display title in bold
    print(_apply_styling(title, bold=True))

    # Display options
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")

    print_prompt(prompt, bgcolor, color, bold, italic)

    input_buffer = []
    while True:
        char = _get_input()
        if char is None:
            continue

        if char == '\r' or char == '\n':  # Enter key
            print()  # New line after input
            input_str = ''.join(input_buffer).strip()

            # Try to parse as number
            try:
                option_index = int(input_str) - 1
                if 0 <= option_index < len(options):
                    return options[option_index]
            except ValueError:
                pass  # Not a number, return raw input

            # Return raw input if not a valid option number
            return input_str
        elif char == '\x03':  # Ctrl+C
            raise KeyboardInterrupt
        elif char == '\x7f':  # Backspace
            if input_buffer:
                input_buffer.pop()
                # Move cursor back, erase character, move cursor back again
                print('\b \b', end='', flush=True)
        else:
            input_buffer.append(char)
            print(char, end='', flush=True)


def print_prompt(prompt: str, bgcolor: str | None, color: str | None, bold: bool, italic: bool):
    styled_prompt = _apply_styling(prompt + ' ', color, bgcolor, bold, italic)
    print(styled_prompt, end='', flush=True)
    styled_prompt = _apply_styling("⯈", bgcolor, None, True, False)
    print(styled_prompt, end='', flush=True)
    print(' ', end='', flush=True)

