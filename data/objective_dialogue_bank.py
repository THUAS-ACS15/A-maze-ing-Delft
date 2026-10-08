# -----------------------------------------------------------------------------
# File: objective_dialogue_bank.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

# ruff: noqa: E501
# ^ disable ruff checking long lines, as this is dialogue

objective_dialogue_bank: dict = {
    0: "None",
    1: "Go to the front desk to register for a new student ID card.", # obtains Student ID card
    2: "Go to Teacher's Room 1 and help the teacher there", # obtains Staff Keycard
    3: "Go to Teacher's Room 2 and help the teacher inside", # obtains Wi-Fi creds
    4: "Find a computer in Teacher's Room 4 and use the Wi-Fi credentials to connect to the school's intranet", # obtains Encrypted API & Prompt USB
    5: "Search Project Room 2 for scraps to make a mic & speaker combo for A.I.G.I.S.", # obtains Makeshift Mic and Speaker Combo
    6: "Go to Classroom D2.035 and see about obtaining a motherboard from one of the AI units there", # obtains Motherboard
    7: "Search the storage racks in Classrooms D2.015 and D2.031 for some memory sticks", # obtains 64GB Memory Sticks
    8: "Assemble A.I.G.I.S on the workbench in Lab D2.001" # game finish! 
}