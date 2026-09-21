# -----------------------------------------------------------------------------
# File: lobby.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Sadanand
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clearScreen


def enterLobby(state):
    """Starter function for the Lobby room."""
    clearScreen()
    print("🚶 You are standing in the school's main lobby.")
    print("You see a long corridor with many doors and glass walls on both sides. Behind these doors are rooms, waiting to be explored.")

    # Safe check for student ID to prevent KeyError crashes
    has_id = state.get("student_id_obtained", False) or ("student id card" in state.get("inventory", []))
    if not has_id:
        print("💡 You notice you're missing your student ID. You should check out the Front Desk to see if you can obtain a new one.")

    # --- List of accessible rooms from here ---
    # Now includes Sadanand's rooms: projectroom1, frontdesk, classroomd2015
    available_rooms = [
        "labd2001",
        "store",
        "teachersroom1",
        "teachersroom2",
        "frontdesk",
        "projectroom1",
        "classroomd2015"
    ]

    # Mapping to allow players to type room names with spaces
    room_aliases = {
        "front desk": "frontdesk",
        "frontdesk": "frontdesk",
        "project room 1": "projectroom1",
        "projectroom 1": "projectroom1",
        "projectroom1": "projectroom1",
        "p1": "projectroom1",
        "classroom d2.015": "classroomd2015",
        "classroom d2015": "classroomd2015",
        "classroom2015": "classroomd2015",
        "classroomd2015": "classroomd2015",
        "d2015": "classroomd2015",
        "d2.015": "classroomd2015",
        "lab": "labd2001",
        "lab d2001": "labd2001",
        "labd2001": "labd2001",
        "store": "store",
        "teachers room 1": "teachersroom1",
        "teachersroom 1": "teachersroom1",
        "teachersroom1": "teachersroom1",
        "teachers room 2": "teachersroom2",
        "teachersroom 2": "teachersroom2",
        "teachersroom2": "teachersroom2"
    }

    # --- Command handlers ---

    def handle_look():
        """
        Describes the room and gives clues.
        
        This function describes the room and gives clues to the player which
        rooms they can go to.
        
        Inputs: NONE
        Outputs: NONE
        """
        clearScreen()
        print("You take a look around.")
        print("Students and teachers are walking in both directions along the corridor. You see several labeled doors:")
        print(f"- Possible doors: {', '.join(available_rooms)}")
        print("- Your current inventory:", state.get("inventory", []))
        print(f"- Coin balance: €{state.get('coin_balance', 0)}")

    def handle_help():
        """
        Lists available commands.
        
        This function lists the available commands for the player to use in the room.
        
        Inputs: NONE
        Outputs: NONE
        """
        clearScreen()
        print("Available commands:")
        print("- look around         : See what's in the corridor and where you can go.")
        print("- go <room name>      : Move to another room. Examples: 'go front desk', 'go project room 1'")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

    def handle_go(room_name):
        """
        Handles movement out of the room.
        
        Checks if destination is valid directly or through aliases,
        then returns the standardized room string for main.py.
        """
        clearScreen()
        cleaned_target = room_name.lower().strip()

        # Check aliases first, then check direct membership
        target_room = room_aliases.get(cleaned_target, cleaned_target)

        if target_room in available_rooms:
            print(f"You walk toward the door to {target_room}...")
            state["previous_room"] = "lobby"
            return target_room
        else:
            print(f" '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    # --- Main corridor command loop ---
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

        elif command == "quit":
            clearScreen()
            print("👋 You leave the school and the adventure comes to an end. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
