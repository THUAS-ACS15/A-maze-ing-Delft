# -----------------------------------------------------------------------------
# File: prompt.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe
# -----------------------------------------------------------------------------

from rich.console import Console
from rich.prompt import Prompt


def prompt(
    choices: list,
    console: Console = Console(),
    command: str = "",
) -> str:
    """
    Display a Rich prompt and return the user's selected command.

    Args:
        console (Console): Rich console used for displaying the prompt.
        choices (list[str]): List of valid choices shown to the user.
        command(str, optional): command to display what is expected of the user.

    Returns:
        str: The command or choice entered by the user.
    """
    return Prompt.ask(
        command,
        choices=choices,
        show_choices=False,
        console=console,
    )
