import re

from .utils.aliases import ROOM_ALIASES, ROOM_NAME_ALIASES, VERB_ALIASES, ITEM_ALIASES
from .utils.username_generator import generate_random_username as random_name_generator


def normalize_room_key(raw: str) -> str:
    return " ".join(raw.strip().lower().replace("_", " ").split())

def resolve_room_target(raw: str) -> str:
    """Resolve user input to a direction ('north') or room_id ('lobby').

    Direction aliases take precedence; otherwise room name/alias map;
    falls back to the normalized raw string.
    """
    key = normalize_room_key(raw)
    if key in ROOM_ALIASES:
        return ROOM_ALIASES[key]
    if key in ROOM_NAME_ALIASES:
        return ROOM_NAME_ALIASES[key]
    underscored = key.replace(" ", "_")
    if underscored in ROOM_NAME_ALIASES:
        return ROOM_NAME_ALIASES[underscored]
    return underscored

def parse(raw_input: str) -> tuple[str, dict]:
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
        return "EMPTY", {}

    tokens = cleaned.split()
    first_token = tokens[0]

    # Case 1: Single-token movement ("n", "south", "lobby", "d2015").
    if len(tokens) == 1 and (
        first_token in ROOM_ALIASES or first_token in ROOM_NAME_ALIASES
    ):
        return "go", {"target": resolve_room_target(cleaned), "raw": cleaned}

    # Resolve primary verb
    verb = VERB_ALIASES.get(first_token)
    if not verb:
        return "UNKNOWN", {"raw": raw_input}

    # Argument processing
    args = tokens[1:]
    arg_str = " ".join(args)

    if verb == "look":
        return "look", {"raw": arg_str}

    if verb == "inventory":
        return "inventory", {"raw": arg_str}

    if verb == "help":
        return "help", {"raw": arg_str}

    if verb == "clear":
        return "clear", {"raw": arg_str}

    if verb == "register":
        username = args[0] if args else random_name_generator()
        return "register", {"target": username, "raw": arg_str}

    if verb == "login":
        if not args:
            return ("INVALID", {
                "message": "You have to enter a valid username (e.g., 'login user1')."})
        username = args[0]
        return "login", {"target": username, "raw": arg_str}

    if verb == "save":
        slot = args[0] if args else None
        return "save", {"target": slot, "raw": arg_str}

    if verb == "saves":
        return "saves", {"raw": arg_str}

    if verb == "load":
        if not args:
            return ("INVALID", {
                "message": "Enter a valid slot to load (e.g., 'load user_slot_1')."})
        slot = args[0]
        return "load", {"target": slot, "raw": arg_str}

    if verb == "restart":
        return "restart", {"raw": arg_str}

    if verb == "quit":
        return "quit", {"raw": arg_str}

    if verb == "activate":
        return "activate", {"raw": arg_str}

    if verb == "go":
        if not args:
            return ("INVALID", {
                "message": "Go where? Specify a direction (north, south, east, west) or room name."})
        target = resolve_room_target(arg_str)
        return "go", {"target": target, "raw": arg_str}

    if verb == "inspect":
        if not args:
            return ("INVALID", {
                "message": "Inspect what? Specify an item or object (e.g., 'inspect desk')."})
        target_id = ITEM_ALIASES.get(arg_str, arg_str)
        return "inspect", {"target": target_id, "raw": arg_str}

    if verb == "take":
        if not args:
            return ("INVALID", {
                "message": "Take what? Specify an item (e.g., 'take battery_pack')."})
        # Handle "pick up <item>"
        if first_token == "pick" and args and args[0] == "up":
            item_tokens = args[1:]
            arg_str = " ".join(item_tokens)
        target_id = ITEM_ALIASES.get(arg_str, arg_str)
        return "take", {"target": target_id, "raw": arg_str}

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
            return "use", {"target": item_id, "indirect": None, "raw": arg_str}

    return "UNKNOWN", {"raw": raw_input}