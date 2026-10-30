# ACS15 A-maze-ing-Delft

A terminal adventure game built as the Q1 project for the Applied Computer Science (ACS) programme at The Hague University of Applied Sciences (THUAS).

**A-maze-ing-Delft** is set in the THUAS Delft building. The player is locked inside after hours and discovers an unfinished robotics project called **A.I.G.I.S.** (Autonomous Intellect & Generalized Interface System). By exploring the campus, solving room puzzles, and collecting the missing hardware, the player can assemble A.I.G.I.S. and escape.

## Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the game](#running-the-game)
- [Controls](#controls)
- [Saves and scoreboard](#saves-and-scoreboard)
- [Project layout](#project-layout)
- [Quality checks](#quality-checks)
- [Documentation](#documentation)
- [Known gaps / not yet wired](#known-gaps--not-yet-wired)

## Features

- **15 registered rooms**: the lobby, three connecting corridors, and eleven challenge rooms.
- **8-step objective chain** tracked by `current_objective_id`, from registration at the front desk to assembling A.I.G.I.S. in Lab D2.001.
- **Optional content**: Project Room 1, Classroom D2.031, and the Equinox Student Society quiz are not required for the main ending.
- **Three SQLite save slots** with room, inventory, objective, and play-time data.
- **Inventory viewer** with item art and descriptions from the `data/` banks.
- **Campus map** that marks unvisited, visited, and completed rooms.
- **Status screen and status bar** showing room, exploration percentage, completion state, and elapsed time.
- **Virtual NixOS terminal** in Teacher's Room 4 with a small in-memory filesystem.
- **Ending cutscene** and an optional local scoreboard entry.
- **Optional AI module** in `utilities/chat.py` and `utilities/langchain.py`. It is present in the repository but is not connected to the current game ending.

## Requirements

- **Python 3.10 or newer.** The project metadata declares Python 3.12+; the CI workflow currently uses 3.10 and the Docker image uses 3.11. Use 3.12+ if you want to match `pyproject.toml`.
- `pip`
- Optional: Docker and Docker Compose
- Optional: API keys for the unused AI module (`GEMINI_API_KEY`, `GROQ_API_KEY`, or `OPENAI_API_KEY`). No key is needed to play the game.

## Installation

### Standard setup

```bash
git clone https://github.com/THUAS-ACS15/A-maze-ing-Delft.git
cd A-maze-ing-Delft
python -m venv .venv
```

Activate the virtual environment:

```powershell
# Windows PowerShell / CMD
.venv\Scripts\activate
```

```bash
# macOS / Linux
source .venv/bin/activate
```

Install the dependencies and start the game:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python main.py
```

`main.py` also runs `install_dependencies.check_dependencies()` before importing the rest of the game. That check compares the installed packages with `requirements.txt` and attempts to install anything missing. Installing manually first is still recommended because it gives you clearer error messages.

### Docker

```bash
docker compose up --build
```

The Compose configuration keeps stdin open and allocates a TTY, which the terminal menus need.

## Running the game

Start the game from the repository root:

```bash
python main.py
```

The main menu has five options:

| Option | Behaviour |
| --- | --- |
| `CONTINUE` | Opens the load menu for save slots 1–3. |
| `NEW GAME` | Starts a fresh game with the default state. |
| `CREDITS` | Shows the scrolling credits, then returns to the menu. |
| `SCOREBOARD` | Shows local completed runs, ten entries per page. |
| `EXIT` | Leaves the game. |

`NEW GAME` does not ask for a save slot; it starts with the default state. Use `save` or `pause` in a room to choose a slot later.

## Controls

### Menus

- **Up / Down arrow keys**: move the selection.
- **Enter**: confirm.

### Rooms

Most rooms share these commands. Aliases and availability differ by room; see [docs/COMMAND_REFERENCE.md](docs/COMMAND_REFERENCE.md) for the full matrix.

| Command | Purpose |
| --- | --- |
| `look around` | Describe the room, clues, exits, and objective. |
| `go` | Open the room-selection menu. |
| `?` | Show the room's help. |
| `status` / `check status` | Show progress, inventory, room flags, and time. |
| `map` | Show the campus map. |
| `inv` / `inventory` | Open the inventory viewer. |
| `save` / `pause` | Open the save-slot menu. |
| `quit` | Quit the game. In Teacher's Room 4, use `leave` or `exit` instead. |

Room-specific commands include `inspect <object>`, `take <item>`, `answer <answer>`, `talk to teacher`, `look at database`, `start puzzle`, `start stacking`, and `sit down`. The Teacher's Room 4 computer opens a virtual shell with `ls`, `cd`, `pwd`, `cat`, `find`, `tree`, `clear`, `whoami`, `exit`, and `help`.

## Saves and scoreboard

The game stores local data in two SQLite files created in the working directory (normally the repository root):

- **`saves.db`** — three save slots. The tables are `general`, `room_visited_status`, `room_completed_status`, `inventory`, and `store_items`.
- **`scoreboard.db`** — completed runs, ordered by exploration percentage (descending) and time (ascending).

Both files are listed in `.gitignore` and should not be committed. The game no longer uses `user_state.json`, `game_state.json`, `save_slot_*.json`, or any other JSON save format.

Room-local puzzle progress (for example, an in-progress locker or rover puzzle) is not written to `saves.db`. Save after finishing a room puzzle if you want that room's completion flag and reward preserved.

## Project layout

```text
A-maze-ing-Delft/
├── main.py                     # Entry point: dependency check, menu, room loop
├── install_dependencies.py     # Checks/installs packages from requirements.txt
├── rooms/
│   ├── dispatcher.py           # Room registry and objective gates
│   └── *.py                    # One module per room
├── utilities/
│   ├── main_menu.py            # Arrow-key main menu
│   ├── save_management.py      # SQLite save/load layer
│   ├── save_gui.py             # Save and load slot screens
│   ├── scoreboard.py           # Local scoreboard
│   ├── status_bar.py           # In-game status bar
│   ├── game_map.py             # Campus map
│   ├── inventory_viewer.py     # Interactive inventory
│   ├── shell.py                # Virtual shell used in Teacher's Room 4
│   ├── chat.py                 # Optional, currently unwired AI chat helper
│   └── langchain.py            # Optional LangChain provider factory
├── data/                       # Dialogue, objective, item, and render banks
├── assets/                     # Terminal art assets
├── tests/                      # Pytest suite
├── docs/                       # Architecture, design, commands, state schema
├── requirements.txt
├── pyproject.toml
├── Dockerfile
└── docker-compose.yml
```

## Quality checks

Run the same checks used by the CI workflow:

```bash
python -m ruff check .
python -m mypy .
python -m pytest -q
```

The suite currently contains 93 tests. CI runs on pushes and pull requests to `main`; see [.github/workflows/lint-typecheck-testing.yml](.github/workflows/lint-typecheck-testing.yml).

## Documentation

- [Architecture](docs/ARCHITECTURE.md) — runtime flow, module boundaries, persistence, and known gaps.
- [Command reference](docs/COMMAND_REFERENCE.md) — shared and room-specific commands.
- [Game design](docs/GAME_DESIGN.md) — story, objective chain, room graph, items, and puzzle solutions.
- [State schema](docs/STATE_SCHEMA.md) — runtime state fields and SQLite schemas.
- [AI integration reference](docs/PROMPT_ENGINEERING.md) — the optional LangChain module and why it is not part of the current ending.
- [Contributing](CONTRIBUTING.md) — branch, code, test, and review conventions.

## Known gaps / not yet wired

These are implementation gaps in the current code, not features the documentation is hiding:

- `rooms/store.py` exists, but the store is not registered in `rooms/dispatcher.py`, so it cannot be reached during normal play. The `coin_balance` and `store_available_items` state fields it expects are also not initialised.
- The AI chat helpers in `utilities/chat.py` and `utilities/langchain.py` are not imported by any room or by `main.py`. The current ending is the `play_game_complete()` cutscene.
- Coins printed by Project Room 1 are not added to a persistent balance.
- Project Room 1's Locker 2 needs a brass key that the current room code does not make obtainable.
- Classroom D2.031 awards a Classroom 2.021 key, while the objective text mentions memory sticks in D2.015 and D2.031. D2.021 does not exist as a room.
- The Lab D2.001 box puzzle does not exit automatically after the boxes are arranged. Type `quit` inside the puzzle to leave it and record completion.
- Some room-local puzzle state is transient and is not saved: Project Room 1's opened lockers, Classroom D2.015's rover stages, Classroom D2.035's seating flag, and Project Room 2's colour order.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md#known-gaps) for a fuller list.
