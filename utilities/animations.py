# -----------------------------------------------------------------------------
# File: animations.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from time import sleep
from utilities.clear_screen import clearScreen
from utilities.animation_frames import puzzle_frames, quiz_frames, qte_frames

def showActivityAnimation(type: str) -> None:
    """
    Clears the screen and displays the specified animation, frame-by-frame.

    This function takes the specified type, clears the screen and prints 
    that animation in the CLI.

    Inputs:
        - type (str): only "puzzle" and "quiz" are currently supported, more TBD
        - state (dict): the game state dict, to pass to clearScreen
    
    Outputs: NONE
    """
    frames_to_print = []
    # Switch to set frames_to_print based on type passed
    match type:
        case "puzzle":
            frames_to_print = puzzle_frames
        case "quiz":
            frames_to_print = quiz_frames
        case "qte":
            frames_to_print = qte_frames
        case _:
            raise ValueError(f"Invalid animation type {type} in {__name__}. Must be one of: puzzle, quiz, qte.")

    # Render frames except last two, with 0.3s delay
    for frame in frames_to_print[:-2]:
        clearScreen()
        print(frame)
        sleep(0.30)
    
    repeat_counter = 0
    clearScreen()
    # Repeat last two frames 3 times, then print second to last to have last end with NE orientation
    while repeat_counter < 3:
        for frame in frames_to_print[-2:]:
            clearScreen()
            print(frame)
            sleep(0.30)
        repeat_counter += 1
    clearScreen()
    print(frames_to_print[-2])