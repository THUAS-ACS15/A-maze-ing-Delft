"""Rendering of the current room.

:func:`render` is the single entry point used after almost every command to redraw the screen (header, narrative
text, footer). It lives in its own module so that state, engine and room modules can all import it without cycles.
"""

from __future__ import annotations

from .display import header, footer
from .display import out
from .state import state

def render(text: str | None = None, asset: str | None = None) -> None:
    """Redraw the current room: header, narrative, optional ASCII asset and footer.

    Side effect: un-pauses the game timer (``state["game_state"]["duration"]["pause"] = False``). Screens that pause
    the clock (inventory, help, status, scoreboard) do not call this, so the clock resumes as soon as the player is
    back in a room view.

    Args:
        text: Narrative to show. Defaults to the current room's ``description``. May contain ANSI codes.
        asset: Optional pre-rendered ASCII art printed between the header and the narrative.

    Raises:
        KeyError: If the current room id is missing from ``state["rooms"]``.
    """
    state["game_state"]["duration"]["pause"] = False
    header()
    current_room = state["player"]["current_room"]
    room_data = state["rooms"][current_room]

    if text is None:
       text = room_data["description"]

    # Asset
    if asset:
        print(asset)
    # Room Narrative

    out(f"\n{text}\n")
    footer()