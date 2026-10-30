# Command Reference

This reference describes the commands the current game actually accepts. A-maze-ing-Delft does not have a global parser: each room reads its own input and implements its own command loop. The same word can therefore behave differently, or be unavailable, in another room.

## 1. Input handling

- Most rooms call `input().lower().strip()`. Input is case-insensitive and surrounding spaces are removed.
- Teacher's Room 2 calls `input().lower()` without `.strip()`. Leading or trailing spaces can make a command fail there.
- Commands are matched as whole strings unless the room explicitly uses `startswith()` (for example, `inspect <object>` and `answer <text>`).
- `go` opens a room-selection menu. Typing `go teachersroom1` still opens the menu; the destination text after `go` is ignored by the rooms that use the shared `go` branch.
- There are no global `north`/`south`/`east`/`west` aliases, no global `take`/`drop`/`use`, and no keypad-code command.
- `quit` usually calls `sys.exit()` immediately. In Teacher's Room 4, use `leave` or `exit` to return to the East Corridor.

## 2. Main menu

| Control | Action |
| --- | --- |
| Up / Down arrow | Move the selection. |
| Enter | Confirm. |

The menu options are `CONTINUE`, `NEW GAME`, `CREDITS`, `SCOREBOARD`, and `EXIT`.

- `CONTINUE` opens the load menu.
- `NEW GAME` starts a fresh game without a slot picker.
- `CREDITS` and `SCOREBOARD` return to the main menu when closed.
- `EXIT` leaves the program.

## 3. Shared room commands

The exact aliases vary by room. The table below lists the common forms.

| Command | Purpose | Notes |
| --- | --- | --- |
| `look around` | Describe the room and show clues/exits. | Some rooms also accept `look`, `ls`, `l`, `lk`, or `la`. Corridors accept only `look around`. |
| `?` | Show room help. | Some rooms also accept `help`. Teacher's Room 2 accepts only `?`. |
| `go` | Open the room-selection menu. | Also accepts `g`, `goto`, `move`, and sometimes `mv`. |
| `map` | Show the campus map. | Press Enter to leave the map. |
| `inv` / `inventory` | Open the inventory viewer. | Not available in Teacher's Room 4's room loop. |
| `status` / `check status` | Show the detailed status screen. | Not available in Teacher's Room 4. Most rooms open it in pause mode; type `exit` to return. The Lobby's status view returns immediately. |
| `pause` / `save` | Open the save-slot menu. | Slots 1–3; `quit` leaves the menu without saving. |
| `quit` | Quit the game. | Most rooms call `sys.exit()`. Teacher's Room 4 uses `leave`/`exit`. |

## 4. Room-by-room commands

### Lobby (`lobby`)

| Command | Result |
| --- | --- |
| `look around` / `look` / `l` / `lk` / `la` | First look gives the Robot Chassis Frame and advances objective 0 → 1. |
| `go` | Destinations: Front Desk, Student Wing, East Corridor, Teaching Area. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

The Teaching Area and Student Wing are gated by objective, so they reject entry until the relevant progress has been made.

### Front Desk (`frontdesk`)

