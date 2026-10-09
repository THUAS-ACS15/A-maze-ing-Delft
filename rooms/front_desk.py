# -----------------------------------------------------------------------------
# File: front_desk.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
# The Front Desk. The player registers here and gets a Student ID card.
# This room can be entered at any time. Only the printer remembers that the ID was already printed.

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_current_objective

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

room_loot: dict[str, str] = {}
room_dialogue_bank = story_dialogue_bank["rooms"]["frontdesk"]
valid_destinations = ["lobby"]

def handle_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the printer).")
    print("- take <item>         : Pick up an item.")
    print("- go [room]           : Leave the room.")
    print("- status / save       : Show your status / open the save menu.")
    print("- ?                   : Show this help message.")
    print("- quit                : Quit the game entirely.")


def handle_look(state):
    """Describe the room and what the player can do here."""
    loot = room_loot
    print_dialogue(look_around_dialogue_bank["frontdesk"])
    print("Things you can inspect: counter, printer, logbook, map")
    if len(loot) > 0:
        print("In the printer tray:", ", ".join(loot))
    if state["completed"]["frontdesk"]:
        print("You already have your Student ID card.")
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])

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
        return ""

def register(state):
    """The small quest: type a name and an 8 digit student number to print the ID card."""
    print_dialogue(room_dialogue_bank["register_intro"])
    print_dialogue(room_dialogue_bank["register_prompt"])

    name = input("\"What's your name?\" > ").strip()
    state["player_name"] = name
    if name.lower() == "cancel":
        print_dialogue(room_dialogue_bank["register_cancel_name"])
        return
    if name == "":
        name = "Student"
    state["player_name"] = name

    # Keep asking until the student number is exactly 8 digits.
    while True:
        number = input("\"And your 8-digit student number?\" > ").strip()
        if number.lower() == "cancel":
            print_dialogue(room_dialogue_bank["register_cancel_number"])
            return
        if len(number) != 8:
            print("\"That's", len(number), "characters. A student number is exactly 8 digits long.\"")
        elif not number.isnumeric():
            print("\"Digits only, please. No letters in a student number.\"")
        else:
            break

    # The quest is done: remember it and put the card in the printer tray.
    state["student_id_obtained"] = True
    state["current_objective_id"] += 1
    state["completed"]["frontdesk"] = True
    room_loot.append("Student ID card")
    print_dialogue(room_dialogue_bank["register_complete"], print_newline_after=False)
    print_dialogue(state["player_name"] + ". " + room_dialogue_bank["register_story"])
    print_dialogue(room_dialogue_bank["register_terminal"])
    print_dialogue(room_dialogue_bank["register_collect"])
    print_dialogue(room_dialogue_bank["register_doors"])
    print_dialogue(room_dialogue_bank["register_society"])
    print_dialogue(room_dialogue_bank["register_pickup"])

    print_current_objective(state)

def inspect_object(state, name):
    """Look closer at one object in the room."""
    if name == "printer":
        if state["completed"]["frontdesk"]:
            print_dialogue(room_dialogue_bank["inspect_completed"])
        else:
            register(state)
    elif name == "counter":
        print_dialogue(room_dialogue_bank["counter_sign"])
    elif name == "logbook":
        print_dialogue(room_dialogue_bank["logbook_first"])
        print_dialogue(room_dialogue_bank["logbook_second"])
        print_dialogue(room_dialogue_bank["logbook_third"])
    else:
        print("There is no '" + name + "' here.")

def take_item(state, item_name):
    """Move an item from the printer tray into the inventory."""
    loot = room_loot
    for thing in loot:
        if item_name != "" and item_name in thing.lower():
            loot.remove(thing)
            state["inventory"].append(thing)
            print("You took the " + thing + ".")
            return  # stop right after removing, so the list is not changed while the loop runs
    print("There is no '" + item_name + "' here to take.")

def enter_front_desk(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    clear_screen()
    print_dialogue(room_dialogue_bank["legacy_header"])
    print_dialogue(room_dialogue_bank["legacy_enter"])
    print_dialogue(room_dialogue_bank["legacy_enter_map"])

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
            clear_screen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)
        elif command == "pause" or command == "save":
            display_save_menu(state)
        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit_game"])
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
