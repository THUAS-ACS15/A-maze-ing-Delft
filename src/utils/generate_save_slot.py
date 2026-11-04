"""Automatic save-slot naming."""

import re

def next_save_slot(name: str) -> str:
    """Return the next unused auto-save slot for ``name``.

    Slots are named ``<name>_save_slot_<n>``; ``n`` is one more than the highest number found in ``data/saves``, so
    gaps from deleted files are not reused.

    Args:
        name: Player name used as the slot prefix.

    Returns:
        The next slot name (without the ``.json`` extension).
    """
    from src.state import SAVE_DIR

    prefix = f"{name}_save_slot_"
    numbers = []
    if SAVE_DIR.exists():
        for path in SAVE_DIR.glob(f"{prefix}*.json"):
            match = re.fullmatch(rf"{re.escape(prefix)}(\d+)\.json", path.name)
            if match:
                numbers.append(int(match.group(1)))
    return f"{prefix}{max(numbers, default=0) + 1}"