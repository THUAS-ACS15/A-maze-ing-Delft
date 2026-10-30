# -----------------------------------------------------------------------------
# File: teachersroom1.py
# Project: AMazeingDelft
# Organization: THUAS
# Location: Delft
# Date: September 2026
# Contributors: Dominik
# -----------------------------------------------------------------------------

"""Teacher Room 1: code-snippet puzzle awarding the staff keycard."""

import sys

from data.look_around_dialogue_bank import look_around_dialogue_bank
from data.story_dialogue_bank import story_dialogue_bank
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.game_map import display_map
from utilities.inventory_viewer import display_inventory
from utilities.print_helpers import print_current_objective, print_dialogue
from utilities.save_gui import display_save_menu

valid_destinations = ["eastcorridor"]
room_dialogue_bank = story_dialogue_bank["rooms"]["teachersroom1"]

def enter_teachers_room1(state: dict) -> str:
    """Starter function for Teachers Room 1."""

    state["previous_room"] = "teachersroom1"

    clear_screen()
    state["visited"]["teachersroom1"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"], print_newline_after = False)

    def handle_look():
        """Describe the room and show the code puzzle until it is solved."""
        print_dialogue(look_around_dialogue_bank["teachersroom1"])
        if not state["completed"]["teachersroom1"]:
            print_dialogue(room_dialogue_bank["puzzle_not_complete"])
        print(f"- Possible exits: {','.join(valid_destinations)}")
        print()
        print_current_objective(state)

    def handle_help():
        """Print the room's available commands."""
        print("\nAvailable commands:")
        print("- ?                   : Show this help message.")
        print("- look around         : Examine the room and the code on screen.")
        print("- inventory           : Show what items are in your inventory.")
        print("- save                : Save the current game state.")
        print("- status              : Show current game status.")
        if not state["completed"]["teachersroom1"]:
            print("- answer <snippet>    : Try to fill in the missing piece of code.")
        print("- go                  : Leave the room and return to the corridor.")
        print("- quit                : Quit the game entirely.")

    def handle_answer(answer):
        """Check the code snippet and award the staff keycard on success."""
        if state["completed"]["teachersroom1"]:
            print_dialogue(room_dialogue_bank["puzzle_already_complete"])
            return
        # accept a few equivalent ways of writing "n % 2"
        normalized = answer.strip().lower().replace(" ", "")
        accepted = ["n%2", "n % 2"]
        if normalized in accepted:
            state["completed"]["teachersroom1"] = True
            state["current_objective_id"] += 1
            clear_screen()
            print_dialogue(room_dialogue_bank["puzzle_answer_correct"])
            print_dialogue(room_dialogue_bank["puzzle_take_keycard"])
            state["inventory"].append("Staff Keycard")
        else:
            print_dialogue(room_dialogue_bank["puzzle_answer_incorrect"])

    while True:
        command = input("\n> ").strip().lower()

        if command in ["look around", "lk", "look", "l", "la"]:
            clear_screen()
            handle_look()

        elif command in ["?", "help"]:
            clear_screen()
            handle_help()

        elif command in ["g", "go", "goto", "move", "mv"] or command.startswith("go "):
            result = display_selection_menu("Choose room to go to:", valid_destinations)
            if result:
                return result

        elif command.startswith("answer "):
            clear_screen()
            answer = command[7:].strip()
            handle_answer(answer)

        elif command == "map":
            display_map(state)

        elif command in ["inv", "inventory"]:
            clear_screen()
            display_inventory(state["inventory"])
    
        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
