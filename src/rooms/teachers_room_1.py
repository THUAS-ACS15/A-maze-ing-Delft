from ..state_functional import state

DESK_CODE = "2015"
REWARD = "keycard_lvl1"


def inspect_desk() -> tuple[bool, str]:
    flags = state["flags"]
    if flags["tr1_desk_unlocked"]:
        return True, "The desk drawer is open. You already took the keycard."
    desk = state["rooms"]["teachers_room_1"]["interactables"]["desk"]
    hint = desk["hint"] if isinstance(desk, dict) else desk
    return False, f"The desk is locked with a keypad.\n{hint} (use: 'use 2015 on desk')"

def use_desk_code(item: str, target: str | None = None) -> tuple[bool, str]:
    desk = state["rooms"]["teachers_room_1"]["interactables"]["desk"]
    desk_code = desk["code"]
    flags = state["flags"]

    if target is not None and target != "desk":
        return False, "Nothing happens."

    if flags["tr1_desk_unlocked"]:
        return True, "The desk is already unlocked."

    if item == desk_code:
        flags["tr1_desk_unlocked"] = True
        inventory = state["player"]["inventory"]
        reward = desk["reward"]
        if reward not in inventory:
            inventory.append(reward)
            return True, "Keypad clicks green. You obtain the Level-1 Staff Keycard."
        return True, "You already have a Level-1 Staff keycard."

    return False, "Keypad buzzes red: Incorrect code entered."

# def use(item_id: str, target: str | None) -> tuple[bool, str]:
#     # Accept both `use 2015 on desk` and `enter 2015` style via item_id==code.
#     code = item_id if (target == "desk" or target is None) else None
#     if target == "desk" or (target is None and item_id == DESK_CODE):
#         flags = get_state(key="flags")
#         if flags.get("tr1_desk_unlocked"):
#             return False, "The desk is already unlocked."
#         if code == DESK_CODE:
#             flags["tr1_desk_unlocked"] = True
#             inv = get_state("player", {}).setdefault("inventory", [])
#             if REWARD not in inv:
#                 inv.append(REWARD)
#             return True, "Keypad clicks green. You obtain the Level-1 Staff Keycard."
#         return False, "Keypad buzzes red: Incorrect code entered."
#     return global_use(item_id, target, state)