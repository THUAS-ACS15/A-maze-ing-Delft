inventory = []
location = "room"
corner_items = ["pen", "marker", "notes", "key"]

# Locker database: status, code, and contents
lockers = {
    "1": {"open": False, "code": "182", "item": "50 euro"},
    "2": {"open": False, "code": "key", "item": "master keycard"},
    "3": {"open": False, "code": "30",  "item": None},
    "4": {"open": False, "code": "46",  "item": "50 euro"},
    "5": {"open": False, "code": "10",  "item": None}
}

print("=== ESCAPE THE CLASSROOM ===")
print("Professor Vance locks the door: 'Nobody leaves without solving the lockers!'")
print("Type 'help' at any time to see your commands.\n")

while True:
    cmd = input("> ").strip().lower()

    if cmd == "quit":
        print("You gave up. Game over!")
        break

    elif cmd == "help":
        print("\n--- HELP MENU ---")
        print("COMMANDS:")
        print("  look around               - Inspect where you are right now")
        print("  go to <board/desks/corner/room> - Move to a specific area to search")
        print("  take <item>               - Pick up an item you spotted")
        print("  inventory                 - View carried items")
        print("  open locker <1-5>         - Attempt to open a locker")
        print("  unlock door               - Swipe the keycard to escape\n")

    elif cmd == "inventory":
        print("Your backpack:", inventory if inventory else "empty")

    # Movement commands
    elif cmd in ["go to board", "board"]:
        location = "board"
        print("You walk to the front of the class near the whiteboard. Type 'look around'.")

    elif cmd in ["go to desks", "desks"]:
        location = "desks"
        print("You walk over between the student desks. Type 'look around'.")

    elif cmd in ["go to corner", "corner"]:
        location = "corner"
        print("You walk over to the messy corner pile. Type 'look around'.")

    elif cmd in ["go to room", "room", "go back"]:
        location = "room"
        print("You return to the center of the classroom facing the 5 lockers.")

    # Look around based on exact location
    elif cmd == "look around":
        if location == "room":
            print("Front: Prof Vance standing by the whiteboard.")
            print("Center: Rows of wooden student desks.")
            print("Back wall: 5 metal lockers (1 to 5) and the locked exit door.")
            print("Corner: A messy pile of broken desks and chairs.")
            print("(Move closer to an area with 'go to <place>' to inspect it!)")

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

    # Picking up items
    elif cmd.startswith("take "):
        item = cmd.replace("take ", "").strip()
        if location != "corner":
            print("There are no loose items to pick up here.")
        elif item in corner_items:
            corner_items.remove(item)
            inventory.append(item)
            print(f"You picked up: {item}")
        else:
            print("That item isn't here!")

    # Opening lockers
    elif cmd.startswith("open locker ") or cmd.startswith("unlock locker "):
        num = cmd.split()[-1]
        if num not in lockers:
            print("Choose a valid locker from 1 to 5.")
            continue

        lock = lockers[num]
        if lock["open"]:
            print(f"Locker {num} is already wide open.")
            continue

        if num == "2":
            if "key" in inventory:
                lock["open"] = True
                print("You insert the brass key from the corner. Click! Locker 2 opens!")
                print(f"Inside you found: {lock['item']}! (Added to inventory)")
                inventory.append(lock["item"])
            else:
                print("Locker 2 has a physical padlock. You need to find a key!")
        else:
            code = input(f"Enter code for Locker {num}: ").strip()
            if code == lock["code"]:
                lock["open"] = True
                print(f"Click! Locker {num} unlocks!")
                if lock["item"]:
                    print(f"Jackpot! You found: {lock['item']}! (Added to inventory)")
                    inventory.append(lock["item"])
                else:
                    print("It's completely empty... just old dust.")
            else:
                print("Wrong code! Buzzer sounds: BZZT.")

    # Door escape
    elif cmd in ["unlock door", "open door", "escape"]:
        if "master keycard" in inventory:
            print("\nYou swipe the master keycard on the door scanner...")
            print("BEEP! Green light! The exit door clicks open!")
            money = inventory.count("50 euro") * 50
            print(f"You escaped Prof Vance's room with €{money} in your pocket! You win!")
            break
        else:
            print("The exit door requires a master keycard. Keep cracking lockers!")

    else:
        print("Unknown command. Type 'help' to see what you can do.")