import pytest
import json

from src.state import DEFAULT_GAME_STATE_PATH

@pytest.fixture
def state():
    with open(DEFAULT_GAME_STATE_PATH) as df:
        return json.load(df)