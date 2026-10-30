# -----------------------------------------------------------------------------
# File: corridor_east.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

"""East corridor: connects the lobby to Teacher Rooms 1, 2, and 4."""

import sys

from data.look_around_dialogue_bank import look_around_dialogue_bank
from data.story_dialogue_bank import story_dialogue_bank
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.game_map import display_map
from utilities.inventory_viewer import display_inventory
from utilities.print_helpers import print_current_objective, print_dialogue
from utilities.centralized_commands import display_help
from utilities.save_gui import display_save_menu

valid_destinations = ["lobby", "teachersroom1", "teachersroom2", "teachersroom4"]
room_dialogue_bank = story_dialogue_bank["rooms"]["eastcorridor"]

def enter_east_corridor(state: dict) -> str:
    """Starter function for the East Corridor"""

    state["previous_room"] = "eastcorridor"

    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        box stacking puzzle. It also shows the possible exits and the
        player's current inventory.
        """
        
        print_dialogue(look_around_dialogue_bank["eastcorridor"])
        print(f"- Possible exits: {', '.join(valid_destinations)}")
        print(f"- Your current inventory: {state['inventory']}")
        print()
        print_current_objective(state)

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command in ["?", "help"]:
            clear_screen()
            display_help()
        
        elif command in ["g", "go", "goto", "move"] or command.startswith("go "):
            result = display_selection_menu("Choose room to go to:", valid_destinations)
            if result:
                return result

        elif command == "map":
            display_map(state)
            
        elif command in ["inv", "inventory"]:
            clear_screen()
            display_inventory(state["inventory"])
    
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
