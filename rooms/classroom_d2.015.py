inventory = []
location = "room"
bench_items = ["usb cable", "resistor", "multimeter"]

# Challenge states
power_set = False
rover_fixed = False

print("=== CLASSROOM D2.015: EMBEDDED SYSTEMS LAB ===")
print("You enter D2.015. A test arena dominates the room with a small robot rover stuck inside.")
print("The door lock is humming. Type 'help' at any time to see commands.\n")

while True:
    cmd = input("> ").strip().lower()

    if cmd == "quit":
        print("You left the lab. Game over!")
        break

    elif cmd == "help":
        print("\n--- HELP MENU ---")
        print("COMMANDS:")
        print("  look around              - Inspect your current surroundings")
        print("  go to <bench/track/room> - Move to a specific workstation")
        print("  take <item>              - Pick up an item from the workbench")
        print("  inventory                - View items in your backpack")
        print("  set power <val>          - Set the DC power supply voltage")
        print("  calibrate rover <val>    - Send the IR frequency code to the rover")
        print("  start rover              - Run the rover after setting power and frequency")
        print("  quit                     - Exit game\n")

    elif cmd == "inventory":
        print("Your backpack:", inventory if inventory else "empty")

    # Movement
    elif cmd in ["go to bench", "bench"]:
        location = "bench"
        print("You step up to the messy electronics workbench. Type 'look around'.")

    elif cmd in ["go to track", "track", "go to rover"]:
        location = "track"
        print("You kneel beside the robot testing track in the center. Type 'look around'.")

    elif cmd in ["go to room", "room", "go back"]:
        location = "room"
        print("You step back into the center of Classroom D2.015.")

    # Looking around
    elif cmd == "look around":
        if location == "room":
            print("Room D2.015 is filled with electronics gear.")
            print("East side: A workbench glowing with test equipment (type 'go to bench').")
            print("Floor: A marked test track with a stuck robot rover (type 'go to track').")
            print("Power unit: A bench supply waiting for a target voltage ('set power <val>').")

        elif location == "bench":
            print("The workbench has soldering irons and a lab notebook open to a page titled:")
            print("  'BENCH SUPPLY CALCULATION: Set line voltage to: 12 - 2 * 4 + 6'")
            if bench_items:
                print("Items lying on the antistatic mat:", ", ".join(bench_items))
            else:
                print("The workbench mat has no more loose items.")

        elif location == "track":
            print("The miniature rover sits unpowered. A sticker on its chassis reads:")
            print("  'IR CARRIER FREQUENCY: (40 + 20) / 2 kHz'")
            if rover_fixed:
                print("The rover's green indicator is solid. It has completed the run!")
            else:
                print("Status screen: 'OFFLINE - Needs power unit active and correct frequency calibration.'")

    # Taking items
    elif cmd.startswith("take "):
        item = cmd.replace("take ", "").strip()
        if location != "bench":
            print("There are no loose items to pick up here. Check the workbench!")
        elif item in bench_items:
            bench_items.remove(item)
            inventory.append(item)
            print(f"You picked up: {item}")
        else:
            print("That item isn't on the bench!")

    # Puzzle 1: Power supply setting (12 - 2 * 4 + 6 = 10)
    elif cmd.startswith("set power "):
        val = cmd.replace("set power ", "").strip()
        if val == "10":
            power_set = True
            print("Click-turn! The power supply stabilizes at 10V. The track rails energize!")
        else:
            print("BZZT! Overvoltage warning on the display. Check your BODMAS math: 12 - 2 * 4 + 6.")

    # Puzzle 2: Sensor calibration ((40 + 20) / 2 = 30)
    elif cmd.startswith("calibrate rover "):
        val = cmd.replace("calibrate rover ", "").strip()
        if not power_set:
            print("Nothing happens. The track rails have no power yet! Set the power supply first.")
        elif val == "30":
            print("Beep-boop! The rover's IR sensor syncs to 30 kHz. Ready to run!")
        else:
            print("Wrong frequency! The rover's receiver chirps an error tone.")

    # Running the challenge
    elif cmd == "start rover":
        if not power_set:
            print("The track has no power. Adjust the power supply first!")
        elif rover_fixed:
            print("The rover has already completed its route.")
        else:
            print("\nThe rover's twin motors buzz to life!")
            print("It speeds through the test track, maneuvers around the obstacles, and hits the target pad.")
            print("A hidden compartment pops open on its side!")
            print("Inside you find: a 'security dongle' and a '50 euro' lab prize!")
            inventory.append("security dongle")
            inventory.append("50 euro")
            rover_fixed = True
            print("\nYou solved Classroom D2.015! Type 'inventory' to admire your loot.")

    else:
        print("Unknown command. Type 'help' to see what you can do.")
