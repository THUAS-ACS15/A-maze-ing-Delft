import time

try:
    from utilities.clear_screen import clear_screen
except ImportError:
    def clear_screen():
        import os
        os.system("cls" if os.name == "nt" else "clear")

try:
    import utilities.status_bar as sb
    if hasattr(sb, "display_status_bar"):
        display_status_bar = sb.display_status_bar
    elif hasattr(sb, "status_bar"):
        display_status_bar = sb.status_bar
    else:
        display_status_bar = None
except ImportError:
    display_status_bar = None

try:
    import utilities.inventory_viewer as iv
    if hasattr(iv, "display_inventory"):
        show_inventory = iv.display_inventory
    elif hasattr(iv, "show_inventory"):
        show_inventory = iv.show_inventory
    elif hasattr(iv, "view_inventory"):
        show_inventory = iv.view_inventory
    else:
        show_inventory = None
except ImportError:
    show_inventory = None


def show_local_inventory(game_state):
    """Displays items currently in the shared backpack."""
    inventory = game_state.get("inventory", [])
    if show_inventory is not None:
        try:
            show_inventory(inventory)
            return
        except TypeError:
            try:
                show_inventory(game_state)
                return
            except Exception:
                pass

    print("\n--- INVENTORY ---")
    if not inventory:
        print("Your backpack is currently empty.")
    else:
        for item in inventory:
            if isinstance(item, dict):
                print(f"- {item.get('name', 'Item')}: {item.get('description', '')}")
            else:
                print(f"- {item}")
    print("-----------------\n")


def show_help():
    """Displays commands matching the original script."""
    print("\n--- HELP MENU ---")
    print("COMMANDS:")
    print("  look around               - Inspect your current surroundings")
    print("  go to <bench/track/room> - Move to a specific workstation")
    print("  take <item>               - Pick up an item from the workbench")
    print("  inventory                 - View items in your backpack")
    print("  set power <val>           - Set the DC power supply voltage")
    print("  calibrate rover <val>     - Send the IR frequency code to the rover")
    print("  start rover               - Run the rover after setting power and frequency")
    print("  go lobby / leave          - Exit back to the Lobby")
    print("  quit                      - Exit game\n")


