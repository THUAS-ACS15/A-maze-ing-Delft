# -----------------------------------------------------------------------------
# File: inventory_viewer.py
# ACS Q1 Project - A-maze-ing Delft
# Organization: THUAS (The Hague University of Applied Sciences)
# Location: Delft
# Date: September 2026
# Contributors: Leon
# -----------------------------------------------------------------------------

"""Interactive inventory viewer with item art and descriptions."""

from rich.align import Align
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from data.item_description_bank import item_description_bank
from data.item_render_bank import item_render_bank
from utilities.clear_screen import clear_screen
from utilities.main_menu import read_key
from utilities.status_bar import display_top_bar

NO_RENDER_PLACEHOLDER = (
    "   ___   \n"
    "  |   |  \n"
    "  | ? |  \n"
    "  |___|  \n"
)

NO_DESCRIPTION_PLACEHOLDER = "No description available."

controls_str = "[italic]^ next item | use enter to go back | v previous item[/italic]"

def create_list_panel(inventory: list[str], selected: int, panel_height: int) -> Panel:
    """Creates the left panel that displays items currently in inventory.

    Args:
        inventory: list of items in inventory, aka state["inventory"]
        selected: index of the currently highlighted item.
        panel_height: panel height in terminal lines.

    Returns:
        rich panel containing the scrollable list.
    """

    # how many list rows fit inside the panel (subtract 2 for border)
    visible_rows = max(1, panel_height - 2)

    # scroll window to keep the selected item in view
    half = visible_rows // 2
    start = max(0, min(selected - half, len(inventory) - visible_rows))
    end   = min(len(inventory), start + visible_rows)

    items_to_display = inventory[start:end]

    # create the actual list of items
    # if index is same as selected, highlight it
    text = Text()
    for i, name in enumerate(items_to_display):
        index = start + i
        if index == selected:
            text.append(f"  > {name}\n", style="bold green")
        else:
            text.append(f"    {name}\n")

    # pad to fill panel height so the panel stays a fixed size
    lines_used = end - start
    for _ in range(visible_rows - lines_used):
        text.append("\n")

    return Panel(
        text,
        title="[bold]Items[/bold]",
        title_align="left",
        border_style="default",
    )


def create_item_details_panel(item_name: str | None, panel_height: int) -> Panel:
    """Builds the right-side detail panel showing the item render and description.

    Args:
        item_name: name of the selected item, or None if empty.
        panel_height: panel height in terminal lines.

    Returns:
        a rich Panel containing the render + description sub-panels.
    """

    # get texts for item name and desc,
    # if they don't exist use 
    render_text = (
        item_render_bank.get(item_name, NO_RENDER_PLACEHOLDER)
        if item_name is not None
        else NO_RENDER_PLACEHOLDER
    )

    desc_text = (
        item_description_bank.get(item_name, NO_DESCRIPTION_PLACEHOLDER)
        if item_name is not None
        else NO_DESCRIPTION_PLACEHOLDER
    )

    render_panel = Panel(
        Align.center(render_text, vertical="middle"),
        title_align="left",
        border_style="default",
        height = 11
    )

    # wrap description to fixed height
    desc_panel = Panel(
        desc_text,
        title="[bold]Description[/bold]",
        title_align="left",
        border_style="default",
        height = 8
    )

    body = Group(render_panel, desc_panel)
    title_str = f"[bold]{item_name}[/bold]" if item_name else "[dim]No item selected[/dim]"
    return Panel(body, title = title_str, title_align = "left", border_style = "default")


def render_inventory(console: Console, inventory: list[str], selected: int) -> None:
    """Clears the screen and draws the full inventory UI.

    Args:
        console: rich Console.
        inventory: list of items in inventory, aka state["inventory"]
        selected: index of the currently highlighted item. (starts at 0)
    """

    console.clear()
    display_top_bar(console)
    console.print(Align.center("[bold]Your inventory[/bold]"))
    console.print('\n')

    item_name = inventory[selected] if inventory else None

    # this sets the grid so that inventory takes up exactly 2/3 and render + desc take last 1/3
    layout = Table.grid(expand = True)
    layout.add_column(ratio = 2)
    layout.add_column(ratio = 1)

    list_panel = create_list_panel(inventory, selected, 20)
    details_panel = create_item_details_panel(item_name, 20)
    layout.add_row(list_panel, details_panel)

    console.print(layout)
    console.print('\n')
    console.print(Align.center(controls_str))


def display_inventory(inventory: list[str]) -> None:
    """Opens the inventory viewer, letting the player scroll through their items.

    The screen is split into a 2/3 item list on the left and a 1/3 detail
    panel on the right. Up / Down arrows move the selection;
    Enter closes the viewer.

    Args:
        inventory: list of items in inventory, aka state["inventory"]
    """
    console  = Console()
    selected = 0

    if len(inventory) == 0:
        # if no items in inv show an empty state and wait for enter
        console.clear()
        display_top_bar(console)
        console.print(Align.center("\n[italic]Your inventory is empty.[/italic]\n\n"))
        console.print(Align.center(controls_str))
        while True:
            if read_key() == "enter":
                break
        return

    render_inventory(console, inventory, selected)

    while True:
        key = read_key()

        if key == "up":
            selected = (selected - 1) % len(inventory)
            render_inventory(console, inventory, selected)
        elif key == "down":
            selected = (selected + 1) % len(inventory)
            render_inventory(console, inventory, selected)
        elif key == "enter":
            clear_screen()
            break
