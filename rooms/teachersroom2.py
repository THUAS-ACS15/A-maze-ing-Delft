# -----------------------------------------------------------------------------
# File: teachersroom2.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Dominik
# -----------------------------------------------------------------------------

import sys
from utilities.clear_screen import clearScreen

def enterTeachersRoom2(state):
    clearScreen()
    print("You walk towards Teachers Room 2 ...")
    print("You step into Teachers Room 2.")
    print("A teacher sits at the desk, surrounded by printed tables, tapping a pen anxiously against a mug of cold coffee.")
    print("You can tell he needs help with something...")

    def handle_look():
        clearScreen()
        print("You take a look around.")
        if not state["visited"]["teachersroom2"]:
            print("The teacher glances up, clearly relieved to see someone.")
            print("\"Oh, thank goodness. I'm trying to sort out an enrollment mix-up and I've lost track of who's who.\"")
            print("\"I need to email one specific student about it, but I need your help figuring out which one it is.\"")
            print("""
Students table:
| student_id | name |
|-----------:|------|
| 1          | Mia  |
| 2          | Sam  |
| 3          | Noah |

Courses table:
| course_id | course_name   | teacher       |
|----------:|---------------|---------------|
| 10        | Databases     | Mrs. Jansen   |
| 11        | Python        | Mr. der Linde |
| 12        | Cybersecurity | Mr. Baker     |

Enrollments table:
| student_id | course_id |
|-----------:|-----------|
| 1          | 10        |
| 1          | 11        |
| 2          | 12        |
| 3          | 11        |
| 3          | 12        |
""")
            print("\"I know this student takes Python with Mr. der Linde. But I need to be sure they're NOT")
            print("also in Cybersecurity with Mr. Baker - otherwise I've got completely the wrong person.\"")
            print("\"Can you work out who it is?\"")
        else:
            print("The teacher looks much calmer now, sorting the printouts into a neat stack.")
            if "db_credentials" not in state["inventory"]:
                print("A sticky note with login credentials is still lying on the desk.")
            else:
                print("The desk is tidy now, you've already taken the credentials.")
        print("- Possible exits: lobby")
        print("- Your current inventory:", state["inventory"])

    def handle_help():
        clearScreen()
        print("Available commands:")
        print("- look around         : See what the teacher needs help with.")
        if not state["visited"]["teachersroom2"]:
            print("- answer <name>       : Tell the teacher the student's name.")
        if state["visited"]["teachersroom2"] and "db_credentials" not in state["inventory"]:
            print("- take credentials    : Pick up the login credentials once offered.")
        print("- go lobby / back     : Leave the room and return to the lobby.")
        print("- ?                   : Show this help message.")
        print("- quit                : Quit the game entirely.")

    def handle_take(item):
        if item in ["credentials", "login credentials", "db_credentials", "note", "sticky note"]:
            if not state["visited"]["teachersroom2"]:
                print("There's nothing to take yet. Maybe help the teacher first.")
            elif "db_credentials" in state["inventory"]:
                print("You already have the credentials in your backpack.")
            else:
                print("You pick up the sticky note. \"Here, take this - I don't need it anymore,\" the teacher says.")
                state["inventory"].append("db_credentials")
        else:
            print(f"There is no '{item}' here to take.")

    def handle_go(destination):
        if destination in ["lobby", "back"]:
            print("You leave the teacher to their emails and step back into the lobby.")
            return "lobby"
        else:
            print(f"You can't go to '{destination}' from here.")
            return None

    def handle_answer(answer):
        if state["visited"]["teachersroom2"]:
            print("You've already solved this challenge.")
            return
        normalized = answer.strip()
        if normalized == "mia" or normalized == "Mia":
            state["coin_balance"] += 5
            clearScreen()
            print("Correct! The teacher's face lights up: \"Mia - of course! Thank you, I would've emailed the wrong student entirely.\"")
            print("The teacher hands you the login credentials for the database on a small sticky note: \"Here you go can you please dispose of this for me so that nobody else can access this database?\"")
            print("As you take the sticky note and begin to head towards the door, you suddenly kick a small plastic bag containing some coins. You take them (+ 5 coins)")
            state["visited"]["teachersroom2"] = True
            state["completed"]["teachersroom2"] = True
        else:
            print("The teacher frowns: \"Hmm, I don't think that's right. Trace it step by step -")
            print("First find der Linde's course, then Baker's course, then check who's in one but not the other.\"")

    while True:
        command = input("\n> ").strip().lower()

        if command == "look around":
            clearScreen()
            handle_look()

        elif command == "?":
            clearScreen()
            handle_help()

        elif command.startswith("take "):
            clearScreen()
            item = command[5:].strip()
            handle_take(item)

        elif command.startswith("go "):
            clearScreen()
            destination = command[3:].strip()
            result = handle_go(destination)
            if result:
                return result

        elif command.startswith("answer "):
            clearScreen()
            answer = command[7:].strip()
            handle_answer(answer)

        elif command == "quit":
            clearScreen()
            print("You leave the teacher to their paperwork and exit the maze.")
            sys.exit()

        else:
            clearScreen()
            print("Unknown command. Type '?' to see available commands.")