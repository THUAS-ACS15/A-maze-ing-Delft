# -----------------------------------------------------------------------------
# File: project_room_2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: João
# -----------------------------------------------------------------------------

import sys
import random
from time import sleep
from utilities.animations import showActivityAnimation
from utilities.clear_screen import clearScreen

rainbow_colors_correct = ["Red", "Orange", "Yellow", "Green", "Blue", "Indigo", "Violet"]

colors_on_projector = rainbow_colors_correct.copy()
while colors_on_projector == rainbow_colors_correct:
    random.shuffle(colors_on_projector)


def enterProjectRoom2(state: dict) -> str:
    """Starter function for the Project Room."""

    clearScreen()
    state["visited"]["projectroom2"] = True
    print("🎨 You enter the Project Room.")
    print("In the middle of the room stands an old projector, humming quietly.")
    print("It projects 7 colored slides onto the wall, but they look completely out of order.")
    print("Maybe you should take a closer look at the projector.")

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printPuzzleInstructions() -> None:
        """
        Helper function to print puzzle instructions.

        This function prints the instructions for the color ordering puzzle,
        along with the current order of colors shown on the projector.

        Inputs: NONE

        Outputs: NONE
        """

        clearScreen()
        print("Type two positions (1-7) to swap the colors shown there. Arrange them in rainbow order.")
        print("Current order on the projector:")
        for position, color in enumerate(colors_on_projector, start=1):
            print(f"    {position}. {color}")

    def colorPuzzleCheck() -> bool:
        """
        Checks if the color puzzle is solved correctly. Returns True if solved, False otherwise.

        The function checks if the colors on the projector are in the exact
        order of the rainbow (Red, Orange, Yellow, Green, Blue, Indigo, Violet).

        Inputs: NONE

        Outputs:
            - bool: True if the puzzle is solved correctly, False otherwise.
        """

        return colors_on_projector == rainbow_colors_correct

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        color ordering puzzle. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """

        if not state["completed"]["projectroom2"]:
            print("You take a closer look at the projector.")
            print("The 7 slides show colors, but shuffled in a random order.")
            print("It looks like they are meant to be arranged in the order of the rainbow.")
            print("Maybe you should try swapping the slides around.")
        else:
            print("You've already arranged the colors correctly. There's nothing more for you to do.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handleHelp() -> None:
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """

        print("\nAvailable commands:")
        print("- look around         : Examine the room for clues.")
        if not state["completed"]["projectroom2"]:
            print("- start puzzle        : Try arranging the colors on the projector.")
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
            print("You decide to leave the projector behind and return to the lobby.")
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handlePuzzleStart() -> None:
        """
        Handles starting the color ordering puzzle.

        This function starts the color ordering puzzle by showing an animation, printing the puzzle instructions,
        and allowing the player to swap two positions at a time until the colors are in the correct rainbow order.

        Once the puzzle is solved, it updates the state dict to mark the puzzle as completed.

        Inputs: NONE

        Outputs: NONE
        """

        showActivityAnimation("puzzle")
        sleep(1)
        printPuzzleInstructions()

        # Loops until function returns true, i.e. if puzzle is completed
        while colorPuzzleCheck() != True:
            try:
                first = input("\nChoose the first position to swap (1-7) > ").strip()
                second = input("Choose the second position to swap (1-7) > ").strip()
                first_int = int(first)
                second_int = int(second)
            except ValueError:
                printPuzzleInstructions()
                print("❌ Please enter numbers between 1 and 7.")
                continue

            # Check if both positions are valid and different, then swap them
            if first_int in range(1, 8) and second_int in range(1, 8) and first_int != second_int:
                index_one = first_int - 1
                index_two = second_int - 1
                colors_on_projector[index_one], colors_on_projector[index_two] = colors_on_projector[index_two], colors_on_projector[index_one]
                printPuzzleInstructions()
            else:
                printPuzzleInstructions()
                print("❌ Please choose two different positions between 1 and 7.")

        # When loop exits, re-check if solve is valid and then set room as completed
        if colorPuzzleCheck():
            state["completed"]["projectroom2"] = True
            clearScreen()
            print("🌈 The slides light up in perfect rainbow order, congratulations!")
            state["inventory"].append("labd2003keycard")
            print("💳 A small compartment on the projector opens, revealing a keycard labeled 'LAB D2.003'. You take it.")
            print("It looks like it could open the door to LAB D2.003 somewhere else in the building.")

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

        elif command == "start puzzle":
            handlePuzzleStart()

        elif command == "quit":
            clearScreen()
            print("👋 You switch off the projector and close your eyes. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
