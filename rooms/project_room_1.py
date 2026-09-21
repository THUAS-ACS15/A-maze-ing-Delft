import time
from utilities.clear_screen import clearScreen

try:
    import utilities.status_bar as sb
    statusBar = getattr(sb, "statusBar", getattr(sb, "display_status_bar", None))
except Exception:
    statusBar = None


def showHelp():
    print("\n--- HELP MENU ---")
    print("COMMANDS:")
    print("  look around                    - Inspect where you are right now")
    print("  go to <board/desks/corner/room>- Move to a specific area to search")
    print("  take <item>                    - Pick up an item you spotted")
    print("  inventory                      - View carried items in your backpack")
    print("  open locker <1-5>              - Attempt to unlock a locker")
    print("  unlock door / escape           - Swipe master keycard to escape to Lobby")
    print("  go lobby                       - Try to exit through the door")
    print("  quit                           - Exit the game\n")


def enterProjectRoom1(state):
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

    feedback = "Professor Vance locks the door: 'Nobody leaves without solving the lockers!'"

    while True:
        clearScreen()

        if statusBar:
            try:
                statusBar(state)
            except Exception:
                pass

        print("=" * 64)
        print("           PROJECT ROOM 1 - ESCAPE PROFESSOR VANCE           ")
        print("=" * 64)

        if feedback:
            print(f"\n{feedback}\n")
            feedback = ""

        location = data["location"]
        cmd = input(f"Project Room 1 [{location}] > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd == "help":
            showHelp()
            input("Press Enter to continue...")

        elif cmd in ["inventory", "inv", "backpack"]:
            print("\nYour backpack:", state["inventory"] if state["inventory"] else "empty")
            print(f"Current coin balance: €{state.get('coin_balance', 0)}")
            input("\nPress Enter to continue...")

        elif cmd in ["go to board", "board"]:
            data["location"] = "board"
            feedback = "You walk to the front of the class near the whiteboard."

        elif cmd in ["go to desks", "desks"]:
            data["location"] = "desks"
            feedback = "You walk over between the student desks."

        elif cmd in ["go to corner", "corner"]:
            data["location"] = "corner"
            feedback = "You walk over to the messy corner pile."

        elif cmd in ["go to room", "room", "go back"]:
            data["location"] = "room"
            feedback = "You return to the center of the classroom facing the 5 lockers."

        elif cmd in ["look around", "look"]:
            print()
            if location == "room":
                print("Front: Prof Vance standing by the whiteboard.")
                print("Center: Rows of wooden student desks.")
                print("Back wall: 5 metal lockers (1 to 5) and the locked exit door.")
                print("Corner: A messy pile of broken desks and chairs.")
                print("(Move closer with 'go to board', 'go to desks', or 'go to corner')")

            elif location == "board":
                print("You look closely at the whiteboard:")
                print("  Main Challenge: Box A: 2+6*30 | Box B: (2+6)*3 | Box C: 36/6+2")
                print("  Bonus scratch in bottom corner: '(10 + 10) / 2'")

            elif location == "desks":
                print("You check the desks. Carved into the side of desk #3 you spot: '50 - 5 * 4'.")

            elif location == "corner":
                print("You dig into the pile. On the chair you spot a sticker: '2^4 + 3 * 10'.")
                if corner_items:
                    print("Lying around in the pile:", ", ".join(corner_items))
                else:
                    print("No more loose items left in the pile.")
            input("\nPress Enter to continue...")

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
                        f"You insert the brass key from the corner. Click! Locker 2 opens!\n"
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

        elif cmd in ["unlock door", "open door", "escape", "go lobby", "exit", "door", "leave"]:
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
                feedback = "The exit door is locked. Prof Vance: 'Nobody leaves without solving the lockers!'"

        else:
            feedback = f"Unknown command: '{cmd}'. Type 'help' to see what you can do."
