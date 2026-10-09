# -----------------------------------------------------------------------------
# File: teachersroom2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Dominik, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_assembly_part_obtained, print_current_objective

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

valid_destinations = ["eastcorridor"]
room_dialogue_bank = story_dialogue_bank["rooms"]["teachersroom2"]

DATABASES = """
Students table:
| student_id | name |
|-----------:|------|
| 1          | Mia  |
| 2          | Sam  |
| 3          | Noah |

Courses table:
| course_id | course_name   | teacher       |
|----------:|---------------|---------------|
| 10        | Databases     | Mrs. Jansen   |
| 11        | Python        | Mr. der Linde |
| 12        | Cybersecurity | Mr. Baker     |

Enrollments table:
| student_id | course_id |
|-----------:|-----------|
| 1          | 10        |
| 1          | 11        |
| 2          | 12        |
| 3          | 11        |
| 3          | 12        |
"""

def enter_teachers_room2(state):
    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    def handle_look():
        clear_screen()
        print("You take a look around.")
        if not state["completed"]["teachersroom2"]:
            print_dialogue(look_around_dialogue_bank["teachersroom2"])
        else:
            print_dialogue(room_dialogue_bank["puzzle_already_complete"])
            if "Wi-Fi Credentials" not in state["inventory"]:
                print("A sticky note with login credentials is still lying on the desk.")
            else:
                print("The desk is tidy now, you've already taken the credentials.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])
        print()
        print_current_objective(state)

    def handle_help():
        clear_screen()
        print("Available commands:")
        print("- look around         : See what the teacher needs help with.")
        if not state["completed"]["teachersroom2"]:
            print("- look at database    : See the tables the teacher is working with.")
            print("- talk to teacher     : Ask the teacher what they need help with.")
            print("- answer <name>       : Tell the teacher the student's name.")
        if state["visited"]["teachersroom2"] and "Wi-Fi Credentials" not in state["inventory"]:
            print("- take credentials    : Pick up the Wi-Fi credentials.")
        print("- go lobby / back     : Leave the room and return to the lobby.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item == "credentials":
            if not state["completed"]["teachersroom2"]:
                print("There's nothing to take yet. Maybe help the teacher first.")
            elif "Wi-Fi Credentials" in state["inventory"]:
                print("You already have the credentials in your inventory.")
            else:
                print_dialogue(room_dialogue_bank["puzzle_take_wifi_credentials"])
                print_assembly_part_obtained("(+ Wi-Fi Credentials)")
                state["inventory"].append("Wi-Fi Credentials")
                state["current_objective_id"] += 1
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in valid_destinations:
            return destination
        else:
            print(f"You can't go to '{destination}' from here.")
            return ""

    def handle_answer(answer):
        if state["completed"]["teachersroom2"]:
            print("You've already solved this challenge.")
            return
        normalized = answer.strip()
        if normalized == "mia" or normalized == "Mia":
            state["coin_balance"] += 5
            state["completed"]["teachersroom2"] = True
            clear_screen()
            print_dialogue(room_dialogue_bank["puzzle_answer_correct"])
            state["completed"]["teachersroom2"] = True
        else:
            print_dialogue(room_dialogue_bank["puzzle_answer_incorrect"])

    while True:
        command = input("\n> ").lower()

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

        elif command == "talk to teacher":
            clear_screen()
            print_dialogue(room_dialogue_bank["talk_to_teacher"])

        elif command == "look at database":
            clear_screen()
            print(DATABASES)

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
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)
    
        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
