# vision/marker_fsm.py

from kiosk_guide_model import EXPECTED_ROUTE


class KioskFSM:
    def __init__(self, route):
        if not route or len(route) < 2:
            raise ValueError("FSM route must have at least 2 states")

        self.route = route
        self.index = 0
        self.current_id = self.route[0]
        self.last_valid_id = self.current_id

    def update(self, detected_id: int):
        print(
            f"[FSM] current={self.current_id}, "
            f"detected={detected_id}, "
            f"index={self.index}"
        )

        if detected_id == self.current_id:
            return self._result(True, "same_state")

        next_id = self.route[self.index + 1] if self.index + 1 < len(self.route) else None

        print(
            f"[FSM] next_expected={next_id}"
        )

        if detected_id == next_id:
            self.index += 1
            self.current_id = detected_id
            self.last_valid_id = detected_id

            # 마지막 0번 복귀 시 FSM 초기화
            if self.index == len(self.route) - 1 and detected_id == 0:
                self.index = 0
                self.current_id = 0
                self.last_valid_id = 0
                return self._result(True, "payment_complete_reset")

            return self._result(True, "valid_next")

        return {
            "ok": False,
            "message": "invalid_transition",
            "current_id": self.current_id,
            "detected_id": detected_id,
            "expected_id": next_id,
            "recovery": True
        }

    def _result(self, ok, message):
        return {
            "ok": ok,
            "message": message,
            "current_id": self.current_id,
            "expected_id": self.route[self.index + 1] if self.index + 1 < len(self.route) else None,
            "recovery": False
        }
