# -----------------------------------------------------------------------------
# File: equinox_society.py
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

def enterEquinoxStudentSociety(state: dict) -> str:
    """Starter function for the Equinox Student Society room."""

    clearScreen()
    state["visited"]["equinox_student_society"] = True
    print("📚 You scan your student ID on the doorknob and enter the Equinox Student Society room.")
    print("You find a disorganized room. The center of the room has a table with 3 chairs, and an opened board game box on it.")
    print("Looks like they were in the middle of a Dungeons and Dragons campaign, but had to leave in a hurry.")
    print("You also notice an office desk and chair, with some stuff on it.")
    print("Maybe you should look around and see if you can find any interesting things around.")

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
        print(" Select an option to answer! Use the number keys to select option 1, 2, 3 or 4.")

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

        if not state["completed"]["equinox_society"]:
            print("You take a close look at the board game box, and notice that it contains a small statue of a dragon.")
            print("Next to it, you find some coins. Looks like it was hoarding some treasure. Thankfully it's just a statue, so you pick them up. (+10 coins)")
            state["coin_balance"] += 10
            print("\nYou also notice that the computer on the desk is turned on! You quickly sit down and find a quiz on the screen.")
            print("Looks like you need to answer some questions to find out what's on the computer.")
        else:
            print("You've already finished the quiz and claimed your reward, so there's nothing else to do here.")
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
            print("- start quiz  : Try answering the quiz on the computer.")
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

    def handleQuizStart() -> None:
        """
        Handles starting the quiz.

        This function starts the quiz by showing an animation, printing the quiz instructions,
        and allowing the player to input their answers until the quiz is completed correctly.

        Once the quiz is solved, it rewards the player and updates the state dict to mark the room as completed.

        Inputs: NONE

        Outputs: NONE
        """

        showActivityAnimation("quiz")
        sleep(1)
        printPuzzleInstructions()



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

        elif command == "start quiz":
            handlePuzzleStart()

        elif command == "quit":
            clearScreen()
            print("👋 You lean too hard on the chair and fall asleep. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")