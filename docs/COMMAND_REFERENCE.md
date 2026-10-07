# A-maze-ing-Delft - Command Reference Manual

This manual lists all supported commands, shortcuts, directional aliases, and phase-specific mechanics in A-maze-ing-Delft.

## 1. Input Processing Rules

The engine normalizes all user input before passing it to `src/parser.py`:

- **Case-Insensitive:** `GO <ROOM>`, `Go <Room>`, and `go <north>` are treated identically.
- **Trimmed Whitespace:** Leading, trailing, and duplicate spaces are stripped (`take   battery_pack` → `take battery_pack`).
- **Noise Word Stripping:** Articles like `the`, `a`, and `an` are ignored (`take the battery_pack` → `take battery_pack`).

## 2. Exploration Phase Commands

During EXPLORATION mode, player commands follow a `VERB [TARGET]` or `VERB [ITEM] ON [TARGET]` pattern.

### Spatial Movement

| Command Syntax | Aliases / Shortcuts          | Example              | Target Action / Result                            |
| -------------- | ---------------------------- | -------------------- | ------------------------------------------------- |
| `go [room]`    | `move [room]`, `walk [room]` | `go teachers_room_1` | Moves player to the destination room if unlocked. |

### Environment & Inspection

| Command Syntax     | Aliases / Shortcuts                                   | Example                                | Target Action / Result                                              |
| ------------------ | ----------------------------------------------------- | -------------------------------------- | ------------------------------------------------------------------- |
| `look`             | `l`, `ls`, `examine room`                             | `look`                                 | Displays current room title, description, visible items, and exits. |
| `inspect [target]` | `examine [target]`, `read [target]`, `check [target]` | `inspect desk`, `inspect battery_pack` | Inspects a room object or item.                                     |

### Inventory Management

| Command Syntax | Aliases / Shortcuts                           | Example             | Target Action / Result                                                    |
| -------------- | --------------------------------------------- | ------------------- | ------------------------------------------------------------------------- |
| `inventory`    | `inv`, `i`                                    | `inventory`         | Lists all items currently held in player inventory.                       |
| `take [item]`  | `get [item]`, `grab [item]`, `pick up [item]` | `take battery_pack` | Transfers an item from the current room floor into player inventory.      |
| `drop [item]`  | `discard [item]`                              | `drop battery_pack` | Transfers an item from player inventory back onto the current room floor. |

### Interactions & Puzzles

| Command Syntax           | Aliases / Shortcuts                                  | Example                    | Target Action / Result                                                   |
| ------------------------ | ---------------------------------------------------- | -------------------------- | ------------------------------------------------------------------------ |
| `use [item]`             | `apply [item]`                                       | `use keycard_lvl1`         | Uses an item in the current context (e.g., swiping a keycard at a door). |
| `use [item] on [target]` | `apply [item] to [target]`, `put [item] on [target]` | `use keycard_lvl1 on door` | Direct interaction between an inventory item and a room interactable.    |
| `enter [code]`           | `type [code]`, `unlock [code]`                       | `enter 2015`               | Submits a keypad code to an interactable.                                |

### System & Meta Commands

| Command Syntax | Aliases / Shortcuts | Example | Target Action / Result                                              |
| -------------- | ------------------- | ------- | ------------------------------------------------------------------- |
| `save`         | `save game`         | `save`  | Writes current in-memory state to `saves/save_slot_1.json`.         |
| `load`         | `load game`         | `load`  | Restores game state from `saves/save_slot_1.json`.                  |
| `help`         | `?`, `commands`     | `help`  | Renders a quick summary of command verbs inside the CLI.            |
| `quit`         | `exit`, `q`         | `quit`  | Prompts for save verification, then cleanly terminates application. |

## 3. Assembly Phase Commands

When all 7 required components are placed on the workbench in `lab_d2001`, `game_phase` transitions to `"ASSEMBLY"`.

| Command Syntax      | Aliases / Shortcuts         | Example             | Target Action / Result                                              |
| ------------------- | --------------------------- | ------------------- | ------------------------------------------------------------------- |
| `activate`          | `power on`, `start`, `boot` | `activate`          | Triggers boot sequence animation and transitions game to CHAT_MODE. |
| `inspect workbench` | `check workbench`           | `inspect workbench` | Displays list of installed hardware parts vs. missing components.   |
| `look`              | `l`, `ls`                   | `look`              | Re-renders terminal header and workbench state.                     |

> **Note:** Navigation (`go`) and item dropping are disabled while in the Assembly state until the unit is activated.

## 4. Phase 3 (AI Chat Mode) Mechanics

Once `activate` is executed, standard command verbs are bypassed. All user input is treated as freeform natural language.

### Input Handling Pipeline

```text
Player Input -> src/client.py -> OpenAI Chat Completions API -> Streaming Response
```

## 5. Parser Error & Feedback Matrix

| Scenario / Error Condition | Parser / Engine Output                                                          |
| -------------------------- | ------------------------------------------------------------------------------- |
| Unknown Command            | `I don't understand that command. Type 'help' for a list of available actions.` |
| Missing Target Parameter   | `What do you want to [verb]? (e.g., '[verb] battery_pack')`                     |
| Item Not in Room           | `There is no '[item]' here.`                                                    |
| Item Not in Inventory      | `You are not carrying '[item]'.`                                                |
| Target Door Locked         | `The door is locked. Access requires: Level-1 Staff Keycard.`                   |
| Invalid Direction          | `You cannot go [direction] from here.`                                          |
| Incorrect Keypad Code      | `Keypad buzzes red: Incorrect code entered.`                                    |
