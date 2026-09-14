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
from utilities.animation_frames import puzzle_frames

def showActivityAnimation(type: str, state: dict) -> None:
    """
    Clears the screen and displays the specified animation, frame-by-frame.

    This function takes the specified type, clears the screen and prints 
    that animation in the CLI.

    Inputs:
        - type (str): only "puzzle" currently, more TBD
        - state (dict): the game state dict, to pass to clearScreen
    
    Outputs: NONE
    """

    if type == "puzzle":
        for frame in puzzle_frames[:-2]:
            clearScreen()
            print(frame)
            sleep(0.30)
        repeat_counter = 0
        clearScreen()
        while repeat_counter < 3:
            for frame in puzzle_frames[-2:]:
                clearScreen()
                print(frame)
                sleep(0.30)
            repeat_counter += 1
        clearScreen()
        print(puzzle_frames[6])