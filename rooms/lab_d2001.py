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
from utilities.animations import showActivityAnimation
from utilities.clear_screen import clearScreen

available_boxes = [5, 95, 47, 53, 10, 90]

forklifts = [[], [], []]

def enterLabD2001(state: dict) -> str:
    """Starter function for Lab D2.001."""

    clearScreen()
    state["visited"]["labd2001"] = True
    print("🧪 You enter Lab D2.001.")
    print("You find a work-in-progress construction project. Various materials and tools are laid out on the floor.")
    print("You spot three forklifts on one side of the room, and six boxes on the other.")
    print("Maybe you should check it out.")

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printPuzzleInstructions() -> None:
        """
        Helper function to print puzzle instructions.
        
        This function prints the instructions for the box stacking puzzle,
        along with the status of the forklifts and available boxes.
        
        Inputs: NONE
        
        Outputs: NONE
        """

        clearScreen()
        print(" First, type the kilogram value of one of the available boxes, and then which of the forklifts to place it on.")
        print(f"    - Available boxes: {available_boxes}")
        print(f"    - Forklift 1: {forklifts[0]}")
        print(f"    - Forklift 2: {forklifts[1]}")
        print(f"    - Forklift 3: {forklifts[2]}")

    def boxPuzzleCheck() -> bool:
        """
        Checks if the box puzzle is solved correctly. Returns True if solved, False otherwise.
        
        The function checks if the puzzle is solved correctly,
        i.e. if each forklift has exactly two boxes and the total 
        weight of the boxes on each forklift is exactly 100kg.
        
        Inputs: NONE
        
        Outputs:
            - bool: True if the puzzle is solved correctly, False otherwise.
        """

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

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.
        
        This function describes the room and gives clues to the player about the 
        box stacking puzzle. It also shows the possible exits and the 
        player's current inventory.
        
        Inputs: NONE
        
        Outputs: NONE
        """

        if not state["completed"]["labd2001"]:
            print("You take a closer look at the forklifts.")
            print("You make out a label on the forklifts that says \"MAX. 100kg\".")
            print("It seems that they can only have space for two boxes at a time.")
            print("You turn to the boxes, and notice each of them have their weight listed on them: 5kg, 53kg, 95kg, 10kg, 47kg and 90kg.")
            print("This looks like a puzzle. Maybe you should try stacking the boxes on the forklifts.")
        else:
            print("You've already stacked the boxes correctly. There's nothing more for you to do.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handleHelp() -> None:
        """
        Lists available commands.
        
        This function lists the available commands for the player to use in the room.
        
        Inputs: NONE
        
        Outputs: NONE
        """

        print("Available commands:")
        print("- look around         : Examine the room for clues.")
        if not state["completed"]["labd2001"]:
            print("- start stacking      : Try stacking the boxes.")
        print("- go lobby / back     : Leave the room and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handleGo(destination: str) -> str:
        """
        Handles movement out of the room.
        
        This function checks if the player can move to the given destination from this room.
        If the destination is valid, it returns the destination string. Otherwise, it prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.
        
        Outputs:
            - location (str): The destination if valid, None otherwise.
        """
        valid_destinations = ["lobby", "back"]
        
        if destination in valid_destinations:
            print("You decide to get out of the lab and return to the lobby.")
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handlePuzzleStart() -> None:
        """
        Handles starting the box stacking puzzle.

        This function starts the box stacking puzzle by showing an animation, printing the puzzle instructions,
        and allowing the player to input their choices for stacking boxes on forklifts until the puzzle is solved correctly.

        Once the puzzle is solved, it updates the state dict to mark the puzzle as completed.

        Inputs: NONE

        Outputs: NONE
        """

        showActivityAnimation("puzzle")
        sleep(1)
        printPuzzleInstructions()

        # Loops until function returns true, i.e. if puzzle is completed
        while boxPuzzleCheck() != True:
            try:
                box = input("\nChoose a box > ").strip().lower()
                if box == "quit":
                    clearScreen()
                    break
                box_int = int(box)
            except ValueError:
                printPuzzleInstructions()
                continue

            # Check if box exists in available_boxes, same with forklift, if both pass
            # then add box to forklift and remove from available_boxes
            if box.isnumeric() and box_int in available_boxes:
                printPuzzleInstructions()
                try:
                    forklift = input("\nChoose a forklift > ").strip().lower()
                except ValueError:
                    printPuzzleInstructions()
                    continue

                if forklift.isnumeric() and int(forklift) in range(1, 4):
                    box_index = available_boxes.index(box_int)
                    box_to_add = available_boxes.pop(box_index)
                    forklifts[int(forklift) - 1].append(box_to_add)
                    printPuzzleInstructions()
            else:
                printPuzzleInstructions()

        # When loop exits, re-check if solve is valid and then set room as
        if boxPuzzleCheck():
            state["completed"]["labd2001"] = True
            state["coin_balance"] += 10
            clearScreen()
            print("Looks like you stacked the boxes correctly, congratulations!")
            print("You hear a loud \"click\" sound, and one of the boxes falls open.")
            print("Inside, you find some coins, which you pick up. (+10 coins)")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clearScreen()
            handleLook()

        elif command == "?":
            clearScreen()
            handleHelp()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handleGo(destination)
            if result:
                return result

        elif command == "start stacking":
            handlePuzzleStart()

        elif command == "quit":
            clearScreen()
            print("👋 You sit on one of the chairs in the Lab and close your eyes. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")