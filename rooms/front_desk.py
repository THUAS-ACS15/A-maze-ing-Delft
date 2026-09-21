# -----------------------------------------------------------------------------
# File: front_desk.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clearScreen

# Items lying on the reception desk that the player can pick up.
# list survives between visits to the room.
desk_items = ["pen", "visitor badge", "campus flyer"]

# The reward for registering at the desk: the deposit refund on the old ID card.
ID_CARD_REFUND = 5


def printFloorMap() -> None:
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


def enterFrontDesk(state: dict) -> str:
    """Starter function for the Front Desk Office."""

    clearScreen()
    state["visited"]["frontdesk"] = True
    print("🛎️  You push open the glass door of the Front Desk Office.")
    print("A staff member is hunched over a laptop behind a wide reception counter.")
    print("Behind him, a large campus floor plan is pinned to the wall.")

    # +----------------------------+
    # | Registration helper method |
    # +----------------------------+

    def handleRegister() -> None:
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

        clearScreen()
        print("The staff member looks up over his glasses.")
        print("\"Why are you walking around campus without your student ID card?\"")
        print("\"Sit down, I'll print you a new one. Type 'cancel' if you're in a hurry.\"")

        name = input("\n\"What's your name?\" > ").strip()

        if name.lower() == "cancel":
            clearScreen()
            print("\"Fine, fine. Come back when you've got a minute.\"")
            return

        # Empty input still needs a name for the card, so fall back to a default
        if not name:
            name = "Student"
        state["player_name"] = name

        # Keep asking until the player gives an 8 digit number or cancels
        while True:
            student_no = input("\"And your 8 digit student number?\" > ").strip()

            if student_no.lower() == "cancel":
                clearScreen()
                print("\"Suit yourself. The card will be waiting here.\"")
                return

            # Check length first, then that every character is a digit
            if len(student_no) != 8:
                clearScreen()
                print(f"\"That's {len(student_no)} characters. A student number is exactly 8.\"")
            elif not student_no.isnumeric():
                clearScreen()
                print("\"Digits only, please. No letters in a student number.\"")
            else:
                break

        # Registration succeeded, hand out the card and the deposit refund
        state["inventory"].append("Student ID card")
        state["student_id_obtained"] = True
        state["completed"]["frontdesk"] = True
        state["coin_balance"] += ID_CARD_REFUND

        clearScreen()
        print(f"The printer whirs. \"There you go, {name}. Don't lose this one.\"")
        print("He slides a fresh student ID card across the counter.")
        print(f"\"Oh, and here's the deposit back on your old card.\" (+{ID_CARD_REFUND} coins)")
        print("")
        print("His desk phone rings. He picks up, and his face changes.")
        print(">> \"Security? Yes, we filed the report. Something strange is going on\"")
        print(">> \"down the E-W corridor, inside the Equinox student society room.\"")
        print(">> \"Send someone over. Now.\"")
        print("")
        print("He hangs up and pretends you didn't hear any of that.")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the room and gives clues.

        This function describes the reception office, points the player at the
        wall map and the registration desk, and lists the loose items that are
        still lying on the counter. It also shows the exits and the inventory.

        Inputs: NONE

        Outputs: NONE
        """

        print("You take a look around the office.")
        print("The staff member keeps typing. A queue ticket machine blinks '000'.")
        print("A large 2nd Floor Campus Map is pinned to the wall ('read map').")

        # Only nudge the player towards registration while they still need it
        if not state["completed"]["frontdesk"]:
            print("The counter has a sign: 'Lost your ID? Register here' ('register').")
        else:
            print("Your new student ID card is already clipped to your bag.")

        if desk_items:
            print("On the corner of the counter you spot:", ", ".join(desk_items))
        else:
            print("The counter is completely clear now.")

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
        print("- look around         : Examine the reception office.")
        print("- read map            : Study the 2nd floor campus floor plan.")
        if not state["completed"]["frontdesk"]:
            print("- register            : Ask the staff member for a new student ID.")
        print("- take <item>         : Pick up something from the counter.")
        print("- go lobby / back     : Leave the office and return to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handleTake(item: str) -> None:
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

    def handleGo(destination: str) -> str:
        """
        Handles movement out of the room.

        This function checks if the player can move to the given destination from
        this room. If the destination is valid it returns the destination string,
        otherwise it prints an error message and returns None.

        Inputs:
            - destination (str): The destination the player wants to go to.

        Outputs:
            - location (str): "lobby" if valid, None otherwise.
        """

        valid_destinations = ["lobby", "back"]

        if destination in valid_destinations:
            print("You thank the staff member and step back out into the Lobby.")
            state["previous_room"] = "frontdesk"
            return "lobby"
        else:
            print(f"❌ You can't go to '{destination}' from here.")
            return None

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

        elif command == "register":
            if state["completed"]["frontdesk"]:
                clearScreen()
                print("\"You've already got your card. Stop wasting my toner.\"")
            else:
                handleRegister()

        elif command in ["read map", "look at map", "map"]:
            clearScreen()
            print("--- 2ND FLOOR CAMPUS MAP ---")
            printFloorMap()

        elif command.startswith("take "):
            clearScreen()
            item = command[5:].strip()
            handleTake(item)

        elif command.startswith("go "):
            clearScreen()
            destination = command[3:].strip()
            result = handleGo(destination)
            if result:
                return result

        elif command == "quit":
            clearScreen()
            print("👋 You sign yourself out at reception and walk home. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
