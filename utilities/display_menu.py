def display_menu(console,commands) -> None:
    """Display the room's command list."""
    console.print("List of all available commands for this room")
    for command, description in commands:
        console.print(f"{'':<3}{command:<20} {description}")