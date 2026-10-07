# -----------------------------------------------------------------------------
# File: lobby.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

def enter_lobby(state):
    """Starter function for the Lobby room."""
    clear_screen()
    print("🚶 You are standing in the school's main lobby.")
    print(
        "You see a long corridor with many doors and glass walls on both sides. There are lots of doors waiting to be "
        "explored."
    )
    if not state["student_id_obtained"]:
        print(
            "You notice you're missing your student ID. You should check out the Front Desk to see if you can obtain "
            "a new one."
        )

    available_rooms = [
        "classroomd2035",
        "teachersroom1"
    ]

    def handle_look():
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player which
        rooms they can go to.

        Inputs: NONE

        Outputs: NONE
        """
        clear_screen()
        print("You take a look around.")
        print("Students and teachers are walking in both directions along the corridor. You see several labeled doors:")
        print(f"- Possible doors: {', '.join(available_rooms)}")
        print(f"- Your inventory: {state['inventory']}")

    def handle_help():
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """
        clear_screen()
        print("Available commands:")
        print("- look around         : See what's in the corridor and where you can go.")
        print("- go <room name>      : Move to another room. Examples: 'go frontdesk', 'go projectroom1'")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

    def handle_go(room_name):
        """
        Handles movement out of the room.

        Checks if destination is valid directly or through aliases,
        then returns the standardized room string for main.py.
        """
        clear_screen()

        if room_name in available_rooms:
            state["previous_room"] = "lobby"
            return room_name
        else:
            print(f"❌ '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command in ["?", "help"]:
            handle_help()

        elif command.startswith("go "):
            room = command[3:].strip()
            result = handle_go(room)
            if result:
                return result

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print("👋 You leave the school and the adventure comes to an end. Game over.")
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
