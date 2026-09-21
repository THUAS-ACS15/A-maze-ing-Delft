# -----------------------------------------------------------------------------
# File: __init__.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# -----------------------------------------------------------------------------

import importlib.util
from pathlib import Path

from .lobby import enterLobby
from .store import enterStore
from .lab_d2001 import enterLabD2001
from .teachersroom1 import enterTeachersRoom1
from .teachersroom2 import enterTeachersRoom2

from .project_room_1 import enterProjectRoom1
from .front_desk import enterFrontDesk

enterClassroomD2015 = None
_current_dir = Path(__file__).parent

for candidate_filename in ["classroom_d2.015.py", "classroom_d2_015.py"]:
    candidate_path = _current_dir / candidate_filename
    if candidate_path.exists():
        try:
            spec = importlib.util.spec_from_file_location("classroom_d2_015", str(candidate_path))
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            enterClassroomD2015 = getattr(mod, "enterClassroomD2015", None)
            if enterClassroomD2015 is not None:
                break
        except Exception:
            pass
