"""
A-maze-ing-Delft. - Command Parser Module (src/parser.py)

Normalizes raw user text input into structured command tuples:
(canonical_verb, args) or (canonical_verb, target, indirect_target)
"""

import re

# Direction aliases (n/s/e/w -> canonical direction)
ROOM_ALIASES = {
    "n": "north",
    "s": "south",
    "e": "east",
    "w": "west",
    "north": "north",
    "south": "south",
    "east": "east",
    "west": "west",
}

# Room name/alias -> canonical room_id (adjacent-only travel, see State.move_player).
# Keys must be lowercase; lookup normalizes underscores to spaces.
ROOM_NAME_ALIASES = {
    "lobby": "lobby",
    "floor lobby": "lobby",
    "classroom_d2015": "classroom_d2015",
    "classroom d2015": "classroom_d2015",
    "classroom d 2015": "classroom_d2015",
    "d2015": "classroom_d2015",
    "d 2015": "classroom_d2015",
    "classroom_d2035": "classroom_d2035",
    "classroom d2035": "classroom_d2035",
    "classroom d 2035": "classroom_d2035",
    "d2035": "classroom_d2035",
    "d 2035": "classroom_d2035",
    "teachers_room_1": "teachers_room_1",
    "teachers room 1": "teachers_room_1",
    "teacher room 1": "teachers_room_1",
    "tr1": "teachers_room_1",
    "teachers_room_2": "teachers_room_2",
    "teachers room 2": "teachers_room_2",
    "teacher room 2": "teachers_room_2",
    "tr2": "teachers_room_2",
    "project_room_1": "project_room_1",
    "project room 1": "project_room_1",
    "pr1": "project_room_1",
    "project_room_2": "project_room_2",
    "project room 2": "project_room_2",
    "pr2": "project_room_2",
    "teacher_room_4": "teacher_room_4",
    "teacher room 4": "teacher_room_4",
    "teachers room 4": "teacher_room_4",
    "tr4": "teacher_room_4",
    "lab_d2001": "lab_d2001",
    "lab d2001": "lab_d2001",
    "lab d 2001": "lab_d2001",
    "lab": "lab_d2001",
    "d2001": "lab_d2001",
}


def _normalize_room_key(raw: str) -> str:
    return " ".join(raw.strip().lower().replace("_", " ").split())


