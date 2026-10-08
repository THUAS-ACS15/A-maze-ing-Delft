from rich.console import Console
from rich.align import Align
from rich.live import Live

from time import sleep
import textwrap

from utilities.clear_screen import clear_screen
from utilities.status_bar import display_top_bar

from data.story_dialogue_bank import story_dialogue_bank

def play_intro() -> None:
    """
    Plays the intro that sets the story context for the player.
    
    This function creates a Rich console, clears the screen and prints the story
    intro text in a typewriter effect. 
    It waits for the player to press Enter before returning and letting the code continue.
    
    Inputs: NONE
    
    Outputs: NONE
    """
    
    console = Console()
    clear_screen("", False)
    display_top_bar(console)
    print('\n' * 8)

    intro_text = textwrap.fill(story_dialogue_bank["story_important_flags"]["intro"], width = 55)
    delay = 0.025

    displayed_text = ""
    # streaming this centered text requires a Live context manager
    # to update the console in real-time, we use 20fps for this
    # and add the text that was already displayed to the new text, 
    # so that it appears to be typed out
    with Live(console = console, refresh_per_second = 20) as terminal:
        for t in intro_text:
            displayed_text += t
            terminal.update(Align.center(displayed_text), refresh=True)
            sleep(delay)

    sleep(3)
    console.print(Align.center("\n\n[bold gray]\\[press enter to continue][/bold gray]"))
    input()

def play_game_complete() -> None:
    pass