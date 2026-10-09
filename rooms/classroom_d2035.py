# -----------------------------------------------------------------------------
# File: classroom_d2035.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_current_objective, print_assembly_part_obtained

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

# Right order of the students: seat 1 (window) to seat 4 (aisle).
SEATING_ANSWER = ["ana", "chloe", "dev", "ben"]

# The timetable sequence. The gaps are 4, 6, 8, 10 so the next gap is 12 and 30 + 12 = 42.
SEQUENCE = [2, 6, 12, 20, 30]
SEQUENCE_ANSWER = 42

room_loot: dict[str, str] = {}
valid_destinations = ["teachingarea"]
room_dialogue_bank = story_dialogue_bank["rooms"]["classroomd2035"]

def enter_classroom_d2035(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    
    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    def handle_look(state):
        """Describe the room and what the player can do here."""
        loot = room_loot
        print("You take a look around.")
        print_dialogue(look_around_dialogue_bank["classroomd2035"])
        if len(loot) > 0:
            print("In the podium drawer:", ", ".join(loot))
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])
        print()
        print_current_objective(state)

    def handle_help():
        """Print the list of commands."""
        print("Available commands:")
        print("- look around         : Describe the room.")
        print("- inspect <object>    : Look closer (try the podium).")
        print("- take <item>         : Pick up an item.")
        print("- go [room]           : Leave the room.")
        print("- status / save       : Show your status / open the save menu.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

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

    def show_seating_clues():
        """Print the lecturer's note with the seating clues."""
        print_dialogue(room_dialogue_bank["seating_intro"])
        print_dialogue(room_dialogue_bank["seating_ana"])
        print_dialogue(room_dialogue_bank["seating_ben"])
        print_dialogue(room_dialogue_bank["seating_chloe"])
        print_dialogue(room_dialogue_bank["seating_dev"])

    def play_seating(state):
        """Part 1: the player has 3 tries to type the students in the right order."""
        print("PART 1: SEATING PLAN")
        show_seating_clues()
        for _ in range(3):
            guess = input("Seats 1-4, names separated by spaces (e.g. ana ben chloe dev) > ").lower().split()
            if guess == SEATING_ANSWER:
                state["d2035_progress"]["seating"] = True
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
        print(SEQUENCE, "and then ?")
        print_dialogue(room_dialogue_bank["podium_rule"])
        for _ in range(3):
            answer = input("Next number > ").strip()
            if answer == str(SEQUENCE_ANSWER):
                print_dialogue(room_dialogue_bank["podium_success"])
                return True
            print("Wrong. Look at the gaps between the numbers: 4, 6, 8, 10 ... The gap grows by 2 each time.")
        return False

    def play_podium(state):
        """Run both parts. Returns True when the player solved everything."""
        # Skip part 1 if the player already solved it on an earlier try.
        if not state["d2035_progress"]["seating"]:
            if not play_seating(state):
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
                loot.append("A.I.G.I.S. Motherboard")
                print_dialogue(room_dialogue_bank["drawer"])
                print_dialogue(room_dialogue_bank["drawer_pickup"])
            else:
                print("No worries, inspect the podium again whenever you like to retry.")
        else:
            print(f"There is no {name} here.")

    def take_item(state, item_name):
        """Move an item from the podium drawer into the inventory."""
        loot = room_loot
        for thing in loot:
            if item_name != "" and item_name in thing.lower():
                loot.remove(thing)
                print("You took the " + thing + ".")
                state["inventory"].append(thing)
                if item_name == "A.I.G.I.S. Motherboard":
                    state["current_objective_id"] += 1
                    print_assembly_part_obtained("(+ A.I.G.I.S. Motherboard)")
                    print()
                    print_current_objective(state)
                return  # stop right after removing, so the list is not changed while the loop runs
        print("There is no '" + item_name + "' here to take.")

    # The main loop: read a command, do what it says, repeat.
    while True:
        command = input("\n> ").lower().strip()

        if command == "look around" or command == "look" or command == "ls":
            clear_screen()
            handle_look(state)
        
        elif command == "?":
            clear_screen()
            handle_help()
        
        elif command.startswith("inspect "):
            clear_screen()
            inspect_object(state, command[8:].strip())
    
        elif command.startswith("take "):
            clear_screen()
            take_item(state, command[5:].strip())
    
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
            print("Unknown command. Type '?' to see available commands.")
