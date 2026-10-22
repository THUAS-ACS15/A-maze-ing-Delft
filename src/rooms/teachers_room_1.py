from ..display import colorize
from ..room import render
from ..utils.colors import RED, GREEN
from ..state import state


def use_desk_code(item: str, target: str | None = None) -> None:
    desk = state["rooms"]["teachers_room_1"]["interactables"]["desk"]
    desk_code = desk["code"]
    flags = state["flags"]


    if target is not None and target != "desk":
        render(text=colorize("Nothings happens", color_code=RED))
        return None


    if flags["tr1_desk_unlocked"]:
        render(text=colorize("The desk is already unlocked.", color_code=GREEN))
        return None

    if item == desk_code.lower():
        flags["tr1_desk_unlocked"] = True
        reward = desk["reward"]
        if reward not in state["player"]["inventory"]:
            state["player"]["inventory"].append(reward)
            render(text=colorize("Keypad clicks green. You've obtained the Level-1 Staff Keycard.", color_code=GREEN))
            return None
        render(
            text=colorize(
                "You already have a Level-1 Staff keycard.",
                color_code=GREEN
                )
            )
        return None
    render(
        text=colorize(
            f"Keypad buzzes red: Incorrect code entered.: {item}",
            color_code=RED
        )
    )
    return None