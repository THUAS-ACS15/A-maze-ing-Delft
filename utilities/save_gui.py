# -----------------------------------------------------------------------------
# File: save_gui.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from utilities.save_management import get_save_info, load_save, save_game
from utilities.status_bar import display_top_bar
from utilities.clear_screen import clear_screen

from time import sleep

from rich.align import Align
from rich.console import Console
from rich.table import Table

CHOOSE_SAVE_ART: str = """
██▀██ ██ ██ ██▀██ ██▀██ ██▀██ ██▀██      ██▀██ ██▀██ ██ ██ ██▀██      ██▀██ ██    ██▀██ ▀██▀
██    ██▄██ ██ ██ ██ ██ ██▄▄▄ ██▄        ██▄▄▄ ██▄██ ██ ██ ██▄        ██▄▄▄ ██    ██ ██  ██ 
█▓░▄▄ █▓░█▓ █▓░█▓ █▓░█▓ ▄▄ █▓ █▓░▄▄      ▄▄ █▓ █▓░█▓ █▓░█▓ █▓░▄▄      ▄▄ █▓ █▓░▄▄ █▓░█▓  █▓░
▀▀▀▀▀ ▀▀ ▀▀ ▀▀▀▀▀ ▀▀▀▀▀ ▀▀▀▀▀ ▀▀▀▀▀      ▀▀▀▀▀ ▀▀ ▀▀  ▀▀▀  ▀▀▀▀▀      ▀▀▀▀▀ ▀▀▀▀▀ ▀▀▀▀▀  ▀▀ """

SAVE_1_INDICATOR:str = """▄▄▄ 
▀██ 
 ██ 
 ██
 ██ 
 ▀▀ """

SAVE_2_INDICATOR: str = """▄▄▄▄▄ 
▀▀▀██ 
 ▄█▀▀ 
██▀
██▄██ 
▀▀▀▀▀"""

SAVE_3_INDICATOR: str = """▄▄▄▄▄ 
▀▀▀██ 
  ▀██ 
▄▄ ██
▀█▄█▀ 
 ▀▀▀ """

def display_save_art(console: Console):
    """
    Displays the save menu art and the save slot indicators.
    
    This function clears the screen, displays the top bar for decoration,
    and then prints the save menu art along with the indicators for each save slot.
    It also shows the current state of each save slot (empty or with some info).

    Inputs:
        - console (Console): The rich Console object used for printing to the terminal.

    Outputs: NONE
    """
    clear_screen("", False)
    display_top_bar(console)
    console.print(Align.center(CHOOSE_SAVE_ART, vertical="middle"))
    slot_indicators = [SAVE_1_INDICATOR, SAVE_2_INDICATOR, SAVE_3_INDICATOR]

    slots = Table.grid(padding=(0, 2))
    slots.add_column(justify="center")

    for slot, indicator in enumerate(slot_indicators, start = 1):
        save_info = get_save_info(slot)
        if save_info is None:
            info_rows = ["", "[dim]Empty[/dim]", "[dim]slot[/dim]", ""]
        else:
            info_rows = [
                f"Room: {save_info['current_room']}",
                f"Exploration: {round(save_info['exploration_percent'], 2)}%",
                f"Coins: {save_info['coin_balance']}",
                f"Time: {round(save_info['time_elapsed'], 2)}s",
            ]

        indicator_rows = indicator.strip("\n").splitlines()
        for row, indicator_line in enumerate(indicator_rows):
            info_line = info_rows[row - 1] if 1 <= row <= 4 else ""
            slots.add_row(indicator_line, info_line)

        slots.add_row("", "")

    console.print(Align.center(slots, vertical="middle"))

def display_save_menu(state: dict):
    """
    Displays the save menu, allowing the player to choose a save slot to SAVE their progress.
    
    This function displays the save menu art and prompts the player to select a save slot (1, 2, or 3) or to quit.
    It validates the input and saves the game state to the chosen slot. 
    If the player chooses to quit, it exits the save menu.
    
    Inputs:
        - state (dict): The current game state to be saved.
        
    Outputs: NONE
    """
    console: Console = Console()

    display_save_art(console)

    while True:
        save_slot_input = console.input("\n[bold white]SAVE YOUR PROGRESS TO SLOT:[/bold white] ")

        if save_slot_input not in ["1", "2", "3", "quit"]:
            console.print(Align.center("[bold red]Invalid input. Please enter 1, 2, 3, or 'quit'.[/bold red]"))
            sleep(2)
            clear_screen("", False)
            display_save_art(console)
            continue
        if save_slot_input == "quit":
            console.print(Align.center("[bold red]Exiting save menu...[/bold red]"))
            sleep(1)
            return None
        save_slot = int(save_slot_input)

        save_game(state, save_slot)
        console.print(Align.center(f"[bold green]GAME SAVED TO SLOT {save_slot}![/bold green]"))
        sleep(2)
        return

def display_load_menu():
    """
    Displays the save menu, allowing the player to choose a save slot to LOAD their progress.
    
    This function displays the save menu art and prompts the player to select a save slot (1, 2, or 3) or to quit.
    It validates the input and loads the game state from the chosen slot. 
    If the player chooses to quit, it exits the load menu.
    
    Inputs: NONE
        
    Outputs: NONE
    """
    console: Console = Console()

    display_save_art(console)

    while True:
        save_slot_input = console.input("\n[bold white]LOAD YOUR PROGRESS FROM SLOT:[/bold white] ")

        if save_slot_input not in ["1", "2", "3", "quit", "exit", "back"]:
            console.print(Align.center("[bold red]Invalid input. Please enter 1, 2, 3, or 'quit'.[/bold red]"))
            sleep(2)
            clear_screen("", False)
            display_save_art(console)
            continue
        if save_slot_input == "quit" or save_slot_input == "exit" or save_slot_input == "back":
            return None
        save_slot = int(save_slot_input)
        
        loaded_state = load_save(save_slot)
        
        if loaded_state is not None:
            console.print(Align.center(f"[bold green]Game loaded from slot {save_slot}![/bold green]"))
            return loaded_state
        else:
            console.print(Align.center(f"[bold red]No save found in slot {save_slot}. Please try again.[/bold red]"))