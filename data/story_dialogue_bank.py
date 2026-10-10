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
If you can gather the missing hardware across the school and assemble it, its LLM core might know the exit code.""",

        "game_finish": """You assemble A.I.G.I.S. and it whirs to life. The LLM core starts speaking before you do.
"Looks like you need to exit, you look tired. The exit code is 2628. Yes, it is the postal code of the building, maybe
you should have tried to guess that. Anyway, now you're out!" You punch the code into the lock and it opens. You're finally free!
Congratulations! You have completed the game and escaped the school building!"""
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
            "register_intro": "The staff member looks up over his glasses. \"Why are you walking around without your ID card?\"",
            "register_prompt": "\"Sit down, I'll print you a new one.\" (type 'cancel' to walk away)",
            "register_cancel_name": "\"Fine, fine. Come back when you've got a minute.\"",
            "register_cancel_number": "\"Suit yourself. The card will be waiting here.\"",
            "register_complete": "The printer whirs. \"There you go,",
            "register_story": "Don't lose this one.",
            "register_terminal": "He taps the lobby terminal: 'PROJECT A.I.G.I.S. ASSEMBLY REQUIRED'. \"The professor left it unfinished.",
            "register_collect": "Collect every part on this floor and assemble it in Lab D2.001.",
            "register_doors": "Doors are locked after hours, so every room needs something.\"",
            "register_society": "\"Your ID opens the Student Society, by the way. Good luck.\"",
            "register_pickup": "Your new Student ID card is waiting in the printer tray. Use 'take student id card' to pick it up.",
            "inspect_completed": "You have already completed this room. There is nothing else to do here.",
            "counter_sign": "A sign: 'Lost your ID? Register here.' Inspect the printer to get a new Student ID card.",
            "logbook_first": "Night guard's logbook: 'The professor left PROJECT A.I.G.I.S. unfinished.",
            "logbook_second": "Doors lock themselves after hours.'",
            "logbook_third": "'Every room wants something from another room. Talk to people, read the boards, trust no lock.'",
            "leave": "You nod at the staff member and step back into the lobby.",
            
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
                "The teacher's eyes light up: \"n % 2 — of course! Thank you!\" "
                "The teacher points to a keycard on the table and tells you to take it, as a reward for your help."
            ),
            "puzzle_answer_incorrect": "The teacher shakes their head: \"Not quite.\" ",
            "puzzle_already_complete": "The teacher grins: \"That fix worked perfectly, thanks again!\" ",
            "puzzle_take_keycard": (
                "You pick up the keycard. It looks to be a staff keycard, which will "
                "allow you to enter some restricted areas. "
                "After taking it, you notice something shiny in the corner of your eye. "
                "You look closer and realize you found some shiny coins, and the teacher "
                "allows you to take them (+10 coins). "
                "The teacher also asks you to check out the second teacher's room, as it might have "
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
        },
        "classroomd2015": {
            "header": "🤖 You enter Classroom D2.015.",
            "enter": "A marked test track fills the floor and a dead robot rover sits in the middle.",
            "enter_bins": "Leftover student project bins line the wall and a workbench hums with test equipment.",
            "rover_complete": "The rover races down the track and stops on the target pad. A hatch pops open.",
            "rover_digits": "The rover's log screen shows the FINAL CODE DIGITS:",
            "memory_pickup": "The hatch holds the Memory sticks you really need. Use 'take memory sticks' to pick it up.",
            "memory_story": "64GB!? Wow, seems like you really hit the jackpot this time, you ",
            "memory_story_car": "could trade this in for a used car with how memory prices are now.",
            "memory_story_objective": "\nWell, now you have all the components necessary to assemble A.I.G.I.S.",
            "memory_story_advance": "You should probably head to a lab to get all these components together on a workbench.",
            "quit": "👋 You leave the classroom and exit."
        },
        "classroomd2031": {
            "header": "🤖 You enter Classroom D2.031.",
            "enter": "A dim classroom full of dead monitors. A locked key box is bolted to the wall.",
            "board_intro": "Scrawled on the board, in the professor's handwriting:",
            "board_cipher": "Under it: 'Caesar cipher. Every letter was pushed FORWARD 3 places in the alphabet.'",
            "board_monitor": "'I switched one monitor on for you. It shows how to decode.'",
            "monitor_intro": "Every screen is dead except one, flickering green. It shows a decoder table:",
            "monitor_example": "Example: D on the board is really A. Look up each letter of the board message.",
            "cipher_intro": "The key box wants the real password. The board only shows it in code.",
            "cipher_read": "Read the board and the working monitor first (inspect board, inspect monitors).",
            "cipher_open": "Click. The key box opens.",
            "cipher_key": "A tag on the key reads: 'Classroom 2.021. Also fits the Project Room 1 side door.'",
            "key_pickup": "Inside the key box: the Classroom 2.021 key. Use 'take classroom 2.021 key' to pick it up.",
            "quit": "👋 You leave the dark classroom and exit."
        },
        "classroomd2035": {
            "header": "🤖 You enter Classroom D2.035.",
            "enter": "A lecturer is frowning at a messy seating chart. A podium stands at the front with a number lock.",
            "seating_intro": "A lecturer's note lists four students and four seats (1 = window, 4 = aisle):",
            "seating_ana": "  - Ana sits by the window.",
            "seating_ben": "  - Ben sits at the aisle, in the last seat.",
            "seating_chloe": "  - Chloe sits right next to Ana.",
            "seating_dev": "  - Dev sits between Chloe and Ben.",
            "seating_success": "Everyone is in the right seat. The lecturer hands you the Seating plan.",
            "seating_transfer": "\"Classroom D2.031 keeps a coded message about it. Take this plan there.\"",
            "podium_intro": "PART 2: TIMETABLE SEQUENCE",
            "podium_slip": "Timetable slip:",
            "podium_rule": "Each number follows a rule. Work out the pattern between neighbours (2 to 6 is +4, ...).",
            "podium_success": "Correct! The podium drawer slides open.",
            "lecturer": "Lecturer: \"My students never sit where they should. Arrange them, and I will hand over the plan.\"",
            "lecturer_sequence": "\"After that, finish the timetable sequence on the podium. The D2.015 lab opens with it.\"",
            "drawer": "The drawer holds a Mainboard!",
            "drawer_pickup": "Use 'take mainboard' and 'take timetable' to pick them up.",
            "quit": "👋 You leave the lecture hall and exit."
        },
        "projectroom1": {
            "header": "🤖 You enter the 1st Project Room.",
            "enter": "A project room. Professor Vance stands at the front, capping a whiteboard marker.",
            "lockers": "Five lockers line the back wall.",
            "whiteboard_intro": "You step up to the whiteboard. Vance's handwriting is terrible.",
            "whiteboard_bodmas": "Vance has added a reminder: BODMAS. Brackets first, then multiply/divide, then add/subtract.",
            "whiteboard_more": "(Two more codes are written somewhere else in the room.)",
            "desks_intro": "Between the rows of wooden desks, something is carved into desk #3:",
            "pile_intro": "A pile of broken desks and chairs. A sticker peels off a snapped chair:",
            "pile_hint": "Something shiny is half buried in the pile (try 'look' and 'take').",
            "vance_first": "Vance: \"Five lockers, five combinations, every number is somewhere in this room.",
            "vance_second": "The USB cable and the keycard for the old Linux room are in there. Earn them.\"",
            "quit": "👋 You leave Project Room 1 and exit."
        },
        "equinoxstudentsociety": {
            "header": "📚 You scan your student ID on the doorknob and enter the Equinox Student Society room.",
            "enter": "The room is well-lit and organized, with a few tables and chairs arranged neatly.",
            "enter_computer_desc": "A computer is set up on an office table, and a small shelf holds some books and board games.",
            "quiz_shutdown": "The computer has shut down after you finished the quiz.",
            "quiz_no_boot": "You can't seem to be able to get it to boot up again, so you decide to leave it alone.",
            "step_away": "You step away from the computer.",
            "certificate": "For your efforts, you receive a certificate of completion!",
            "quit": "👋 You decide to try your hand at the Dungeons and Dragons game, and lose track of time. Game over."
        },
        "store": {
            "header": "🏪 You enter the store.",
            "enter": "You find some interesting items placed randomly around it.",
            "enter_prompt": "Maybe you should check it out.",
            "completed": "Looks like you've bought everything in the store. Congratulations!",
            "look_intro": "You take a closer look at the items in the store.",
            "look_detail": "It seems like there's some interesting items here.",
            "look_items": "You see the following items:",
            "look_done": "You've already bought everything useful in the store. You should probably explore elsewhere.",
            "leave": "You decide to leave the store and return to the lobby.",
            "quit": "👋 You leave the store and close your eyes. Game over."
        },
        "labd2001": {
            "header": "🧪 You enter Lab D2.001.",
            "enter": "This room has some tables, filled with electronics equipment and cables on top.",
            "enter_food": "You notice a table with some chairs, filled with sandwiches and drinks.",
            "enter_tools": "The rest of the room is filled with construction tools, unopened boxes and materials.",
            "puzzle_quit": "You decide to step away from the platforms and boxes for now.",
            "puzzle_return": "Maybe you'll come back later.",
            "puzzle_complete": "Looks like you stacked the boxes correctly, congratulations!",
            "puzzle_click": "You hear a loud \"click\" sound, and one of the boxes falls open.",
            "puzzle_coins": "Inside, you find some coins, which you pick up. (+10 coins)",
            "already_complete": "You've already forced the boxes open. There's nothing more to do here.",
            "quit": "👋 You sit on one of the chairs in the Lab and close your eyes. Game over."
        },

        "eastcorridor": {
            "header": "🚪 You enter the East Corridor.",
            "enter": "You see a long corridor with many doors and glass walls on both sides. Coffee machines and printers line the walls, along with some houseplants.",
            "quit": "👋 You decide to turn back ."
        },
        "studentwing": {
            "header": "🚪 You enter the Student Wing.",
            "enter": "This corridor is quite worthy of it's name; colorful designs and posters cover the walls, along with greenery everywhere.",
            "quit": "👋 You decide to turn back."
        },
        "teachingarea": {
            "header": "🚪 You enter the Teaching Area.",
            "enter": "It looks very serious, made to be functional more than anything. Makes sense, with all the classrooms you can go to from here.",
            "quit": "👋 You decide to turn back."
        },
    },
}