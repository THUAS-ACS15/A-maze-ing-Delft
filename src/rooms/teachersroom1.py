
from ..room import Room


class TeachersRoom1(Room):
    """Desk keypad puzzle: code '2015' -> Level-1 Staff Keycard."""

    DESK_CODE = "2015"
    REWARD = "keycard_lvl1"

    def on_inspect(self, target: str, state) -> str:
        if target != "desk":
            return super().on_inspect(target, state)
        flags = state.state.setdefault("flags", {})
        if flags.get("tr1_desk_unlocked"):
            return "The desk drawer is open. You already took the keycard."
        desk = self.interactables.get("desk", {})
        hint = desk.get("hint", "Keypad hint: 'Room number where CS101 was held.'") if isinstance(desk, dict) else desk
        return f"A locked desk with a keypad. {hint} (use: 'use 2015 on desk')"

    def on_use(self, item_id: str, target: str | None, state) -> tuple[bool, str]:
        # Accept both `use 2015 on desk` and `enter 2015` style via item_id==code.
        code = item_id if (target == "desk" or target is None) else None
        if target == "desk" or (target is None and item_id == self.DESK_CODE):
            flags = state.state.setdefault("flags", {})
            if flags.get("tr1_desk_unlocked"):
                return False, "The desk is already unlocked."
            if code == self.DESK_CODE:
                flags["tr1_desk_unlocked"] = True
                inv = state.state.setdefault("player", {}).setdefault("inventory", [])
                if self.REWARD not in inv:
                    inv.append(self.REWARD)
                return True, "Keypad clicks green. You obtain the Level-1 Staff Keycard."
            return False, "Keypad buzzes red: Incorrect code entered."
        return super().on_use(item_id, target, state)

