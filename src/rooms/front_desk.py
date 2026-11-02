from src.room import render
from src.state import state

def inspect_receptionist():
    receptionist = state["rooms"]["front_desk"]["interactables"]["receptionist"]
    render(text=receptionist)
    return None