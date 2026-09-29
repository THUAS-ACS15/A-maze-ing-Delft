# -----------------------------------------------------------------------------
# File: animations.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from time import sleep

from art import text2art # type: ignore[import-untyped]
from rich.console import Console
from utilities.print_line import print_line

PUZZLE_FINAL_TEXT = "PUZZLE!"
QUIZ_FINAL_TEXT = "QUIZ!"
QTE_FINAL_TEXT = "QUICK TIME!"


def show_activity_animation(type: str, text_delay: float = 0.002, final_delay: float = 2.0) -> None:
    """
    Clears the screen and displays the specified animation, frame-by-frame.

    This function takes the specified type, clears the screen and prints
    that animation in the CLI.

    Inputs:
        - type (str): "puzzle", "quiz" or "qte"
        - text_delay (float): delay between printing each line of the animation
        - final_delay (float): delay after the animation is fully printed

    Outputs: NONE
    """
    console = Console(legacy_windows=False)

    match type:
        case "puzzle":
            text_to_print = PUZZLE_FINAL_TEXT
        case "quiz":
            text_to_print = QUIZ_FINAL_TEXT
        case "qte":
            text_to_print = QTE_FINAL_TEXT
        case _:
            raise ValueError(f"Invalid type: {type}. Must be 'puzzle', 'quiz', or 'qte'.")

    print_line(text2art(text_to_print, font="univers", chr_ignore=True), text_delay, console)
    sleep(final_delay)
