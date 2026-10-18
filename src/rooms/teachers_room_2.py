from ..room_functional import inspect as global_inspect
from ..state_functional import get_state

def inspect(target: str) -> str:
    text = global_inspect(target)
    if target == "whiteboard":
        get_state("flags", {}).set("tr2_whiteboard_inspected", True)
    return text