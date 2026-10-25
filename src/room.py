from __future__ import annotations

from .display import header, footer
from .display import out
from .state import state

def render(text: str | None = None, asset: str | None = None) -> None:
    """Displays current location, description, exits, items, and interactable features."""
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    if text is None:
       text = room_data["description"]
    header()

    # Asset
    if asset:
        print(asset)
    # Room Narrative

    out(f"\n{text}\n")
    footer()