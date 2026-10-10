# -----------------------------------------------------------------------------
# File: project_room_1.py
# ACS Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
# Project Room 1. Professor Vance's locker room.
# The player needs the Classroom 2.021 key (from D2.031) or a staff keycard to get in.
# The puzzle: open five lockers with codes. The codes are maths sums hidden in the room (BODMAS).
# Rewards: Sensory Module, USB cable, Teachers Room 4 Keycard and some coins.

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

# The five lockers. For each locker: its code, the coins inside and the item inside.
# A code of 0 means the locker has no code. It opens with the brass key instead.
# An item of "" means there is no item in that locker, only coins.
LOCKERS = {
    "1": {"code": 182, "coins": 50, "item": "Sensory Module"},
    "2": {"code": 0, "coins": 0, "item": "USB cable"},
    "3": {"code": 24, "coins": 20, "item": "Teachers Room 4 Keycard"},
    "4": {"code": 30, "coins": 30, "item": ""},
    "5": {"code": 46, "coins": 20, "item": ""},
}

room_loot: list[str] = []
valid_destinations = ["studentwing"]
room_dialogue_bank = story_dialogue_bank["rooms"]["projectroom1"]

def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the lockers).")
    print("- take <item>         : Pick up an item.")
    print("- go lobby / back     : Leave the room.")
    print("- status / save       : Show your status / open the save menu.")
    print("- ?                   : Show this help message.")
    print("- quit                : Quit the game entirely.")

def look_around(state):
    """Describe the room and what the player can do here."""
    loot = room_loot
    print_dialogue(look_around_dialogue_bank["projectroom1"])
    if len(loot) > 0:
        print("On the floor:", ", ".join(loot))
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])

def play_lockers(state):
    """The player opens lockers one by one. Returns True when all five are open."""
    opened = state["projectroom1_progress"]["opened"]

    while len(opened) < len(LOCKERS):
        # Show which lockers are open and which are shut.
        print("\nBack wall:")
        for number in LOCKERS:
            if number in opened:
                print("  Locker " + number + ": open")
            else:
                print("  Locker " + number + ": shut")

        choice = input("Which locker (1-5)? ('back' to step away) > ").strip().lower()

        if choice == "back":
            print("Vance calls after you: \"The lockers will still be here!\"")
            return False
        if choice not in LOCKERS:
            print("There are only five lockers, numbered 1 to 5.")
            continue
        if choice in opened:
            print("That one is already open and empty.")
            continue

        locker = LOCKERS[choice]

        if locker["code"] == 0:
            # This locker has an old padlock and needs the brass key.
            if "brass key" not in state["inventory"]:
                print("Locker 2 has an old brass padlock. The key must be in the pile in the corner.")
                continue
            print("You try the brass key. Click, it turns.")
        else:
            code = input("Code for locker " + choice + " > ").strip()
            if not code.isdigit() or int(code) != locker["code"]:
                print("BZZT. The keypad resets. BODMAS: do the multiplication BEFORE adding or subtracting.")
                continue
            print("Click. Locker " + choice + " swings open.")

        # The locker is open: remember it and hand out the rewards.
        opened.append(choice)
        if locker["coins"] > 0:
            state["coin_balance"] = state["coin_balance"] + locker["coins"]
            print("Cash inside. (+" + str(locker["coins"]) + " coins)")
        if locker["item"] != "":
            state["inventory"].append(locker["item"])
            print("You find: " + locker["item"] + ". (Added to your inventory)")

    print("All five lockers are open. Vance applauds, once. \"Now get out of my room.\"")
    return True

def inspect_object(state, name):
    """Look closer at one object in the room."""
    if name == "whiteboard":
        print_dialogue(room_dialogue_bank["whiteboard_intro"])
        print('    "LOCKER 1:  2 + 6 * 30"')
        print('    "LOCKER 3:  (2 + 6) * 3"')
        print_dialogue(room_dialogue_bank["whiteboard_bodmas"])
        print_dialogue(room_dialogue_bank["whiteboard_more"])
    elif name == "desks":
        print_dialogue(room_dialogue_bank["desks_intro"])
        print('    "LOCKER 4:  50 - 5 * 4"')
    elif name == "pile":
        print_dialogue(room_dialogue_bank["pile_intro"])
        print('    "LOCKER 5:  2 ** 4 + 3 * 10"')
        print_dialogue(room_dialogue_bank["pile_hint"])
    elif name == "vance":
        print_dialogue(room_dialogue_bank["vance_first"])
        print_dialogue(room_dialogue_bank["vance_second"])
    elif name == "lockers":
        if play_lockers(state):
            state["completed"]["projectroom1"] = True
        else:
            print("No worries, inspect the lockers again whenever you like to continue.")
    else:
        print("There is no '" + name + "' here.")

def handle_go(destination: str) -> str:
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

def take_item(state, item_name):
    """Move an item from the room into the inventory."""
    loot = room_loot["projectroom1"]
    for thing in loot:
        if item_name != "" and item_name in thing.lower():
            loot.remove(thing)
            state["inventory"].append(thing)
            print("You took the " + thing + ".")
            return  # stop right after removing, so the list is not changed while the loop runs
    print("There is no '" + item_name + "' here to take.")

def enter_project_room1(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    clear_screen()
    print_dialogue(room_dialogue_bank["enter"])
    print_dialogue(room_dialogue_bank["lockers"])

    # The main loop: read a command, do what it says, repeat.
    while True:
        command = input("\n> ").lower().strip()

        if command == "look around" or command == "look" or command == "ls":
            clear_screen()
            look_around(state)
        elif command == "?":
            clear_screen()
            show_help()
        elif command.startswith("inspect "):
            clear_screen()
            inspect_object(state, command[8:].strip())
        elif command.startswith("take "):
            clear_screen()
            take_item(state, command[5:].strip())
        elif command.startswith("go "):
            clear_screen()
            destination = command[3:].strip()
            if destination == "lobby" or destination == "back":
                print("You leave Vance to his lockers and step back into the lobby.")
                return "lobby"
            print("You can't go to '" + destination + "' from here.")
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
