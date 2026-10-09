# -----------------------------------------------------------------------------
# File: project_room_2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: João, Gift Odigwe
# -----------------------------------------------------------------------------

import random
import sys

from utilities.animations import show_activity_animation
from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu
from utilities.print_helpers import print_dialogue, print_current_objective, print_assembly_part_obtained

from data.story_dialogue_bank import story_dialogue_bank
from data.look_around_dialogue_bank import look_around_dialogue_bank

rainbow_colors_correct = [
    "Red",
    "Orange",
    "Yellow",
    "Green",
    "Blue",
    "Indigo",
    "Violet",
]

colors_on_projector = rainbow_colors_correct.copy()
while colors_on_projector == rainbow_colors_correct:
    random.shuffle(colors_on_projector)

valid_destinations = ["studentwing"]
room_dialogue_bank = story_dialogue_bank["rooms"]["projectroom2"]

def enter_project_room2(state: dict) -> str:
    """Starter function for the Project Room."""

    clear_screen()
    print_dialogue(room_dialogue_bank["header"])
    print_dialogue(room_dialogue_bank["enter"])

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def print_puzzle_instructions() -> None:
        """
        Helper function to print puzzle instructions.

        This function prints the instructions for the color ordering puzzle,
        along with the current order of colors shown on the projector.

        Inputs: NONE

        Outputs: NONE
        """

        clear_screen()
        print("Type two positions (1-7) to swap the colors shown there. Arrange them in rainbow order.")
        print("Current order on the projector:")
        for position, color in enumerate(colors_on_projector, start=1):
            print(f"    {position}. {color}")

    def color_puzzle_check() -> bool:
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

    def handle_look() -> None:
        """
        Describes the room and gives clues.

        This function describes the room and gives clues to the player about the
        color ordering puzzle. It also shows the possible exits and the
        player's current inventory.

        Inputs: NONE

        Outputs: NONE
        """

        print_dialogue(look_around_dialogue_bank["projectroom2"])
        if not state["completed"]["projectroom2"]:
            print_dialogue(room_dialogue_bank["puzzle_not_complete"])
        else:
            print_dialogue(room_dialogue_bank["puzzle_already_complete"])
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])
        print()
        print_current_objective(state)

    def handle_help() -> None:
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

    def handle_go(destination: str) -> str:
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

        if destination in valid_destinations:
            return destination
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return ""

    def handle_puzzle_start() -> None:
        """
        Handles starting the color ordering puzzle.

        This function starts the color ordering puzzle by showing an animation, printing the puzzle instructions,
        and allowing the player to swap two positions at a time until the colors are in the correct rainbow order.

        Once the puzzle is solved, it updates the state dict to mark the puzzle as completed.

        Inputs: NONE

        Outputs: NONE
        """

        show_activity_animation("puzzle", text_delay=0.002, final_delay=1.0)
        print_puzzle_instructions()

        # Loops until function returns true, i.e. if puzzle is completed
        while not color_puzzle_check():
            try:
                first = input("\nChoose the first position to swap (1-7) > ").strip()
                second = input("Choose the second position to swap (1-7) > ").strip()
                first_int = int(first)
                second_int = int(second)
            except ValueError:
                print_puzzle_instructions()
                print("❌ Please enter numbers between 1 and 7.")
                continue

            # Check if both positions are valid and different, then swap them
            if first_int in range(1, 8) and second_int in range(1, 8) and first_int != second_int:
                index_one = first_int - 1
                index_two = second_int - 1
                colors_on_projector[index_one], colors_on_projector[index_two] = (
                    colors_on_projector[index_two],
                    colors_on_projector[index_one],
                )
                print_puzzle_instructions()
            else:
                print_puzzle_instructions()
                print("❌ Please choose two different positions between 1 and 7.")

        # When loop exits, re-check if solve is valid and then set room as completed
        if color_puzzle_check():
            state["completed"]["projectroom2"] = True
            state["inventory"].append("Makeshift Mic and Speaker Combo")
            state["current_objective_id"] += 1
            clear_screen()
            print_dialogue(room_dialogue_bank["puzzle_completed"])
            print_dialogue(room_dialogue_bank["puzzle_take_mic_and_speaker"], print_newline_after = False)
            print_assembly_part_obtained("(+ Makeshift Mic and Speaker Combo)")
            print_current_objective(state)

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

        elif command == "start puzzle":
            if not state["completed"]["projectroom2"]:
                clear_screen()
                handle_puzzle_start()
            else:
                clear_screen()
                print_dialogue(room_dialogue_bank["puzzle_already_complete"])

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause = True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print_dialogue(room_dialogue_bank["quit"])
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
