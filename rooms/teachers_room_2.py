# -----------------------------------------------------------------------------
# File: teachersroom2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Dominik, Gift Odigwe
# -----------------------------------------------------------------------------

"""Teacher Room 2: database puzzle awarding the Wi-Fi credentials."""

import sys

from data.look_around_dialogue_bank import look_around_dialogue_bank
from data.story_dialogue_bank import story_dialogue_bank
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.game_map import display_map
from utilities.inventory_viewer import display_inventory
from utilities.print_helpers import (
    print_assembly_part_obtained,
    print_current_objective,
    print_dialogue,
)
from utilities.save_gui import display_save_menu
from utilities.centralized_commands import display_help
from utilities.scoreboard import display_scoreboard

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

room_commands = [
    (
        "talk to teacher",
        "Talk to the teacher."
    ),
    (
        "answer <answer>",
        "Answer the teacher's question."
    ),
    (
        "look at database",
        "See what the database schema looks like."
    ),
    (
        "take credentials",
        "Take the credentials after helping the teacher."
    )
]

def enter_teachers_room2(state):
    """Starter function for Teachers Room 2."""

    state["previous_room"] = "teachersroom2"

    clear_screen()
    state["visited"]["teachersroom2"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    def handle_look():
        """Describe the room and the teacher's database puzzle."""
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
        print()
        print_current_objective(state)

    def handle_take(item):
        """Pick up the Wi-Fi credentials once the puzzle is solved."""
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

    def handle_answer(answer):
        """Check the student name answer and mark the puzzle complete."""
        if state["completed"]["teachersroom2"]:
            print("You've already solved this challenge.")
            return
        normalized = answer.strip()
        if normalized == "mia" or normalized == "Mia":
            state["completed"]["teachersroom2"] = True
            clear_screen()
            print_dialogue(room_dialogue_bank["puzzle_answer_correct"])
            state["completed"]["teachersroom2"] = True
        else:
            print_dialogue(room_dialogue_bank["puzzle_answer_incorrect"])

    while True:
        command = input("\n> ").lower()

        if command in ["look around", "lk", "look", "l", "la"]:
            clear_screen()
            handle_look()

        elif command in ["?", "help"]:
            clear_screen()
            display_help(room_commands)

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

        elif command in ["g", "go", "goto", "move"] or command.startswith("go "):
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
            check_status(state, pause = True)

        elif command in ["scoreboard", "sb"]:
            display_scoreboard()
    
        elif command in ["pause", "save"]:
            display_save_menu(state)
        
        elif command in ["quit", "exit"]:
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
