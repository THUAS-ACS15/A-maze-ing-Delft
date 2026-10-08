# A-maze-ing-Delft - Game State Schema Specification

This document defines the data structure, schema definitions, validation rules, and default JSON representation for the `game_state` object in A-maze-ing-Delft.

## 1. Schema Overview & Data Integrity Rules

The `game_state` object is the single source of truth for the game runtime. It tracks game progression, world topology, item ownership, and assembly triggers across three distinct execution phases.

### Data Integrity Rules

- **Strict JSON Serialization:** Only primitive types (`string`, `number`, `boolean`), arrays (`list`), and key-value objects (`dict`) are permitted. Custom class instances, function pointers, or lambda expressions are strictly forbidden.
- **Canonical Identifiers:** All lookups for rooms, items, and flags must use canonical snake_case keys (e.g., `teachers_room_1`, `battery_pack`). Never use human-readable display names in conditional logic or state lookups.
- **Template Immutability:** `data/game_state.json` serves as the read-only initial world state. Runtime mutations must occur solely on the in-memory state dictionary and be saved to `saves/save_slot_1.json`.

## 2. Root Structure & Key Specifications

The root object contains `game_phase`, `running`, `player`, `workbench`, `flags`, `items`, and `rooms`. See detailed definitions below and the full template in Section 4.

## 3. Detailed Field Definitions

### Player State (`player`)

```json
"player": {
    "current_room": "string",
    "inventory": ["string"]
}
```

### Workbench Tracker (`workbench`)

```json
"workbench": {
    "installed_parts": ["string"],
    "required_parts": ["string"],
    "is_ready": "boolean"
}
```

### Story Flags (`flags`)

Dictionary of boolean keys used for tracking non-item progression events.

| Flag Key                   | Type    | Default | Trigger Condition / Meaning                                         |
| -------------------------- | ------- | ------- | ------------------------------------------------------------------- |
| `tr1_desk_unlocked`        | boolean | false   | true when the desk keypad code (2015) in teachers_room_1 is solved. |
| `tr2_whiteboard_inspected` | boolean | false   | true when inspect whiteboard is issued in teachers_room_2.          |
| `tr4_drawer_decrypted`     | boolean | false   | true when the desk in teacher_room_4 is searched/decrypted.         |
| `lab_power_on`             | boolean | false   | true when power is restored to the workbench terminal in lab_d2001. |

### Item Entities (`items`)

```json
"items": {
    "item_id": {
        "name": "string",
        "description": "string",
        "is_assembly_part": "boolean"
    }
}
```

### Room Graph Entities (`rooms`)

Dictionary mapping unique room_id strings to room definition objects.

```json
"rooms": {
    "room_id": {
        "name": "string",
        "description": "string",
        "is_locked": "boolean",
        "required_item": "string | null",
        "exits": {
            "direction": "room_id"
        },
        "items": ["string"],
        "interactables": {
            "object_name": "string | object"
        }
    }
}
```

## 4. Master Template JSON (`data/game_state.json`)

Below is the baseline `game_state.json` template file:

