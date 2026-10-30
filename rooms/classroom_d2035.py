# -----------------------------------------------------------------------------
# File: classroom_d2035.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

"""Classroom D2.035: seating and sequence puzzles awarding the A.I.G.I.S. motherboard."""

import sys

from data.look_around_dialogue_bank import look_around_dialogue_bank
from data.story_dialogue_bank import story_dialogue_bank
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.game_map import display_map
from utilities.inventory_viewer import display_inventory
from utilities.centralized_commands import display_help
from utilities.print_helpers import (
    print_assembly_part_obtained,
    print_current_objective,
    print_dialogue,
)
from utilities.save_gui import display_save_menu
from utilities.scoreboard import display_scoreboard

# Right order of the students: seat 1 (window) to seat 4 (aisle).
SEATING_ANSWER = ["ana", "chloe", "dev", "ben"]

# The timetable sequence. The gaps are 4, 6, 8, 10 so the next gap is 12 and 30 + 12 = 42.
SEQUENCE = [2, 6, 12, 20, 30]
SEQUENCE_ANSWER = 42

room_loot: dict[str, str] = {}
valid_destinations = ["teachingarea"]
room_dialogue_bank = story_dialogue_bank["rooms"]["classroomd2035"]

seating_done = False

room_commands = [
    (
        "inspect <object>",
        "Look closer (try the printer)."
    ),
    (
        "take <item>",
        "Pick up an item."
    )
]

def enter_classroom_d2035(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    state["previous_room"] = "classroomd2035"

    clear_screen()
    state["visited"]["classroomd2035"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    def handle_look(state):
        """Describe the room and what the player can do here."""
        loot = room_loot
        print("You take a look around.")
        print_dialogue(look_around_dialogue_bank["classroomd2035"])
        if len(loot) > 0:
            print("In the podium drawer:", ", ".join([item for item in loot.keys()]))
        print(f"- Possible exits: {', '.join(valid_destinations)}")
        print()
        print_current_objective(state)

    def show_seating_clues():
        """Print the lecturer's note with the seating clues."""
        print_dialogue(room_dialogue_bank["seating_intro"])
        print_dialogue(room_dialogue_bank["seating_ana"])
        print_dialogue(room_dialogue_bank["seating_ben"])
        print_dialogue(room_dialogue_bank["seating_chloe"])
        print_dialogue(room_dialogue_bank["seating_dev"])

    def play_seating(state):
        """Part 1: the player has 3 tries to type the students in the right order."""
        global seating_done
        
        print("PART 1: SEATING PLAN")
        show_seating_clues()
        for _ in range(3):
            guess = input("Seats 1-4, names separated by spaces (e.g. ana ben chloe dev) > ").lower().split()
            if guess == SEATING_ANSWER and not state["completed"]["classroomd2035"]:
                seating_done = True
                state["inventory"].append("Seating plan")
                print_dialogue(room_dialogue_bank["seating_success"])
                print_dialogue(room_dialogue_bank["seating_transfer"])
                return True
            print("The students shuffle around and nobody is happy. Check each clue against the seat numbers.")
        return False

    def play_sequence():
        """Part 2: the player has 3 tries to find the next number."""
        print_dialogue(room_dialogue_bank["podium_intro"])
        print_dialogue(room_dialogue_bank["podium_slip"], print_newline_after=False)
        print(SEQUENCE, "and then?")
        print_dialogue(room_dialogue_bank["podium_rule"])
        for _ in range(3):
            answer = input("Next number > ").strip()
            if answer == str(SEQUENCE_ANSWER):
                print_dialogue(room_dialogue_bank["podium_success"])
                return True
            print("Wrong. Look at the gaps between the numbers: 4, 6, 8, 10.")
        return False

    def play_podium(state):
        """Run both parts. Returns True when the player solved everything."""
        # Skip part 1 if the player already solved it on an earlier try.
        if not seating_done and not play_seating(state):
            return False
        return play_sequence()

    def inspect_object(state, name):
        """Look closer at one object in the room."""
        loot = room_loot
        if name == "desks":
            show_seating_clues()
        elif name == "lecturer":
            print_dialogue(room_dialogue_bank["lecturer"])
            print_dialogue(room_dialogue_bank["lecturer_sequence"])
        elif name == "podium":
            if state["completed"]["classroomd2035"]:
                print("You have already completed this room. There is nothing else to do here.")
            elif play_podium(state):
                state["completed"]["classroomd2035"] = True
                loot["motherboard"] = "A.I.G.I.S. Motherboard"
                print_dialogue(room_dialogue_bank["drawer"])
                print_dialogue(room_dialogue_bank["drawer_pickup"])
            else:
                print("No worries, inspect the podium again whenever you like to retry.")
        else:
            print(f"There is no {name} here.")

    def take_item(state, item_name):
        """Move an item from the podium drawer into the inventory."""
        loot = room_loot
        for shortcut, name in loot.items():
            if item_name != "" and item_name in name.lower():
                del loot[shortcut]
                print("You took the " + name + ".")
                state["inventory"].append(name)
                if name == "A.I.G.I.S. Motherboard":
                    state["current_objective_id"] += 1
                    state["completed"]["classroomd2035"] = True
                    print_assembly_part_obtained("(+ A.I.G.I.S. Motherboard)")
                    print()
                    print_current_objective(state)
                return  # stop right after removing, so the list is not changed while the loop runs
        print("There is no '" + item_name + "' here to take.")

    # The main loop: read a command, do what it says, repeat.
    while True:
        command = input("\n> ").lower().strip()

        if command in ["look around", "look", "ls", "l"]:
            clear_screen()
            handle_look(state)
        
        elif command in ["?", "help"]:
            clear_screen()
            display_help(room_commands)
        
        elif command.startswith("inspect "):
            clear_screen()
            inspect_object(state, command[8:].strip())
    
        elif command.startswith("take "):
            clear_screen()
            take_item(state, command[5:].strip())
    
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

        elif command in ["scoreboard", "sb"]:
            display_scoreboard(state)
        
        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command in ["quit", "exit"]:
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
