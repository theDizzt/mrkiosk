# vision/marker_fsm.py

class KioskFSM:
    def __init__(self, route, debug=False):
        if not route or len(route) < 2:
            raise ValueError("FSM route must have at least 2 states")

        self.route = route
        self.index = 0
        self.current_id = self.route[0]
        self.last_valid_id = self.current_id
        self.debug = debug

    def _log(self, message):
        if self.debug:
            print(message)

    def update(self, detected_id: int):
        """
        detected_id:
            현재 카메라가 인식한 상태 마커 ID

        return:
            current_id: FSM이 인정한 현재 상태
            expected_id: 다음에 가야 할 상태
        """

        next_id = self.route[self.index + 1] if self.index + 1 < len(self.route) else None

        # 1. 현재 상태와 같은 마커를 계속 보고 있는 경우
        if detected_id == self.current_id:
            return self._result(True, "same_state")

        # 2. 정상적으로 다음 상태로 이동한 경우
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

        # 3. route 안에 있는 상태를 중간에 다시 잡은 경우
        # 예: 상태 인식이 잠깐 흔들렸다가 route 내부 상태로 재동기화
        if detected_id in self.route:
            self.index = self.route.index(detected_id)
            self.current_id = detected_id
            self.last_valid_id = detected_id
            return self._result(True, "sync_state")

        # 4. route에 없는 이상한 상태가 들어온 경우
        return {
            "ok": False,
            "message": "invalid_transition",
            "current_id": self.current_id,
            "detected_id": detected_id,
            "expected_id": next_id,
            "recovery": True,
        }

    def _result(self, ok, message):
        next_id = self.route[self.index + 1] if self.index + 1 < len(self.route) else None

        return {
            "ok": ok,
            "message": message,
            "current_id": self.current_id,
            "expected_id": next_id,
            "recovery": False,
        }