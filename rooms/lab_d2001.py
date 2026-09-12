# -----------------------------------------------------------------------------
# File: lab_d2001.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

import sys
from time import sleep
from utilities.animations import show_activity_animation
from utilities.status_bar import update_status_bar
from utilities.utils import clearScreen

available_boxes = [5, 95, 47, 53, 10, 90]

forklifts = [[], [], []]

def enterLabD2001(state):
    # --- Room entry description ---
    clearScreen(state)
    print("🧪 You enter Lab D2.001.")
    print("You find a work-in-progress construction project. Various materials and tools are laid out on the floor.")
    print("You spot three forklifts on one side of the room, and six boxes on the other.")
    print("Maybe you should check it out.")

    # Function to print puzzle instructions so we don't have to copy-paste 5 lines
    def print_puzzle_instructions():
        clearScreen(state)
        print(" First, type the kilogram value of one of the available boxes, and then the which of the forklifts to place it on.")
        print(f"    - Available boxes: {available_boxes}")
        print(f"    - Forklift 1: {forklifts[0]}")
        print(f"    - Forklift 2: {forklifts[1]}")
        print(f"    - Forklift 3: {forklifts[2]}")

    # Checker for if the box puzzle solve is valid
    def box_puzzle_check():
        correct_count = 0
        for forklift in forklifts:
            if len(forklift) < 2:
                return False
            elif sum(forklift) != 100:
                return False
            else:
                correct_count += 1
        if correct_count == 3:
            return True
        else:
            return False

    # --- Command handlers ---

    def handle_look():
        """Describe the room and give clues."""
        if not state["visited"]["labd2001"]:
            print("You take a closer look at the forklifts.")
            print("You make out a label on the forklifts that says \"MAX. 100kg\".")
            print("It seems that they can only have space for two boxes at a time.")
            print("You turn to the boxes, and notice each of them have their weight listed on them: 5kg, 53kg, 95kg, 10kg, 47kg and 90kg.")
            print("This looks like a puzzle. Maybe you should try stacking the boxes on the forklifts.")
        else:
            print("You've already stacked the boxes correctly. There's nothing more for you to do.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        """List available commands."""
        print("\nAvailable commands:")
        print("- look around         : Examine the room for clues.")
        if not state["visited"]["labd2001"]:
            print("- start stacking      : Try stacking the boxes.")
        print("- go lobby / back     : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handle_go(destination):
        """Handle movement out of the room."""
        if destination in ["lobby", "back"]:
            print("You decide to get out of the lab and return to the lobby.")
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_puzzle_start():
        show_activity_animation("puzzle", state)
        sleep(1)
        print_puzzle_instructions()
        while box_puzzle_check() != True:
            box = input("\nChoose a box > ").strip().lower()

            if box in ["exit", "quit"]:
                break

            box_int = int(box)
            if box.isnumeric() and box_int in available_boxes:
                print_puzzle_instructions()
                forklift = input("\nChoose a forklift > ").strip().lower()
                if forklift in ["exit", "quit"]:
                    break
                if forklift.isnumeric() and int(forklift) in range(1, 4):
                    box_index = available_boxes.index(box_int)
                    box_to_add = available_boxes.pop(box_index)
                    forklifts[int(forklift) - 1].append(box_to_add)
                    print_puzzle_instructions()
            else:
                print_puzzle_instructions()
        if box_puzzle_check():
            state["visited"]["labd2001"] = True
            clearScreen(state)
            print('Looks like you stacked the boxes correctly, congratulations!')

    # --- Main command loop ---
    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clearScreen(state)
            handle_look()

        elif command == "?":
            clearScreen(state)
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "start stacking":
            handle_puzzle_start()

        elif command == "quit":
            clearScreen(state)
            print("👋 You sit on one of the chairs in the Lab and close your eyes. Game over.")
            sys.exit()

        else:
            clearScreen(state)
            print("❓ Unknown command. Type '?' to see available commands.")
