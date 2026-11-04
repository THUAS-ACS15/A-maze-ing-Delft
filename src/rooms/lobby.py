"""Lobby room.

No lobby-specific logic is needed: its data lives in ``data/default_state.json`` and the lobby ``terminal``
interaction is handled by :func:`src.engine.inspect`.
"""
from src.assets.logo import logo
from src.room import render
from src.state import state


def inspect_terminal() -> None:
    render(text=state["rooms"]["lobby"]["interactables"]["terminal"], asset=logo)
    return None
