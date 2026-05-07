
import json
from pathlib import Path

from config import STATE_MAP

# 정상 주문 흐름
ROUTE = [
    "IDLE",
    "LISTENING",
    "CATEGORY_SELECT",
    "ITEM_SELECT",
    "OPTION_SELECT",
    "PAYMENT_SELECT",
    "CONFIRM"
]

# 오류/예외 상태
ERROR_STATES = {
    "ERROR_RECOVERY",
    "FAIL_SAFE",
    "UNKNOWN_STATE"
}


class MarkerFSM:
    def __init__(self, states_file: str = "states.json"):
        self.current_state = "IDLE"
        self.previous_state = None
        self.last_valid_state = "IDLE"
        self.states_data = self._load_states(states_file)

    def _load_states(self, states_file: str):
        path = Path(states_file)

        if not path.exists():
            raise FileNotFoundError(f"State file not found: {states_file}")

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_valid_transition(self, current_state: str, new_state: str) -> bool:

        # 정상 Route 기준으로 상태 전이가 가능한지 검사
        # 허용
        # 1) 같은 상태 유지
        # 2) 바로 다음 상태
        # 3) 바로 이전 상태
        # 4) 오류 상태로 진입

        if new_state in ERROR_STATES:
            return True

        if current_state in ERROR_STATES:
            # 복구 상태에서는 마지막 정상 상태 또는 IDLE로만 복귀 허용
            return new_state == self.last_valid_state or new_state == "IDLE"

        if current_state not in ROUTE or new_state not in ROUTE:
            return False

        current_idx = ROUTE.index(current_state)
        new_idx = ROUTE.index(new_state)

        return (
            new_idx == current_idx or
            new_idx == current_idx + 1 or
            new_idx == current_idx - 1
        )

    def update_by_marker_id(self, marker_id: int) -> bool:
        # 2x5 상태 마커 ID를 입력받아 FSM 상태를 갱신
        # 반환값
        # True: 상태 변경 발생
        # False: 상태 유지 또는 무시

        new_state = STATE_MAP.get(marker_id)

        # STATE_MAP에 없는 ID는 무시하지 않고 ERROR_RECOVERY로 보냄
        if new_state is None:
            print(f"[WARN] Unknown marker ID: {marker_id}")
            return self.force_error_recovery(reason=f"unknown_marker_id:{marker_id}")

        # 같은 상태면 변경 없음
        if new_state == self.current_state:
            return False

        # 정상 전이 검사
        if self.is_valid_transition(self.current_state, new_state):
            self.previous_state = self.current_state

            if self.current_state not in ERROR_STATES:
                self.last_valid_state = self.current_state

            self.current_state = new_state

            if self.current_state not in ERROR_STATES:
                self.last_valid_state = self.current_state

            return True

        # 잘못된 전이 감지
        print(f"[WARN] Invalid transition: {self.current_state} -> {new_state}")
        return self.force_error_recovery(
            reason=f"invalid_transition:{self.current_state}->{new_state}"
        )

    def force_error_recovery(self, reason: str = "") -> bool:
        # 강제로 ERROR_RECOVERY 상태로 전환

        if self.current_state == "ERROR_RECOVERY":
            return False

        self.previous_state = self.current_state

        if self.current_state not in ERROR_STATES:
            self.last_valid_state = self.current_state

        self.current_state = "ERROR_RECOVERY"

        if reason:
            print(f"[RECOVERY] Entered ERROR_RECOVERY: {reason}")

        return True

    def recover_to_last_valid_state(self) -> bool:
        # 마지막 정상 상태로 복귀한다.

        if self.current_state != "ERROR_RECOVERY":
            return False

        self.previous_state = self.current_state
        self.current_state = self.last_valid_state

        print(f"[RECOVERY] Recovered to {self.current_state}")
        return True

    def reset(self):
        # FSM 초기화

        self.previous_state = self.current_state
        self.current_state = "IDLE"
        self.last_valid_state = "IDLE"

    def get_current_state(self):
        return self.current_state

    def get_previous_state(self):
        return self.previous_state

    def get_last_valid_state(self):
        return self.last_valid_state

    def get_state_payload(self):
        # 현재 상태의 payload를 반환한다.
        # ERROR_RECOVERY payload가 states.json에 없으면 기본값 제공.

        if self.current_state in self.states_data:
            return self.states_data[self.current_state]

        if self.current_state == "ERROR_RECOVERY":
            return {
                "screen": "recovery",
                "target_button": "back_button",
                "local_position": {"x": -0.10, "y": -0.05, "z": 0.0},
                "message": "잘못된 상태가 감지되었습니다. 이전 단계로 돌아가세요."
            }

        return {
            "screen": "unknown",
            "target_button": None,
            "local_position": {"x": 0.0, "y": 0.0, "z": 0.0},
            "message": "Unknown state"
        }
