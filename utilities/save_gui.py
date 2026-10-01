# -----------------------------------------------------------------------------
# File: save_gui.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from utilities.save_management import get_save_info, load_save, save_game
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
    clear_screen()
    console.print(Align.center(CHOOSE_SAVE_ART, vertical="middle"))

    slot_indicators = [SAVE_1_INDICATOR, SAVE_2_INDICATOR, SAVE_3_INDICATOR]

    slots = Table.grid(padding=(0, 2))
    slots.add_column(justify="center")
    slots.add_column(justify="center")

    for slot, indicator in enumerate(slot_indicators, start = 1):
        save_info = get_save_info(slot)
        if save_info is None:
            info_rows = ["", "[dim]Empty[/dim]", "[dim]slot[/dim]", ""]
        else:
            info_rows = [
                f"Room: {save_info['current_room']}",
                f"Exploration: {save_info['exploration_percent']}%",
                f"Coins: {save_info['coin_balance']}",
                f"Time: {save_info['time_elapsed']}s",
            ]

        indicator_rows = indicator.strip("\n").splitlines()
        for row, indicator_line in enumerate(indicator_rows):
            info_line = info_rows[row - 1] if 1 <= row <= 4 else ""
            slots.add_row(indicator_line, info_line)

        slots.add_row("", "")

    console.print(Align.center(slots, vertical="middle"))

def display_save_menu(state: dict):
    console: Console = Console()

    display_save_art(console)

    while True:
        save_slot_input = console.input("\n[bold white]SAVE YOUR PROGRESS TO SLOT:[/bold white] ")

        if save_slot_input not in ["1", "2", "3", "quit"]:
            console.print(Align.center("[bold red]Invalid input. Please enter 1, 2, 3, or 'quit'.[/bold red]"))
            sleep(2)
            clear_screen()
            display_save_art(console)
            continue
        if save_slot_input == "quit":
            console.print(Align.center("[bold red]Exiting save menu...[/bold red]"))
            sleep(1)
            return
        save_slot = int(save_slot_input)

        save_game(state, save_slot)
        console.print(Align.center(f"[bold green]GAME SAVED TO SLOT {save_slot}![/bold green]"))
        sleep(2)
        return

def display_load_menu():
    console: Console = Console()

    display_save_art(console)

    while True:
        save_slot_input = console.input("\n[bold white]LOAD YOUR PROGRESS FROM SLOT:[/bold white] ")

        if save_slot_input not in ["1", "2", "3", "quit"]:
            console.print(Align.center("[bold red]Invalid input. Please enter 1, 2, 3, or 'quit'.[/bold red]"))
            sleep(2)
            clear_screen()
            display_save_art(console)
            continue
        if save_slot_input == "quit":
            console.print(Align.center("[bold red]Exiting...[/bold red]"))
            sleep(1)
            return None
        save_slot = int(save_slot_input)
        
        loaded_state = load_save(save_slot)
        
        if loaded_state is not None:
            console.print(Align.center(f"[bold green]Game loaded from slot {save_slot}![/bold green]"))
            return loaded_state
        else:
            console.print(Align.center(f"[bold red]No save found in slot {save_slot}. Please try again.[/bold red]"))