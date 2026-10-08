# -----------------------------------------------------------------------------
# File: print_line.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Gift Odigwe, Leon
# -----------------------------------------------------------------------------

import time
import textwrap

from rich.console import Console

from data.objective_dialogue_bank import objective_dialogue_bank

def print_dialogue(dialogue_line: str, width: int = 80, print_newline_after: bool = True) -> None:
    """
    Cleans up dictionary strings and wraps them to a set terminal width.

    This function is used to print dialogue lines from the dialogue_bank dictionary
    in a wrapped and readable format. 
    It removes leading spaces, replaces manual line breaks with spaces,
    and wraps the text to a specified width for better readability in the terminal.

    Inputs:
         - dialogue_line (str): The dialogue line to be printed.
         - width (int): The maximum width of the text in the terminal.

    Outputs: NONE
    """

    # dedent and strip fix the indentation of dialogue lines in multi line strings,
    # and we also replace newlines with spaces so the text can be wrapped cleanly.
    clean_text = textwrap.dedent(dialogue_line).strip().replace('\n', ' ')
    
    # use textwrap to wrap the text within a certain width, so it looks good
    # in the terminal window
    wrapped_text = textwrap.fill(clean_text, width = width)
    
    if print_newline_after:
        print(wrapped_text + '\n')
    else:
        print(wrapped_text)

def print_assembly_part_obtained(text: str) -> None:
    """
    Prints a message indicating that the player has obtained an assembly part.

    This function is used to notify the player that they have obtained an assembly part
    in the game. It uses Rich's Console for styled output.

    Inputs:
        - text (str): The message to print.
    """
    console = Console()

    console.print(text, style="bold green")

def print_current_objective(state: dict) -> None:
    """
    Prints a message indicating the new objective, based on its ID.

    This function is used to notify the player of their new objective.
    It uses Rich's Console for styled output.

    Inputs: 
        - state (dict): The current game state, which contains the objective ID.

    Outputs: NONE
    """
    console = Console()

    console.print(f"Current objective: ", style = "bold white", end = "")
    console.print(objective_dialogue_bank[state["current_objective_id"]], style = "bold green")

def print_line(
    text: str,
    delay: float | int = 0,
    console: Console | None = None,
    style: str | None = None,
) -> None:
    """
    Print a single line of text to the console, optionally with Rich styling.

    If no console is provided, a new Rich Console instance is created. When a
    style is given, the text is rendered using Rich's Text object; otherwise,
    the plain text is printed.

    Args:

        text (str): The text to print.
        delay (float | int): Delay between lines in seconds to preserve a streaming effect.
        console (Console): Rich console used for output.
        style (str | None): Optional Rich style, for example ``"bold cyan"``.

    Returns:
        None
    """
    if console is None:
        console = Console()

    if delay > 0:
        for t in text:
            console.print(t, end="", style = style)
            time.sleep(delay)
        console.print("\n", style = style)
    else:
        console.print(text, style = style)
