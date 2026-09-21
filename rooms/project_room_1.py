# -----------------------------------------------------------------------------
# File: project_room_1.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Sadanand
# -----------------------------------------------------------------------------

import time
from utilities.clear_screen import clearScreen


def showHelp() -> str:
    """
    Builds the help menu text.

    Returns the text instead of printing it, so the caller can show it
    through the feedback panel and it stays on screen after the redraw.

    Inputs: NONE

    Outputs:
        - str: the formatted help menu.
    """
    return (
        "--- HELP MENU ---\n"
        "  look around                     - Inspect where you are right now\n"
        "  go to <board/desks/corner/room> - Move to a specific area to search\n"
        "  take <item>                     - Pick up an item you spotted\n"
        "  inventory                       - View carried items in your backpack\n"
        "  open locker <1-5>               - Attempt to unlock a locker\n"
        "  unlock door / escape            - Swipe the master keycard for the full escape\n"
        "  go lobby / back / leave         - Walk out and return to the Lobby\n"
        "  quit                            - Exit the game"
    )


def describe(location: str, data: dict) -> str:
    """
    Builds the description of the area the player is standing in.

    Returns the text instead of printing it, so it can be passed back as
    feedback and survive the next clearScreen() call.

    Inputs:
        - location (str): the area the player is in (room/board/desks/corner).
        - data (dict): this room's saved data from the game state.

    Outputs:
        - str: the description of that area.
    """
    corner_items = data["corner_items"]

    if location == "board":
        return (
            "You look closely at the whiteboard:\n"
            "  Main Challenge: Box A: 2+6*30 | Box B: (2+6)*3 | Box C: 36/6+2\n"
            "  Bonus scratch in the bottom corner: '(10 + 10) / 2'"
        )

    if location == "desks":
        return "You check the desks. Carved into the side of desk #3 you spot: '50 - 5 * 4'."

    if location == "corner":
        text = "You dig into the pile. On the chair you spot a sticker: '2^4 + 3 * 10'."
        if corner_items:
            text += "\nLying around in the pile: " + ", ".join(corner_items)
        else:
            text += "\nNo more loose items left in the pile."
        return text

    return (
        "Front: Prof Vance standing by the whiteboard.\n"
        "Center: Rows of wooden student desks.\n"
        "Back wall: 5 metal lockers (1 to 5) and the exit door.\n"
        "Corner: A messy pile of broken desks and chairs.\n"
        "(Move closer with 'go to board', 'go to desks' or 'go to corner')\n"
        "Exits: the door back to the Lobby ('go lobby')."
    )


