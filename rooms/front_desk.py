# -----------------------------------------------------------------------------
# File: front_desk.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Front Desk: register for a Student ID card, read the guard's logbook, and hear about the Equinox mystery."""

from rooms.project_room_1 import ask, run_room, say

FLOOR_MAP = """[cyan]
    
+--------------------------- NORTH (Julianalaan) ----------------------------+
|            |            |       | Front Desk | Classroom | Classroom |     |
|  LAB 2.001 |  LAB 2.003 |       |   Office   |   2.015   |   2.021   | T4  |
|            |            |       +------------+-----------+-----------+-----|
|            |            | Lobby        === E-W corridor ===          |     |
|------------+------------+       +------------------------------------+-----|
|                         |       | Teachers | T2 | Equinox | Proj | N-S |   |
|                         |--|--| |  Room 1  |    | Society | Rm 3 | cor.|2.035|
|                         |P1|P2| +-----------------------------------+-----|
|                         |--|--|            Exit Passage                    |
+-- EAST (Rotterdamseweg) ------- SOUTH (Main Stairs) ---- WEST (Leeghwater) -+
"""

# The logbook only sets the mood. It does not say which room holds which part, the player has to explore.
LOGBOOK = (
    "[bold #ffd75f]📖 Night guard's logbook:[/] 'The professor left PROJECT A.I.G.I.S. unfinished. "
    "Doors lock themselves after hours.'\n"
    "  [dim]'Every room wants something from another room. Talk to people, read the boards, trust no lock.'[/]"
)


# Mini game: type a name and an 8-digit student number to print the Student ID card (needed for D2.035).
def register(state: dict) -> bool:
    """Easy quest: type a name and an 8-digit student number to print an ID card."""
    say("[#5fd7ff]The staff member looks up over his glasses. \"Why are you walking around without your ID card?\"")
    say("[#5fd7ff]\"Sit down, I'll print you a new one.\" (type 'cancel' to walk away)[/]")
    name = ask("\"What's your name?\" > ").strip()
    if name.lower() == "cancel":
        say("[#ffaf5f]\"Fine, fine. Come back when you've got a minute.\"[/]")
        return False
    state["player_name"] = name or "Student"
    while True:
        number = ask("\"And your 8-digit student number?\" > ").strip()
        if number.lower() == "cancel":
            say("[#ffaf5f]\"Suit yourself. The card will be waiting here.\"[/]")
            return False
        if len(number) != 8:
            say(f"[#ffaf5f]\"That's {len(number)} characters. A student number is exactly 8 digits long.\"[/]")
        elif not number.isnumeric():
            say("[#ffaf5f]\"Digits only, please. No letters in a student number.\"[/]")
        else:
            break
    state["student_id_obtained"] = True
    say(f"[bold #87ff87]🖨️  The printer whirs. \"There you go, {state['player_name']}. Don't lose this one.\"[/]")
    say("[#af87ff]He taps the lobby terminal: 'PROJECT A.I.G.I.S. ASSEMBLY REQUIRED'. "
        "\"The professor left it unfinished.")
    say("[#af87ff]Collect every part on this floor and assemble it in Lab D2.001. Doors are locked"
        " after hours, so every room needs something.\"[/]")
    say("[#5fd7ff]\"Your ID opens the Student Society, by the way. Good luck.\"[/]")
    return True


# Entry point called by the dispatcher. Hands this room's description to run_room().
def enter_front_desk(state: dict) -> str:
    cfg = {
        "key": "frontdesk",
        "title": "FRONT DESK OFFICE",
        "emoji": "🛎️",
        "color": "#5fd7ff",
        "intro": [
            "[#ffd75f]A staff member is hunched over a laptop behind a wide reception counter.[/]",
            "[#af87ff]A campus map is pinned to the wall and an old logbook lies open.[/]",
        ],
        "objects": {
            "counter": "[#87ff87]A sign: 'Lost your ID? Register here.' Inspect [bold]printer[/]"
             " to get a new Student ID card.[/]",
            "printer": "",
            "logbook": LOGBOOK,
            "map": FLOOR_MAP,
        },
        # The printer is the puzzle; solving it puts the Student ID card in the printer tray.
        "reenter": True,  # the Front Desk can be visited any time; only the printer says "already done"
        "game": {"name": "STUDENT ID PRINTER", "object": "printer", "play": register},
        "reward": "Student ID card",
        "loot_text": "Your new Student ID card is waiting in the printer tray.",
    }
    return run_room(state, cfg)
