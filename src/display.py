# Standard Colors
from typing import Any


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

    def draw_line(self, char: str = "─") -> None:
        print(self.colorize(char * self.terminal_width, "\033[2m"))

    def render_room(self, room_id: str, room_data: dict[str, Any],
                    items_db: dict[str, Any]) -> None:
        """Displays current location, description, exits, items, and interactable features."""
        self.draw_line("═")
        room_name = room_data.get("name", room_id).upper()
        print(
            self.colorize(f"LOCATION: {room_name}", Colors.BRIGHT_YELLOW + Colors.BOLD)
            )
        self.draw_line("═")

        # Room Narrative
        print(f"\n{room_data.get('description', '')}\n")

        # Exits
        exits = room_data.get("exits", {})
        if exits:
            formatted_exits = [f"{direction.upper()} -> {target}" for direction, target
                               in exits.items()]
            print(self.colorize(f"Exits: {', '.join(formatted_exits)}", Colors.CYAN))
        else:
            print(self.colorize("Exits: None available.", Colors.RED))

        # Loose Items
        room_items = room_data.get("items", [])
        if room_items:
            print(self.colorize("\nItems in area:", Colors.BRIGHT_WHITE + Colors.BOLD))
            for item_id in room_items:
                item_data = items_db.get(item_id, {})
                display_name = item_data.get("name", item_id)
                component_tag = (
                    f" {self.colorize('[ASSEMBLY PART]', Colors.BRIGHT_GREEN)}"
                    if item_data.get("is_assembly_part")
                    else ""
                )
                print(
                    f"  • {self.colorize(display_name, Colors.BRIGHT_YELLOW)}{component_tag}"
                    )

        # Points of Interest
        interactables = room_data.get("interactables", {})
        if interactables:
            print(self.colorize("\nInteractive Objects:", Colors.DIM))
            for poi_key in interactables.keys():
                print(f"  • {self.colorize(poi_key, Colors.WHITE)}")

        print()

    def render_inventory(self, inventory: list[str], items_db: dict[str, Any]) -> None:
        """Renders carried items and displays total core assembly parts held."""
        self.draw_line("─")
        print(self.colorize("INVENTORY", Colors.BRIGHT_CYAN + Colors.BOLD))
        self.draw_line("─")

        if not inventory:
            print(self.colorize("Your inventory is empty.", Colors.DIM))
            print()
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

            print(f" • {self.colorize(name, Colors.BRIGHT_YELLOW)}{tag}")
            print(f"   {self.colorize(desc, Colors.DIM)}")

        print(
            self.colorize(
                f"\nAssembly Components Carried: {parts_carried}/7", Colors.BRIGHT_WHITE
                )
            )
        print()

    def render_workbench(self, workbench_data: dict[str, Any],
                         items_db: dict[str, Any]) -> None:
        """Displays workbench assembly status in Lab D 2001."""
        installed = workbench_data.get("installed_parts", [])
        required = workbench_data.get("required_parts", [])

        self.draw_line("═")
        print(
            self.colorize(
                "WORKBENCH ASSEMBLY STATUS", Colors.BRIGHT_MAGENTA + Colors.BOLD
                )
            )
        self.draw_line("═")
        print(f"Progress: {len(installed)} / {len(required)} components installed.\n")

        for part_id in required:
            item_data = items_db.get(part_id, {})
            part_name = item_data.get("name", part_id)

            if part_id in installed:
                status = self.colorize(
                    "[ INSTALLED ]", Colors.BRIGHT_GREEN + Colors.BOLD
                    )
            else:
                status = self.colorize("[ MISSING   ]", Colors.RED + Colors.DIM)

            print(f" {status} - {part_name}")

        print()
        if len(installed) == len(required):
            print(
                self.colorize(
                    ">> ALL CORE COMPONENTS INSTALLED <<",
                    Colors.BRIGHT_GREEN + Colors.BOLD
                    )
                )
            print(
                self.colorize(
                    "Type 'activate' or 'power on' to start the neural link.",
                    Colors.BRIGHT_YELLOW
                    )
                )
        else:
            remaining = len(required) - len(installed)
            print(
                self.colorize(
                    f"Locate remaining {remaining} part(s) to complete assembly.",
                    Colors.DIM
                    )
                )
        print()

    # def render_system_ready(self) -> None:
    #     """Displays initialization message when assembly complete."""
    #     banner = f"""