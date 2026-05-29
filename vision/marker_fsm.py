import json
from pathlib import Path

from config import STATE_MAP

# 정상 주문 흐름 (HCI 평가 연계)
# LISTENING 단계를 완벽히 제외하고 실제 유저 터치 진도에 맞춘 직렬 구조로 개편.
ROUTE = [
    "IDLE",
    "CATEGORY_SELECT",
    "ITEM_SELECT",
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
        # 최상위 경로 및 vision/ 하위 경로 모두 대응할 수 있도록 처리
        path = Path(states_file)
        if not path.exists():
            path = Path("vision") / states_file
            
        if not path.exists():
            # states.json 파일이 없을 때 에러로 죽지 않도록 빈 딕셔너리 예외 처리
            print(f"[WARN] States file not found: {states_file}. Using layout fallbacks.")
            return {}

        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def is_valid_transition(self, current_state: str, new_state: str) -> bool:
        # 정상 Route 기준으로 상태 전이가 가능한지 검사
        if new_state in ERROR_STATES:
            return True

        if current_state in ERROR_STATES:
            # 복구 상태에서는 마지막 정상 상태 또는 IDLE로만 복귀 허용
            return new_state == self.last_valid_state or new_state == "IDLE"

        if current_state not in ROUTE or new_state not in ROUTE:
            return False

        current_idx = ROUTE.index(current_state)
        new_idx = ROUTE.index(new_state)

        # 바로 다음 단계(+1), 이전 단계(-1), 또는 현재 단계 유지만 정상으로 판정
        return (
            new_idx == current_idx or
            new_idx == current_idx + 1 or
            new_idx == current_idx - 1
        )

    def update_by_marker_id(self, marker_id: int) -> bool:
        # 아루코 마커 ID를 정수형으로 확실하게 형변환 안전장치 추가
        try:
            m_id = int(marker_id)
        except (TypeError, ValueError):
            print(f"[WARN] Invalid marker_id type: {marker_id}")
            return self.force_error_recovery(reason="invalid_marker_id_type")

        new_state = STATE_MAP.get(m_id)

        # STATE_MAP에 없는 ID는 ERROR_RECOVERY로 전송
        if new_state is None:
            print(f"[WARN] Unknown marker ID: {m_id}")
            return self.force_error_recovery(reason=f"unknown_marker_id:{m_id}")

        # 같은 상태면 변경 없음
        if new_state == self.current_state:
            return False

        # 정상 전이 검사
        if self.is_valid_transition(self.current_state, new_state):
            print(f"[FSM 이동 성공] {self.current_state} -> {new_state} (마커: {m_id})")
            self.previous_state = self.current_state

            if self.current_state not in ERROR_STATES:
                self.last_valid_state = self.current_state

            self.current_state = new_state

            if self.current_state not in ERROR_STATES:
                self.last_valid_state = self.current_state

            return True

        # 잘못된 전이 감지
        print(f"[WARN] Invalid transition guard triggered: {self.current_state} -> {new_state} (마커: {m_id})")
        return self.force_error_recovery(
            reason=f"invalid_transition:{self.current_state}->{new_state}"
        )

    def force_error_recovery(self, reason: str = "") -> bool:
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
        if self.current_state != "ERROR_RECOVERY":
            return False

        self.previous_state = self.current_state
        self.current_state = self.last_valid_state

        print(f"[RECOVERY] Recovered to {self.current_state}")
        return True

    def reset(self):
        self.previous_state = self.current_state
        self.current_state = "IDLE"
        self.last_valid_state = "IDLE"

    public_state = property(lambda self: self.current_state)

    def get_current_state(self):
        return self.current_state

    def get_previous_state(self):
        return self.previous_state

    def get_last_valid_state(self):
        return self.last_valid_state

    def get_state_payload(self):
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