import time
from utilities.clear_screen import clearScreen

try:
    import utilities.status_bar as sb
    statusBar = getattr(sb, "statusBar", getattr(sb, "display_status_bar", None))
except Exception:
    statusBar = None


def showMap():
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


def showHelp():
    print("\n--- HELP MENU ---")
    print("COMMANDS:")
    print("  look around   - Inspect the front desk office")
    print("  look at map   - View the 2nd floor campus floor plan")
    print("  take <item>   - Pick up an item from the reception desk")
    print("  inventory     - Check your backpack")
    print("  go to equinox - Investigate the Equinox corridor")
    print("  go lobby      - Return through the doors into the Lobby")
    print("  quit          - Exit game\n")


def enterFrontDesk(state):
    state["current_room"] = "frontdesk"
    state["visited"]["frontdesk"] = True

    if "frontdesk_data" not in state:
        state["frontdesk_data"] = {
            "desk_items": ["pen", "visitor badge", "campus flyer"],
            "has_id_card": False,
            "onboarding_done": False
        }

    data = state["frontdesk_data"]
    desk_items = data["desk_items"]

    if not data["onboarding_done"]:
        clearScreen()
        if statusBar:
            try:
                statusBar(state)
            except Exception:
                pass

        print("=" * 64)
        print("                        FRONT DESK OFFICE                       ")
        print("=" * 64)
        print("A staff member looks up from his laptop and asks: ")
        print("'Why are you walking around without your student ID card?'\n")

        name = input("Staff asks: 'What is your name?' > ").strip()
        if not name:
            name = "Student"
        state["player_name"] = name

        while not data["has_id_card"]:
            student_no = input("Staff asks: 'Enter your 8-character student number' > ").strip()
            if len(student_no) == 8:
                print(f"\nStaff: 'Matches our records. Here is your new Student ID card, {name}!'")
                if "student id card" not in state["inventory"]:
                    state["inventory"].append("student id card")
                data["has_id_card"] = True
                state["completed"]["frontdesk"] = True
            else:
                print(f"Staff: 'That ID has {len(student_no)} characters. A valid student number must be exactly 8!'")

        print("\nThe staff member's desk phone rings. He answers:")
        print(">> 'Security? Yes, we received a report. Something strange is happening down the E-W corridor")
        print(">> inside the Equinox student society room. Send someone to check it.'")
        data["onboarding_done"] = True
        input("\nPress Enter to continue...")

    feedback = "You are at the Front Desk Office. The receptionist is typing on his laptop."

    while True:
        clearScreen()
        if statusBar:
            try:
                statusBar(state)
            except Exception:
                pass

        print("=" * 64)
        print("                        FRONT DESK OFFICE                       ")
        print("=" * 64)

        if feedback:
            print(f"\n{feedback}\n")
            feedback = ""

        cmd = input("Front Desk > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd == "help":
            showHelp()
            input("Press Enter to continue...")

        elif cmd in ["inventory", "inv"]:
            print("\nYour backpack:", state["inventory"] if state["inventory"] else "empty")
            input("\nPress Enter to continue...")

        elif cmd in ["look around", "look"]:
            print("\nThe front desk staff is typing on his laptop.")
            print("Hanging on the office wall is a large 2nd Floor Campus Map (type 'look at map').")
            if desk_items:
                print("On the corner of the reception desk you see:", ", ".join(desk_items))
            else:
                print("The reception desk surface is clear.")
            print("Exits: Door back to Lobby ('go lobby').")
            input("\nPress Enter to continue...")

        elif cmd in ["look at map", "view map", "map"]:
            print("\n--- 2ND FLOOR CAMPUS MAP ---")
            showMap()
            input("\nPress Enter to continue...")

        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if item in desk_items:
                desk_items.remove(item)
                state["inventory"].append(item)
                feedback = f"You took the {item}."
            else:
                feedback = f"'{item}' isn't on the reception desk."

        elif cmd in ["go to equinox", "equinox"]:
            clearScreen()
            print("\nYou peek down the E-W corridor toward the Equinox Student Society room...")
            print("The door is locked with police caution tape across the handle.")
            print("A security notice reads: 'Under investigation for Sprint 2. Return to Lobby.'")
            input("\nPress Enter to return to the Front Desk...")

        elif cmd in ["go lobby", "go to lobby", "leave", "exit", "lobby"]:
            clearScreen()
            print("\nYou step back out into the Lobby...")
            time.sleep(0.8)
            state["previous_room"] = "frontdesk"
            return "lobby"

        else:
            feedback = "Unknown command. Type 'help' to see what you can type."
