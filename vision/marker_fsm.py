import json
from pathlib import Path
from config import STATE_MAP


class MarkerFSM:
    def __init__(self, states_file: str = "states.json"):
        self.current_state = "IDLE"
        self.previous_state = None
        self.states_data = self._load_states(states_file)

    def _load_states(self, states_file: str):
        path = Path(states_file)
        if not path.exists():
            raise FileNotFoundError(f"State file not found: {states_file}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def update_by_marker_id(self, marker_id: int):
        new_state = STATE_MAP.get(marker_id)

        if new_state is None:
            return False

        if new_state != self.current_state:
            self.previous_state = self.current_state
            self.current_state = new_state
            return True

        return False

    def get_current_state(self):
        return self.current_state

    def get_state_payload(self):
        return self.states_data.get(self.current_state, {})

    def get_previous_state(self):
        return self.previous_state