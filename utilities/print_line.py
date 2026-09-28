from rich.console import Console
from rich.syntax import Syntax
from rich.text import Text
import time


def print_line(
    text: str,
    delay: float | int = 0,
    console: Console | None = Console(),
) -> None:
    """
    Print a single line of text to the console, optionally with Rich styling.

    If no console is provided, a new Rich Console instance is created. When a
    style is given, the text is rendered using Rich's Text object; otherwise,
    the plain text is printed.

    Args:

        text (str): The text to print.
        delay (float | int): Delay between lines in seconds to preserve a streaming
            effect. Currently not used in the function body.
        console (Console): Rich console used for output.

    Returns:
        None
    """
    if console is None:
        console = Console()
    if delay > 0:
        for t in text:
            console.print(t, end="")
            time.sleep(delay)
        console.print("\n")
    else:
        console.print(text)