```json
{
  "game_phase": "EXPLORATION",
  "running": true,
  "player": {
    "current_room": "lobby",
    "inventory": []
  },
  "workbench": {
    "installed_parts": [],
    "required_parts": [
      "chassis_frame",
      "battery_pack",
      "mainboard",
      "sensory_module",
      "wifi_credentials",
      "motors_speakers",
      "api_usb"
    ],
    "is_ready": false
  },
  "flags": {
    "tr1_desk_unlocked": false,
    "tr2_whiteboard_inspected": false,
    "tr4_drawer_decrypted": false,
    "lab_power_on": false
  },
  "items": {
    "blueprint": {
      "name": "Robot Assembly Blueprint",
      "description": "Schematic diagram outlining all 7 sub-assemblies needed for Project A.I.G.I.S.",
      "is_assembly_part": false
    },
    "chassis_frame": {
      "name": "Robot Chassis Frame",
      "description": "An aluminum structural frame equipped with component mounting brackets.",
      "is_assembly_part": true
    },
    "battery_pack": {
      "name": "High-Capacity Battery Pack",
      "description": "A heavy 24V lithium-ion battery array delivering high power output.",
      "is_assembly_part": true
    },
    "keycard_lvl1": {
      "name": "Level-1 Staff Keycard",
      "description": "A magnetic keycard. Grants access to restricted project rooms.",
      "is_assembly_part": false
    },
    "mainboard": {
      "name": "Microcontroller / Mainboard",
      "description": "High-performance mainboard integrated with neural co-processing units.",
      "is_assembly_part": true
    },
    "sensory_module": {
      "name": "Sensory Module (Cam/Mic)",
      "description": "Combined hardware housing a high-resolution camera and dual-microphone array.",
      "is_assembly_part": true
    },
    "wifi_credentials": {
      "name": "Wi-Fi Credentials Note",
      "description": "Paper note listing network ID 'CS_LAB_NET' and WPA2 passkey 'Tr0janH0rse!'.",
      "is_assembly_part": true
    },
    "motors_speakers": {
      "name": "Servo Motors & Speakers",
      "description": "High-torque precision servos paired with an integrated audio driver unit.",
      "is_assembly_part": true
    },
    "api_usb": {
      "name": "Encrypted API & Prompt USB",
      "description": "Flash drive containing encrypted OpenAI API authentication keys and system persona prompts.",
      "is_assembly_part": true
    }
  },
  "rooms": {
    "lobby": {
      "name": "Floor Lobby",
      "description": "The main floor lobby. An emergency bulletin terminal blinks near the entrance.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "north": "classroom_d2015",
        "east": "teachers_room_1"
      },
      "items": ["blueprint", "chassis_frame"],
      "interactables": {
        "terminal": "System display blinks: 'PROJECT A.I.G.I.S. ASSEMBLY REQUIRED FOR OVERRIDE.'"
      }
    },
    "classroom_d2015": {
      "name": "Classroom D 2015",
      "description": "A large lecture room with rows of empty desks and whiteboards.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "south": "lobby",
        "east": "classroom_d2035"
      },
      "items": ["battery_pack"],
      "interactables": {
        "podium": "A wooden podium with a sign reading 'CS101 - Intro to Systems Mechanics'."
      }
    },
    "teachers_room_1": {
      "name": "Teachers Room 1",
      "description": "A faculty office crowded with filing cabinets and a locked desk.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "west": "lobby",
        "north": "classroom_d2035"
      },
      "items": [],
      "interactables": {
        "desk": {
          "is_locked": true,
          "code": "2015",
          "reward_item": "keycard_lvl1",
          "hint": "Keypad note reads: 'Code is the room number where CS101 was held.'"
        }
      }
    },
    "classroom_d2035": {
      "name": "Classroom D 2035",
      "description": "An advanced computing lab with workbenches and workstation monitors.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "west": "classroom_d2015",
        "south": "teachers_room_1",
        "east": "project_room_1"
      },
      "items": ["mainboard"],
      "interactables": {}
    },
    "project_room_1": {
      "name": "Project Room 1",
      "description": "A high-security hardware testing bay containing robotics testing rigs.",
      "is_locked": true,
      "required_item": "keycard_lvl1",
      "exits": {
        "west": "classroom_d2035",
        "south": "teachers_room_2"
      },
      "items": ["sensory_module"],
      "interactables": {}
    },
    "teachers_room_2": {
      "name": "Teachers Room 2",
      "description": "An administrative staff office with a large floor-to-ceiling whiteboard.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "north": "project_room_1",
        "east": "project_room_2"
      },
      "items": ["wifi_credentials"],
      "interactables": {
        "whiteboard": "Written in marker: 'Lab Network Pass: Tr0janH0rse! - Do not erase!'"
      }
    },
    "project_room_2": {
      "name": "Project Room 2",
      "description": "A mechanical assembly shop filled with component crates and tool racks.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "west": "teachers_room_2",
        "south": "teacher_room_4"
      },
      "items": ["motors_speakers"],
      "interactables": {}
    },
    "teacher_room_4": {
      "name": "Teacher Room 4",
      "description": "The senior professor's office. Research notes cover the desk.",
      "is_locked": true,
      "required_item": "keycard_lvl1",
      "exits": {
        "north": "project_room_2",
        "west": "lab_d2001"
      },
      "items": ["api_usb"],
      "interactables": {}
    },
    "lab_d2001": {
      "name": "Lab D 2001",
      "description": "The primary robotics lab equipped with a central industrial assembly workbench.",
      "is_locked": false,
      "required_item": null,
      "exits": {
        "east": "teacher_room_4"
      },
      "items": [],
      "interactables": {
        "workbench": "An industrial metal table wired directly into the main server terminal."
      }
    }
  }
}
```
