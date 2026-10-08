# -----------------------------------------------------------------------------
# File: classroom_d2031.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
# Classroom D2.031. The player needs the Seating plan (from D2.035) to get in.
# The puzzle is a secret message on the board that must be decrypted (a Caesar cipher).
# Solving it opens the key box and gives the Classroom 2.021 key.

import sys
import time

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# The name of this room in the game state (the dispatcher uses the same name).
ROOM_KEY = "classroomd2031"

# Caesar cipher: every letter of the secret word was moved forward by SHIFT places.
SHIFT = 3
SECRET_WORD = "sesame"

# The item that opens the door.
DOOR_ITEM = "Seating plan"


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


def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the keybox).")
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
        print("Things you can inspect: board, monitors, keybox")
        if len(loot) > 0:
            print("In the key box:", ", ".join(loot))
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])


def encrypt(word):
    """Turn a word into its secret form, for example sesame becomes VHVDPH."""
    result = ""
    for letter in word:
        number = ord(letter) - 97          # a = 0, b = 1, c = 2 ...
        number = (number + SHIFT) % 26     # move forward and wrap around after z
        result = result + chr(number + 65) # back to a capital letter
    return result


def show_board():
    """The board shows the ENCRYPTED word. The player has to decrypt it."""
    print("Scrawled on the board, in the professor's handwriting:")
    print('    "KEY BOX PASSWORD (ENCRYPTED):  ' + encrypt(SECRET_WORD) + '"')
    print("Under it: 'Caesar cipher. Every letter was pushed FORWARD 3 places in the alphabet.'")
    print("'I switched one monitor on for you. It shows how to decode.'")


def show_monitors():
    """One monitor still works and shows a table that helps with decrypting."""
    print("Every screen is dead except one, flickering green. It shows a decoder table:")
    print("    ENCRYPTED:  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z")
    print("    DECRYPTED:  X Y Z A B C D E F G H I J K L M N O P Q R S T U V W")
    print("Example: D on the board is really A. Look up each letter of the board message.")


def play_cipher():
    """The player has 3 tries to type the decrypted word. Returns True when it is right."""
    print("The key box wants the real password. The board only shows it in code.")
    print("Read the board and the working monitor first (inspect board, inspect monitors).")
    for attempt in range(3):
        guess = input("Decrypted password > ").strip().lower()
        if guess == SECRET_WORD:
            print("Click. The key box opens.")
            print("A tag on the key reads: 'Classroom 2.021. Also fits the Project Room 1 side door.'")
            return True
        print("Nothing happens. Shift every letter BACK by 3 to decrypt it.")
        if attempt == 1:
            print("Hint: D becomes A, so " + encrypt(SECRET_WORD)[0] + " becomes " + SECRET_WORD[0].upper() + ".")
    return False


def inspect_object(state, name):
    """Look closer at one object in the room."""
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is shut. Try 'use <item> on door'.")
    elif name == "board":
        show_board()
    elif name == "monitors":
        show_monitors()
    elif name == "keybox":
        if state["completed"][ROOM_KEY]:
            print("You have already completed this room. There is nothing else to do here.")
        elif play_cipher():
            state["completed"][ROOM_KEY] = True
            state["room_loot"][ROOM_KEY].append("Classroom 2.021 key")
            print("Inside the key box: the Classroom 2.021 key. Use 'take classroom 2.021 key' to pick it up.")
        else:
            print("No worries, inspect the keybox again whenever you like to retry.")
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
        print("Beep! The plan matches the slot. The door unlocks.")
    else:
        print("Nothing happens.")


def enter_classroom_d2031(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    prepare_state(state)

    # Already finished and nothing left to pick up? Then skip the room and say so.
    if state["completed"][ROOM_KEY] and len(state["room_loot"][ROOM_KEY]) == 0:
        clear_screen()
        print("You have already completed this room. There is nothing else to do here.")
        time.sleep(2)
        return "lobby"

    clear_screen()
    print("You stand in front of Classroom D2.031.")
    if not state["room_unlocked"][ROOM_KEY]:
        print("The door is locked. A slot on it matches a seating plan. (Try: use <item> on door)")
    else:
        print("A dim classroom full of dead monitors. A locked key box is bolted to the wall.")

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
                print("You step out of the dark classroom and back into the lobby.")
                return "lobby"
            print("You can't go to '" + destination + "' from here.")
        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)
        elif command == "pause" or command == "save":
            display_save_menu(state)
        elif command == "quit":
            clear_screen()
            print("You leave the dark classroom and exit the maze.")
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
