# -----------------------------------------------------------------------------
# File: front_desk.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand, Gift Odigwe
# -----------------------------------------------------------------------------

import sys

from utilities.check_status import check_status
from utilities.clear_screen import clear_screen
from utilities.save_gui import display_save_menu

# Items lying on the reception desk that the player can pick up.
# list survives between visits to the room.
desk_items = [
    "pen",
    "visitor badge",
    "campus flyer",
]

# The reward for registering at the desk: the deposit refund on the old ID card.
ID_CARD_REFUND = 5


def print_floor_map() -> None:
    """
    Prints the 2nd floor campus map that hangs on the office wall.

    This function only draws the ASCII map. It is kept outside enterFrontDesk()
    because it does not need the game state at all.

    Inputs: NONE

    Outputs: NONE
    """

    print("""
+--------------------------- NORTH (Julianalaan) ----------------------------+
|            |            |       | Front Desk | Classroom | Classroom |     |
|  LAB 2.001 |  LAB 2.003 |       |   Office   |   2.015   |   2.021   | T4  |
|            |            |       +------------+-----------+-----------+-----|
|            |            | Lobby        === E-W corridor ===          |     |
|------------+------------+       +------------------------------------+-----|
|                         |       | Teachers | T2 | Equinox | Proj | N-S |   |
|                         |--|--| |  Room 1  |    | Society | Rm 3 | cor.|2.035|
|                         |P1|P2| +-----------------------------------+-----|
|                         |--|--|            Exit Passage                    |
+-- EAST (Rotterdamseweg) ------- SOUTH (Main Stairs) ---- WEST (Leeghwater) -+
""")


def handle_go(destination):
    pass


def enter_front_desk(state: dict) -> str:
    """Starter function for the Front Desk Office."""

    clear_screen()
    print("🛎️  You push open the glass door of the Front Desk Office.")
    print("A staff member is hunched over a laptop behind a wide reception counter.")
    print("Behind him, a large campus floor plan is pinned to the wall.")

    # +----------------------------+
    # | Registration helper method |
    # +----------------------------+

    def handle_register() -> None:
        """
        Runs the student ID registration with the staff member.

        This function asks the player for their name and an 8 digit student
        number. Once a valid number is given, it adds the student ID card to the
        inventory, unlocks the Lobby hint by setting student_id_obtained, marks
        the room as completed and pays out the old card's deposit refund.

        The player can type 'cancel' at any prompt to walk away without an ID.

        Inputs: NONE

        Outputs: NONE
        """

        clear_screen()
        print("The staff member looks up over his glasses.")
        print('"Why are you walking around campus without your student ID card?"')
        print("\"Sit down, I'll print you a new one. Type 'cancel' if you're in a hurry.\"")

        name = input('\n"What\'s your name?" > ').strip()

        if name.lower() == "cancel":
            clear_screen()
            print('"Fine, fine. Come back when you\'ve got a minute."')
            return

        # Empty input still needs a name for the card, so fall back to a default
        if not name:
            name = "Student"
        state["player_name"] = name

        # Keep asking until the player gives an 8 digit number or cancels
        while True:
            student_no = input('"And your 8-digit student number?" > ').strip()

            if student_no.lower() == "cancel":
                clear_screen()
                print('"Suit yourself. The card will be waiting here."')
                return

            # Check length first, then that every character is a digit
            if len(student_no) != 8:
                clear_screen()
                print(f'"That\'s {len(student_no)} characters. A student number is exactly 8 digits long."')
            elif not student_no.isnumeric():
                clear_screen()
                print('"Digits only, please. No letters in a student number."')
            else:
                break

        # Registration succeeded, hand out the card and the deposit refund
        state["inventory"].append("Student ID card")
        state["student_id_obtained"] = True
        state["completed"]["frontdesk"] = True
        state["coin_balance"] += ID_CARD_REFUND

        clear_screen()
        print(f'The printer whirs. "There you go, {name}. Don\'t lose this one."')
        print("He slides a fresh student ID card across the counter.")
        print(f'"Oh, and here\'s the deposit back on your old card." (+{ID_CARD_REFUND} coins)')
        print("")
        print("His desk phone rings. He picks up, and his face changes.")
        print('>> "Security? Yes, we filed the report. Something strange is going on"')
        print('>> "down the E-W corridor, inside the Equinox student society room."')
        print('>> "Send someone over. Now."')
        print("")
        print("He hangs up and pretends you didn't hear any of that.")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handle_help() -> None:
        """
        Lists available commands.

        This function lists the available commands for the player to use in the room.

        Inputs: NONE

        Outputs: NONE
        """

        print("Available commands:")
        print("- ?                   : Show this help message.")
        print("- look around         : Examine the reception office.")
        print("- read map            : Study the 2nd floor campus floor plan.")
        if not state["completed"]["frontdesk"]:
            print("- register            : Ask the staff member for a new student ID.")
        print("- take <item>         : Pick up something from the counter.")
        print("- go lobby / back     : Leave the office and return to the corridor.")
        print("- quit                : Quit the game completely.")

    def handle_look() -> None:
        """
        Handles picking up an item from the reception counter.

        This function checks whether the named item is still on the counter. If
        it is, the item is moved from the counter into the player's inventory.

        Inputs:
            - item (str): The name of the item the player wants to take.

        Outputs: NONE
        """

        if item in desk_items:
            desk_items.remove(item)
            state["inventory"].append(item)
            print(f"You slip the {item} into your bag.")
        else:
            print(f"❌ There's no '{item}' on the counter.")

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clear_screen()
            handle_look()

        elif command == "?":
            clear_screen()
            handle_help()

        elif command == "register":
            if state["completed"]["frontdesk"]:
                clear_screen()
                print('"You\'ve already got your card. Stop wasting my toner."')
            else:
                handle_register()

        elif command in [
            "read map",
            "look at map",
            "map",
        ]:
            clear_screen()
            print("--- 2ND FLOOR CAMPUS MAP ---")
            print_floor_map()

        elif command.startswith("take "):
            clear_screen()
            item = command[5:].strip()
            handle_look()

        elif command.startswith("go "):
            clear_screen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command in ["status", "check status"]:
            clear_screen()
            check_status(state, pause=True)

        elif command in ["pause", "save"]:
            display_save_menu(state)
        
        elif command == "quit":
            clear_screen()
            print("👋 You sign yourself out at reception and walk home. Game over.")
            sys.exit()

        else:
            clear_screen()
            print("❓ Unknown command. Type '?' to see available commands.")