| Command | Result |
| --- | --- |
| `inspect printer` | Starts registration. Enter a name, then an 8-digit student number. Type `cancel` at either prompt to stop. An empty name becomes `Student`. |
| `inspect counter` | Prints the counter sign. |
| `inspect logbook` | Prints the logbook entries. |
| `go` | Returns to the Lobby. |
| `look around`, `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

The help text mentions `take <item>`, but the Front Desk command loop does not implement a `take` branch.

### East Corridor (`eastcorridor`)

| Command | Result |
| --- | --- |
| `look around` | Describes the corridor. |
| `go` | Destinations: Lobby, Teacher's Room 1, Teacher's Room 2, Teacher's Room 4. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

### Teacher's Room 1 (`teachersroom1`)

| Command | Result |
| --- | --- |
| `look around` | Shows the code-snippet challenge. |
| `answer <snippet>` | Submits a code snippet. The correct snippet gives the Staff Keycard and advances objective 2 → 3; see [GAME_DESIGN.md](GAME_DESIGN.md) for the solution. |
| `go` | Returns to the East Corridor. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

### Teacher's Room 2 (`teachersroom2`)

| Command | Result |
| --- | --- |
| `look at database` | Prints the student database table. |
| `talk to teacher` | Prints the teacher's dialogue. |
| `answer <name>` | Submits the student's name. The correct name marks the puzzle solved; see [GAME_DESIGN.md](GAME_DESIGN.md). The command is lowercased. |
| `take credentials` | After solving the puzzle, gives Wi-Fi Credentials and advances objective 3 → 4. |
| `look around` | Describes the room. |
| `go` | Returns to the East Corridor. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

Remember that this room does not strip surrounding whitespace. Type commands without leading or trailing spaces.

### Teacher's Room 4 (`teachersroom4`)

| Command | Result |
| --- | --- |
| `use computer` / `inspect computer` / `boot computer` / `computer` | Boots the virtual NixOS terminal. |
| `?` / `help` | Shows the room command list. |
| `pause` / `save` | Opens the save menu. |
| `map` | Shows the campus map. |
| `leave` / `exit` | Returns to the East Corridor. |

There is no room-level `status`, `inventory`, or `quit` command. The shell's `exit` command leaves the shell and returns to the room; use `leave`/`exit` again to return to the corridor.

#### Virtual shell commands

The Teacher's Room 4 computer runs `utilities/shell.py`, a pure in-memory shell.

| Command | Purpose |
| --- | --- |
| `ls [-a] [-l] [path...]` | List directory contents. `-a` includes hidden entries; `-l` uses a long format. |
| `cd [path]` | Change directory. With no path, go to `/home/teacher`. |
| `pwd` | Print the working directory. |
| `cat <file...>` | Print file contents. |
| `find [path] [-name pattern] [-iname pattern] [-type f]` | Search below a path for files. |
| `find [path] [-name pattern] [-iname pattern] [-type d]` | Search below a path for directories. |
| `tree [-a] [path]` | Show an indented directory tree. `-a` includes hidden entries. |
| `clear` | Clear the terminal. |
| `whoami` | Print the current user. |
| `exit` | Leave the shell. |
| `help` | Show the shell command list. |

Reading the hidden secret file gives the Encrypted API & Prompt USB and advances objective 4 → 5. The path and search strategy are in [GAME_DESIGN.md](GAME_DESIGN.md); the shell supports `-a` for hidden entries.

### Student Wing (`studentwing`)

| Command | Result |
| --- | --- |
| `look around` | Describes the wing. |
| `go` | Destinations: Lobby, Project Room 1, Project Room 2, Lab D2.001, Equinox Student Society. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

### Project Room 1 (`projectroom1`)

| Command | Result |
| --- | --- |
| `inspect whiteboard` | Shows the BODMAS clues for lockers 1 and 3. |
| `inspect desks` | Shows the clue for locker 4. |
| `inspect pile` | Shows the clue for locker 5 and mentions the brass key. |
| `inspect vance` | Prints Vance's dialogue. |
| `inspect lockers` | Starts the locker puzzle. Choose a locker 1–5, or `back` to step away. |
| `take <item>` | Implemented, but the room's floor-loot list starts empty. Locker rewards are added directly to the inventory. |
| `go` | Returns to the Student Wing. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

Locker codes and rewards are listed in [GAME_DESIGN.md](GAME_DESIGN.md). Locker 2 requires a brass key that is not currently obtainable, so the room cannot be fully completed.

### Project Room 2 (`projectroom2`)

| Command | Result |
| --- | --- |
| `look around` | Describes the projector puzzle. |
| `start puzzle` | Starts the colour-ordering puzzle. Choose two positions from 1 to 7 to swap. |
| `go` | Returns to the Student Wing. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

Solving the puzzle gives the Makeshift Mic and Speaker Combo and advances objective 5 → 6.

### Lab D2.001 (`labd2001`)

| Command | Result |
| --- | --- |
| `look around` | Describes the lab. |
| `start stacking` | Starts the box-stacking puzzle. Enter a box weight, then a platform number 1–3. |
| `reset` | Resets the box puzzle if it is not already complete. |
| `assemble` | Runs the ending when `current_objective_id >= 8`; otherwise prints a reminder to collect more components. |
| `go` | Returns to the Student Wing. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

Inside the stacking puzzle, `quit` leaves the puzzle and `reset` restarts it. The current loop does not exit automatically after a correct arrangement; type `quit` after placing all boxes so the completion check runs.

### Teaching Area (`teachingarea`)

| Command | Result |
| --- | --- |
| `look around` | Describes the area. |
| `go` | Destinations: Lobby, Classroom D2.015, Classroom D2.031, Classroom D2.035. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

### Classroom D2.015 (`classroomd2015`)

| Command | Result |
| --- | --- |
| `inspect bins` | Describes the spare parts and battery. |
| `inspect workbench` | Shows the voltage calculation. |
| `inspect rover` | Shows the frequency calculation. |
| `inspect track` | Starts the two-stage rover calibration. |
| `take memory sticks` | After solving the rover, gives Memory Sticks and advances objective 7 → 8. |
| `go` | Returns to the Teaching Area. |
| `look around`, `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

