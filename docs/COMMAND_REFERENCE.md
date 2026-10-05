# A-maze-ing-Delft - Command Reference Manual
This manual lists all supported commands, shortcuts, directional aliases, and phase-specific mechanics in A-maze-ing-Delft

## Input Processing Rules
The engine normalizes all user input before passing it to src/parser.py:

* Case-Insensitive: GO NORTH, Go North, and go north are treated identically.
* Trimmed Whitespace: Leading, trailing, and duplicate spaces are stripped ( take   battery_pack  $\rightarrow$ take battery_pack)
* Noise Word Stripping: Articles like the, a, and an are ignored (take the battery_pack $\rightarrow$ take battery_pack).

## 2. Exploration Phase Commands
During EXPLORATION mode, player commands follow a VERB [TARGET] or VERB [ITEM] ON [TARGET] pattern.

### Spatial Movement
Command Syntax                       Aliases / Shortcuts                      Example                                     Target Action / Result
go [room]                            move [room], walk [room]                 go teachers_room_1                          Moves player to the destination room if unlocked.


### Environment & Inspection
Command Syntax                       Aliases / Shortcuts                      Example                                     Target Action / Result
`look`                                l, ls, examine room                      look                                        Displays current room title, description, visible items, and exits.
inspect [target]                     examine [target],                        inspect desk, inspect battery_pack
                                     read [target], check [target]

### Inventory Management
Command Syntax                       Aliases / Shortcuts                      Example                                     Target Action / Result
inventory                            inv, i                                   inventory                                   Lists all items currently held in player inventory.
take [item]                          get [item], grab [item], pick up [item]  take battery_pack                           Transfers an item from the current room floor into player inventory.
drop [item]                          discard [item]                           drop battery_pack                           Transfers an item from player inventory back onto the current room floor.

### Interactions & Puzzles
Command Syntax                       Aliases / Shortcuts                      Example                                     Target Action / Result
use [item]                           apply [item]                             use keycard_lvl1                            Uses an item in the current context (e.g., swiping a keycard at a door).
use [item] on [target]               apply [item] to [target],                use keycard_lvl1 on door                    Direct interaction between an inventory item and a room interactable. 
                                     put [item] on [target]
enter [code]                         type [code], unlock [code]