import time

# Screen clearing utility
try:
    from utilities.clear_screen import clear_screen
except ImportError:
    def clear_screen():
        import os
        os.system("cls" if os.name == "nt" else "clear")

# Status bar utility
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


def show_map():
    """Prints the original 2nd-floor ASCII campus map."""
    print("""
+----------------------------------- NORTH (Julianalaan) ------------------------------------+
|            |            |       | Front Desk | Classroom | Classroom | Teachers Room 4 |       |
|  LAB 2.001 |  LAB 2.003 |       |   Office   |   2.015   |   2.021   |-----------------| 2.031 |
|            |            |       +------------+-----------+-----------+ Stair |         |       |
|            |            | Lobby                                       |  exit |         |-------|
|------------+------------+       ================ E-W corridor ========+-------+         |       |
|                         |       | Teachers | T2 | T3 | Equinox | Proj | Stor- |  N-S    | 2.035 |
|                         |---|---|  Room 1  |    |    | Society | Rm 3 |  age  | corridor|       |
|                         |P1 |P2 |---------------------------------------------+---------+-------+
|                         |---|---|           Exit Passage                                    |
+-- EAST (Rotterdamseweg) --------- SOUTH (Main Stairs) ------------------- WEST (Leeghwater)-+
""")


def show_help():
    
    print("\n--- HELP MENU ---")
    print("COMMANDS:")
    print("  look around   - Inspect the front desk office")
    print("  look at map   - View the 2nd floor campus floor plan")
    print("  take <item>   - Pick up an item from the reception desk")
    print("  inventory     - Check your backpack")
    print("  go to equinox - Head down the corridor toward the Equinox room")
    print("  go lobby      - Return through the doors into the Lobby")
    print("  quit          - Exit game\n")


def front_desk(game_state):
    """
    Main loop for Front Desk Office.
    Preserves Sadanand's original receptionist interaction and student ID verification.
    """
    # 1. Update exploration progress (fixes BUG-06)
    if "rooms" in game_state and isinstance(game_state["rooms"], dict):
        game_state["rooms"]["front_desk"] = True

    # 2. Shared inventory reference
    if "inventory" not in game_state or not isinstance(game_state["inventory"], list):
        game_state["inventory"] = []
    inventory = game_state["inventory"]

    # 3. Persistent state for Front Desk
    if "front_desk_state" not in game_state:
        game_state["front_desk_state"] = {
            "desk_items": ["pen", "visitor badge", "campus flyer"],
            "has_id_card": False,
            "onboarding_done": False
        }

    desk_state = game_state["front_desk_state"]
    desk_items = desk_state["desk_items"]

    # 4. Initial student onboarding interaction (runs on first visit)
    if not desk_state["onboarding_done"]:
        clear_screen()
        if display_status_bar is not None:
            try:
                display_status_bar(game_state)
            except Exception:
                pass

        print("=" * 64)
        print("                        FRONT DESK OFFICE                       ")
        print("=" * 64)
        print("A staff member looks up from his laptop and asks: ")
        print("'Why are you walking around without your student ID card?'\n")

        
        name = game_state.get("player_name", "").strip()
        if not name or name.lower() == "student":
            name = input("Staff asks: 'What is your name?' > ").strip()
            if not name:
                name = "Student"
            game_state["player_name"] = name

        while not desk_state["has_id_card"]:
            student_no = input("Staff asks: 'Enter your 8-character student number' > ").strip()
            if len(student_no) == 8:
                print(f"\nStaff: 'Matches our records. Here is your new Student ID card, {name}!'")
                if "student id card" not in inventory:
                    inventory.append("student id card")
                desk_state["has_id_card"] = True
            else:
                print(f"Staff: 'That ID has {len(student_no)} characters. A valid student number must be exactly 8!'")

        print("\nThe staff member's desk phone rings. He answers:")
        print(">> 'Security? Yes, we received a report. Something strange is happening down the E-W corridor")
        print(">> inside the Equinox student society room. Send someone to check it.'")
        desk_state["onboarding_done"] = True
        input("\nPress Enter to continue...")

    feedback_text = "You are at the Front Desk Office. The receptionist is typing on his laptop."

    # 5. Room Command Loop
    while True:
        clear_screen()
        if display_status_bar is not None:
            try:
                display_status_bar(game_state)
            except Exception:
                pass

        print("=" * 64)
        print("                        FRONT DESK OFFICE                       ")
        print("=" * 64)

        if feedback_text:
            print(f"\n{feedback_text}\n")
            feedback_text = ""

        cmd = input("Front Desk > ").strip().lower()

        # Quit
        if cmd == "quit":
            return "quit"

        # Help
        elif cmd == "help":
            show_help()
            input("Press Enter to continue...")

        # Inventory
        elif cmd in ["inventory", "i", "inv"]:
            show_local_inventory(game_state)
            input("Press Enter to return...")

        # Look around
        elif cmd in ["look around", "look"]:
            print("\nThe front desk staff is typing on his laptop.")
            print("Hanging on the office wall is a large 2nd Floor Campus Map (type 'look at map').")
            if desk_items:
                print("On the corner of the reception desk you see:", ", ".join(desk_items))
            else:
                print("The reception desk surface is clear.")
            print("Exits: Door back to Lobby (type 'go lobby'), or head to Equinox ('go to equinox').")
            input("\nPress Enter to continue...")

        # Campus map
        elif cmd in ["look at map", "view map", "map"]:
            print("\n--- 2ND FLOOR CAMPUS MAP ---")
            show_map()
            print("Tip: The Equinox room is south across the E-W corridor between Teachers Room 3 and Project Room 3.")
            input("\nPress Enter to continue...")

        # Take items
        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if item in desk_items:
                desk_items.remove(item)
                inventory.append(item)
                feedback_text = f"You took the {item}."
            else:
                feedback_text = "That item isn't on the desk."

        # Navigation: Go to Equinox
        elif cmd in ["go to equinox", "equinox"]:
            clear_screen()
            print("\nYou exit the Front Desk Office, cross into the E-W corridor, and head toward the Equinox room...")
            time.sleep(1.2)
            return "equinox_student_society"

        # Navigation: Go back to Lobby
        elif cmd in ["go lobby", "go to lobby", "leave", "exit", "lobby"]:
            clear_screen()
            print("\nYou step back out into the Lobby...")
            time.sleep(0.8)
            return "lobby"

        else:
            feedback_text = "Unknown command. Type 'help' to see what you can type."
