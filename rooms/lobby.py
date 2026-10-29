# -----------------------------------------------------------------------------
# File: lobby.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

from utilities.check_status import check_status
from utilities.display_menu import display_selection_menu
from utilities.clear_screen import clear_screen
from utilities.inventory_viewer import display_inventory
from utilities.save_gui import display_save_menu
from utilities.game_map import display_map
from utilities.print_helpers import print_dialogue, print_assembly_part_obtained, print_current_objective

room_dialogue_bank = story_dialogue_bank["rooms"]["lobby"]
valid_destinations = ["frontdesk", "studentwing", "eastcorridor", "teachingarea"]

def enter_lobby(state):
    """Starter function for the Lobby room."""

    state["previous_room"] = "lobby"

    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])
    if not state["student_id_obtained"]:
        print_dialogue(room_dialogue_bank["no_student_id"], print_newline_after = False)

    def handle_look():
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player which
        rooms they can go to.

        Inputs: NONE

        Outputs: NONE
        """

        clear_screen()
        print_dialogue(look_around_dialogue_bank["lobby"])
        if "Robot Chassis Frame" not in state["inventory"]:
            print_dialogue(look_around_dialogue_bank["lobby-chassis-pickup"], print_newline_after = False)
            print_assembly_part_obtained("(+ Robot Chassis Frame)")
            state["current_objective_id"] += 1
            state["inventory"].append("Robot Chassis Frame")

        
        print(f"- Possible destinations: {', '.join(valid_destinations)}")
        print(f"- Your inventory: {state['inventory']}")
        print()
        print_current_objective(state)

    def handle_help():
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """
        clear_screen()
        print("Available commands:")
        print("- look around         : See what's in the corridor and where you can go.")
        print("- go <room name>      : Move to another room.'")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")
        print("- inventory           : Show what items are in your inventory.")
        print("- status              : Show current game status.")
        print("- save                : Save the current game state.")

        print()
        print_current_objective(state)

    while True:
        command = input("\n> ").strip().lower()

        if command in ["look around", "lk", "look", "l", "la"]:
            handle_look()

        elif command in ["?", "help"]:
            handle_help()

        elif command in ["g", "go", "goto", "move", "mv"] or command.startswith("go "):
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
            check_status(state)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
