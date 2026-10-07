# ACS15 A-maze-ing-Delft

## Description
This repository contains our Q1 Project for the Applied Computer Science (ACS) program at The Hague University of Applied Sciences (THUAS). 

**A-maze-ing-Delft** is an interactive, text-based adventure and maze game set on the THUAS Delft campus grounds. In **A-maze-ing-delft** (Autonomous Intellect & Generalized Interface System), players explore the facility, scavenge missing hardware modules across campus rooms, assemble an AI core on the lab workbench, and interact directly with a real-time streaming AI terminal to complete diagnostic tasks and secure facility control.

The goal of the project is to:
* Develop a modular Python terminal application adhering to clean architecture principles.
* Implement structured state management (`user_state.json`) with dynamic persistence.
* Integrate streaming AI model interaction via LLM APIs (`google-genai` / `openai`) alongside a offline mock fallback.
* Provide an engaging CLI user interface using ANSI terminal formatting and status rendering.

---

## Features
* **Multi-Phase Gameplay**: 
  * **Phase 1 (Hardware Assembly)**: Explore rooms, collect assembly components, track room state, and mount parts on the workbench.
  * **Phase 2 (Neural Link Diagnostics)**: Power on the assembled core and engage in a live interactive streaming chat with A.I.G.I.S.
* **ANSI Color Display Engine**: Custom CLI renderer (`DisplayManager`) featuring stylized banners, color-coded status reports, dynamic inventory tracking, and streaming AI token output.
* **Dual-Mode AI Engine**: `AIClient` streams responses from Gemini / OpenAI endpoints when configured, or seamlessly falls back to an offline simulated processor if no API keys are present.
* **JSON State Persistence**: Player inventory, room progress, workbench status, and game flags are cleanly stored and restored.

---

## Installation

### Prerequisites
* Python 3.10+ installed
* (Optional) Docker & Docker Compose
* (Optional) `GEMINI_API_KEY` or `OPENAI_API_KEY` set as an environment variable for live LLM streaming.

### Standard Setup

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/THUAS-ACS15/A-maze-ing-Delft.git](https://github.com/THUAS-ACS15/A-maze-ing-Delft.git)
   cd A-maze-ing-Delft