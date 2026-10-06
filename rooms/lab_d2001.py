# -----------------------------------------------------------------------------
# File: lab_d2001.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.animations import show_activity_animation
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# Vars used in puzzle
available_boxes = [5, 95, 47, 53, 10, 90]

platforms:  list[list[int]]  = [[], [], []]

def enter_lab_d2001(state: dict) -> str:
    """Starter function for Lab D2.001."""

    clear_screen()
    print("🧪 You enter Lab D2.001.")
    print("This room has some tables, filled with electronics equipment and cables on top.")
    print("You notice a table with some chairs, filled with sandwiches and drinks.")
    print("The rest of the room is filled with construction tools, unopened boxes and materials.")

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def print_puzzle_instructions(header_message: str = "stuck? use \"quit\" to quit or \"reset\" to redo",) -> None:
        """
        Helper function to print puzzle instructions.

        This function prints the instructions for the box stacking puzzle,
        along with the status of the platforms and available boxes.

        Inputs: header_message (str): A message to display at the top of the status bar, passed to clear_screen().

        Outputs: NONE
        """

        clear_screen(header_message)
        print(" First, type the kilogram value of one of the available boxes, and")
        print(" then type the number of the platform you want to place it on (1, 2 or 3).\n")

        print(f"    - Available boxes: {', '.join([f'{box}kg' for box in available_boxes])}")
        print(f"    - Platform 1: {', '.join([f'{box}kg' for box in platforms[0]])}")
        print(f"    - Platform 2: {', '.join([f'{box}kg' for box in platforms[1]])}")
        print(f"    - Platform 3: {', '.join([f'{box}kg' for box in platforms[2]])}")

    def box_puzzle_check() -> bool:
        """
        Checks if the box puzzle is solved correctly. Returns True if solved, False
        otherwise.

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

    def box_puzzle_reset() -> None:
        """
        Resets the box puzzle to its initial state.

        This function resets the box puzzle by clearing the platforms and restoring the
        available boxes to their original state.

        Inputs: NONE

        Outputs: NONE
        """
        global available_boxes, platforms
        available_boxes = [5, 95, 47, 53, 10, 90]
        platforms = [[], [], []]
        print_puzzle_instructions("puzzle reset!")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_look() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        box stacking puzzle. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """
    
        print("You take a quick look around, and conclude that this is a work-in-progress construction project.")
        print("Beside the tables with lab equipment and the one corner with sandwiches and drinks,")
        print("the rest of the room is filled with construction tools, unopened boxes and materials.")
        print("Judging by the amount of sandwiches, these contractors were quite clearly Dutch.")
        print("You are most curious about all the unopened boxes, and wonder what could be inside them.")
        print("Maybe you could overload the boxes onto the platforms, and see if they open up & reveal their contents.")
        print("- Possible exits: lobby")
        print(f"- Your current inventory: {state['inventory']}")

    def handle_help() -> None:
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
        valid_destinations = ["projectroom2", "teachersroom1", "teachersroom4"]
        if destination in valid_destinations:
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

    def handle_puzzle_start() -> None:
        """
        Handles starting the box stacking puzzle.

        This function starts the box stacking puzzle by showing an animation, printing
        the puzzle instructions, and allowing the player to input their choices for
        stacking boxes on platforms until the puzzle is solved correctly.

        Once the puzzle is solved, it updates the state dict to mark the puzzle as
        completed.

        Inputs: NONE

        Outputs: NONE
        """

        show_activity_animation("puzzle", text_delay=0.002, final_delay=1.0)
        print_puzzle_instructions()

        # Loops until function returns true, i.e. if puzzle is completed
        while not box_puzzle_check():
            try:
                box = input("\nChoose a box > ").strip().lower()
                if box == "quit":
                    clear_screen()
                    print("You decide to step away from the platforms and boxes for now.")
                    print("Maybe you'll come back later.")
                    break
                if box == "reset":
                    box_puzzle_reset()
                    continue
                box_int = int(box)
            except ValueError:
                print_puzzle_instructions('type a valid number! | use "quit" to quit')
                continue

            # Check if box exists in available_boxes, same with platform, if both pass
            # then add box to platform and remove from available_boxes
            if box.isnumeric() and box_int in available_boxes:
                print_puzzle_instructions()
                try:
                    platform = input("\nChoose a platform > ").strip().lower()
                    if platform == "quit":
                        clear_screen()
                        print(
                            "You decide to step away from the platforms and boxes for "
                            "now. Maybe you'll come back later."
                        )
                        break
                    if platform == "reset":
                        box_puzzle_reset()
                        continue
                except ValueError:
                    print_puzzle_instructions('type a valid number | use "quit" to quit')
                    continue

                if platform.isnumeric() and int(platform) in range(1, 4):
                    if len(platforms[int(platform) - 1]) >= 2:
                        print_puzzle_instructions('platform is full! | use "quit" to quit')
                        continue

                    box_index = available_boxes.index(box_int)
                    box_to_add = available_boxes.pop(box_index)
                    platforms[int(platform) - 1].append(box_to_add)
                    print_puzzle_instructions()
                else:
                    print_puzzle_instructions('platform number doesn\'t exist | use "quit" to quit')
            else:
                print_puzzle_instructions('box number doesn\'t exist | use "quit" to quit')

        # When loop exits, re-check if solve is valid and then set room as
        if box_puzzle_check():
            state["completed"]["labd2001"] = True
            state["coin_balance"] += 10
            state["inventory"].append("Teacher Access Keycard")
            clear_screen()
            print("Looks like you stacked the boxes correctly, congratulations!")
            print('You hear a loud "click" sound, and one of the boxes falls open.')
            print("Inside, you find some coins, which you pick up. (+10 coins)")

    # +--------------+
    # | Command loop |
    # +--------------+

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("go "):
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command == "start stacking":
            if not state["completed"]["labd2001"]:
                clear_screen()
                handle_puzzle_start()
            else:
                clear_screen()
                print("You've already forced the boxes open. There's nothing more to do here.")

        elif command == "reset":
            if not state["completed"]["labd2001"]:
                clear_screen()
                box_puzzle_reset()
            else:
                clear_screen()
                print("You've already forced the boxes open. There's nothing more to do here.")

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print("👋 You sit on one of the chairs in the Lab and close your eyes. Game over.")
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
