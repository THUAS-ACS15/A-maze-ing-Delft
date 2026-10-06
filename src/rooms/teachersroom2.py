from ..room import Room


class TeachersRoom2(Room):
    """Whiteboard puzzle: inspecting reveals Wi-Fi pass, sets flag."""

    def on_inspect(self, target: str, state) -> str:
        text = super().on_inspect(target, state)
        if target == "whiteboard":
            state.state.setdefault("flags", {})["tr2_whiteboard_inspected"] = True
        return text