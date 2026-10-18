from ..state_functional import get_state
from ..room_functional import use as global_use

DESK_CODE = "2015"
REWARD = "keycard_lvl1"

def inspect(target) -> str | None:
    if target != "desk":
        return None
    flags = get_state("flags", {})
    if flags.get("tr1_desk_unlocked"):
        return "The desk drawer is open. You already took the keycard."
    desk = get_state("interactables", {})
    hint = desk.get(
        "hint", "Keypad hint: 'Room number where CS101 was held.'"
        ) if isinstance(desk, dict) else desk
    return f"A locked desk with a keypad. {hint} (use: 'use 2015 on desk')"

def use(item_id: str, target: str | None) -> tuple[bool, str]:
    state = get_state()
    # Accept both `use 2015 on desk` and `enter 2015` style via item_id==code.
    code = item_id if (target == "desk" or target is None) else None
    if target == "desk" or (target is None and item_id == DESK_CODE):
        flags = get_state(key="flags")
        if flags.get("tr1_desk_unlocked"):
            return False, "The desk is already unlocked."
        if code == DESK_CODE:
            flags["tr1_desk_unlocked"] = True
            inv = get_state("player", {}).setdefault("inventory", [])
            if REWARD not in inv:
                inv.append(REWARD)
            return True, "Keypad clicks green. You obtain the Level-1 Staff Keycard."
        return False, "Keypad buzzes red: Incorrect code entered."
    return global_use(item_id, target, state)