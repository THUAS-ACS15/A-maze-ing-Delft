from ..room import inspect
from ..state import state


def inspect_whiteboard(target: str) -> tuple[bool, str]:
    ok, message = inspect(target)
    if target == "whiteboard":
        state["flags"]["tr2_whiteboard_inspected"] = True
    return ok, message