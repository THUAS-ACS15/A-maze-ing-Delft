# -----------------------------------------------------------------------------
# File: story_dialogue_bank.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

# ruff: noqa: E501
# ^ disable ruff checking long lines, as this is dialogue

# story_dialogue_bank is a dictionary that contains all the story-related dialogue and text for the game.
# "story_important_flags" contains important story flags and their associated text.
# "rooms" contains the dialogue and text for each room in the game, including headers, descriptions, and any other extra dialogue.

# updated so far with dialogue func: lobby, teachersroom1, teachersroom2, teachersroom4, projectroom2
# TODO: TO UPDATE AFTER REFACTOR: front desk, classrooms d2015, d2031, d2035, teachersroom4 (partially)

# the rooms are ordered based on their story appearance
story_dialogue_bank: dict = {
    "story_important_flags": {
        "intro": """You are a student locked in the THUAS Delft building.
You don't remember how you got here, but you need to find a way out.
The main exit is blocked by a 4-digit combination lock.
A blinking message on a terminal in the lobby reveals an unfinished robotics project: 'Project A.I.G.I.S.'.
If you can gather the missing hardware across the school and assemble it, its LLM core might know the exit code."""
    },

    "rooms": {
        "lobby": {
            "header": "🚶 You are standing in the school's main lobby.",
            "enter": "You see a long corridor with many doors and glass walls on both sides. There are lots of doors waiting to be explored.",
            "no_student_id": "You notice you're missing your student ID. You should check out the Front Desk to see if you can obtain one.",
            "quit": "👋 You leave the school and the adventure comes to an end."
        },
        "frontdesk": {
            "header": "🛎️ You step into the Front Desk office.",
            "enter": "A staff member is hunched over a laptop behind a wide reception counter.",
            "no_student_id": "You can probably ask to register for a new ID card here.",
            "after_register": (
                "The staff member hands you a newly printed, shiny ID card. "
                "You take this opportunity to ask why the school doors are locked. They "
                "tell you that they don't know much, but you could learn more by asking one of the "
                "teachers. You can find some of their rooms on the E-W corridor."
            ),
            "quit": "👋 You leave the front desk and do something else."
        },
        "teachersroom1": {
            "header": "👩 You step into Teacher's Room 1.",
            "enter": (
                "A teacher is sitting at a laptop, muttering under their breath at the screen. "
                "Sticky notes covered in function names are scattered across the desk."
            ),
            "puzzle_not_complete": (
                "The teacher looks up: \"Oh, perfect timing. I\'m missing one last piece of this code. "
                "I need to check whether a number n is even in Python. What is the expression I "
                "should use to check that?\""
            ),
            "puzzle_answer_correct": (
                "The teacher's eyes light up: \"n % 2 — of course! Thank you!\"",
                "The teacher points to a keycard on the table and tells you take it, as a reward for your help."
            ),
            "puzzle_answer_incorrect": "The teacher shakes their head: \"Not quite.\"",
            "puzzle_already_complete": "The teacher grins: \"That fix worked perfectly, thanks again!\"",
            "puzzle_take_keycard": (
                "You pick up the keycard. It looks to be a staff keycard, which will"
                "After taking it, you notice something shiny in the corner of your eye. "
                "You look closer and realize you found some shiny coins, and the teacher "
                "allows you to take them (+10 coins). "
                "The teacher also asks you to check out the second teacher's room, as they might have "
                "another piece of the code you need to complete A.I.G.I.S."
            ),
            "quit": "👋 You leave the teacher alone and go somewhere else."
        },
        "teachersroom2": {
            "header": "👨 You swipe the Staff Keycard and step into Teacher's Room 2.",
            "enter": (
                "A teacher is sitting at a desk, surrounded by printed tables, walking and "
                "stressing about something."
            ),
            "talk_to_teacher": (
                "The teacher seems to stop pacing and replies to your greeting: "
                "\"Oh, hey there! I'm Wesley. I'm trying to sort out an enrollment mix-up and "
                "I've lost track of who's who. I need to email one specific student about it, "
                "but can't fire out out which one it is. I suppose I'll have to ask for your help. "
                "Could you look at these databases and see if you notice someone that is doing the "
                "Python course, but not the Cybersecurity one?\""
            ),
            "puzzle_answer_correct": (
                "Wesley looks up from the tables and says: \"Oh, thank goodness. I was worried "
                "I wouldn't be able to get this email out in time. Thank you for your help!\" "
                "He looks through his desk and places a sticky note with Wi-Fi credentials on the desk "
                ", telling you to take it. It seems to contain the login information you'll "
                "need to connect to the school's intranet."
            ),
            "puzzle_answer_incorrect": "The teacher frowns: \"Hmm, I don't think that's right. Try again.\" ",
            "puzzle_already_complete": "Wesley looks much calmer now, now writing that pesky email to Mia.",
            "puzzle_take_wifi_credentials": (
                "You pick up the sticky note with the Wi-Fi credentials. It seems to "
                "contain the login information you'll need to connect to "
                "the school's intranet. You should now find a computer to use these credentials on."
            ),
            "quit": "👋 You leave the teacher alone and go somewhere else."
        },
        "teachersroom4": {
            "header": "👩 You step into Teacher's Room 4.",
            "enter": (
                "The room looks pretty empty, except for a computer on a desk. This might"
                "be your chance to log in with chose credentials on a computer and get something "
                "useful from the school's intranet."
            ),
            "puzzle_take_api_and_prompt_usb": (
                "# Congrats, you completed this challenge! "
                "# Inside, you find code for an encrypted API and some prompts for the LLM, "
                "# you store it onto a USB drive and safely eject it. "
                "# You now realize that you actually need to be able to talk and hear A.I.G.I.S., "
                "# so you should search for some kind of speaker module. Maybe one of the project "
                "# rooms might have it."
            ),
            "quit": "👋 You leave the computer alone and exit."
        },
        "projectroom2": {
            "header": "🎨 You enter the 2nd Project Room.",
            "enter": (
                "In the middle of the room stands an old projector, humming quietly. "
                "It projects 7 colored slides onto the wall, but they look completely out of order. "
                "Maybe you should take a closer look at the projector."
            ),
            "puzzle_not_complete": (
                "You take a closer look at the projector. "
                "The 7 slides show colors, but shuffled in a random order. "
                "It looks like they are meant to be arranged in the order of the rainbow. "
                "Maybe you should try swapping the slides around."
            ),
            "puzzle_already_complete": "You've already arranged the colors correctly. There's nothing more for you to do.",
            "puzzle_completed": "🌈 The slides light up in perfect rainbow order, congratulations!",
            "puzzle_take_mic_and_speaker_combo": (
                "A small compartment on the projector opens, which means you can tinker inside it."
                "You manage to take out a mic and a speaker, and you wire them together on the spot. "
                "You now have a makeshift mic and speaker combo, which should allow you to talk to A.I.G.I.S. and hear its responses. "
                "You realize it can't remember your responses without some memory, you should search for some memory sticks to add to it. "
            ),
            "quit": "👋 You switch off the projector and close your eyes. Game over."
        }
    },
}