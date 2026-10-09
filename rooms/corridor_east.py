# -----------------------------------------------------------------------------
# File: corridor_east.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_current_objective

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

valid_destinations = ["lobby", "teachersroom1", "teachersroom2", "teachersroom4"]
room_dialogue_bank = story_dialogue_bank["rooms"]["eastcorridor"]

def enter_east_corridor(state: dict) -> str:
    """Starter function for the East Corridor"""

    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        box stacking puzzle. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """
        
        print_dialogue(look_around_dialogue_bank["eastcorridor"])
        print(f"- Possible exits: {', '.join(valid_destinations)}")
        print(f"- Your current inventory: {state['inventory']}")
        print()
        print_current_objective(state)

    def handle_help() -> None:
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """

        print("Available commands:")
        print("- ?                : Show this help message.")
        print("- look around      : Examine the room for clues.")
        print("- go [room]        : Leave the room and return to the corridor.")
        print("- quit             : Quit the game completely or exit a puzzle if in progress.")
        print("- status           : Show current game status.")
        print("- save             : Save the current game state.")

    def handle_go(destination: str) -> str | None:
        """
        Handles movement out of the room.

        This function checks if the player can move to the given destination from this room.
        If the destination is valid, it returns the destination string. Otherwise, it prints an error message and
        returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.

        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
 
        if destination in valid_destinations:
            return destination
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
