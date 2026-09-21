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
    print("  look around              - Inspect your current surroundings")
    print("  go to <bench/track/room> - Move to a specific workstation")
    print("  take <item>              - Pick up an item from the workbench")
    print("  inventory                - View items in your backpack")
    print("  set power <val>          - Set the DC power supply voltage")
    print("  calibrate rover <val>    - Send the IR frequency code to the rover")
    print("  start rover              - Run the rover after setting power and frequency")
    print("  go lobby                 - Return back to the Lobby")
    print("  quit                     - Exit game\n")


def enterClassroomD2015(state):
    state["current_room"] = "classroomd2015"
    state["visited"]["classroomd2015"] = True

    if "classroomd2015_data" not in state:
        state["classroomd2015_data"] = {
            "location": "room",
            "bench_items": ["usb cable", "resistor", "multimeter"],
            "power_set": False,
            "rover_calibrated": False,
            "rover_fixed": False
        }

    data = state["classroomd2015_data"]
    bench_items = data["bench_items"]

    feedback = "You enter D2.015. A test arena dominates the room with a small robot rover stuck inside."

    while True:
        clearScreen()
        if statusBar:
            try:
                statusBar(state)
            except Exception:
                pass

        print("=" * 64)
        print("           CLASSROOM D2.015: EMBEDDED SYSTEMS LAB            ")
        print("=" * 64)

        if feedback:
            print(f"\n{feedback}\n")
            feedback = ""

        location = data["location"]
        cmd = input(f"D2.015 [{location}] > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd == "help":
            showHelp()
            input("Press Enter to continue...")

        elif cmd in ["inventory", "inv"]:
            print("\nYour backpack:", state["inventory"] if state["inventory"] else "empty")
            print(f"Current coin balance: €{state.get('coin_balance', 0)}")
            input("\nPress Enter to continue...")

        elif cmd in ["go to bench", "bench"]:
            data["location"] = "bench"
            feedback = "You step up to the messy electronics workbench."

        elif cmd in ["go to track", "track", "go to rover"]:
            data["location"] = "track"
            feedback = "You kneel beside the robot testing track in the center."

        elif cmd in ["go to room", "room", "go back"]:
            data["location"] = "room"
            feedback = "You step back into the center of Classroom D2.015."

        elif cmd in ["look around", "look"]:
            print()
            if location == "room":
                print("Room D2.015 is filled with electronics gear.")
                print("East side: A workbench glowing with test equipment ('go to bench').")
                print("Floor: A marked test track with a stuck robot rover ('go to track').")
                print("Power unit: A bench supply waiting for a target voltage ('set power <val>').")
                print("Exits: Door back to Lobby ('go lobby').")

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
                if data["rover_fixed"]:
                    print("The rover's green indicator is solid. It has completed the run!")
                else:
                    print("Status screen: 'OFFLINE - Needs power unit active and correct frequency calibration.'")
            input("\nPress Enter to continue...")

        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if location != "bench":
                feedback = "There are no loose items to pick up here. Check the workbench!"
            elif item in bench_items:
                bench_items.remove(item)
                state["inventory"].append(item)
                feedback = f"You picked up: {item}"
            else:
                feedback = f"'{item}' isn't on the workbench!"

        elif cmd.startswith("set power"):
            parts = cmd.split()
            val = parts[-1] if len(parts) >= 3 else input("Enter target DC voltage: ").strip()
            if val == "10":
                data["power_set"] = True
                feedback = "Click-turn! The power supply stabilizes at 10V. The track rails energize!"
            else:
                feedback = f"BZZT! {val}V is an overvoltage. Check your BODMAS math: 12 - 2 * 4 + 6."

        elif cmd.startswith("calibrate rover"):
            parts = cmd.split()
            val = parts[-1] if len(parts) >= 3 else input("Enter IR carrier frequency in kHz: ").strip()
            if not data["power_set"]:
                feedback = "Nothing happens. The track rails have no power yet! Set the power supply first."
            elif val == "30":
                data["rover_calibrated"] = True
                feedback = "Beep-boop! The rover's IR sensor syncs to 30 kHz. Ready to run!"
            else:
                feedback = f"BEEP! {val} kHz is rejected. Check: (40 + 20) / 2."

        elif cmd == "start rover":
            if not data["power_set"]:
                feedback = "The track has no power. Adjust the power supply first ('set power 10')!"
            elif not data["rover_calibrated"]:
                feedback = "The rover's frequency is not calibrated. Calibrate the IR sensor first!"
            elif data["rover_fixed"]:
                feedback = "The rover has already completed its route."
            else:
                data["rover_fixed"] = True
                state["completed"]["classroomd2015"] = True
                state["inventory"].append("security dongle")
                state["inventory"].append("50 euro")
                state["coin_balance"] = state.get("coin_balance", 0) + 50
                feedback = (
                    "The rover's twin motors buzz to life!\n"
                    "It speeds through the test track, maneuvers around obstacles, and hits the target pad.\n"
                    "A hidden compartment pops open on its side!\n"
                    "Inside you find: a 'security dongle' and a '50 euro' lab prize! (Added to backpack and balance)"
                )

        elif cmd in ["go lobby", "go to lobby", "leave", "exit", "lobby"]:
            clearScreen()
            print("\nYou exit Classroom D2.015 and return to the Lobby...")
            time.sleep(0.8)
            state["previous_room"] = "classroomd2015"
            return "lobby"

        else:
            feedback = "Unknown command. Type 'help' to see what you can do."
