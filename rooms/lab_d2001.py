# -----------------------------------------------------------------------------
# File: lab_d2001.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys
from time import sleep
from utilities.animations import showActivityAnimation
from utilities.clear_screen import clearScreen
from utilities.check_status import checkStatus

available_boxes = [5, 95, 47, 53, 10, 90]

platforms = [[], [], []]

def enterLabD2001(state: dict) -> str:
    """Starter function for Lab D2.001."""

    clearScreen()
    state["visited"]["labd2001"] = True
    print("🧪 You swipe the keycard you found and enter Lab D2.001.")
    print("You find a work-in-progress construction project. Various materials and tools are laid out on the floor.")

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printPuzzleInstructions(header_message: str = "stuck? use \"quit\" to quit or \"reset\" to redo") -> None:
        """
        Helper function to print puzzle instructions.
        
        This function prints the instructions for the box stacking puzzle,
        along with the status of the platforms and available boxes.
        
        Inputs: NONE
        
        Outputs: NONE
        """
        clearScreen(header_message)
        print(" You take a closer look at the platforms.")
        print(" You make out a label on the platforms that says \"MAX. 100kg\".")
        print(" It seems that they can only have space for two boxes at a time.")
        print(" You turn to the boxes, and notice each of them have their weight listed on them: 5kg, 53kg, 95kg, 10kg, 47kg and 90kg.")
        print(" You might be able to overload the platforms if you stack the boxes in the right way, and force the boxes open.")
            
        print("\n First, type the kilogram value of one of the available boxes, and then which of the platforms to place it on.")
        print(" Stuck? Use \"quit\" to quit the puzzle or \"reset\" to redo it from the start.")
        print(f"\n    - Available boxes: {', '.join(f'{box}kg' for box in available_boxes)}")
        print(f"    - Platform 1: {', '.join(f'{box}kg' for box in platforms[0]) if platforms[0] else 'empty!'}")
        print(f"    - Platform 2: {', '.join(f'{box}kg' for box in platforms[1]) if platforms[1] else 'empty!'}")
        print(f"    - Platform 3: {', '.join(f'{box}kg' for box in platforms[2]) if platforms[2] else 'empty!'}")

    def boxPuzzleCheck() -> bool:
        """
        Checks if the box puzzle is solved correctly. Returns True if solved, False otherwise.
        
        The function checks if the puzzle is solved correctly,
        i.e. if each platform has exactly two boxes and the total 
        weight of the boxes on each platform is exactly 100kg.
        
        Inputs: NONE
        
        Outputs:
            - bool: True if the puzzle is solved correctly, False otherwise.
        """

        correct_count = 0
        for platform in platforms:
            if len(platform) < 2:
                return False
            elif sum(platform) != 100:
                return False
            else:
                correct_count += 1
        if correct_count == 3:
            return True
        else:
            return False

    def boxPuzzleReset() -> None:
        """
        Resets the box puzzle to its initial state.

        This function resets the box puzzle by clearing the platforms and restoring the available boxes to their original state.

        Inputs: NONE

        Outputs: NONE
        """
        global available_boxes, platforms
        available_boxes = [5, 95, 47, 53, 10, 90]
        platforms = [[], [], []]
        printPuzzleInstructions("puzzle reset!")

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
            print("The entire lab is filled with construction materials, tools and boxes. It looks like a construction site.")
            print("In a corner, you notice a table with some chairs, bottles of water and a mountain of about 10 sandwiches.")
            print("There's no doubt, these contractors were clearly Dutch.")
            print("There's also some platforms and boxes that you can't seem to get to open.")
            print("You might be able to overload the platforms and get the boxes to open if you stack them correctly.")
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
        print("- ?                   : Show this help message.")
        print("- look around         : Examine the room for clues.")
        print("- status              : Check your current status.")
        if not state["completed"]["labd2001"]:
            print("- start stacking      : Try stacking the boxes.")
            print("- reset               : Reset the puzzle to its initial state.")
        print("- go lobby / back     : Leave the room and return to the corridor.")
        print("- quit                : Quit the game completely or exit a puzzle if in progress.")

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
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handlePuzzleStart() -> None:
        """
        Handles starting the box stacking puzzle.

        This function starts the box stacking puzzle by showing an animation, printing the puzzle instructions,
        and allowing the player to input their choices for stacking boxes on platforms until the puzzle is solved correctly.

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
                    print("You decide to step away from the platforms and boxes for now. Maybe you'll come back later.")
                    break
                if box == "reset":
                    boxPuzzleReset()
                    continue
                box_int = int(box)
            except ValueError:
                printPuzzleInstructions("please type a valid number, or use \"quit\" to quit")
                continue

            # Check if box exists in available_boxes, same with platform, if both pass
            # then add box to platform and remove from available_boxes
            if box.isnumeric() and box_int in available_boxes:
                printPuzzleInstructions()
                try:
                    platform = input("\nChoose a platform > ").strip().lower()
                    if platform == "quit":
                        clearScreen()
                        print("You decide to step away from the platforms and boxes for now. Maybe you'll come back later.")
                        break
                    if platform == "reset":
                        boxPuzzleReset()
                        continue
                except ValueError:
                    printPuzzleInstructions("please type a valid number, or use \"quit\" to quit")
                    continue
                
                if platform.isnumeric() and int(platform) in range(1, 4):
                    if len(platforms[int(platform) - 1]) >= 2:
                        printPuzzleInstructions("platform is full! try again, use \"quit\" to quit")
                        continue
                    
                    box_index = available_boxes.index(box_int)
                    box_to_add = available_boxes.pop(box_index)
                    platforms[int(platform) - 1].append(box_to_add)
                    printPuzzleInstructions()
                else:
                    printPuzzleInstructions("platform number doesn't exist, or use \"quit\" to quit")
            else:
                printPuzzleInstructions("box number doesn't exist, or use \"quit\" to quit")

        # When loop exits, re-check if solve is valid and then set room as
        if boxPuzzleCheck():
            state["completed"]["labd2001"] = True
            state["coin_balance"] += 10
            state["inventory"].append("Teacher Access Keycard")
            clearScreen()
            print("Looks like you successfully overloaded the platforms! One of the boxes falls open.")
            print("You quickly peer inside, and find a small keycard labeled 'Teacher Access Keycard'.")
            print("Looks like you can get inside all of the private teacher rooms now.")
            print("Around the keycard, you find some coins, which you pick up. (+10 coins)")

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
            if not state["completed"]["labd2001"]:
                clearScreen()
                handlePuzzleStart()
            else:
                clearScreen()
                print("You've already forced the boxes open. There's nothing more to do here.")

        elif command in ["status", "check status"]:
            clearScreen()
            checkStatus(state, pause = True)

        elif command == "quit":
            clearScreen()
            print("👋 You sit on one of the chairs in the Lab and close your eyes. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")