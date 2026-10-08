# -----------------------------------------------------------------------------
# File: classroom_d2035.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
# Classroom D2.035. The player needs the Student ID card to get in.
# Inside there are two puzzles at the podium:
#   part 1: put four students in the right seats  -> the player gets the Seating plan
#   part 2: find the next number in a sequence   -> the player gets the Mainboard and the D2.015 timetable

import sys
import time

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# The name of this room in the game state (the dispatcher uses the same name).
ROOM_KEY = "classroomd2035"

# The item that opens the door.
DOOR_ITEM = "Student ID card"

# Right order of the students: seat 1 (window) to seat 4 (aisle).
SEATING_ANSWER = ["ana", "chloe", "dev", "ben"]

# The timetable sequence. The gaps are 4, 6, 8, 10 so the next gap is 12 and 30 + 12 = 42.
SEQUENCE = [2, 6, 12, 20, 30]
SEQUENCE_ANSWER = 42


def prepare_state(state):
    """Make sure the game state has every place this room needs."""
    if ROOM_KEY not in state["completed"]:
        state["completed"][ROOM_KEY] = False
    if "room_loot" not in state:
        state["room_loot"] = {}
    if ROOM_KEY not in state["room_loot"]:
        state["room_loot"][ROOM_KEY] = []
    if "room_unlocked" not in state:
        state["room_unlocked"] = {}
    if ROOM_KEY not in state["room_unlocked"]:
        state["room_unlocked"][ROOM_KEY] = False
    if "d2035_progress" not in state:
        # Part 1 stays solved once it is done, so the player never has to repeat it.
        state["d2035_progress"] = {"seating": False}


def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the podium).")
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
        print("The door is shut. Lecture halls only open for students with a valid ID.")
    else:
        print("Things you can inspect: desks, lecturer, podium")
        if len(loot) > 0:
            print("In the podium drawer:", ", ".join(loot))
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])


def show_seating_clues():
    """Print the lecturer's note with the seating clues."""
    print("A lecturer's note lists four students and four seats (1 = window, 4 = aisle):")
    print("  - Ana sits by the window.")
    print("  - Ben sits at the aisle, in the last seat.")
    print("  - Chloe sits right next to Ana.")
    print("  - Dev sits between Chloe and Ben.")


def play_seating(state):
    """Part 1: the player has 3 tries to type the students in the right order."""
    print("PART 1: SEATING PLAN")
    show_seating_clues()
    for _ in range(3):
        guess = input("Seats 1-4, names separated by spaces (e.g. ana ben chloe dev) > ").lower().split()
        if guess == SEATING_ANSWER:
            state["d2035_progress"]["seating"] = True
            state["inventory"].append("Seating plan")
            print("Everyone is in the right seat. The lecturer hands you the Seating plan.")
            print("\"Classroom D2.031 keeps a coded message about it. Take this plan there.\"")
            return True
        print("The students shuffle around and nobody is happy. Check each clue against the seat numbers.")
    return False


def play_sequence():
    """Part 2: the player has 3 tries to find the next number."""
    print("PART 2: TIMETABLE SEQUENCE")
    print("Timetable slip:", SEQUENCE, "and then ?")
    print("Each number follows a rule. Work out the pattern between neighbours (2 to 6 is +4, ...).")
    for _ in range(3):
        answer = input("Next number > ").strip()
        if answer == str(SEQUENCE_ANSWER):
            print("Correct! The podium drawer slides open.")
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
    loot = state["room_loot"][ROOM_KEY]
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is shut. Try 'use <item> on door'.")
    elif name == "desks":
        show_seating_clues()
    elif name == "lecturer":
        print("Lecturer: \"My students never sit where they should. Arrange them, and I will hand over the plan.\"")
        print("\"After that, finish the timetable sequence on the podium. The D2.015 lab opens with it.\"")
    elif name == "podium":
        if state["completed"][ROOM_KEY]:
            print("You have already completed this room. There is nothing else to do here.")
        elif play_podium(state):
            state["completed"][ROOM_KEY] = True
            loot.append("Microcontroller / Mainboard")
            loot.append("D2.015 timetable")
            print("The drawer holds a Microcontroller / Mainboard and the D2.015 timetable.")
            print("Use 'take mainboard' and 'take timetable' to pick them up.")
        else:
            print("No worries, inspect the podium again whenever you like to retry.")
    else:
        print("There is no '" + name + "' here.")


def take_item(state, item_name):
    """Move an item from the podium drawer into the inventory."""
    loot = state["room_loot"][ROOM_KEY]
    for thing in loot:
        if item_name != "" and item_name in thing.lower():
            loot.remove(thing)
            state["inventory"].append(thing)
            print("You took the " + thing + ".")
            return  # stop right after removing, so the list is not changed while the loop runs
    print("There is no '" + item_name + "' here to take.")


def use_item(state, item_name, target):
    """Use an item from the inventory. Only the Student ID card on the door does something."""
    owned = None
    for thing in state["inventory"]:
        if thing.lower() == item_name:
            owned = thing
    if owned is None:
        print("You don't have '" + item_name + "'.")
    elif target == "door" and not state["room_unlocked"][ROOM_KEY] and owned == DOOR_ITEM:
        state["room_unlocked"][ROOM_KEY] = True
        print("Beep! ID accepted, you slip inside.")
    else:
        print("Nothing happens.")


def enter_classroom_d2035(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    prepare_state(state)

    # Already finished and nothing left to pick up? Then skip the room.
    if state["completed"][ROOM_KEY] and len(state["room_loot"][ROOM_KEY]) == 0:
        clear_screen()
        print("You have already completed this room. There is nothing else to do here.")
        time.sleep(2)
        return "lobby"

    clear_screen()
    print("You stand in front of Classroom D2.035, a lecture hall with tiered seating.")
    if not state["room_unlocked"][ROOM_KEY]:
        print("A card reader beside the door blinks red. Lecture halls only open for students with a valid ID.")
        print("(Try: use <item> on door)")
    else:
        print("A lecturer is frowning at a messy seating chart. A podium stands at the front with a number lock.")

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
                print("You leave the lecture hall and step back into the lobby.")
                return "lobby"
            print("You can't go to '" + destination + "' from here.")
        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)
        elif command == "pause" or command == "save":
            display_save_menu(state)
        elif command == "quit":
            clear_screen()
            print("You leave the lecture hall and exit the maze.")
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
