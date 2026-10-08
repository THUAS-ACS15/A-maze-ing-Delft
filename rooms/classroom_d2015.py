# -----------------------------------------------------------------------------
# File: classroom_d2015.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
# Classroom D2.015. The player needs the D2.015 timetable (from D2.035) to get in.
# The puzzle is calibrating a rover: first the bench voltage, then the IR frequency.
# Solving it gives the High-Capacity Battery Pack and shows the final code digits.

import sys
import time

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# The name of this room in the game state (the dispatcher uses the same name).
ROOM_KEY = "classroomd2015"

# The right answers of the two stages.
CORRECT_VOLTAGE = 10     # 12 - 2 * 4 + 6
CORRECT_FREQUENCY = 30   # (40 + 20) / 2

# The final digits of the story code, shown by the rover at the end.
FINAL_DIGITS = "7 3"

# The item that opens the door.
DOOR_ITEM = "D2.015 timetable"


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
    if "d2015_progress" not in state:
        # Remember which stages are done, so the player does not have to repeat them.
        state["d2015_progress"] = {"power_set": False, "rover_calibrated": False}


def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the track).")
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
        print("Things you can inspect: bins, workbench, rover, track")
        if len(loot) > 0:
            print("In the rover hatch:", ", ".join(loot))
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])


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

    print("The rover races down the track and stops on the target pad. A hatch pops open.")
    print("The rover's log screen shows the FINAL CODE DIGITS:", FINAL_DIGITS)
    return True


def inspect_object(state, name):
    """Look closer at one object in the room."""
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is shut. Try 'use <item> on door'.")
    elif name == "bins":
        print("Old circuit boards and wiring. Nothing useful, but a heavy battery pack sits in the rover hatch.")
    elif name == "workbench":
        print("A lab notebook is open at 'BENCH SUPPLY CALCULATION':")
        print('    "Set line voltage to:  12 - 2 * 4 + 6"')
    elif name == "rover":
        print("A sticker on the rover chassis reads:")
        print('    "IR CARRIER FREQUENCY:  (40 + 20) / 2 kHz"')
    elif name == "track":
        if state["completed"][ROOM_KEY]:
            print("You have already completed this room. There is nothing else to do here.")
        elif play_rover(state):
            state["completed"][ROOM_KEY] = True
            state["room_loot"][ROOM_KEY].append("High-Capacity Battery Pack")
            print("The hatch holds the High-Capacity Battery Pack. Use 'take battery pack' to pick it up.")
        else:
            print("No worries, inspect the track again whenever you like to retry.")
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
    elif target == "door" and not state["room_unlocked"][ROOM_KEY] and owned == DOOR_ITEM:
        state["room_unlocked"][ROOM_KEY] = True
        print("Beep! The timetable matches. The door opens.")
    else:
        print("Nothing happens.")


def enter_classroom_d2015(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    prepare_state(state)

    # Already finished and nothing left to pick up? Then skip the room and say so.
    if state["completed"][ROOM_KEY] and len(state["room_loot"][ROOM_KEY]) == 0:
        clear_screen()
        print("You have already completed this room. There is nothing else to do here.")
        time.sleep(2)
        return "lobby"

    clear_screen()
    print("You stand in front of Classroom D2.015, the embedded systems lab.")
    if not state["room_unlocked"][ROOM_KEY]:
        print("The lab is closed outside timetabled hours. You need the D2.015 timetable. (Try: use <item> on door)")
    else:
        print("A marked test track fills the floor and a dead robot rover sits in the middle.")
        print("Leftover student project bins line the wall and a workbench hums with test equipment.")

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
                print("You leave the lab and step back into the lobby.")
                return "lobby"
            print("You can't go to '" + destination + "' from here.")
        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)
        elif command == "pause" or command == "save":
            display_save_menu(state)
        elif command == "quit":
            clear_screen()
            print("You leave the lab and exit the maze.")
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