### Classroom D2.031 (`classroomd2031`)

| Command | Result |
| --- | --- |
| `inspect board` | Shows the encrypted key-box password. |
| `inspect monitors` | Shows the Caesar-cipher decoder table. |
| `inspect keybox` | Starts the three-attempt cipher puzzle. |
| `take key` | After solving the cipher, takes the Classroom 2.021 key. |
| `go` | Returns to the Teaching Area. |
| `look around`, `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

The reward is a key for a room that does not exist in the current build; this room does not advance the objective counter.

### Classroom D2.035 (`classroomd2035`)

| Command | Result |
| --- | --- |
| `inspect desks` | Shows the seating clues. |
| `inspect lecturer` | Shows the lecturer's notes and the sequence hint. |
| `inspect podium` | Starts the two-part podium puzzle. |
| `take motherboard` | After solving both parts, gives the A.I.G.I.S. Motherboard and advances objective 6 → 7. |
| `go` | Returns to the Teaching Area. |
| `look around`, `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

The podium puzzle has a seating part and a sequence part; the answers are in [GAME_DESIGN.md](GAME_DESIGN.md). The `Seating plan` item is added after the seating part.

### Equinox Student Society (`equinoxstudentsociety`)

| Command | Result |
| --- | --- |
| `look around` | Describes the society room. |
| `sit down` | Boots the quiz computer. At the prompt, use `start`, `quit`, or `?`. |
| `go` | Returns to the Student Wing. |
| `map`, `inv`, `status`, `save`, `?`, `quit` | Shared commands. |

The quiz has six multiple-choice questions. Answer with `a`, `b`, `c`, or `d`. More than three correct answers passes and awards the Quiz certificate. The quiz is optional and does not advance the objective counter.

## 5. Menu and overlay controls

### Save menu

- Enter `1`, `2`, or `3` to save to that slot.
- Enter `quit` to leave without saving.

### Load menu

- Enter `1`, `2`, or `3` to load that slot.
- Enter `quit`, `exit`, or `back` to return to the main menu.

### Inventory viewer

- Up / Down arrow: move between items.
- Enter: return to the room.

### Map

- Enter: leave the map.

### Status screen

- Enter `exit` to return to the current room.

### Ending scoreboard prompt

- Up / Down arrow: choose whether to save the run.
- Enter: confirm.

## 6. Feedback and error messages

The exact text varies by room, but these are the common outcomes:

| Situation | Typical output |
| --- | --- |
| Unknown room command | `Unknown command. Type '?' to see available commands.` |
| Invalid save/load slot | `Invalid input. Please enter 1, 2, 3, or 'quit'.` |
| No item to take | `There is no '<item>' here to take.` |
| Gated room too early | The room-specific rejection message from `ROOM_REQUIREMENTS`, followed by a return to the previous room. |
| Wrong puzzle answer | A room-specific failure message; most puzzles let you retry. |
| Save menu cancelled | `Exiting save menu...` |
| No save in a slot | `No save found in slot <n>. Please try again.` |

## 7. Unreachable store commands

`rooms/store.py` contains a store command loop (`look around`, `?`, `go <room>`, `buy <item>`, `map`, `status`, `save`, `quit`), but the store is not registered in `rooms/dispatcher.py`. It cannot be reached during normal play. See the known gaps in [ARCHITECTURE.md](ARCHITECTURE.md#known-gaps).
