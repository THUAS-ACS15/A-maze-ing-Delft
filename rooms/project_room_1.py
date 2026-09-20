import time

# Screen clearing utility
try:
    from utilities.clear_screen import clear_screen
except ImportError:
    def clear_screen():
        import os
        os.system("cls" if os.name == "nt" else "clear")

try:
    import utilities.status_bar as sb
    if hasattr(sb, "display_status_bar"):
        display_status_bar = sb.display_status_bar
    elif hasattr(sb, "status_bar"):
        display_status_bar = sb.status_bar
    else:
        display_status_bar = None
except ImportError:
    display_status_bar = None

# Inventory viewer utility
try:
    import utilities.inventory_viewer as iv
    if hasattr(iv, "display_inventory"):
        show_inventory = iv.display_inventory
    elif hasattr(iv, "show_inventory"):
        show_inventory = iv.show_inventory
    elif hasattr(iv, "view_inventory"):
        show_inventory = iv.view_inventory
    else:
        show_inventory = None
except ImportError:
    show_inventory = None


def show_local_inventory(game_state):
    """Displays items currently in the shared backpack."""
    inventory = game_state.get("inventory", [])
    if show_inventory is not None:
        try:
            show_inventory(inventory)
            return
        except TypeError:
            try:
                show_inventory(game_state)
                return
            except Exception:
                pass

    print("\n--- INVENTORY ---")
    if not inventory:
        print("Your backpack is currently empty.")
    else:
        for item in inventory:
            if isinstance(item, dict):
                print(f"- {item.get('name', 'Item')}: {item.get('description', '')}")
            else:
                print(f"- {item}")
    print("-----------------\n")


def display_room_header():

    print("=" * 64)
    print("           PROJECT ROOM 1 - ESCAPE PROFESSOR VANCE           ")
    print("=" * 64)


def show_help_menu():

    print("\n--- HELP MENU ---")
    print("COMMANDS:")
    print("  look around                    - Inspect where you are right now")
    print("  go to <board/desks/corner/room>- Move to a specific area to search")
    print("  take <item>                    - Pick up an item you spotted")
    print("  inventory                      - View carried items in your backpack")
    print("  open locker <1-5>              - Attempt to open a locker")
    print("  unlock door / escape           - Swipe the keycard to escape to Lobby")
    print("  quit                           - Exit the game\n")


def project_room_1(game_state):
    if "rooms" in game_state and isinstance(game_state["rooms"], dict):
        game_state["rooms"]["project_room_1"] = True

    # 2. Shared inventory reference
    if "inventory" not in game_state or not isinstance(game_state["inventory"], list):
        game_state["inventory"] = []
    inventory = game_state["inventory"]

    # 3. Persistent state for Sadanand's original room elements
    if "project_room_1_state" not in game_state:
        game_state["project_room_1_state"] = {
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

    room_state = game_state["project_room_1_state"]
    corner_items = room_state["corner_items"]
    lockers = room_state["lockers"]

    feedback_message = "Professor Vance locks the door: 'Nobody leaves without solving the lockers!'"

    # 4. Main Command Loop
    while True:
        clear_screen()
        if display_status_bar is not None:
            try:
                display_status_bar(game_state)
            except Exception:
                pass

        display_room_header()

        if feedback_message:
            print(f"\n{feedback_message}\n")
            feedback_message = ""

        location = room_state["location"]
        cmd = input(f"Project Room 1 [{location}] > ").strip().lower()

        # Quit
        if cmd == "quit":
            return "quit"

        # Help
        elif cmd == "help":
            show_help_menu()
            input("Press Enter to continue...")

        # Inventory
        elif cmd in ["inventory", "i", "inv"]:
            show_local_inventory(game_state)
            input("Press Enter to return...")

        # Movement commands
        elif cmd in ["go to board", "board"]:
            room_state["location"] = "board"
            feedback_message = "You walk to the front of the class near the whiteboard."

        elif cmd in ["go to desks", "desks"]:
            room_state["location"] = "desks"
            feedback_message = "You walk over between the student desks."

        elif cmd in ["go to corner", "corner"]:
            room_state["location"] = "corner"
            feedback_message = "You walk over to the messy corner pile."

        elif cmd in ["go to room", "room", "go back"]:
            room_state["location"] = "room"
            feedback_message = "You return to the center of the classroom facing the 5 lockers."

        # Look around based on exact location
        elif cmd in ["look around", "look"]:
            print()
            if location == "room":
                print("Front: Prof Vance standing by the whiteboard.")
                print("Center: Rows of wooden student desks.")
                print("Back wall: 5 metal lockers (1 to 5) and the locked exit door.")
                print("Corner: A messy pile of broken desks and chairs.")
                print("(Move closer to an area with 'go to <board/desks/corner>' to inspect it!)")

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

        # Picking up items
        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if location != "corner":
                feedback_message = "There are no loose items to pick up here. Try checking the corner!"
            elif item in corner_items:
                corner_items.remove(item)
                inventory.append(item)
                feedback_message = f"You picked up: {item}"
            else:
                feedback_message = "That item isn't here!"

        # Opening lockers
        elif cmd.startswith("open locker ") or cmd.startswith("unlock locker "):
            num = cmd.split()[-1]
            if num not in lockers:
                feedback_message = "Choose a valid locker from 1 to 5."
                continue

            lock = lockers[num]
            if lock["open"]:
                feedback_message = f"Locker {num} is already wide open."
                continue

            if num == "2":
                if "key" in inventory:
                    lock["open"] = True
                    item_found = lock["item"]
                    inventory.append(item_found)
                    feedback_message = (
                        f"You insert the brass key from the corner. Click! Locker 2 opens!\n"
                        f"Inside you found: {item_found}! (Added to inventory)"
                    )
                else:
                    feedback_message = "Locker 2 has a physical padlock. You need to find a key in the room!"
            else:
                code = input(f"Enter code for Locker {num}: ").strip()
                if code == lock["code"]:
                    lock["open"] = True
                    if lock["item"]:
                        item_found = lock["item"]
                        inventory.append(item_found)
                        if item_found == "50 euro":
                            game_state["coins"] = game_state.get("coins", 0) + 50
                        feedback_message = (
                            f"Click! Locker {num} unlocks!\n"
                            f"Jackpot! You found: {item_found}! (Added to inventory and coins)"
                        )
                    else:
                        feedback_message = f"Click! Locker {num} unlocks! It's completely empty... just old dust."
                else:
                    feedback_message = "Wrong code! Buzzer sounds: BZZT."

        # Door escape & navigation back to Lobby
        elif cmd in ["unlock door", "open door", "escape", "go lobby", "exit", "door", "leave"]:
            if room_state["door_unlocked"] or "master keycard" in inventory:
                room_state["door_unlocked"] = True
                clear_screen()
                print("\nYou swipe the master keycard on the door scanner...")
                print("BEEP! Green light! The exit door clicks open!")
                money = inventory.count("50 euro") * 50
                print(f"You escaped Prof Vance's room with €{money} in your pocket!")
                print("Stepping back into the Lobby...")
                time.sleep(1.5)
                return "lobby"
            else:
                feedback_message = "The exit door requires a master keycard. Keep cracking lockers!"

        else:
            feedback_message = f"Unknown command: '{cmd}'. Type 'help' to see available actions."