def resolve_room_target(raw: str) -> str:
    """Resolve user input to a direction ('north') or room_id ('lobby').

    Direction aliases take precedence; otherwise room name/alias map;
    falls back to the normalized raw string.
    """
    key = _normalize_room_key(raw)
    if key in ROOM_ALIASES:
        return ROOM_ALIASES[key]
    if key in ROOM_NAME_ALIASES:
        return ROOM_NAME_ALIASES[key]
    underscored = key.replace(" ", "_")
    if underscored in ROOM_NAME_ALIASES:
        return ROOM_NAME_ALIASES[underscored]
    return underscored

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
    "clear": "clear",
    "cls": "clear",
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
    "Blueprint": "blueprint",
    "BLUEPRINT": "blueprint",
    "robot assembly blueprint": "blueprint",
    "Robot Assembly Blueprint": "blueprint",
    "ROBOT ASSEMBLY BLUEPRINT": "blueprint",
    "schematic": "blueprint",
    "Schematic": "blueprint",
    "SCHEMATIC": "blueprint",
    "chassis": "chassis_frame",
    "Chassis": "chassis_frame",
    "CHASSIS": "chassis_frame",
    "chassis_frame": "chassis_frame",
    "chassis frame": "chassis_frame",
    "Chassis Frame": "chassis_frame",
    "CHASSIS FRAME": "chassis_frame",
    "robot chassis frame": "chassis_frame",
    "Robot Chassis Frame": "chassis_frame",
    "ROBOT CHASSIS FRAME": "chassis_frame",
    "frame": "chassis_frame",
    "Frame": "chassis_frame",
    "FRAME": "chassis_frame",
    "battery": "battery_pack",
    "Battery": "battery_pack",
    "BATTERY": "battery_pack",
    "battery_pack": "battery_pack",
    "battery pack": "battery_pack",
    "Battery Pack": "battery_pack",
    "BATTERY PACK": "battery_pack",
    "keycard": "keycard_lvl1",
    "Keycard": "keycard_lvl1",
    "KEYCARD": "keycard_lvl1",
    "keycard_lvl1": "keycard_lvl1",
    "level-1 staff keycard": "keycard_lvl1",
    "Level-1 Staff Keycard": "keycard_lvl1",
    "LEVEL-1 STAFF KEYCARD": "keycard_lvl1",
    "level 1 keycard": "keycard_lvl1",
    "Level 1 Keycard": "keycard_lvl1",
    "LEVEL 1 KEYCARD": "keycard_lvl1",
    "card": "keycard_lvl1",
    "Card": "keycard_lvl1",
    "CARD": "keycard_lvl1",
    "mainboard": "mainboard",
    "Mainboard": "mainboard",
    "MAINBOARD": "mainboard",
    "microcontroller": "mainboard",
    "Microcontroller": "mainboard",
    "MICROCONTROLLER": "mainboard",
    "microcontroller / mainboard": "mainboard",
    "Microcontroller / Mainboard": "mainboard",
    "MICROCONTROLLER / MAINBOARD": "mainboard",
    "board": "mainboard",
    "Board": "mainboard",
    "BOARD": "mainboard",
    "sensory_module": "sensory_module",
    "sensory module": "sensory_module",
    "Sensory Module": "sensory_module",
    "SENSORY MODULE": "sensory_module",
    "camera": "sensory_module",
    "Camera": "sensory_module",
    "CAMERA": "sensory_module",
    "mic": "sensory_module",
    "Mic": "sensory_module",
    "MIC": "sensory_module",
    "sensors": "sensory_module",
    "Sensors": "sensory_module",
    "SENSORS": "sensory_module",
    "wifi_credentials": "wifi_credentials",
    "wifi credentials": "wifi_credentials",
    "Wifi Credentials": "wifi_credentials",
    "WIFI CREDENTIALS": "wifi_credentials",
    "wi-fi credentials note": "wifi_credentials",
    "Wi-Fi Credentials Note": "wifi_credentials",
    "wifi": "wifi_credentials",
    "Wifi": "wifi_credentials",
    "WIFI": "wifi_credentials",
    "credentials": "wifi_credentials",
    "Credentials": "wifi_credentials",
    "CREDENTIALS": "wifi_credentials",
    "wifi note": "wifi_credentials",
    "Wifi Note": "wifi_credentials",
    "WIFI NOTE": "wifi_credentials",
    "passkey": "wifi_credentials",
    "Passkey": "wifi_credentials",
    "PASSKEY": "wifi_credentials",
    "motors_speakers": "motors_speakers",
    "motors and speakers": "motors_speakers",
    "Motors and Speakers": "motors_speakers",
    "servo motors": "motors_speakers",
    "Servo Motors": "motors_speakers",
    "SERVO MOTORS": "motors_speakers",
    "motors": "motors_speakers",
    "Motors": "motors_speakers",
    "MOTORS": "motors_speakers",
    "speakers": "motors_speakers",
    "Speakers": "motors_speakers",
    "api_usb": "api_usb",
    "encrypted api usb": "api_usb",
    "Encrypted Api USB": "api_usb",
    "ENCRYPTED API USB": "api_usb",
    "usb": "api_usb",
    "USB": "api_usb",
    "drive": "api_usb",
    "Drive": "api_usb",
    "DRIVE": "api_usb",
    "usb drive": "api_usb",
    "USB Drive": "api_usb",
    "USB DRIVE": "api_usb"
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

        # Case 1: Single-token movement ("n", "south", "lobby", "d2015").
        if len(tokens) == 1 and (
            first_token in ROOM_ALIASES or first_token in ROOM_NAME_ALIASES
        ):
            return ("go", {"target": resolve_room_target(cleaned), "raw": cleaned})

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

        if verb == "clear":
            return ("clear", {"raw": arg_str})

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
                    "message": "Go where? Specify a direction (north, south, east, west) or room name."})
            target = resolve_room_target(arg_str)
            return ("go", {"target": target, "raw": arg_str})

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