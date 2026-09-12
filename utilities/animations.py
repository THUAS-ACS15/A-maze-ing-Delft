from time import sleep
from utilities.utils import clearScreen
from utilities.animation_frames import puzzle_frames

def show_activity_animation(type: str, state):
    if type == "puzzle":
        for frame in puzzle_frames[:-2]:
            clearScreen(state)
            print(frame)
            sleep(0.30)
        repeat_counter = 0
        clearScreen(state)
        while repeat_counter < 3:
            for frame in puzzle_frames[-2:]:
                clearScreen(state)
                print(frame)
                sleep(0.30)
            repeat_counter += 1
        clearScreen(state)
        print(puzzle_frames[6])