# -----------------------------------------------------------------------------
# File: choose_next_room.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributor: Gift Odigwe
# -----------------------------------------------------------------------------

from utilities.clear_screen import clear_screen


def choose_next_room(choices):
    print("\n🔀 Choose a door:")
    for i, room in enumerate(choices, start=1):
        print(f"{i}. {room}")
    choice = input("Enter the number of your choice: ")

    try:
        index = int(choice) - 1
        if 0 <= index < len(choices):
            clear_screen()
            return choices[index]
        else:
            print("Invalid choice.")
            return None
    except ValueError:
        print("Invalid input.")
        return None
