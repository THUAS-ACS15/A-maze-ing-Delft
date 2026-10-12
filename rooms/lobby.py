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
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_assembly_part_obtained, print_current_objective

room_dialogue_bank = story_dialogue_bank["rooms"]["lobby"]
available_rooms = ["frontdesk", "studentwing", "eastcorridor", "teachingarea"]

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

        
        print(f"- Possible doors: {', '.join(available_rooms)}")
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
        print("- status              : Show current game status.")
        print("- save                : Save the current game state.")

        print()
        print_current_objective(state)

    def handle_go(room_name):
        """
        Handles movement out of the room.

        Checks if destination is valid directly or through aliases,
        then returns the standardized room string for main.py.
        """
        clear_screen()

        if room_name in available_rooms:
            return room_name
        else:
            print(f"❌ '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command in ["?", "help"]:
            handle_help()

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

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
