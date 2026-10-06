# Architecture & System Design Specification
This document provides a technical overview of  engine architecture module boundaries, data pipelines, state machines, and execution phase transitions.


## System Overview & Core Principles

               ┌──────────────────────────────────────────────┐
               │                  main.py                     │
               │  (Bootstrapper & Environment Initializer)    │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │                src/engine.py                 │
               │     (Main Loop & Phase State Controller)     │
               └──────────────┬────────────────┬──────────────┘
                              │                │
            ┌─────────────────┘                └─────────────────┐
    EXPLORATION PHASE                                    [CHAT_MODE PHASE]
            │                                                    │
            ▼                                                    ▼
┌───────────────────────┐                            ┌───────────────────────┐
│     src/parser.py     │                            │   src/ai.py    │
│  (Command Normalizer) │                            │  (OpenAI API Bridge)  │
└───────────┬───────────┘                            └───────────┬───────────┘
            │                                                    │
            └─────────────────┐                ┌─────────────────┘
                              │                │
                              ▼                ▼
               ┌──────────────────────────────────────────────┐
               │                src/state.py                  │
               │    (StateManager & Single Source of Truth)   │
               └──────────────────────┬───────────────────────┘
                                      │
                                      ▼
               ┌──────────────────────────────────────────────┐
               │               src/display.py                 │
               │   (Terminal Renderer & Screen Formatting)    │
               └──────────────────────────────────────────────┘

## Finite State Machine Architecture
The engine operates on a finite state machine governed by game_state["game_phase"].

[ EXPLORATION ] ──(All 7 parts placed)──> [ ASSEMBLY ] ──(Player runs 'activate')──> [ CHAT_MODE ]
         │                                       │                                         │
   Input handled by                        Validation phase                       Input routed to
  src/parser.py                            checks workbench                       src/ai.py

 ┌─────────────────┐       All 7 Parts Placed       ┌─────────────────┐
 │   EXPLORATION   │ ─────────────────────────────> │    ASSEMBLY     │
 └────────┬────────┘                                └────────┬────────┘
          ▲                                                  │
          │ Invalid Command                                  │ 'activate' / 'power on'
          └──────────────────────────────────────────────────┘
                                                             │
                                                             ▼
                                                    ┌─────────────────┐
                                                    │    CHAT_MODE    │
                                                    └─────────────────┘

### Phase Definitions
1. **EXPLORATION** Phase
2. **ASSEMBLY** Phase
3. **CHAT_MODE** Phase

[EXPLORATION PHASE]
  │  - Parser accepts: look, go, inspect, take, use
  │  - State updates inventory, room objects, and room lock flags
  ▼
[ASSEMBLY PHASE]
  │  - Triggered when workbench.is_ready == True
  │  - Player issues 'activate' or 'power on' command in Lab D 2001
  ▼
[CHAT_MODE PHASE]
  │  - Command parser is bypassed
  │  - User input routes directly to ai_client.py -> OpenAI ChatGPT API
  └─ Response streams directly back to CLI prompt

## Detailed Module Specifications
`main.py` – **Application Bootstrapper**
`../src/utils`– **State Manager & Data Mutations**

                ┌──────────────────────────────────────┐
                │          src/state.py                │
                ├──────────────────────────────────────┤
                │ - state: dict                        │
                ├──────────────────────────────────────┤
                │ + load_default_state()               │
                │ + move_player(direction) -> bool     │
                │ + take_item(item_id) -> bool         │
                │ + use_workbench(item_id) -> bool     │
                │ + save_game(slot_name) -> None       │
                │ + load_game(slot_name) -> bool       │
                └──────────────────────────────────────┘

`../src/display.py`– **UI & CLI Formatting**

### Standard Terminal Header Layout

================================================================================
LOCATION: Lab D 2001                       | INVENTORY: [Blueprint, API USB]
================================================================================
The final assembly lab equipped with an industrial workbench.

Visible Items: None
Exits: [East -> Teacher Room 4]

>

## Persistence & File Layout
Directory structure separating template data from player saves:

A-maze-ing-Delft/
├── data/
│   ├── game_state.json      # Master read-only default game state
│   └── system_prompt.txt   # System persona prompt for OpenAI API
└── saves/
    ├── save_slot_1.json     # Active player save file
    └── save_slot_2.json     # Backup save slot