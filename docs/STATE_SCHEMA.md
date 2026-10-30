# Game State & Persistence Schema

This document describes the runtime state dictionary created in `main.py` and the SQLite files used to save progress and scores.

The old `game_state` JSON template, JSON save-slot files, and `StateManager` design no longer exist. The current game uses a plain Python dictionary plus `saves.db` and `scoreboard.db`.

## Contents

- [Runtime state](#runtime-state)
- [Room key sets](#room-key-sets)
- [Objective state](#objective-state)
- [Transient and missing fields](#transient-and-missing-fields)
- [SQLite saves](#sqlite-saves)
- [SQLite scoreboard](#sqlite-scoreboard)
- [Save/load behaviour](#saveload-behaviour)
- [Data integrity rules](#data-integrity-rules)
- [Known gaps](#known-gaps)

## Runtime state

`main.py` initializes this dictionary:

```python
state: dict = {
    "player_name": "",
    "current_room": "lobby",
    "previous_room": None,
    "time_elapsed": 0.0,
    "start_time": time.time(),
    "has_intro_played": False,
    "is_gametime_paused": False,
    "current_objective_id": 0,
    "student_id_obtained": False,
    "visited": { ... },
    "completed": { ... },
    "inventory": [],
}
```

| Field | Type | Initial value | Persisted? | Purpose |
| --- | --- | --- | --- | --- |
| `player_name` | `str` | `""` | Yes — `general.player_name` | Name entered at the Front Desk; used by the scoreboard. |
| `current_room` | `str` | `"lobby"` | Yes — `general.current_room` | Room ID currently being executed. |
| `previous_room` | `str \| None` | `None` | Yes — `general.previous_room` | Room to return to when a gate rejects the player. Most room handlers set it to their own ID on entry; Project Room 1 leaves the previous value unchanged. |
| `time_elapsed` | `float` | `0.0` | Yes — `general.time_elapsed` | Accumulated active play time in seconds. |
| `start_time` | `float` | `time.time()` | No | Start of the current active session. Reset on load. |
| `has_intro_played` | `bool` | `False` | Yes — `general.has_intro_played` | Prevents the intro from replaying after a load. |
| `is_gametime_paused` | `bool` | `False` | No | Pauses play-time accounting while the intro, status screen, map, or virtual shell is open. Save/load menus do not toggle it. Reset to `False` on load. |
| `current_objective_id` | `int` | `0` | Yes — `general.current_objective_id` | Main progression counter, `0`–`8`; also used by room gates and the Lab assembly check. |
| `student_id_obtained` | `bool` | `False` | Yes — `general.student_id_obtained` | Special flag used by the Lobby's opening message. |
| `visited` | `dict[str, bool]` | Eleven `False` values | Yes — `room_visited_status` | Challenge-room visit flags used by the map. |
| `completed` | `dict[str, bool]` | Eleven `False` values | Yes — `room_completed_status` | Challenge-room completion flags used by the status screen, map, and exploration percentage. |
| `inventory` | `list[str]` | `[]` | Yes — `inventory` | Display names of collected items. |

The state is passed by reference to every room handler. There is no `StateManager`, no `load_default_state()`, and no `game_phase` field.

## Room key sets

`visited` and `completed` contain exactly these eleven challenge rooms:

```text
labd2001
projectroom1
projectroom2
teachersroom1
teachersroom2
teachersroom4
frontdesk
equinoxstudentsociety
classroomd2015
classroomd2031
classroomd2035
```

The Lobby, East Corridor, Student Wing, and Teaching Area are not in these dictionaries. The status bar treats them as special rooms, and the map always displays their names.

The store is not in either dictionary because `rooms/store.py` is not registered in `ROOM_HANDLERS`.

## Objective state

`current_objective_id` is the single progression counter. The main chain is:

```text
0 start
1 Robot Chassis Frame (Lobby)
2 Student ID card (Front Desk)
3 Staff Keycard (Teacher's Room 1)
4 Wi-Fi Credentials (Teacher's Room 2)
5 Encrypted API & Prompt USB (Teacher's Room 4)
6 Makeshift Mic and Speaker Combo (Project Room 2)
7 A.I.G.I.S. Motherboard (Classroom D2.035)
8 Memory Sticks (Classroom D2.015)
```

Room gates in `rooms/dispatcher.py` compare this value with a minimum. For example, `teachersroom2` requires at least 3 and `teachingarea` requires at least 6.

The value is persisted in `general.current_objective_id`. The objective text itself is not stored in the state; it is looked up from `data/objective_dialogue_bank.py` by ID.

## Transient and missing fields

These fields are created or used at runtime but are not part of the initial state or the save schema:

| Field | Where it comes from | Persisted? | Notes |
| --- | --- | --- | --- |
| `projectroom1_progress` | Created by `rooms/project_room_1.py` on entry. | No | `{"opened": [...]}` for the five lockers. Re-entering the room resets it. |
| `d2015_progress` | Created by `rooms/classroom_d2015.py` on entry. | No | `{"power_set": bool, "rover_calibrated": bool}`. Re-entering resets it. |
| `seating_done` | Module-level global in `rooms/classroom_d2035.py`. | No | Skips part 1 after a successful seating answer within the same process. |
| `colors_on_projector` | Module-level global in `rooms/project_room_2.py`. | No | The current colour order; reset when the process restarts. |
| `coin_balance` | Read by `utilities/check_status.py` and `rooms/store.py`. | No | Not initialized in `main.py`; `check_status()` uses `state.get("coin_balance", 0)`. |
| `store_available_items` | Read by `rooms/store.py`. | No | Not initialized; the store is unreachable. |

The Lab box puzzle uses module-level `available_boxes` and `platforms` as well. Those are not part of `state` and are not saved.

## SQLite saves

`utilities/save_management.py` creates `saves.db` in the working directory.

### Schema

```sql
CREATE TABLE IF NOT EXISTS general (
    save_slot INTEGER PRIMARY KEY,
    player_name TEXT NOT NULL,
    current_room TEXT NOT NULL,
    previous_room TEXT,
    time_elapsed REAL NOT NULL,
    has_intro_played INTEGER NOT NULL,
    current_objective_id INTEGER NOT NULL,
    student_id_obtained INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS room_visited_status (
    save_slot INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    is_visited INTEGER NOT NULL,
    PRIMARY KEY (save_slot, room_name)
);

CREATE TABLE IF NOT EXISTS room_completed_status (
    save_slot INTEGER NOT NULL,
    room_name TEXT NOT NULL,
    is_complete INTEGER NOT NULL,
    PRIMARY KEY (save_slot, room_name)
);

CREATE TABLE IF NOT EXISTS inventory (
    save_slot INTEGER NOT NULL,
    item TEXT NOT NULL,
    PRIMARY KEY (save_slot, item)
);

CREATE TABLE IF NOT EXISTS store_items (
    save_slot INTEGER NOT NULL,
    item TEXT NOT NULL,
    PRIMARY KEY (save_slot, item)
);
```

`store_items` is created by the schema but is not read or written by the current save/load code.

### Slot model

- Slots are integers `1`, `2`, and `3`.
- `general` has one row per used slot.
- `room_visited_status` and `room_completed_status` have one row per room per slot.
- `inventory` has one row per item per slot.
- There is no JSON column and no serialized blob.

### Save functions

- `save_game(state, slot)` calls `update_elapsed_time(state)`, writes the general row, and upserts room and inventory rows.
- `load_save(slot)` reads the general row and reconstructs `visited`, `completed`, and `inventory`. It sets `start_time` to `time.time()` and `is_gametime_paused` to `False`.
- `get_save_info(slot)` reads preview data for the save/load screen: player name, current room, previous room, time, visited percentage, and completion percentage.
- `recreate_db_table()` runs the `CREATE TABLE IF NOT EXISTS` script. There is no migration system for changing existing columns.

If a slot has no `general` row, `load_save()` returns `None` and `get_save_info()` returns `None`.

## SQLite scoreboard

`utilities/scoreboard.py` creates `scoreboard.db` in the working directory.

```sql
CREATE TABLE IF NOT EXISTS scoreboard (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT NOT NULL,
    exploration_percent REAL NOT NULL,
    time_elapsed REAL NOT NULL
);
```

`add_scoreboard_entry()` inserts a row when the player opts in at the ending. `get_scoreboard_entries()` orders rows by:

```sql
ORDER BY exploration_percent DESC, time_elapsed ASC
```

The scoreboard display paginates ten entries at a time. The ending stores the player name, exploration percentage, and elapsed time.

## Save/load behaviour

1. The player opens the save menu with `save` or `pause`.
2. `display_save_menu()` accepts slot `1`, `2`, or `3`, or `quit`.
3. `save_game()` calls `update_elapsed_time()` before writing. That function adds the active session time unless `is_gametime_paused` is true; the save menu itself does not toggle the pause flag.
4. `CONTINUE` opens `display_load_menu()`, which accepts `1`, `2`, `3`, `quit`, `exit`, or `back`.
5. A successful load replaces the module-level `state` in `main.py` with the reconstructed dictionary.
6. The intro runs only if `has_intro_played` is `False`.

`time_elapsed` is accumulated in seconds. `start_time` is not saved because it is only meaningful for the current process.

## Data integrity rules

- Keep state values to plain Python types: `str`, `int`, `float`, `bool`, `list`, and `dict`.
- Do not attach classes, functions, or lambdas to state.
- Use the compact room IDs already used by the dispatcher and map (`teachersroom1`, `classroomd2015`, etc.).
- Inventory values are display strings such as `"Student ID card"` and `"Memory Sticks"`, not canonical item IDs.
- The state is not a JSON document. Do not add a `data/game_state.json` template or a JSON save path.
- When adding a persisted field, update `main.py`, `utilities/save_management.py`, this document, and the tests.
- When adding a transient field, document it here and make sure a reload cannot leave the game in a broken state.

## Known gaps

- **Transient puzzle progress is lost on load.** Opened lockers, rover stages, the seating flag, and the Project Room 2 colour order are not saved.
- **Stale rows can remain.** `save_game()` uses `INSERT OR REPLACE` but does not delete rows for items or room flags that were removed from the state.
- **No schema versioning.** `CREATE TABLE IF NOT EXISTS` cannot add columns to an existing `saves.db`; a schema change needs a migration or a fresh database.
- **Store fields are missing.** `coin_balance` and `store_available_items` are referenced by the store and status code but are not initialized or persisted.
- **The store table is unused.** `store_items` exists in `saves.db` but nothing reads or writes it.
- **The visited map is not fully represented in status.** `check_status()` uses `completed` for its "Rooms Explored" section instead of `visited`.
- **The AI history is not saved.** `utilities/chat.py` keeps conversation history in a process-local list; it is not part of `saves.db`.
