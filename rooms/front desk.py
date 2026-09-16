inventory = []
desk_items = ["pen", "visitor badge", "campus flyer"]
has_id_card = False

def show_map():
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

print("=== FRONT DESK OFFICE ===")
print("A staff member looks up from his laptop and ask : 'Why are you walking around without your student ID card?'\n")

name = input("Staff asks: 'What is your name?' > ").strip()

while not has_id_card:
    student_no = input("Staff asks: 'Enter your 8-character student number' > ").strip()
    if len(student_no) == 8:
        print(f"\nStaff: 'Matches our records. Here is your new Student ID card, {name}!'")
        inventory.append("student id card")
        has_id_card = True
    else:
        print(f"Staff: 'That ID has {len(student_no)} characters. A valid student number must be exactly 8!'")

print("\nThe staff member's desk phone rings. He answers:")
print(">> 'Security? Yes, we received a report. Something strange is happening down the E-W corridor")
print(">> inside the Equinox student society room. Send someone to check it.'")
print("\nType 'help' at any time to see available commands.\n")

while True:
    cmd = input("> ").strip().lower()

    if cmd == "quit":
        print("You left the front desk. Goodbye!")
        break

    elif cmd == "help":
        print("\n--- HELP MENU ---")
        print("COMMANDS:")
        print("  look around   - Inspect the front desk office")
        print("  look at map   - View the 2nd floor campus floor plan")
        print("  take <item>   - Pick up an item from the reception desk")
        print("  inventory     - Check your backpack")
        print("  go to equinox - Head down the corridor toward the Equinox room")
        print("  quit          - Exit game\n")

    elif cmd == "inventory":
        print("Your backpack:", inventory if inventory else "empty")

    elif cmd == "look around":
        print("The front desk staff is typing on his laptop.")
        print("Hanging on the office wall is a large 2nd Floor Campus Map (type 'look at map').")
        if desk_items:
            print("On the corner of the reception desk you see:", ", ".join(desk_items))
        else:
            print("The reception desk surface is clear.")

    elif cmd in ["look at map", "view map", "map"]:
        print("\n--- 2ND FLOOR CAMPUS MAP ---")
        show_map()
        print("Tip: The Equinox room is south across the E-W corridor between Teachers Room 3 and Project Room 3.")

    elif cmd.startswith("take "):
        item = cmd.replace("take ", "").strip()
        if item in desk_items:
            desk_items.remove(item)
            inventory.append(item)
            print(f"You took the {item}.")
        else:
            print("That item isn't on the desk.")

    elif cmd in ["go to equinox", "equinox"]:
        print("\nYou exit the Front Desk Office, cross into the E-W corridor, and head toward the Equinox room...")
        print("To be continued!")
        break

    else:
        print("Unknown command. Type 'help' to see what you can type.")