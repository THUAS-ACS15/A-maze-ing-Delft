# -----------------------------------------------------------------------------
# File: classroom_d2015.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Classroom D2.015: electrical puzzle room holding the memory sticks."""

# Classroom D2.015. The player needs the D2.015 timetable (from D2.035) to get in.
# The puzzle is calibrating a rover: first the bench voltage, then the IR frequency.
# Solving it gives the High-Capacity Battery Pack and shows the final code digits.

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

# The right answers of the two stages.
CORRECT_VOLTAGE = 10     # 12 - 2 * 4 + 6
CORRECT_FREQUENCY = 30   # (40 + 20) / 2

# The final digits of the story code, shown by the rover at the end.
FINAL_DIGITS = "7 3"

# The item that opens the door.
DOOR_ITEM = "D2.015 timetable"

room_loot: list[str] = []
valid_destinations = ["teachingarea"]
room_dialogue_bank = story_dialogue_bank["rooms"]["classroomd2015"]
seating_done = False

def enter_classroom_d2015(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    state["previous_room"] = "classroomd2015"

    state["d2015_progress"] = {
        "power_set": False,
        "rover_calibrated": False,
    }
    
    clear_screen()
    state["visited"]["classroomd2015"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])
    print_dialogue(room_dialogue_bank["enter_bins"])

    def handle_look(state):
        """Describe the room and what the player can do here."""
        loot = room_loot
        print("You take a look around.")
        print_dialogue(look_around_dialogue_bank["classroomd2015"])
        if len(loot) > 0:
            print("In the rover hatch:", ", ".join(loot))
        print(f"- Possible exits: {', '.join(valid_destinations)}")
        print()
        print_current_objective(state)

    def handle_help():
        """Print the list of commands."""
        print("Available commands:")
        print("- look around         : Describe the room.")
        print("- inspect <object>    : Look closer (try the track).")
        print("- take <item>         : Pick up an item.")
        print("- go [room]           : Leave the room.")
        print("- status / save       : Show your status / open the save menu.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def play_rover(state):
        """Two stages. Returns True when the rover is fully calibrated."""
        progress = state["d2015_progress"]

        # Stage 1: the voltage on the bench power supply.
        if not progress["power_set"]:
            print("Notebook clue: 12 - 2 * 4 + 6")
            answer = input("Target voltage in volts > ").strip()
            if answer != str(CORRECT_VOLTAGE):
                print("BZZT! The bench breaker trips. Multiplication comes before subtraction.")
                return False
            progress["power_set"] = True
            print("The supply settles on", CORRECT_VOLTAGE, "V and the track rails hum.")

        # Stage 2: the infrared carrier frequency.
        if not progress["rover_calibrated"]:
            print("Chassis sticker: (40 + 20) / 2 kHz")
            answer = input("Carrier frequency in kHz > ").strip()
            if answer != str(CORRECT_FREQUENCY):
                print("BEEP! Rejected. Brackets first, then divide.")
                return False
            progress["rover_calibrated"] = True
            print("The rover locks onto", CORRECT_FREQUENCY, "kHz and its LED turns green.")

        print_dialogue(room_dialogue_bank["rover_complete"])
        print_dialogue(room_dialogue_bank["rover_digits"], print_newline_after=False)
        print(FINAL_DIGITS)
        return True


    def inspect_object(state, name):
        """Look closer at one object in the room."""
        if name == "bins":
            print("Old circuit boards and wiring. Nothing useful, but a heavy battery pack sits in the rover hatch.")
        elif name == "workbench":
            print("A lab notebook is open at 'BENCH SUPPLY CALCULATION':")
            print('    "Set line voltage to:  12 - 2 * 4 + 6"')
        elif name == "rover":
            print("A sticker on the rover chassis reads:")
            print('    "IR CARRIER FREQUENCY:  (40 + 20) / 2 kHz"')
        elif name == "track":
            if state["completed"]["classroomd2015"]:
                print("You have already completed this room. There is nothing else to do here.")
            elif play_rover(state):
                state["completed"]["classroomd2015"] = True
                room_loot.append("Memory Sticks")
                print_dialogue(room_dialogue_bank["memory_pickup"])
            else:
                print("No worries, inspect the track again whenever you like to retry.")
        else:
            print("There is no '" + name + "' here.")


    def take_item(state, item_name):
        """Move an item from the podium drawer into the inventory."""
        loot = room_loot
        item_name = item_name.lower().strip()
        for thing in loot:
            if item_name != "" and item_name in thing.lower():
                loot.remove(thing)
                print("You took the " + thing + ".")
                state["inventory"].append(thing)
                if item_name == "memory sticks":
                    state["current_objective_id"] += 1
                    print_dialogue(room_dialogue_bank["memory_story"])
                    print_dialogue(room_dialogue_bank["memory_story_car"])
                    print_dialogue(room_dialogue_bank["memory_story_objective"])
                    print_dialogue(room_dialogue_bank["memory_story_advance"])
                    print_assembly_part_obtained("(+ Memory Sticks)")
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

        elif command in ["g", "go", "goto", "move"] or command.startswith("go "):
            result = display_selection_menu("Choose room to go to:", valid_destinations)
            if result:
                return result

        elif command == "map":
            display_map(state)

        elif command in ["inv", "inventory"]:
            clear_screen()
            display_inventory(state["inventory"])

        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)

        elif command == "pause" or command == "save":
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()
        
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
