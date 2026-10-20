from ..room_functional import inspect
from ..state_functional import state


def inspect_whiteboard(target: str) -> tuple[bool, str]:
    ok, message = inspect(target)
    if target == "whiteboard":
        state["flags"]["tr2_whiteboard_inspected"] = True
    return ok, message