"""Teachers Room 2.

No room-specific logic is needed: its data lives in ``data/default_state.json`` and the ``whiteboard`` interaction
is handled by :func:`src.engine.inspect`.
"""
from src.room import render
from src.state import state


def inspect_whiteboard() -> None:
    state["flags"]["tr2_whiteboard_inspected"] = True
    whiteboard = state["rooms"]["teachers_room_2"]["interactables"]["whiteboard"]
    render(text=whiteboard)
    return None