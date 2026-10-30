# -----------------------------------------------------------------------------
# File: front_desk.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Front desk: register the player and issue the student ID card."""

# The Front Desk. The player registers here and gets a Student ID card.
# This room can be entered at any time. Only the printer remembers that the ID was already printed.

import sys

from data.look_around_dialogue_bank import look_around_dialogue_bank
from data.story_dialogue_bank import story_dialogue_bank
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.display_menu import display_selection_menu
from utilities.game_map import display_map
from utilities.inventory_viewer import display_inventory
from utilities.print_helpers import print_current_objective, print_dialogue
from utilities.save_gui import display_save_menu

room_dialogue_bank = story_dialogue_bank["rooms"]["frontdesk"]
valid_destinations = ["lobby"]

def handle_help():
    """Print the list of commands."""
    print("Available commands:")
    print("- look around         : Describe the room.")
    print("- inspect <object>    : Look closer (try the printer).")
    print("- take <item>         : Pick up an item.")
    print("- go [room]           : Leave the room.")
    print("- inventory           : Show what items are in your inventory.")
    print("- status / save       : Show your status / open the save menu.")
    print("- ?                   : Show this help message.")
    print("- quit                : Quit the game entirely.")


def handle_look(state):
    """Describe the room and what the player can do here."""
    print_dialogue(look_around_dialogue_bank["frontdesk"])
    print("Things you can inspect: counter, printer, logbook")
    if state["completed"]["frontdesk"]:
        print("You already have your Student ID card.")
    print(f"- Possible exits: {', '.join(valid_destinations)}")
    print()
    print_current_objective(state)

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
    state["inventory"].append("Student ID card")
    print_dialogue(room_dialogue_bank["register_complete"], print_newline_after = False)
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

def enter_front_desk(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    state["previous_room"] = "frontdesk"

    clear_screen()
    state["visited"]["frontdesk"] = True
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    # The main loop: read a command, do what it says, repeat.
    while True:
        command = input("\n> ").lower().strip()

        if command in ["look around", "lk", "look", "l", "la"]:
            clear_screen()
            handle_look(state)

        elif command in ["?", "help"]:
            clear_screen()
            handle_help()

        elif command in ["inspect", "insp", "check"] or command.startswith ("inspect"):
            clear_screen()
            inspect_object(state, command[8:].strip())

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
            check_status(state, pause = True)

        elif command == "pause" or command == "save":
            display_save_menu(state)

        elif command in ["quit", "exit"]:
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()
        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
