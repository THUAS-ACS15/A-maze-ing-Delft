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
import time

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# The name of this room in the game state (the dispatcher uses the same name).
ROOM_KEY = "projectroom1"

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

# The items that open the door.
ENTRY_ITEMS = ["Classroom 2.021 key", "Level-1 Staff Keycard", "Level 1 Staff Keycard", "Teacher Access Keycard"]


def prepare_state(state):
    """Make sure the game state has every place this room needs."""
    if ROOM_KEY not in state["completed"]:
        state["completed"][ROOM_KEY] = False
    if "room_loot" not in state:
        state["room_loot"] = {}
    if ROOM_KEY not in state["room_loot"]:
        state["room_loot"][ROOM_KEY] = ["brass key"]
    if "room_unlocked" not in state:
        state["room_unlocked"] = {}
    if ROOM_KEY not in state["room_unlocked"]:
        state["room_unlocked"][ROOM_KEY] = False
    if "projectroom1_progress" not in state:
        # The list of lockers that are already open.
        state["projectroom1_progress"] = {"opened": []}


def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the lockers).")
    print("- take <item>         : Pick up an item.")
    print("- use <item> on door  : Unlock the door with an item.")
    print("- go lobby / back     : Leave the room.")
    print("- status / save       : Show your status / open the save menu.")
    print("- ?                   : Show this help message.")
    print("- quit                : Quit the game entirely.")


def look_around(state):
    """Describe the room and what the player can do here."""
    loot = state["room_loot"][ROOM_KEY]
    print("You take a look around.")
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is shut.")
    else:
        print("Things you can inspect: whiteboard, desks, pile, vance, lockers")
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
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is shut. Try 'use <item> on door'.")
    elif name == "whiteboard":
        print("You step up to the whiteboard. Vance's handwriting is terrible.")
        print('    "LOCKER 1:  2 + 6 * 30"')
        print('    "LOCKER 3:  (2 + 6) * 3"')
        print("Vance has added a reminder: BODMAS. Brackets first, then multiply/divide, then add/subtract.")
        print("(Two more codes are written somewhere else in the room.)")
    elif name == "desks":
        print("Between the rows of wooden desks, something is carved into desk #3:")
        print('    "LOCKER 4:  50 - 5 * 4"')
    elif name == "pile":
        print("A pile of broken desks and chairs. A sticker peels off a snapped chair:")
        print('    "LOCKER 5:  2 ** 4 + 3 * 10"')
        print("Something shiny is half buried in the pile (try 'look' and 'take').")
    elif name == "vance":
        print("Vance: \"Five lockers, five combinations, every number is somewhere in this room.")
        print("The USB cable and the keycard for the old Linux room are in there. Earn them.\"")
    elif name == "lockers":
        if play_lockers(state):
            state["completed"][ROOM_KEY] = True
        else:
            print("No worries, inspect the lockers again whenever you like to continue.")
    else:
        print("There is no '" + name + "' here.")


def take_item(state, item_name):
    """Move an item from the room into the inventory."""
    loot = state["room_loot"][ROOM_KEY]
    for thing in loot:
        if item_name != "" and item_name in thing.lower():
            loot.remove(thing)
            state["inventory"].append(thing)
            print("You took the " + thing + ".")
            return  # stop right after removing, so the list is not changed while the loop runs
    print("There is no '" + item_name + "' here to take.")


def use_item(state, item_name, target):
    """Use an item from the inventory. Only a key item on the door does something."""
    owned = None
    for thing in state["inventory"]:
        if thing.lower() == item_name:
            owned = thing
    if owned is None:
        print("You don't have '" + item_name + "'.")
    elif target == "door" and not state["room_unlocked"][ROOM_KEY] and owned in ENTRY_ITEMS:
        state["room_unlocked"][ROOM_KEY] = True
        print("Beep! The door clicks open.")
    else:
        print("Nothing happens.")


def enter_project_room1(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    prepare_state(state)

    # Already finished? Then skip the room and say so.
    if state["completed"][ROOM_KEY]:
        clear_screen()
        print("You have already completed this room. There is nothing else to do here.")
        time.sleep(2)
        return "lobby"

    clear_screen()
    print("You stand in front of Project Room 1.")
    if not state["room_unlocked"][ROOM_KEY]:
        print("INVITATION ONLY. You need a key or staff keycard. (Try: use <item> on door)")
    else:
        print("A project room. Professor Vance stands at the front, capping a whiteboard marker.")
        print("Five lockers line the back wall.")

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
        elif command.startswith("use ") and " on " in command:
            clear_screen()
            parts = command[4:].split(" on ")
            use_item(state, parts[0].strip(), parts[1].strip())
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
            print("You leave Project Room 1 and exit the maze.")
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
