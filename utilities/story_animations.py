import sys
import textwrap
from threading import Event, Thread
from time import sleep

from rich.align import Align
from rich.console import Console
from rich.live import Live

from data.story_dialogue_bank import story_dialogue_bank
from utilities.clear_screen import clear_screen
from utilities.main_menu import read_key
from utilities.save_management import update_elapsed_time
from utilities.scoreboard import add_scoreboard_entry
from utilities.status_bar import display_top_bar, get_exploration_percent

GAME_COMPLETE_ART: str = """
██▀██  ██▀██ ██▀██▀██ ██▀██      ██▀██ ██▀██ ██▀██▀██ ██▀██ ██    ██▀██ ▀██▀ ██▀██  █
██ ▀▀  ██▄██ ██ ██ ██ ██▄        ██    ██ ██ ██ ██ ██ ██▄█▀ ██    ██▄    ██  ██▄    █
█▓░██▀ █▓░█▓ █▓░█▓░█▓ █▓░▄▄      █▓░▄▄ █▓░█▓ █▓░█▓░█▓ █▓░   █▓░▄▄ █▓░▄▄  █▓░ █▓░▄▄  ▀
▀▀▀▀▀  ▀▀ ▀▀ ▀▀    ▀▀ ▀▀▀▀▀      ▀▀▀▀▀ ▀▀▀▀▀ ▀▀    ▀▀ ▀▀    ▀▀▀▀▀ ▀▀▀▀▀  ▀▀  ▀▀▀▀▀  ▀"""

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
    # create enter event so player can skip with enter
    enter_pressed = Event()

    def wait_for_enter() -> None:
        sys.stdin.readline()
        enter_pressed.set()

    Thread(target=wait_for_enter, daemon=True).start()

    # streaming this centered text requires a Live context manager
    # to update the console in real-time, we use 20fps for this
    # and add the text that was already displayed to the new text, 
    # so that it appears to be typed out
    console.print(Align.center("\n\n[bold gray]\\[press enter to skip][/bold gray]\n"))
    with Live(console = console, refresh_per_second = 20) as terminal:
        for t in intro_text:
            if enter_pressed.is_set():
                break
            displayed_text += t
            terminal.update(Align.center(displayed_text), refresh=True)
            sleep(delay)

    if enter_pressed.is_set():
        clear_screen("", False)
        display_top_bar(console)
        print('\n' * 8)
        console.print(Align.center(intro_text))

    sleep(1)
    console.print(Align.center("\n\n[bold gray]\\[press enter to continue][/bold gray]"))
    input()

    enter_pressed.wait()

def play_game_complete(state) -> None:
    """
    Plays the game complete cutscene and animatio
    
    This function creates a Rich console, clears the screen and prints the story
    intro text in a typewriter effect. 
    It waits for the player to press Enter before continuing with completing the game.
    
    Inputs: NONE
    
    Outputs: NONE
    """
    # menu options for choosing to save to scoreboard
    menu_options = ["Yes, save to scoreboard", "No, don't save to scoreboard"]
    
    console = Console()
    clear_screen("", False)
    display_top_bar(console)
    print('\n' * 8)

    intro_text = textwrap.fill(story_dialogue_bank["story_important_flags"]["game_complete"], width = 55)
    delay = 0.025

    displayed_text = ""
    # create enter event so player can skip with enter
    enter_pressed = Event()

    def wait_for_enter() -> None:
        sys.stdin.readline()
        enter_pressed.set()

    Thread(target=wait_for_enter, daemon=True).start()

    # streaming this centered text requires a Live context manager
    # to update the console in real-time, we use 20fps for this
    # and add the text that was already displayed to the new text, 
    # so that it appears to be typed out
    with Live(console = console, refresh_per_second = 20) as terminal:
        for t in intro_text:
            displayed_text += t
            terminal.update(Align.center(displayed_text), refresh=True)
            sleep(delay)
            if enter_pressed.is_set():
                    break

    if enter_pressed.is_set():
        clear_screen("", False)
        display_top_bar(console)
        print('\n' * 8)
        console.print(Align.center(intro_text))
    
    sleep(1)
    console.print(Align.center("\n\n[bold gray]\\[press enter to continue][/bold gray]"))
    input()

    clear_screen("", False)
    console.print("\n\n\n\n\n\n\n\n")
    console.print(Align.center(GAME_COMPLETE_ART))
    sleep(5)

    console.print("\n\n")
    console.print(Align.center("Do you wish to add your completion to the local scoreboard?"))
    console.print(Align.center("Your player name, exploration percent and time played will be stored.\n"))

    selected_index = 0

    def render_menu() -> None:
        clear_screen("", False)
        console.print("\n" * 8)
        console.print(Align.center("Do you wish to add your completion to the local scoreboard?"))
        console.print(Align.center("Your player name, exploration percent and time played will be stored.\n"))
        console.print(Align.center("\n[italic][use up/down to select][/italic]"))

        # render the menu options with the current selection highlighted
        for index, option in enumerate(menu_options):
            prefix = "> " if index == selected_index else "  "
            suffix = " <" if index == selected_index else "  "

            line = f"{prefix}{option}{suffix}"
            if index == selected_index:
                line = f"[bold green]{line}[/bold green]"
            console.print(Align.center(line))

    render_menu()

    while True:
        key = read_key()

        if key == "up":
            selected_index = (selected_index - 1) % len(menu_options)
            render_menu()
        elif key == "down":
            selected_index = (selected_index + 1) % len(menu_options)
            render_menu()
        elif key == "enter":
            update_elapsed_time(state)
            if selected_index == 0:
                add_scoreboard_entry(
                    state.get("player_name", "Student"),
                    get_exploration_percent(state),
                    state["time_elapsed"],
                )
                console.print(Align.center("\n\n[bold green]Your completion was saved![/bold green]"))
                sleep(2)
                break
            elif selected_index == 1:
                console.print(Align.center("\n\n[bold red]Your completion was not saved.[/bold red]"))
                sleep(2)
                break