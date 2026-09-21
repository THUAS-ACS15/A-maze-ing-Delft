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
    print("  look around               - Inspect your surroundings")
    print("  go to <podium/desks/room> - Move across the lecture hall")
    print("  inspect board             - Read the cipher poem on the chalkboard")
    print("  talk to professor         - Speak with the literature lecturer")
    print("  solve / answer <word>     - Submit the decoded acrostic word")
    print("  take <item>               - Pick up an item from the desks")
    print("  inventory                 - View your carried items")
    print("  go lobby                  - Return to the Lobby")
    print("  quit                      - Exit the game\n")


def enterClassroomD2035(state):
    state["current_room"] = "classroomd2035"
    state["visited"]["classroomd2035"] = True

    if "classroomd2035_data" not in state:
        state["classroomd2035_data"] = {
            "location": "room",
            "desk_items": ["leather bookmark", "quill pen"],
            "riddle_solved": False
        }

    data = state["classroomd2035_data"]
    desk_items = data["desk_items"]

    feedback = "You step into Classroom D2.035. An English Literature lecture is in session."

    while True:
        clearScreen()

        if statusBar:
            try:
                statusBar(state)
            except Exception:
                pass

        print("=" * 64)
        print("          CLASSROOM D2.035: ENGLISH LITERATURE & CIPHERS      ")
        print("=" * 64)

        if feedback:
            print(f"\n{feedback}\n")
            feedback = ""

        location = data["location"]
        cmd = input(f"D2.035 [{location}] > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd == "help":
            showHelp()
            input("Press Enter to continue...")

        elif cmd in ["inventory", "inv"]:
            print("\nYour backpack:", state["inventory"] if state["inventory"] else "empty")
            print(f"Current coin balance: €{state.get('coin_balance', 0)}")
            input("\nPress Enter to continue...")

        elif cmd in ["go to podium", "podium"]:
            data["location"] = "podium"
            feedback = "You walk down toward the lecturer's podium near the chalkboard."

        elif cmd in ["go to desks", "desks"]:
            data["location"] = "desks"
            feedback = "You walk between rows of lecture desks."

        elif cmd in ["go to room", "room", "go back"]:
            data["location"] = "room"
            feedback = "You return to the center of the lecture hall."

        elif cmd in ["look around", "look"]:
            print()
            if location == "room":
                print("Tiered wooden seating rises toward the back of the lecture hall.")
                print("Front: A large chalkboard covered in chalk writing ('go to podium').")
                print("Middle: Student desks with books and papers ('go to desks').")
                print("Exits: Door leading to the Lobby ('go lobby').")

            elif location == "podium":
                print("The lecturer stands here analyzing Elizabethan cryptograms.")
                print("On the chalkboard is a poem titled 'THE FORBIDDEN UNION' ('inspect board').")

            elif location == "desks":
                print("The desks hold open copies of Shakespeare and cryptography notebooks.")
                if desk_items:
                    print("Items left on the front desk:", ", ".join(desk_items))
                else:
                    print("The desks have no more loose items.")
            input("\nPress Enter to continue...")

        elif cmd in ["inspect board", "read board", "board"]:
            print("\n+-------------------------------------------------------------+")
            print("|                THE FORBIDDEN UNION (ACROSTIC)               |")
            print("|                                                             |")
            print("|  [E]ntwined in silence, old secrets reside,                 |")
            print("|  [Q]uietly buried where shadows divide.                     |")
            print("|  [U]nder cold stone, where lost scholars speak,             |")
            print("|  [I]nsight remains for the daring who seek.                 |")
            print("|  [N]ight brings the hour of balance and sight,              |")
            print("|  [O]ver the halls where day equals night.                   |")
            print("|  [X] marks the society hidden from light.                   |")
            print("|                                                             |")
            print("|  Prompt: What 7-letter word is spelled by the first letters?|")
            print("+-------------------------------------------------------------+")
            if data["riddle_solved"]:
                print("Status: Solved (Answer: EQUINOX).")
            else:
                print("Type 'solve' or 'answer <word>' to submit your answer.")
            input("\nPress Enter to continue...")

        elif cmd in ["talk to professor", "talk professor", "professor", "lecturer"]:
            if not data["riddle_solved"]:
                feedback = (
                    "Lecturer: 'Fascinating stanza, isn't it? A student from the East Wing slipped "
                    "it onto my board this morning. Solve the first-letter acrostic if you can!'"
                )
            else:
                feedback = (
                    "Lecturer: 'Splendid work deciphering EQUINOX earlier! Take care with that note—"
                    "strange rumors surround that student society.'"
                )

        elif cmd == "solve" or cmd.startswith("answer"):
            if data["riddle_solved"]:
                feedback = "You have already deciphered the chalkboard poem."
            else:
                if cmd == "solve":
                    guess = input("Enter the decoded word: ").strip().lower()
                else:
                    parts = cmd.split(maxsplit=1)
                    guess = parts[1].strip().lower() if len(parts) > 1 else ""

                if guess == "equinox":
                    data["riddle_solved"] = True
                    state["completed"]["classroomd2035"] = True
                    state["coin_balance"] = state.get("coin_balance", 0) + 30
                    if "equinox cipher note" not in state["inventory"]:
                        state["inventory"].append("equinox cipher note")

                    feedback = (
                        "CORRECT: EQUINOX!\n"
                        "Lecturer: 'Brilliant deduction! Here is an Equinox Cipher Note left behind "
                        "and €30 for your keen scholarship!'"
                    )
                else:
                    feedback = f"'{guess}' is incorrect. Look at the capital letters starting each line."

        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if location != "desks":
                feedback = "There are no loose items here. Try looking around the desks!"
            elif item in desk_items:
                desk_items.remove(item)
                state["inventory"].append(item)
                feedback = f"You took the {item}."
            else:
                feedback = f"'{item}' is not on the desks."

        elif cmd in ["go lobby", "go to lobby", "leave", "exit", "lobby"]:
            clearScreen()
            print("\nYou leave Classroom D2.035 and return to the Lobby...")
            time.sleep(0.8)
            state["previous_room"] = "classroomd2035"
            return "lobby"

        else:
            feedback = f"Unknown command: '{cmd}'. Type 'help' to see what you can do."
