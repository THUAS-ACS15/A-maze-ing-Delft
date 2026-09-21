# -----------------------------------------------------------------------------
# File: lobby.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clearScreen

def enterLobby(state):
    """Starter function for the Lobby room."""
    clearScreen()
    print("🚶 You are standing in the school's main lobby.")
    print("You see a long corridor with many doors and glass walls on both sides. Behind these doors are rooms, waiting to be explored.")
    if not state["student_id_obtained"]:
        print("You notice you're missing your student ID. You should check out the Front Desk to see if you can obtain a new one.")

    # --- List of accessible rooms from here ---
    available_rooms = ["labd2001", "store", "teachersroom1", "teachersroom2","projectroom2"]

    # --- Command handlers ---

    def handle_look():
        """
        Describes the room and gives clues.
        
        This function describes the room and gives clues to the player which\
        rooms they can go to.
        
        Inputs: NONE
        
        Outputs: NONE
        """

        clearScreen()
        print("You take a look around.")
        print("Students and teachers are walking in both directions along the corridor. You see several labeled doors.")
        print(f"- Possible doors: {', '.join(available_rooms)}")
        print("- Your current inventory:", state["inventory"])

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
        print("- go <room name>      : Move to another room. Example: go classroom2015")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game.")

    def handle_go(room_name):
        """
        Handles movement out of the room.
        
        This function checks if the player can move to the given destination from this room.
        If the destination is valid, it returns the destination string. Otherwise, it prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.
        
        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
        
        clearScreen()
        room = room_name.lower()
        if room in available_rooms:
            print(f"You walk toward the door to {room}.")
            state["previous_room"] = "corridor"
            return room
        else:
            print(f" '{room_name}' is not a valid exit. Use 'look around' to see available options.")
            return None

    # --- Main corridor command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            handle_look()

        elif command == "?":
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