def enterProjectRoom1(state: dict) -> str:
    """Starter function for Project Room 1."""

    state["current_room"] = "projectroom1"
    state["visited"]["projectroom1"] = True

    if "projectroom1_data" not in state:
        state["projectroom1_data"] = {
            "location": "room",
            "corner_items": ["pen", "marker", "notes", "key"],
            "lockers": {
                "1": {"open": False, "code": "182", "item": "50 euro"},
                "2": {"open": False, "code": "key", "item": "master keycard"},
                "3": {"open": False, "code": "30",  "item": None},
                "4": {"open": False, "code": "46",  "item": "50 euro"},
                "5": {"open": False, "code": "10",  "item": None}
            },
            "door_unlocked": False
        }

    data = state["projectroom1_data"]
    lockers = data["lockers"]
    corner_items = data["corner_items"]

    feedback = (
        "Professor Vance glances up from his desk: 'Nobody gets the prize without solving "
        "the lockers. You may leave whenever you like, though.'\n"
        "Type 'help' for the list of commands."
    )

    while True:
        clearScreen()

        print("=" * 64)
        print("           PROJECT ROOM 1 - ESCAPE PROFESSOR VANCE           ")
        print("=" * 64)

        location = data["location"]
        print(f"\nYou are at: {location}")

        if feedback:
            print(f"\n{feedback}\n")
            feedback = ""

        cmd = input(f"Project Room 1 [{location}] > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd in ["help", "?"]:
            feedback = showHelp()

        elif cmd in ["inventory", "inv", "backpack"]:
            carried = ", ".join(state["inventory"]) if state["inventory"] else "empty"
            feedback = (
                f"Your backpack: {carried}\n"
                f"Current coin balance: €{state.get('coin_balance', 0)}"
            )

        elif cmd in ["go to board", "board"]:
            data["location"] = "board"
            feedback = "You walk to the front of the class near the whiteboard.\n\n" + describe("board", data)

        elif cmd in ["go to desks", "desks"]:
            data["location"] = "desks"
            feedback = "You walk over between the student desks.\n\n" + describe("desks", data)

        elif cmd in ["go to corner", "corner"]:
            data["location"] = "corner"
            feedback = "You walk over to the messy corner pile.\n\n" + describe("corner", data)

        elif cmd in ["go to room", "room", "go back", "back to room"]:
            data["location"] = "room"
            feedback = "You return to the centre of the classroom facing the 5 lockers.\n\n" + describe("room", data)

        elif cmd in ["look around", "look"]:
            feedback = describe(location, data)

        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if location != "corner":
                feedback = "There are no loose items to pick up here. Try searching the corner pile!"
            elif item in corner_items:
                corner_items.remove(item)
                state["inventory"].append(item)
                feedback = f"You picked up: {item}"
            else:
                feedback = f"'{item}' isn't in the corner pile."

        elif cmd.startswith("open locker") or cmd.startswith("unlock locker"):
            parts = cmd.split()
            if len(parts) >= 3 and parts[-1].isdigit():
                num = parts[-1]
            else:
                num = input("Which locker do you want to open (1-5)? > ").strip()

            if num not in lockers:
                feedback = "Invalid locker number. Choose a locker from 1 to 5."
                continue

            lock = lockers[num]
            if lock["open"]:
                feedback = f"Locker {num} is already wide open."
                continue

            if num == "2":
                if "key" in state["inventory"]:
                    lock["open"] = True
                    found_item = lock["item"]
                    state["inventory"].append(found_item)
                    feedback = (
                        "You insert the brass key from the corner. Click! Locker 2 opens!\n"
                        f"Inside you found: {found_item}! (Added to inventory)"
                    )
                else:
                    feedback = "Locker 2 has a physical padlock. You need to find a key in the room!"
            else:
                code = input(f"Enter code for Locker {num}: ").strip()
                if code == lock["code"]:
                    lock["open"] = True
                    if lock["item"]:
                        found_item = lock["item"]
                        state["inventory"].append(found_item)
                        if found_item == "50 euro":
                            state["coin_balance"] = state.get("coin_balance", 0) + 50
                        feedback = (
                            f"Click! Locker {num} unlocks!\n"
                            f"Jackpot! You found: {found_item}! (Added to backpack and balance)"
                        )
                    else:
                        feedback = f"Click! Locker {num} unlocks! It's completely empty... just old dust."
                else:
                    feedback = "Wrong code! Buzzer sounds: BZZT."

        # --- The full escape: only this wins the room ---
        elif cmd in ["unlock door", "open door", "escape", "swipe keycard"]:
            if data["door_unlocked"] or "master keycard" in state["inventory"]:
                data["door_unlocked"] = True
                state["completed"]["projectroom1"] = True
                clearScreen()
                print("\nYou swipe the master keycard on the door scanner...")
                print("BEEP! Green light! The exit door clicks open!")
                money = state["inventory"].count("50 euro") * 50
                print(f"You escaped Prof Vance's room with €{money} from the lockers!")
                print("Stepping back out into the Lobby...")
                time.sleep(1.5)
                state["previous_room"] = "projectroom1"
                return "lobby"
            else:
                feedback = (
                    "The keycard scanner blinks red. You don't have the master keycard yet.\n"
                    "(You can still walk out the normal way with 'go lobby' and come back later.)"
                )

        # --- Plain exit: always works, matches the other rooms ---
        elif cmd in ["go lobby", "go to lobby", "lobby", "leave", "exit", "back", "go back to lobby", "out"]:
            clearScreen()
            if state["completed"]["projectroom1"]:
                print("\nYou stroll back out into the Lobby.")
            else:
                print("\nYou push the door handle and slip out into the Lobby.")
                print("Prof Vance calls after you: 'The lockers will still be here!'")
            time.sleep(1.0)
            state["previous_room"] = "projectroom1"
            return "lobby"

        else:
            feedback = f"Unknown command: '{cmd}'. Type 'help' to see what you can do."