def classroom_d2_015(game_state):
    """
    Main loop for Classroom D2.015.
    Preserves Sadanand's original rover puzzle and workstation navigation.
    """
    if "rooms" in game_state and isinstance(game_state["rooms"], dict):
        game_state["rooms"]["classroom_d2.015"] = True

    if "inventory" not in game_state or not isinstance(game_state["inventory"], list):
        game_state["inventory"] = []
    inventory = game_state["inventory"]

    if "classroom_d2015_state" not in game_state:
        game_state["classroom_d2015_state"] = {
            "location": "room",
            "bench_items": ["usb cable", "resistor", "multimeter"],
            "power_set": False,
            "rover_calibrated": False,
            "rover_fixed": False
        }

    lab_state = game_state["classroom_d2015_state"]
    bench_items = lab_state["bench_items"]

    feedback_message = (
        "=== CLASSROOM D2.015: EMBEDDED SYSTEMS LAB ===\n"
        "You enter D2.015. A test arena dominates the room with a small robot rover stuck inside.\n"
        "The door lock is humming. Type 'help' at any time to see commands."
    )

    while True:
        clear_screen()
        if display_status_bar is not None:
            try:
                display_status_bar(game_state)
            except Exception:
                pass

        print("=" * 64)
        print("           CLASSROOM D2.015: EMBEDDED SYSTEMS LAB             ")
        print("=" * 64)

        if feedback_message:
            print(f"\n{feedback_message}\n")
            feedback_message = ""

        cmd = input(f"D2.015 [{lab_state['location']}] > ").strip().lower()

        if cmd == "quit":
            return "quit"

        elif cmd == "help":
            show_help()
            input("Press Enter to continue...")

        elif cmd in ["inventory", "i", "inv"]:
            show_local_inventory(game_state)
            input("Press Enter to return...")

        elif cmd in ["go to bench", "bench"]:
            lab_state["location"] = "bench"
            feedback_message = "You step up to the messy electronics workbench. Type 'look around'."

        elif cmd in ["go to track", "track", "go to rover"]:
            lab_state["location"] = "track"
            feedback_message = "You kneel beside the robot testing track in the center. Type 'look around'."

        elif cmd in ["go to room", "room", "go back"]:
            lab_state["location"] = "room"
            feedback_message = "You step back into the center of Classroom D2.015."

        elif cmd in ["look around", "look"]:
            loc = lab_state["location"]
            print()
            if loc == "room":
                print("Room D2.015 is filled with electronics gear.")
                print("East side: A workbench glowing with test equipment (type 'go to bench').")
                print("Floor: A marked test track with a stuck robot rover (type 'go to track').")
                print("Power unit: A bench supply waiting for a target voltage ('set power <val>').")
                print("Exits: Door back to Lobby (type 'go lobby').")

            elif loc == "bench":
                print("The workbench has soldering irons and a lab notebook open to a page titled:")
                print("  'BENCH SUPPLY CALCULATION: Set line voltage to: 12 - 2 * 4 + 6'")
                if bench_items:
                    print("Items lying on the antistatic mat:", ", ".join(bench_items))
                else:
                    print("The workbench mat has no more loose items.")

            elif loc == "track":
                print("The miniature rover sits unpowered. A sticker on its chassis reads:")
                print("  'IR CARRIER FREQUENCY: (40 + 20) / 2 kHz'")
                if lab_state["rover_fixed"]:
                    print("The rover's green indicator is solid. It has completed the run!")
                else:
                    print("Status screen: 'OFFLINE - Needs power unit active and correct frequency calibration.'")
            input("\nPress Enter to continue...")

        elif cmd.startswith("take "):
            item = cmd.replace("take ", "").strip()
            if lab_state["location"] != "bench":
                feedback_message = "There are no loose items to pick up here. Check the workbench!"
            elif item in bench_items:
                bench_items.remove(item)
                inventory.append(item)
                feedback_message = f"You picked up: {item}"
            else:
                feedback_message = "That item isn't on the bench!"

        elif cmd.startswith("set power "):
            val = cmd.replace("set power ", "").strip()
            if val == "10":
                lab_state["power_set"] = True
                feedback_message = "Click-turn! The power supply stabilizes at 10V. The track rails energize!"
            else:
                feedback_message = "BZZT! Overvoltage warning on the display. Check your BODMAS math: 12 - 2 * 4 + 6."

        elif cmd.startswith("calibrate rover "):
            val = cmd.replace("calibrate rover ", "").strip()
            if not lab_state["power_set"]:
                feedback_message = "Nothing happens. The track rails have no power yet! Set the power supply first."
            elif val == "30":
                lab_state["rover_calibrated"] = True
                feedback_message = "Beep-boop! The rover's IR sensor syncs to 30 kHz. Ready to run!"
            else:
                feedback_message = "Wrong frequency! The rover's receiver chirps an error tone."

        elif cmd == "start rover":
            if not lab_state["power_set"]:
                feedback_message = "The track has no power. Adjust the power supply first ('set power 10')!"
            elif not lab_state["rover_calibrated"]:
                feedback_message = "The rover's frequency is not calibrated. Calibrate the IR sensor first!"
            elif lab_state["rover_fixed"]:
                feedback_message = "The rover has already completed its route."
            else:
                lab_state["rover_fixed"] = True
                if "security dongle" not in inventory:
                    inventory.append("security dongle")
                if "50 euro" not in inventory:
                    inventory.append("50 euro")
                game_state["coins"] = game_state.get("coins", 0) + 50

                feedback_message = (
                    "The rover's twin motors buzz to life!\n"
                    "It speeds through the test track, maneuvers around obstacles, and hits the target pad.\n"
                    "A hidden compartment pops open on its side!\n"
                    "Inside you find: a 'security dongle' and a '50 euro' lab prize! (Added to inventory & coins)"
                )

        elif cmd in ["go lobby", "go to lobby", "leave", "exit", "lobby", "door"]:
            clear_screen()
            print("\nYou exit Classroom D2.015 and return to the Lobby...")
            time.sleep(0.8)
            return "lobby"

        else:
            feedback_message = "Unknown command. Type 'help' to see what you can do."
