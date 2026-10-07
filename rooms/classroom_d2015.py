# -----------------------------------------------------------------------------
# File: classroom_d2015.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
"""Classroom D2.015 (needs the D2.015 timetable): 
calibrate the rover, get the Battery Pack and the final code digits."""

import os

from rooms.project_room_1 import ask, run_room, say

# Rover calibration answers: 12 - 2*4 + 6 = 10 V and (40 + 20) / 2 = 30 kHz. FINAL_DIGITS is the story code.
CORRECT_VOLTAGE = 10  # 12 - 2 * 4 + 6
CORRECT_FREQUENCY = 30  # (40 + 20) / 2
FINAL_DIGITS = "7 3"


def _bench(state: dict) -> None:
    say("[#ffd75f]A lab notebook is open at 'BENCH SUPPLY CALCULATION':[/]")
    say('[#ffd75f]    "Set line voltage to:  12 - 2 * 4 + 6"[/]')


def _rover(state: dict) -> None:
    say("[#ffd75f]A sticker on the rover chassis reads:[/]")
    say('[#ffd75f]    "IR CARRIER FREQUENCY:  (40 + 20) / 2 kHz"[/]')


# Mini game in two stages (voltage, then IR frequency). state["d2015_progress"] keeps finished stages.
def rover_game(state: dict) -> bool:
    """Two stages: bench voltage, then IR frequency. Progress is kept in state."""
    prog = state.setdefault("d2015_progress", {"power_set": False, "rover_calibrated": False})
    if not prog["power_set"]:
        say("[#ffd75f]Notebook clue: 12 - 2 * 4 + 6[/]")
        if ask("Target voltage in volts > ").strip() != str(CORRECT_VOLTAGE):
            say("[#ffaf5f]BZZT! The bench breaker trips. Multiplication comes before subtraction.[/]")
            return False
        prog["power_set"] = True
        say(f"[bold #87ff87]⚡ The supply settles on {CORRECT_VOLTAGE}V and the track rails hum.[/]")
    if not prog["rover_calibrated"]:
        say("[#ffd75f]Chassis sticker: (40 + 20) / 2 kHz[/]")
        if ask("Carrier frequency in kHz > ").strip() != str(CORRECT_FREQUENCY):
            say("[#ffaf5f]BEEP! Rejected. Brackets first, then divide.[/]")
            return False
        prog["rover_calibrated"] = True
        say(f"[bold #87ff87]📡 The rover locks onto {CORRECT_FREQUENCY} kHz and its LED turns green.[/]")
    if not os.getenv("AMAZE_FAST"):
        from utilities.animations import show_activity_animation

        show_activity_animation("qte")
    say("[bold #87ff87]The rover races down the track and stops on the target pad. A hatch pops open.[/]")
    say(f"[bold yellow]The rover's log screen shows the FINAL CODE DIGITS: {FINAL_DIGITS}[/]")
    return True


# Entry point. The door needs the D2.015 timetable (from D2.035); the reward is the Battery Pack.
def enter_classroom_d2015(state: dict) -> str:
    return run_room(state, {
        "key": "classroomd2015",
        "title": "Classroom D2.015",
        "emoji": "🔋",
        "color": "#ffaf5f",
        "intro": [
            "[#ffaf5f]The embedded systems lab. A marked test track fills the floor"
             " and a dead robot rover sits in the middle.[/]",
            "[#5fd7ff]Leftover student project bins line the wall and a workbench hums with test equipment.[/]",
        ],
        "lock": {"items": ["D2.015 timetable"],
                 "text": "The lab is closed outside timetabled hours. You need the D2.015 timetable."
                 " (use <item> on door)",
                 "ok": "The timetable matches. The door opens."},
        "objects": {
            "bins": "[#ffd75f]Old circuit boards and wiring. Nothing useful, "
            "but a heavy battery pack sits in the rover hatch.[/]",
            "workbench": _bench, "rover": _rover, "track": "",
        },
        "game": {"name": "ROVER CALIBRATION", "object": "track", "play": rover_game},
        "reward": "High-Capacity Battery Pack",
        "loot_text": "The rover hatch holds the High-Capacity Battery Pack.",
    })
