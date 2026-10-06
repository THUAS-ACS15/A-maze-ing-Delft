from .state import StateManager
from .parser import CommandParser
from .client import AIClient
from .display import DisplayManager


class Engine:
    def __init__(self, state_manager: StateManager):
        self.state = state_manager
        self.parser = CommandParser()
        self.ai_client = AIClient()
        self.display = DisplayManager()

    def run(self) -> None:
        while self.state.is_running():
            phase = self.state.get_phase()

            if phase == "EXPLORATION":
                self.handle_exploration_turn()
            elif phase == "ASSEMBLY":
                self.handle_assembly_turn()
            elif phase == "CHAT_MODE":
                self.handle_chat_turn()
    def get_input(self) -> str:
        return input("What is your name?")

    def handle_exploration_turn(self) -> None:
        while self.state.is_running():
            name = self.get_input()
            print(name)

    def handle_assembly_turn(self) -> None:
        return

    def handle_chat_turn(self) -> None:
        return