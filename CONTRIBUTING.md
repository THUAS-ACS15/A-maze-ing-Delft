# Contributing to A-maze-ing-Delft

Thank you for contributing to Project A-maze-ing-Delft! To ensure smooth collaboration and maintain engine stability, please follow these guidelines when creating features, fixing bugs, or expanding game content.

## 1. Branching & Git Workflow
We use a simple feature-branch workflow. All work should be developed on dedicated branches off main.

* `main`: Production branch. Must always contain working, runnable code.
* `feature/<short-description>`: New gameplay mechanics, engine features, or AI integration (e.g., `feature/parser-alias-matching`).
* `content/<short-description>`: Content-only updates to rooms, items, or puzzles in game_state.json (e.g., `content/add-teachers-room-4-puzzle`).
* `fix/<bug-description>`: Bug fixes and patch work (e.g., `fix/inventory-drop-lock-bug`).

### Commit Message Standards
Use concise, imperative commit messages in line with Conventional Commits:

feat(parser): add support for room direction shortcuts (n/s/e/w)
fix(state): resolve edge case where keycards were consumed on failed unlock
docs(state): update game_state documentation with new flags
content(map): add item descriptions to classroom D 2035

## 2. Code Standards & Python Conventions
* Python Version: Target Python 3.10+.
* Code Style: Follow PEP 8 naming conventions (snake_case for variables/functions, PascalCase for classes, UPPER_SNAKE_CASE for constants).
* Type Annotations: Use Python type hints on all function signatures in src/.

`def move_player(destination_room_id: str) -> bool:`

* Imports: Group imports logically at the top of the file:
    1. Standard library (json, os, sys)
    2. Third-party dependencies (openai, rich, art)
    3. Local application modules (from src.state import GameStateManager)

## 3. Architecture & State Management Rules
All code merged into the repository must strictly adhere to the project state principles:
* Do not directly mutate the state dictionary outside of src/state.py
* Create dedicated helper methods in StateManager (e.g., add_inventory_item(), unlock_room()) to mutate values safely.
* Everything in game_state must remain pure JSON data (dict, list, str, int, bool).
* Never attach custom objects, classes, or function references directly to the state dictionary.
* Room connections, item properties, and puzzle locks belong inside data/game_state.json.
* Never hardcode room layout, inventory requirements, or item behaviors

4. Pull Request (PR) Checklist
Before submitting a PR for review, ensure you have completed the following steps:

* [] Code runs without exceptions from `python main.py.`
* [] All link check return true when `ruff check .` 
* [] All checks return true when `mypy .`
* [] No hardcoded absolute paths exist (use `os.path.join `for file paths).
* [] Any new state attributes added to `data/game_state.json `are documented in the State Architecture documentation.
* [] Environment secrets (like `OPENAI_API_KEY`) are loaded via `.env` and never committed to Git.
* [] All new functions include standard Python docstrings.