# -----------------------------------------------------------------------------
# File: project_room_1.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand
# -----------------------------------------------------------------------------

import sys
from time import sleep
from utilities.animations import showActivityAnimation
from utilities.clear_screen import clearScreen

# Loose items in the pile of broken furniture in the corner.
# The brass key in here is what opens locker 2.
corner_items = ["marker", "lecture notes", "brass key"]

# The five lockers on the back wall.
#   code  : what the player has to type in, worked out from a BODMAS clue
#           hidden somewhere in the room. Locker 2 has no code, it takes the key.
#   coins : money inside, which is added straight to the coin balance
#   item  : an object that goes into the inventory, or None
# Every clue in this room maps to exactly one locker, so nothing is a dead end.
lockers = {
    "1": {"open": False, "code": 182, "coins": 50, "item": None},
    "2": {"open": False, "code": None, "coins": 0,  "item": "master keycard"},
    "3": {"open": False, "code": 24,  "coins": 20, "item": None},
    "4": {"open": False, "code": 30,  "coins": 0,  "item": None},
    "5": {"open": False, "code": 46,  "coins": 0,  "item": "equinox membership card"}
}


def enterProjectRoom1(state: dict) -> str:
    """Starter function for Project Room 1."""

    clearScreen()
    state["visited"]["projectroom1"] = True
    print("🔐 You walk into Project Room 1 and the door clicks shut behind you.")
    print("Professor Vance is at the front, capping a whiteboard marker.")
    print("\"Ah. Five lockers, five combinations, and every number you need is")
    print("somewhere in this room. Nobody takes the prize without earning it.\"")
    print("He shrugs. \"You can walk out any time, of course. Most of them do.\"")

    # Progress is stored in the state dict so it survives leaving and returning.
    if "projectroom1_progress" not in state:
        state["projectroom1_progress"] = {
            "location": "room",
            "money_found": 0
        }

    progress = state["projectroom1_progress"]

    # +-------------------------+
    # | Puzzle helper functions |
    # +-------------------------+

    def printLockerWall() -> None:
        """
        Helper function to print the state of the five lockers.

        This function draws each locker with an open or closed marker, so the
        player can see at a glance which ones they have already cracked.

        Inputs: NONE

        Outputs: NONE
        """

        print("    Back wall:")
        for number in ["1", "2", "3", "4", "5"]:
            if lockers[number]["open"]:
                print(f"    - Locker {number}: 🔓 hanging open.")
            else:
                print(f"    - Locker {number}: 🔒 shut.")

    def describeArea(location: str) -> None:
        """
        Prints the description of whichever part of the room the player is in.

        Each area of the room hides one or more of the BODMAS clues needed for
        the locker codes, so this is where the puzzle information lives.

        Inputs:
            - location (str): the area the player is standing in
              (room, board, desks or corner).

        Outputs: NONE
        """

        if location == "board":
            print("You step up to the whiteboard. Vance's handwriting is terrible.")
            print("    \"LOCKER 1:  2 + 6 * 30\"")
            print("    \"LOCKER 3:  (2 + 6) * 3\"")
            print("(Two more codes are written somewhere else in the room.)")

        elif location == "desks":
            print("You walk between the rows of wooden student desks.")
            print("Someone has carved into the side of desk #3, deep enough to feel:")
            print("    \"LOCKER 4:  50 - 5 * 4\"")

        elif location == "corner":
            print("You dig through the pile of broken desks and chairs.")
            print("There's a sticker peeling off the back of a snapped chair:")
            print("    \"LOCKER 5:  2 ** 4 + 3 * 10\"")
            if corner_items:
                print("Half buried in the pile:", ", ".join(corner_items))
            else:
                print("Nothing else worth pulling out of the pile.")

        else:
            print("You are standing in the middle of the room.")
            print("Front: Professor Vance, waiting by the whiteboard ('go to board').")
            print("Centre: rows of wooden student desks ('go to desks').")
            print("Corner: a pile of broken desks and chairs ('go to corner').")
            printLockerWall()
            print("Next to the lockers is the exit door, with a card scanner beside it.")

    # +------------------+
    # | Command handlers |
    # +------------------+

    def handleLook() -> None:
        """
        Describes the current area and gives clues.

        This function describes whichever part of the room the player has moved
        to, and always shows the exits and the player's current inventory
        underneath, the same as the other rooms in the game.

        Inputs: NONE

        Outputs: NONE
        """

        describeArea(progress["location"])
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
        print("- look around         : Examine wherever you're standing.")
        print("- go to board         : Walk up to the whiteboard.")
        print("- go to desks         : Walk between the student desks.")
        print("- go to corner        : Search the pile of broken furniture.")
        print("- go to room          : Step back to the middle of the room.")
        print("- take <item>         : Pick up something from the corner pile.")
        print("- open locker <1-5>   : Try a locker on the back wall.")
        if not state["completed"]["projectroom1"]:
            print("- swipe keycard       : Use the master keycard on the exit scanner.")
        print("- go lobby / back     : Walk out the normal way, back to the corridor.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game completely.")

    def handleTake(item: str) -> None:
        """
        Handles picking up an item from the corner pile.

        Items can only be taken from the corner, so this function first checks
        where the player is standing before checking the pile itself.

        Inputs:
            - item (str): The name of the item the player wants to take.

        Outputs: NONE
        """

        if progress["location"] != "corner":
            print("There's nothing loose to pick up here. Try the corner pile.")
        elif item in corner_items:
            corner_items.remove(item)
            state["inventory"].append(item)
            print(f"You pull the {item} out of the pile.")
        else:
            print(f"❌ There's no '{item}' in the pile.")

    def handleGo(destination: str) -> str:
        """
        Handles movement, both inside the room and out of it.

        Moving to an area inside the room updates the saved location and prints
        the new description, and returns None so the command loop carries on.
        Moving to the Lobby returns "lobby" so main.py switches rooms.

        Inputs:
            - destination (str): where the player wants to go.

        Outputs:
            - location (str): "lobby" if leaving, None otherwise.
        """

        # Areas inside the room, mapped to the phrasing the player might use
        inside_areas = {
            "to board": "board",
            "board": "board",
            "to desks": "desks",
            "desks": "desks",
            "to corner": "corner",
            "corner": "corner",
            "to room": "room",
            "room": "room"
        }

        if destination in inside_areas:
            progress["location"] = inside_areas[destination]
            describeArea(progress["location"])
            return None

        if destination in ["lobby", "back"]:
            if state["completed"]["projectroom1"]:
                print("You stroll back out into the Lobby, keycard in hand.")
            else:
                print("You push the handle and slip out into the Lobby.")
                print("Vance calls after you: \"The lockers will still be here!\"")
            state["previous_room"] = "projectroom1"
            return "lobby"

        print(f"❌ You can't go to '{destination}' from here.")
        return None

    def handleOpenLocker(number: str) -> None:
        """
        Handles opening one of the five lockers on the back wall.

        Locker 2 has a physical padlock and needs the brass key from the corner
        pile. The other four take a numeric code worked out from a BODMAS clue.
        Any money inside is added straight to the coin balance in the status bar,
        and any object inside goes into the inventory.

        Inputs:
            - number (str): the locker number the player chose, as text.

        Outputs: NONE
        """

        if number not in lockers:
            print("❌ There are only five lockers, numbered 1 to 5.")
            return

        locker = lockers[number]

        if locker["open"]:
            print(f"Locker {number} is already hanging open.")
            return

        # Locker 2 is the odd one out: a padlock, not a keypad
        if locker["code"] is None:
            if "brass key" not in state["inventory"]:
                print(f"Locker {number} has an old brass padlock on it, not a keypad.")
                print("You'd need to find the key somewhere in this room.")
                return
            print("You try the brass key from the corner pile. Click, it turns.")
        else:
            code = input(f"Enter the code for locker {number} > ").strip()

            # Reject anything that isn't a plain number before comparing
            if not code.isnumeric():
                print("The keypad only takes digits.")
                return

            if int(code) != locker["code"]:
                print("BZZT. The keypad flashes red and resets.")
                print("Check your order of operations on that clue.")
                return

            print(f"Click. The keypad goes green and locker {number} swings open.")

        locker["open"] = True

        # Pay out whatever was inside
        if locker["coins"] > 0:
            state["coin_balance"] += locker["coins"]
            progress["money_found"] += locker["coins"]
            print(f"There's cash inside. (+{locker['coins']} coins)")

        if locker["item"]:
            state["inventory"].append(locker["item"])
            print(f"You also find: {locker['item']}. (Added to your inventory)")

        if locker["coins"] == 0 and locker["item"] is None:
            print("Inside: one very old sandwich. You close the door again, quickly.")

    def handleSwipeKeycard() -> str:
        """
        Handles the real escape: swiping the master keycard on the exit scanner.

        Walking out through the normal door is always allowed, but only swiping
        the keycard counts as completing the room. This function checks for the
        keycard, marks the room complete, and returns "lobby" so main.py moves
        the player on.

        Inputs: NONE

        Outputs:
            - location (str): "lobby" on a successful escape, None otherwise.
        """

        if "master keycard" not in state["inventory"]:
            print("The scanner blinks red. You haven't got the master keycard yet.")
            print("It's locked away somewhere on that back wall.")
            return None

        showActivityAnimation("qte")
        sleep(1)
        clearScreen()

        state["completed"]["projectroom1"] = True

        print("You hold the master keycard against the scanner.")
        print("BEEP. Green light. The bolt retracts and the exit door swings wide.")
        print("")
        print("Professor Vance actually applauds, once.")
        print(f"\"{progress['money_found']} coins and my keycard. Go on, get out.\"")
        print("")
        print("Stepping back out into the Lobby...")

        state["previous_room"] = "projectroom1"
        return "lobby"

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

        elif command.startswith("open locker"):
            clearScreen()
            # Everything after "open locker" is the number, e.g. "open locker 3"
            number = command[11:].strip()
            if not number:
                number = input("Which locker (1-5)? > ").strip()
            handleOpenLocker(number)

        elif command in ["swipe keycard", "unlock door", "escape"]:
            clearScreen()
            result = handleSwipeKeycard()
            if result:
                return result

        elif command == "quit":
            clearScreen()
            print("👋 You sit down at one of Vance's desks and give up. Game over.")
            sys.exit()

        else:
            clearScreen()
            print("❓ Unknown command. Type '?' to see available commands.")
