# -----------------------------------------------------------------------------
# File: display_menu.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

from rich.console import Console

from utilities.main_menu import read_key
from utilities.status_bar import room_fancy_names
from utilities.clear_screen import clear_screen

def render_command_options(console: Console, selected_index: int, command_desc: str, commands: dict | list) -> None:
    """
    Renders the command options in the console.
    
    This function is responsible for rendering the command options in the console,
    highlighting the currently selected option.

    Inputs:
        console (Console): The rich console object for rendering.
        selected_index (int): The index of the currently selected command.
        command_desc (str): Description of the command list, outputted above the commands.
        commands (dict | list): A dictionary or list of commands to display.
    
    Outputs: NONE
    """
    clear_screen("use up/down and enter to select", True)
    console.print(command_desc, style = "bold white")

    if isinstance(commands, list):
        lengths = [len(cmd) for cmd in commands]
    else:
        lengths = [len(cmd) for cmd in commands.keys()]
    
    max_length = max(lengths)
    i = 0

    if isinstance(commands, list):
        for option in commands:
            prefix = '   '
            if i == selected_index:
                style = 'bold green'
                prefix = ' > '
            else:
                style = 'white'

            if option in room_fancy_names:
                console.print(f"{prefix}{room_fancy_names[option]}", style = style)
            else:
                console.print(f"{prefix}{option}", style = style)
            i += 1
    else:
        for command, description in commands.items():
            prefix = '   '
            if i == selected_index:
                style = 'bold green'
                prefix = ' > '
            else:
                style = 'white'
            
            console.print(f"{prefix}{command.ljust(max_length)} : {description}", style = style)
            i += 1

def display_selection_menu(command_desc: str, options: dict[str, str] | list) -> str:
    """
    Displays a selection menu for the player to choose from a list of options.

    This function displays a selection menu in the console, allowing the player to
    navigate through the options using the up and down arrow keys and select
    an option by pressing Enter.

    Inputs:
        command_desc (str): Description of the command list, outputted above the commands.
        options (dict[str, str] | list): A dictionary or list of options to display.
    
    Outputs:
        str: The selected option from the menu.
    """

    selected_index = 0

    console = Console()
    console.print(command_desc, style = "bold white")
    render_command_options(console, selected_index, command_desc, options)

    while True:
        key = read_key()

        if key == "up":
            selected_index = (selected_index - 1) % len(options)
            render_command_options(console, selected_index, command_desc, options)
        elif key == "down":
            selected_index = (selected_index + 1) % len(options)
            render_command_options(console, selected_index, command_desc, options)
        elif key == "enter":
            clear_screen()
            return list(options)[selected_index]

def display_menu(console: Console, commands: dict[str, str] | list[tuple[str, str]]):
    """Display the room's command list."""
    console.print("List of all available commands for this room")
    command_items = commands.items() if isinstance(commands, dict) else commands
    for command, description in command_items:
        console.print(f"{'':<3}{command:<20} : {description}")