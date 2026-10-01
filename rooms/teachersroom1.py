# -----------------------------------------------------------------------------
# File: teachersroom1.py
# Project: AMazeingDelft
# Organization: THUAS
# Location: Delft
# Date: September 2026
# Contributors: Dominik, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu


def enter_teachers_room1(state: dict) -> str:
    clear_screen()
    print("\nYou step into Teachers Room 1.")
    print("A teacher is sitting at a laptop, muttering under their breath at the screen.")
    print("Sticky notes covered in function names are scattered across the desk.")

    def handle_look():
        print("\nYou take a look around.")
        print(
            "It's a standard teachers room, shelves full of documents lining the left side wall."
            " On the right there are some posters and notice boards."
        )
        print("The teacher's screen shows a Python code, almost finished.")
        if not state["completed"]["teachersroom1"]:
            print('The teacher looks up: "Oh, perfect timing. I\'m missing one last piece of this code."')
            print("\"If you can figure out why my code doesn't work, I'll make it worth your while.\"")
            print("""
    def sum_even_numbers(numbers):
        total = 0
        for n in numbers:
            if ____ == 0:
                total += n
        return total
""")
            print('The teacher points to the screen: "The code always returns the wrong number"')
        else:
            print('The teacher grins: "That fix worked perfectly, thanks again!"')
            if "debug_notes" not in state["inventory"]:
                print("A small notebook labeled 'Debug Notes' is still sitting on the desk.")
            else:
                print("The desk is tidy now, you've already taken the notebook.")
        print("- Possible exits: Lobby")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        print("\nAvailable commands:")
        print("- ?                   : Show this help message.")
        print("- look around         : Examine the room and the code on screen.")
        if not state["completed"]["teachersroom1"]:
            print("- answer <snippet>    : Try to fill in the missing piece of code.")
        if state["completed"]["teachersroom1"] and "debug_notes" not in state["inventory"]:
            print("- take notebook       : Pick up the notebook once it's offered.")
        print("- go Lobby / back  : Leave the room and return to the Lobby.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item in [
            "notebook",
            "debug notes",
            "debug_notes",
        ]:
            if not state["completed"]["teachersroom1"]:
                print("There's nothing to take yet. Maybe help the teacher first.")
            elif "debug_notes" in state["inventory"]:
                print("You already have the notebook in your backpack.")
            else:
                state["coin_balance"] += 10
                clear_screen()
                print('You pick up the notebook. "Take this, you\'ve earned it," the teacher says.')
                print(
                    "After taking the notebook the teacher is handing you, you notice something shiny in the corner "
                    "of your eye."
                )
                print(
                    "You look closer and realize you found some shiny coins, teacher allows you to take them "
                    "(+ 10 coins)"
                )
                state["inventory"].append("debug_notes")
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["lobby", "back"]:
            print("You wave goodbye to the teacher and step back into the Lobby.")
            return "lobby"
        else:
            print(f"You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer):
        if state["completed"]["teachersroom1"]:
            print("You've already solved this challenge.")
            return
        # accept a few equivalent ways of writing "n % 2"
        normalized = answer.strip().lower().replace(" ", "")
        accepted = ["n%2", "n % 2"]
        if normalized in accepted:
            print('Correct! The teacher\'s eyes light up: "n % 2 — of course! Thank you!"')
            state["completed"]["teachersroom1"] = True
            print("Here, take this! I have no use for this now.")
            print("The teacher points to a small notebook labeled 'Debug Notes'.")
        else:
            print('The teacher shakes their head: "Not quite. Think about how you check if a number is even."')

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command.startswith("take "):
            clear_screen()
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            clear_screen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            clear_screen()
            answer = command[7:].strip()
            handle_answer(answer)

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)

        elif command == "quit":
            clear_screen()
            print("👋 You leave the teacher to their code and exit the room.")
            sys.exit()

        else:
            clear_screen()
            print("Unknown command. Type '?' to see available commands.")
