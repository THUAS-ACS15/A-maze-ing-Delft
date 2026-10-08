# -----------------------------------------------------------------------------
# File: teachersroom1.py
# Project: AMazeingDelft
# Organization: THUAS
# Location: Delft
# Date: September 2026
# Contributors: Dominik
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

from utilities.print_helpers import print_dialogue

room_dialogue_bank = story_dialogue_bank["rooms"]["teachersroom1"]

def enter_teachers_room1(state: dict) -> str:
    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"], print_newline_after = False)

    def handle_look():
        print_dialogue(look_around_dialogue_bank["teachersroom1"])
        if not state["completed"]["teachersroom1"]:
            print_dialogue(room_dialogue_bank["puzzle_not_complete"])
        print("- Possible exits: corridor")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("\nAvailable commands:")
        print("- ?                   : Show this help message.")
        print("- look around         : Examine the room and the code on screen.")
        if not state["completed"]["teachersroom1"]:
            print("- answer <snippet>    : Try to fill in the missing piece of code.")
        if state["completed"]["teachersroom1"] and "Staff Keycard" not in state["inventory"]:
            print("- take keycard       : Pick up the keycard.")
        print("- go corridor / back  : Leave the room and return to the corridor.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "keycard":
            if not state["completed"]["teachersroom1"]:
                print("There's nothing to take yet. Maybe help the teacher first.")
            elif "Staff Keycard" in state["inventory"]:
                print("You already have the keycard in your backpack.")
            else:
                state["coin_balance"] += 10
                clear_screen()
                print_dialogue(room_dialogue_bank["puzzle_take_keycard"])
                state["inventory"].append("Staff Keycard")
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["corridor", "back"]:
            return "lobby"
        else:
            print(f"You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer):
        if state["completed"]["teachersroom1"]:
            print_dialogue(room_dialogue_bank["puzzle_already_complete"])
            return
        # accept a few equivalent ways of writing "n % 2"
        normalized = answer.strip().lower().replace(" ", "")
        accepted = ["n%2", "n % 2"]
        if normalized in accepted:
            state["completed"]["teachersroom1"] = True
            clear_screen()
            print_dialogue(room_dialogue_bank["puzzle_answer_correct"])
            state["completed"]["teachersroom1"] = True
        else:
            print_dialogue(room_dialogue_bank["puzzle_answer_incorrect"])

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("take "):
            clear_screen()
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            clear_screen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            clear_screen()
            answer = command[7:].strip()
            handle_answer(answer)

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
