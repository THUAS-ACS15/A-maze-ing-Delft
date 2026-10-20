from typing import Any

from ..assets.logo import LOGO
from ..state import state


def inspect_terminal() -> tuple[Any, str]:
    raw_text = state["rooms"]["lobby"]["interactables"]["terminal"]
    full_msg = raw_text if isinstance(raw_text, str) else str(raw_text)
    return LOGO, full_msg