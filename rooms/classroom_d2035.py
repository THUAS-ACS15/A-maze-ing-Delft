# -----------------------------------------------------------------------------
# File: classroom_d2035.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Classroom D2.035: arrange the students (seating plan), then crack the sequence (D2.015 timetable + Mainboard)."""

from rooms.project_room_1 import ask, run_room, say

# Correct seat order (seat 1 = window ... seat 4 = aisle) and the number sequence answer.
SEATING_ANSWER = ["ana", "chloe", "dev", "ben"]
SEQUENCE = [2, 6, 12, 20, 30]
SEQUENCE_ANSWER = 42


# Clue object: the lecturer's note that tells where each student sits.
def _clues(state: dict) -> None:
    say("[#ffd75f]A lecturer's note lists four students and four seats (1 = window, 4 = aisle):")
    say("[#ffd75f]  - Ana sits by the window.\n  - Ben sits at the aisle, in the last seat.")
    say("[#ffd75f]  - Chloe sits right next to Ana.\n  - Dev sits between Chloe and Ben.[/]")


def _lecturer(state: dict) -> None:
    say('[#af87ff]Lecturer: "My students never sit where they should. Arrange them, and I will hand over the seating plan."[/]')
    say('[#af87ff]"After that, finish the timetable sequence on the podium. The D2.015 lab opens with it."[/]')


# Mini game with two parts done in ONE visit: (1) seating plan, (2) next number in the sequence.
# state["d2035_progress"] remembers part 1, so a player who fails part 2 does not redo part 1.
def class_game(state: dict) -> bool:
    prog = state.setdefault("d2035_progress", {"seating": False})
    if not prog["seating"]:
        say("[bold #af87ff]PART 1: SEATING PLAN[/]")
        _clues(state)  # show the lecturer's note so the player never has to hunt for it
        for _ in range(3):
            guess = ask("Seats 1-4, names separated by spaces (e.g. ana ben chloe dev) > ").lower().split()
            if guess == SEATING_ANSWER:
                prog["seating"] = True
                state["inventory"].append("Seating plan")
                say("[bold #87ff87]Everyone is in the right seat. The lecturer hands you the Seating plan.[/]")
                say('[#af87ff]"Classroom D2.031 keeps a coded message about it. Take this plan there."[/]')
                break
            say("[#ffaf5f]The students shuffle around and nobody is happy. Check each clue against the seat numbers.[/]")
        else:
            return False
    say("[bold #af87ff]PART 2: TIMETABLE SEQUENCE[/]")
    say("[#ffd75f]Timetable slip: " + ", ".join(map(str, SEQUENCE)) + ", ?[/]")
    say("[dim]Each number follows a rule. Work out the pattern between neighbours (2 to 6 is +4, ...).[/]")
    for _ in range(3):
        if ask("Next number > ").strip() == str(SEQUENCE_ANSWER):
            say("[bold #87ff87]Correct! The podium drawer slides open.[/]")
            return True
        say("[#ffaf5f]Wrong. Look at the gaps between the numbers: 4, 6, 8, 10 ... The gap grows by 2 each time.[/]")
    return False


# Entry point. The door needs the Student ID card; the rewards are the Mainboard and the D2.015 timetable.
def enter_classroom_d2035(state: dict) -> str:
    return run_room(state, {
        "key": "classroomd2035",
        "title": "CLASSROOM D2.035",
        "emoji": "🧠",
        "color": "#af87ff",
        "intro": [
            "[#af87ff]A lecture hall with tiered seating. A lecturer is frowning at a messy seating chart.[/]",
            "[#5fd7ff]A podium stands at the front with a drawer that has a number lock.[/]",
        ],
        "lock": {"items": ["Student ID card"],
                 "text": "A card reader beside the door. Lecture halls only open for students with a valid ID.",
                 "ok": "ID accepted, you slip inside."},
        "objects": {"desks": _clues, "lecturer": _lecturer, "podium": ""},
        "game": {"name": "SEATING PLAN & TIMETABLE", "object": "podium", "play": class_game},
        "reward": ["Microcontroller / Mainboard", "D2.015 timetable"],
        "loot_text": "The drawer holds a Microcontroller / Mainboard and the D2.015 timetable.",
    })
