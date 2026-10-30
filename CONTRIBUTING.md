# Contributing to A-maze-ing-Delft

Thank you for contributing to Project A-maze-ing-Delft. This guide covers the current repository layout, state and save conventions, and the checks a pull request must pass.

## 1. Branching and Git workflow

All work should happen on a dedicated branch created from `main`.

- `main` — production branch. It should always contain runnable code.
- `feature/<short-description>` — new gameplay mechanics, engine work, or tooling. Example: `feature/d2031-hint-system`.
- `content/<short-description>` — room, dialogue, item, or puzzle content. Example: `content/teachers-room-4-filesystem`.
- `fix/<bug-description>` — bug fixes. Example: `fix/save-slot-preview`.
- `docs/<short-description>` — documentation-only changes. Example: `docs/architecture-refresh`.

### Commit messages

Use concise, imperative messages in the Conventional Commits style:

```text
feat(rooms): add optional hint to the D2.031 cipher
fix(save): keep inventory rows in sync when loading a slot
docs(architecture): document the dispatcher and SQLite persistence
content(data): expand the Teacher's Room 4 filesystem
```

## 2. Code standards

- **Runtime:** Python 3.10+ is supported by the current code and CI. `pyproject.toml` declares 3.12+; align the metadata and CI before relying on packaging.
- **Style:** follow PEP 8 naming conventions: `snake_case` for variables and functions, `PascalCase` for classes, and `UPPER_SNAKE_CASE` for constants.
- **Types:** add type hints to public function signatures in `rooms/`, `utilities/`, `data/`, and `tests/`. The project runs `mypy .`.
- **Docstrings:** add a docstring to every new function, class, and module. Explain behaviour and arguments; do not just restate the function name.
- **Imports:** group standard-library, third-party, and local imports. Local imports come from `rooms`, `utilities`, `data`, and `assets`.
- **Linting:** `ruff check .` is the enforced linter. Use a targeted `# noqa` only when the code is intentionally long (dialogue, ANSI art) or deliberately ordered. Prefer a file-level `# ruff: noqa: E501` for prose/art banks over scattering dozens of inline suppressions.
- **Formatting:** `black` is listed in `requirements.txt`, but CI currently enforces Ruff and mypy rather than Black. Match the surrounding style.

Do not create a new `src/` package. The old `src/` engine was removed; the current entry point is `main.py` and the game code lives in `rooms/` and `utilities/`.

## 3. Architecture and state rules

### Runtime state

`main.py` creates a single plain `state` dictionary and passes it to every room handler through `rooms.dispatcher.enter_room()`.

- Room handlers receive `state` and may read or update it directly. There is no `StateManager` class.
- Keep state values to plain Python primitives and containers: `str`, `int`, `float`, `bool`, `list`, and `dict`.
- Use the existing room IDs (`lobby`, `teachersroom1`, `classroomd2015`, etc.). Inventory values are display strings such as `"Student ID card"` and `"Wi-Fi Credentials"`.
- Do not attach custom class instances, functions, or lambdas to `state`.

### Adding a state field

When you add a field that must survive a save/load cycle:

1. Add it to the initial dictionary in `main.py`.
2. Add a column or row mapping in `utilities/save_management.py` (`save_game()` and `load_save()`).
3. Update `docs/STATE_SCHEMA.md`.
4. Add a test in `tests/` if the field affects save/load or room completion.

Transient fields (for example, a puzzle's current step) do not need to be persisted, but say so in the docstring and in `docs/STATE_SCHEMA.md`.

### Adding or changing a room

1. Create or edit the room module in `rooms/`.
2. Register the handler in `ROOM_HANDLERS` in `rooms/dispatcher.py`.
3. If the room is gated, add its minimum `current_objective_id` and rejection message to `ROOM_REQUIREMENTS`.
4. Add the room ID to `state["visited"]` and `state["completed"]` in `main.py` if the room should appear in the map and completion statistics.
5. Add its display name to `utilities/status_bar.py` and `utilities/game_map.py`.
6. Update `docs/GAME_DESIGN.md`, `docs/COMMAND_REFERENCE.md`, and `docs/STATE_SCHEMA.md`.

### Content and dialogue

- Room dialogue lives in `data/story_dialogue_bank.py`.
- Look-around descriptions live in `data/look_around_dialogue_bank.py`.
- Objective text lives in `data/objective_dialogue_bank.py`.
- Item descriptions and terminal art live in `data/item_description_bank.py` and `data/item_render_bank.py`.
- Do not reintroduce `data/game_state.json` or `data/system_prompt.txt`; neither file exists in the current design.

### Paths and secrets

- Do not hardcode absolute paths. Use `pathlib` or paths relative to the repository.
- API keys belong in `.env`, which is ignored by Git. The supported key names are `GEMINI_API_KEY`, `GROQ_API_KEY`, and `OPENAI_API_KEY`.
- `.env.test` lists key names only; never commit values.
- The current game does not require any API key. The AI module is optional and currently unwired.

## 4. Testing and CI

Run the checks locally before opening a pull request:

```bash
python -m ruff check .
python -m mypy .
python -m pytest -q
```

The test suite currently has 93 tests in `tests/`:

- `test_display_menu.py`
- `test_inventory_viewer.py`
- `test_save_management.py`
- `test_shell.py`
- `test_teachers_room_4.py`

CI is defined in `.github/workflows/lint-typecheck-testing.yml`. It installs `requirements.txt`, then runs Ruff, mypy, and pytest on pushes and pull requests to `main`. Add tests for new save/load behaviour, shell commands, room dispatch, or puzzle state changes.

## 5. Pull request checklist

- [ ] The game starts with `python main.py`.
- [ ] `python -m ruff check .` passes.
- [ ] `python -m mypy .` passes.
- [ ] `python -m pytest -q` passes.
- [ ] New rooms are registered in `rooms/dispatcher.py` and gated correctly.
- [ ] New state fields are initialised in `main.py`, persisted in `utilities/save_management.py` when needed, and documented in `docs/STATE_SCHEMA.md`.
- [ ] New dialogue or item text is in the appropriate `data/` bank.
- [ ] No secrets, local database files (`saves.db`, `scoreboard.db`), or virtual-environment files are committed.
- [ ] New functions and classes have docstrings.
- [ ] The README and relevant files under `docs/` are updated.

## 6. Documentation map

Keep these files consistent with the code:

- `README.md` — setup, controls, layout, and limitations.
- `docs/ARCHITECTURE.md` — runtime flow, modules, persistence, and known gaps.
- `docs/COMMAND_REFERENCE.md` — shared and room-specific commands.
- `docs/GAME_DESIGN.md` — story, objective chain, room graph, items, and puzzle solutions.
- `docs/STATE_SCHEMA.md` — runtime state fields and SQLite schemas.
- `docs/PROMPT_ENGINEERING.md` — optional LangChain module reference.

If a change makes one of these documents wrong, update it in the same pull request.
