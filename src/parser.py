"""
A-maze-ing-Delft. - Command Parser Module (src/parser.py)

Normalizes raw user text input into structured command tuples:
(canonical_verb, args) or (canonical_verb, target, indirect_target)
"""

import re

# Direction alias mappings
DIRECTION_ALIASES = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "north": "north",
    "south": "south",
    "east": "east",
    "west": "west"
}

# Verb alias mappings
VERB_ALIASES = {
    # Movement
    "go": "go",
    "move": "go",
    "walk": "go",
    "head": "go",
    "travel": "go",
    "n": "go",
    "s": "go",
    "e": "go",
    "w": "go",
    "north": "go",
    "south": "go",
    "east": "go",
    "west": "go",

    # Looking / Environment
    "look": "look",
    "l": "look",
    "ls": "look",
    "around": "look",

    # Inspection
    "inspect": "inspect",
    "examine": "inspect",
    "x": "inspect",
    "read": "inspect",
    "check": "inspect",
    "search": "inspect",

    # Item Acquisition
    "take": "take",
    "get": "take",
    "grab": "take",
    "pick": "take",
    "pickup": "take",
    "collect": "take",

    # Item Usage / Assembly
    "use": "use",
    "apply": "use",
    "place": "use",
    "put": "use",
    "install": "use",
    "insert": "use",
    "mount": "use",

    # Inventory
    "inventory": "inventory",
    "inv": "inventory",
    "i": "inventory",

    # System & Game Flow
    "help": "help",
    "h": "help",
    "?": "help",
    "commands": "help",
    "save": "save",
    "load": "load",
    "quit": "quit",
    "exit": "quit",
    "q": "quit",

    # Activation
    "activate": "activate",
    "power": "activate",
    "start": "activate",
    "boot": "activate"
}

# Item display name/alias to canonical item_id mapping
ITEM_ALIASES = {
    "blueprint": "blueprint",
    "robot assembly blueprint": "blueprint",
    "schematic": "blueprint",
    "chassis": "chassis_frame",
    "chassis_frame": "chassis_frame",
    "robot chassis frame": "chassis_frame",
    "frame": "chassis_frame",
    "battery": "battery_pack",
    "battery_pack": "battery_pack",
    "battery pack": "battery_pack",
    "keycard": "keycard_lvl1",
    "keycard_lvl1": "keycard_lvl1",
    "level-1 staff keycard": "keycard_lvl1",
    "level 1 keycard": "keycard_lvl1",
    "card": "keycard_lvl1",
    "mainboard": "mainboard",
    "microcontroller": "mainboard",
    "microcontroller / mainboard": "mainboard",
    "board": "mainboard",
    "sensory_module": "sensory_module",
    "sensory module": "sensory_module",
    "camera": "sensory_module",
    "mic": "sensory_module",
    "sensors": "sensory_module",
    "wifi_credentials": "wifi_credentials",
    "wifi credentials": "wifi_credentials",
    "wifi": "wifi_credentials",
    "credentials": "wifi_credentials",
    "wifi note": "wifi_credentials",
    "passkey": "wifi_credentials",
    "motors_speakers": "motors_speakers",
    "motors and speakers": "motors_speakers",
    "servo motors": "motors_speakers",
    "motors": "motors_speakers",
    "speakers": "motors_speakers",
    "api_usb": "api_usb",
    "encrypted api usb": "api_usb",
    "usb": "api_usb",
    "drive": "api_usb",
    "usb drive": "api_usb"
}


class CommandParser:
    """Parses freeform CLI strings into structured command objects."""

    def __init__(self):
        pass

    def parse(self, raw_input: str) -> tuple[str, dict]:
        """
        Parses a raw command string.

        Returns:
            Tuple[str, dict]: (action_verb, details_dict)

            Details dict contains keys like:
            - "target": primary target (room, item, object, or code)
            - "indirect": secondary target (e.g. "workbench", "door")
            - "raw": unmodified argument string
        """
        cleaned = raw_input.strip().lower()
        if not cleaned:
            return ("EMPTY", {})

        tokens = cleaned.split()
        first_token = tokens[0]

        # Case 1: Direction shortcuts ("n", "south", etc.)
        if first_token in DIRECTION_ALIASES and len(tokens) == 1:
            return ("go", {"target": DIRECTION_ALIASES[first_token], "raw": cleaned})

        # Resolve primary verb
        verb = VERB_ALIASES.get(first_token)
        if not verb:
            return ("UNKNOWN", {"raw": raw_input})

        # Argument processing
        args = tokens[1:]
        arg_str = " ".join(args)

        if verb == "look":
            return ("look", {"raw": arg_str})

        if verb == "inventory":
            return ("inventory", {"raw": arg_str})

        if verb == "help":
            return ("help", {"raw": arg_str})

        if verb == "save":
            slot = args[0] if args else "save_slot_1.json"
            return ("save", {"target": slot, "raw": arg_str})

        if verb == "load":
            slot = args[0] if args else "save_slot_1.json"
            return ("load", {"target": slot, "raw": arg_str})

        if verb == "quit":
            return ("quit", {"raw": arg_str})

        if verb == "activate":
            return ("activate", {"raw": arg_str})

        if verb == "go":
            if not args:
                return ("INVALID", {
                    "message": "Go where? Specify a direction (north, south, east, west)."})
            direction = DIRECTION_ALIASES.get(args[0], args[0])
            return ("go", {"target": direction, "raw": arg_str})

        if verb == "inspect":
            if not args:
                return ("INVALID", {
                    "message": "Inspect what? Specify an item or object (e.g., 'inspect desk')."})
            target_id = ITEM_ALIASES.get(arg_str, arg_str)
            return ("inspect", {"target": target_id, "raw": arg_str})

        if verb == "take":
            if not args:
                return ("INVALID", {
                    "message": "Take what? Specify an item (e.g., 'take battery_pack')."})
            # Handle "pick up <item>"
            if first_token == "pick" and args and args[0] == "up":
                item_tokens = args[1:]
                arg_str = " ".join(item_tokens)
            target_id = ITEM_ALIASES.get(arg_str, arg_str)
            return ("take", {"target": target_id, "raw": arg_str})

        if verb == "use":
            if not args:
                return ("INVALID", {
                    "message": "Use what? Syntax: 'use <item>' or 'use <item> on <target>'."})

            # Pattern matching for "use <item> on/with <target>" or "put <item> on <workbench>"
            use_pattern = re.match(r"^(.*?)\s+(?:on|with|in|onto)\s+(.*)$", arg_str)
            if use_pattern:
                item_raw = use_pattern.group(1).strip()
                indirect_raw = use_pattern.group(2).strip()
                item_id = ITEM_ALIASES.get(item_raw, item_raw)
                return ("use",
                        {"target": item_id, "indirect": indirect_raw, "raw": arg_str})
            else:
                item_id = ITEM_ALIASES.get(arg_str, arg_str)
                return ("use", {"target": item_id, "indirect": None, "raw": arg_str})

        return ("UNKNOWN", {"raw": raw_input})