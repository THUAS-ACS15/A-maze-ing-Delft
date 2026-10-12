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

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

# Caesar cipher: every letter of the secret word was moved forward by SHIFT places.
SHIFT = 3
SECRET_WORD = "sesame"

room_loot: list[str] = []
valid_destinations = ["teachingarea"]
room_dialogue_bank = story_dialogue_bank["rooms"]["classroomd2031"]

def enter_classroom_d2031(state):
    """Called by the dispatcher. Runs the room until the player leaves."""

    state["previous_room"] = "classroomd2031"

    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    def handle_look(state):
        """Describe the room and what the player can do here."""
        loot = room_loot
        print("You take a look around.")
        print_dialogue(look_around_dialogue_bank["classroomd2031"])
        if len(loot) > 0:
            print("In the key box:", ", ".join(loot))
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """Print the list of commands."""
        print("Available commands:")
        print("- look around         : Describe the room.")
        print("- inspect <object>    : Look closer (try the keybox).")
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
        print_dialogue(room_dialogue_bank["board_intro"])
        print('    "KEY BOX PASSWORD (ENCRYPTED):  ' + encrypt(SECRET_WORD) + '"')
        print_dialogue(room_dialogue_bank["board_cipher"])
        print_dialogue(room_dialogue_bank["board_monitor"])

    def show_monitors():
        """One monitor still works and shows a table that helps with decrypting."""
        print_dialogue(room_dialogue_bank["monitor_intro"])
        print("    ENCRYPTED:  A B C D E F G H I J K L M N O P Q R S T U V W X Y Z")
        print("    DECRYPTED:  X Y Z A B C D E F G H I J K L M N O P Q R S T U V W")
        print_dialogue(room_dialogue_bank["monitor_example"])

    def play_cipher():
        """The player has 3 tries to type the decrypted word. Returns True when it is right."""
        print_dialogue(room_dialogue_bank["cipher_intro"])
        print_dialogue(room_dialogue_bank["cipher_read"])
        for attempt in range(3):
            guess = input("Decrypted password > ").strip().lower()
            if guess == SECRET_WORD:
                print_dialogue(room_dialogue_bank["cipher_open"])
                print_dialogue(room_dialogue_bank["cipher_key"])
                return True
            print("Nothing happens. Shift every letter BACK by 3 to decrypt it.")
            if attempt == 1:
                print("Hint: D becomes A, so " + encrypt(SECRET_WORD)[0] + " becomes " + SECRET_WORD[0].upper() + ".")
        return False

    def inspect_object(state, name):
        """Look closer at one object in the room."""
        if name == "board":
            show_board()
        elif name == "monitors":
            show_monitors()
        elif name == "keybox":
            if state["completed"]["classroomd2031"]:
                print("You have already completed this room. There is nothing else to do here.")
            elif play_cipher():
                state["completed"]["classroomd2031"] = True
                room_loot.append("Classroom 2.021 key")
                print_dialogue(room_dialogue_bank["key_pickup"])
            else:
                print("No worries, inspect the keybox again whenever you like to retry.")
        else:
            print("There is no '" + name + "' here.")

    def take_item(state, item_name):
        """Move an item from the room into the inventory."""
        loot = room_loot
        for thing in loot:
            if item_name != "" and item_name in thing.lower():
                loot.remove(thing)
                state["inventory"].append(thing)
                print("You took the " + thing + ".")
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
