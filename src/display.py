# Standard Colors
from typing import Any

from rich.console import Console
from rich.text import Text


class Colors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # High-Intensity Colors
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BOLD = "\033[1m"

class DisplayManager:
    def __init__(self, enable_colors: bool = True, terminal_width: int = 80):
        self.enable_colors = enable_colors
        self.terminal_width = terminal_width

    def colorize(self, text: str, color_code: str) -> str:
        return f"{color_code}{text}\033[0m" if self.enable_colors else text

    def _safe(self, text: str) -> str:
        table = str.maketrans({"─": "-", "═": "=", "•": "*", "→": "->", "←": "<-"})
        text = text.translate(table)
        try:
            text.encode("cp1252")
            return text
        except UnicodeEncodeError:
            return text.encode("cp1252", errors="replace").decode("cp1252")

    def _out(self, text: str = "") -> None:
        import builtins

        builtins.print(self._safe(text))

    def draw_line(self, char: str = "-") -> None:
        self._out(self.colorize(char * self.terminal_width, "\033[2m"))

    def render_room(self, room_id: str, room_data: dict[str, Any],
                    items_db: dict[str, Any]) -> None:
        """Displays current location, description, exits, items, and interactable features."""
        self.draw_line("═")
        room_name = room_data.get("name", room_id).upper()
        self._out(
            self.colorize(f"LOCATION: {room_name}", Colors.BRIGHT_YELLOW + Colors.BOLD)
            )
        self.draw_line("═")

        # Room Narrative
        self._out(f"\n{room_data.get('description', '')}\n")

        # Exits
        exits = room_data.get("exits", {})
        if exits:
            formatted_exits = [f"{direction.upper()} -> {target}" for direction, target
                               in exits.items()]
            self._out(self.colorize(f"Exits: {', '.join(formatted_exits)}", Colors.CYAN))
        else:
            self._out(self.colorize("Exits: None available.", Colors.RED))

        # Loose Items
        room_items = room_data.get("items", [])
        if room_items:
            self._out(self.colorize("\nItems in area:", Colors.BRIGHT_WHITE + Colors.BOLD))
            for item_id in room_items:
                item_data = items_db.get(item_id, {})
                display_name = item_data.get("name", item_id)
                component_tag = (
                    f" {self.colorize('[ASSEMBLY PART]', Colors.BRIGHT_GREEN)}"
                    if item_data.get("is_assembly_part")
                    else ""
                )
                self._out(
                    f"  • {self.colorize(display_name, Colors.BRIGHT_YELLOW)}{component_tag}"
                    )

        # Points of Interest
        interactables = room_data.get("interactables", room_data.get("interactable", {}))
        if interactables:
            self._out(self.colorize("\nInteractive Objects:", Colors.DIM))
            for poi_key in interactables.keys():
                self._out(f"  • {self.colorize(poi_key, Colors.WHITE)}")

        self._out()

    def render_art(self, text: str, font: str = "block") -> None:
        """Render ASCII art (pyfiglet if present, else art, else plain)."""
        ascii_text: str = text
        try:
            try:
                import pyfiglet  # type: ignore[import-not-found]

                ascii_text = pyfiglet.figlet_format(text, font=font)
            except Exception:
                try:
                    from art import text2art  # type: ignore[import-untyped]

                    ascii_text = text2art(text, font=font)
                except Exception:
                    ascii_text = text
            try:
                Console(highlight=False).print(Text(ascii_text))
            except Exception:
                self._out(ascii_text)
        except Exception:
            self._out(text)

    def render_inventory(self, inventory: list[str], items_db: dict[str, Any]) -> None:
        """Renders carried items and displays total core assembly parts held."""
        self.draw_line("─")
        self._out(self.colorize("INVENTORY", Colors.BRIGHT_CYAN + Colors.BOLD))
        self.draw_line("─")

        if not inventory:
            self._out(self.colorize("Your inventory is empty.", Colors.DIM))
            self._out()
            return

        parts_carried = 0
        for item_id in inventory:
            item_data = items_db.get(item_id, {})
            name = item_data.get("name", item_id)
            desc = item_data.get("description", "")
            is_part = item_data.get("is_assembly_part", False)

            if is_part:
                parts_carried += 1
                tag = f" {self.colorize('[ASSEMBLY PART]', Colors.BRIGHT_GREEN)}"
            else:
                tag = ""

            self._out(f" • {self.colorize(name, Colors.BRIGHT_YELLOW)}{tag}")
            self._out(f"   {self.colorize(desc, Colors.DIM)}")

        self._out(
            self.colorize(
                f"\nAssembly Components Carried: {parts_carried}/7", Colors.BRIGHT_WHITE
                )
            )
        self._out()

    def render_workbench(self, workbench_data: dict[str, Any],
                         items_db: dict[str, Any]) -> None:
        """Displays workbench assembly status in Lab D 2001."""
        installed = workbench_data.get("installed_parts", [])
        required = workbench_data.get("required_parts", [])

        self.draw_line("═")
        self._out(
            self.colorize(
                "WORKBENCH ASSEMBLY STATUS", Colors.BRIGHT_MAGENTA + Colors.BOLD
                )
            )
        self.draw_line("═")
        self._out(f"Progress: {len(installed)} / {len(required)} components installed.\n")

        for part_id in required:
            item_data = items_db.get(part_id, {})
            part_name = item_data.get("name", part_id)

            if part_id in installed:
                status = self.colorize(
                    "[ INSTALLED ]", Colors.BRIGHT_GREEN + Colors.BOLD
                    )
            else:
                status = self.colorize("[ MISSING   ]", Colors.RED + Colors.DIM)

            self._out(f" {status} - {part_name}")

        self._out()
        if len(installed) == len(required):
            self._out(
                self.colorize(
                    ">> ALL CORE COMPONENTS INSTALLED <<",
                    Colors.BRIGHT_GREEN + Colors.BOLD
                    )
                )
            self._out(
                self.colorize(
                    "Type 'activate' or 'power on' to start the neural link.",
                    Colors.BRIGHT_YELLOW
                    )
                )
        else:
            remaining = len(required) - len(installed)
            self._out(
                self.colorize(
                    f"Locate remaining {remaining} part(s) to complete assembly.",
                    Colors.DIM
                    )
                )
        self._out()

    def render_help(self, phase: str = "EXPLORATION") -> None:
        """Grouped Available Commands table (rich Table, plaintext fallback)."""
        sections: list[tuple[str, list[tuple[str, str, str]]]] = [
            ("Movement", [
                ("go <direction|room>", "Move (n/s/e/w or adjacent room name)", "go north, go lab"),
                ("look", "Re-render current room", "look"),
            ]),
            ("Inspect & Items", [
                ("inspect <target>", "Examine object or item", "inspect desk"),
                ("take <item>", "Pick up item", "take battery_pack"),
                ("use <item> on <target>", "Use item / solve puzzle", "use 2015 on desk"),
                ("inventory", "Show carried items (inv, i)", "inventory"),
            ]),
            ("System", [
                ("save \\[slot]", "Save game", "save"),
                ("load \\[slot]", "Load game", "load"),
                ("help (?, h)", "Show this help", "help"),
                ("quit (q, exit)", "Quit game", "quit"),
            ]),
        ]
        if phase == "ASSEMBLY":
            sections.append(("Assembly", [
                ("activate", "Boot unit (power on, start)", "activate"),
                ("inspect workbench", "Show installed vs missing parts", "inspect workbench"),
            ]))

        try:
            import os

            from rich.console import Console
            from rich.table import Table

            console = Console(highlight=False, force_terminal=None if os.getenv("NO_COLOR") else True)
            for title, rows in sections:
                table = Table(title=title, show_header=True, header_style="bold")
                table.add_column("Command", style="cyan", no_wrap=True)
                table.add_column("Description")
                table.add_column("Example", style="dim")
                for cmd, desc, ex in rows:
                    table.add_row(cmd, desc, ex)
                console.print(table)
        except Exception:
            self._out("Available Commands:")
            for title, rows in sections:
                self._out(f"[{title}]")
                for cmd, desc, ex in rows:
                    self._out(f"  {cmd:<24} {desc}  e.g. {ex}")

    # def render_system_ready(self) -> None:
    #     """Displays initialization message when assembly complete."""
    #     banner = f"""