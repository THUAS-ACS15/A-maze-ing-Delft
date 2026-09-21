# -----------------------------------------------------------------------------
# File: __init__.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------
import importlib

from .lobby import lobby
from .project_room_1 import project_room_1
from .lab_d2001 import lab_d2001
from .store import store
from .teachersroom1 import teachersroom1
from .teachersroom2 import teachersroom2

try:
    from .front_desk import front_desk
except Exception:
    front_desk = None

try:
    from .project_room_2 import project_room_2
except Exception:
    project_room_2 = None

# Dynamically import classroom_d2.015 since it contains a dot in the filename
try:
    d2015_module = importlib.import_module(".classroom_d2.015", package=__name__)
    classroom_d2_015 = getattr(d2015_module, "classroom_d2_015", getattr(d2015_module, "classroom_d2015", None))
except Exception:
    try:
        from .classroom_d2_015 import classroom_d2_015
    except Exception:
        classroom_d2_015 = None
