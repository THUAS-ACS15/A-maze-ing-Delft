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

# The name of this room in the game state (the dispatcher uses the same name).
ROOM_KEY = "frontdesk"

# The map of the school floor, shown when the player inspects the map.
FLOOR_MAP = """
+--------------------------- NORTH (Julianalaan) ----------------------------+
|            |            |       | Front Desk | Classroom | Classroom |     |
|  LAB 2.001 |  LAB 2.003 |       |   Office   |   2.015   |   2.021   | T4  |
|            |            |       +------------+-----------+-----------+-----|
|            |            | Lobby        === E-W corridor ===          |     |
|------------+------------+       +------------------------------------+-----|
|                         |       | Teachers | T2 | Equinox | Proj | N-S |   |
|                         |--|--| |  Room 1  |    | Society | Rm 3 | cor.|2.035|
|                         |P1|P2| +-----------------------------------+-----|
|                         |--|--|            Exit Passage                    |
+-- EAST (Rotterdamseweg) ------- SOUTH (Main Stairs) ---- WEST (Leeghwater) -+
"""


def prepare_state(state):
    """Make sure the game state has every place this room needs."""
    if ROOM_KEY not in state["completed"]:
        state["completed"][ROOM_KEY] = False
    if "room_loot" not in state:
        state["room_loot"] = {}
    if ROOM_KEY not in state["room_loot"]:
        state["room_loot"][ROOM_KEY] = []


def show_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the printer).")
    print("- take <item>         : Pick up an item.")
    print("- go lobby / back     : Leave the room.")
    print("- status / save       : Show your status / open the save menu.")
    print("- ?                   : Show this help message.")
    print("- quit                : Quit the game entirely.")


def look_around(state):
    """Describe the room and what the player can do here."""
    loot = state["room_loot"][ROOM_KEY]
    print("You take a look around.")
    print("Things you can inspect: counter, printer, logbook, map")
    if len(loot) > 0:
        print("In the printer tray:", ", ".join(loot))
    if state["completed"][ROOM_KEY]:
        print("You already have your Student ID card.")
    print("- Possible exits: lobby")
    print("- Your current inventory:", state["inventory"])


def register(state):
    """The small quest: type a name and an 8 digit student number to print the ID card."""
    print("The staff member looks up over his glasses. \"Why are you walking around without your ID card?\"")
    print("\"Sit down, I'll print you a new one.\" (type 'cancel' to walk away)")

    name = input("\"What's your name?\" > ").strip()
    if name.lower() == "cancel":
        print("\"Fine, fine. Come back when you've got a minute.\"")
        return
    if name == "":
        name = "Student"
    state["player_name"] = name

    # Keep asking until the student number is exactly 8 digits.
    while True:
        number = input("\"And your 8-digit student number?\" > ").strip()
        if number.lower() == "cancel":
            print("\"Suit yourself. The card will be waiting here.\"")
            return
        if len(number) != 8:
            print("\"That's", len(number), "characters. A student number is exactly 8 digits long.\"")
        elif not number.isnumeric():
            print("\"Digits only, please. No letters in a student number.\"")
        else:
            break

    # The quest is done: remember it and put the card in the printer tray.
    state["student_id_obtained"] = True
    state["completed"][ROOM_KEY] = True
    state["room_loot"][ROOM_KEY].append("Student ID card")
    print("The printer whirs. \"There you go,", state["player_name"] + ". Don't lose this one.\"")
    print("He taps the lobby terminal: 'PROJECT A.I.G.I.S. ASSEMBLY REQUIRED'. \"The professor left it unfinished.")
    print("Collect every part on this floor and assemble it in Lab D2.001.")
    print("Doors are locked after hours, so every room needs something.\"")
    print("\"Your ID opens the Student Society, by the way. Good luck.\"")
    print("Your new Student ID card is waiting in the printer tray. Use 'take student id card' to pick it up.")


def inspect_object(state, name):
    """Look closer at one object in the room."""
    if name == "printer":
        if state["completed"][ROOM_KEY]:
            print("You have already completed this room. There is nothing else to do here.")
        else:
            register(state)
    elif name == "counter":
        print("A sign: 'Lost your ID? Register here.' Inspect the printer to get a new Student ID card.")
    elif name == "logbook":
        print("Night guard's logbook: 'The professor left PROJECT A.I.G.I.S. unfinished.")
        print("Doors lock themselves after hours.'")
        print("'Every room wants something from another room. Talk to people, read the boards, trust no lock.'")
    elif name == "map":
        print(FLOOR_MAP)
    else:
        print("There is no '" + name + "' here.")


def take_item(state, item_name):
    """Move an item from the printer tray into the inventory."""
    loot = state["room_loot"][ROOM_KEY]
    for thing in loot:
        if item_name != "" and item_name in thing.lower():
            loot.remove(thing)
            state["inventory"].append(thing)
            print("You took the " + thing + ".")
            return  # stop right after removing, so the list is not changed while the loop runs
    print("There is no '" + item_name + "' here to take.")


def enter_front_desk(state):
    """Called by the dispatcher. Runs the room until the player leaves."""
    prepare_state(state)

    clear_screen()
    print("You walk up to the Front Desk Office.")
    print("A staff member is hunched over a laptop behind a wide reception counter.")
    print("A campus map is pinned to the wall and an old logbook lies open.")

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
                print("You nod at the staff member and step back into the lobby.")
                return "lobby"
            print("You can't go to '" + destination + "' from here.")
        elif command == "status" or command == "check status":
            clear_screen()
            check_status(state, pause=True)
        elif command == "pause" or command == "save":
            display_save_menu(state)
        elif command == "quit":
            clear_screen()
            print("You leave the Front Desk and exit the maze.")
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
