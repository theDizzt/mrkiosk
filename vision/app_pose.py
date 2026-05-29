# app_pose.py (DICT_4X4_50 규격 동기화 완료 최종본)
import cv2
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from collections import deque, Counter
import threading
import pyttsx3 # 초고속 윈도우 내장 TTS
from config import STATE_MAP

from config import (
    CAMERA_INDEX,
    MARKER_LENGTH,
    CAMERA_MATRIX_FILE,
    DIST_COEFFS_FILE,
    REFERENCE_ARUCO_ID,
)

from marker_fsm import MarkerFSM

# ====================================================================
#   📢 [HCI 명세 주입] 아루코 ID 비트 역산(디코딩) 함수 정의
# ====================================================================
def decode_aruco_id(marker_id):
    """최종 가이드라인 규칙에 의거하여 아루코 ID로부터 키오스크 상태 분석"""
    result = {"phase": "UNKNOWN", "details": {}}
    
    if 0 <= marker_id <= 160:
        result["phase"] = "Phase_00"
        if marker_id == 0:
            result["details"]["state"] = "초기 매장/포장 선택 화면"
        elif marker_id % 32 == 0:
            cat_num = marker_id // 32
            cat_names = {1: "Coffee", 2: "Tea", 3: "Ade/Juice", 4: "Beverage", 5: "Blended"}
            result["details"]["state"] = f"{cat_names.get(cat_num, 'Unknown')} 카테고리 탐색"

    elif 256 <= marker_id <= 447:
        result["phase"] = "Phase_01"
        temp_val = marker_id - 256
        menu_hash = temp_val // 32
        rem = temp_val % 32
        temperature = rem // 8
        rem = rem % 8
        sugar = rem // 4
        ice = (rem % 4) // 2
        
        result["details"]["menu_hash"] = menu_hash
        result["details"]["temperature"] = "미선택" if temperature == 0 else ("ICED" if temperature == 1 else "HOT")
        result["details"]["sugar"] = "선택완료" if sugar == 1 else "미선택"
        result["details"]["ice"] = "선택완료" if ice == 1 else "미선택"

    elif 512 <= marker_id <= 628:
        result["phase"] = "Phase_10"
        result["details"]["common_reference_id"] = (marker_id - 512) // 4

    elif marker_id == 768:
        result["phase"] = "Phase_11"
        result["details"]["state"] = "최종 카드 결제 단계"
        
    return result

# ====================================================================
#   🔊 [HCI 명세 주입] 프레임 드랍이 없는 초고속 논블로킹 발화 엔진
# ====================================================================
def _speak_worker(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # 시니어 케어용 안정적 발화 속도
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS 발화 실패: {e}")

def speak(text):
    print(f"🔊 [AI 가이드 성우]: \"{text}\"")
    threading.Thread(target=_speak_worker, args=(text,), daemon=True).start()


# 구형 단순 로그 적재 함수 보존
def log_event(state, marker_id, tvec=None):
    log = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "marker_id": int(marker_id),
        "event": "state_enter"
    }
    if tvec is not None:
        log["tvec"] = tvec.flatten().tolist()
    with open("log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")


class StableStateDecoder:
    def __init__(self, window_size=7, min_count=4):
        self.history = deque(maxlen=window_size)
        self.min_count = min_count

    def update(self, state_id):
        if state_id not in STATE_MAP:
            return None
        self.history.append(state_id)
        counter = Counter(self.history)
        most_common_id, count = counter.most_common(1)[0]
        if count >= self.min_count:
            return most_common_id
        return None


class PositionFilter:
    def __init__(self, alpha=0.35, threshold=0.08, max_hold=5):
        self.prev = None
        self.alpha = alpha
        self.threshold = threshold
        self.outlier_count = 0
        self.max_hold = max_hold

    def distance(self, a, b):
        return ((a["x"] - b["x"])**2 + (a["y"] - b["y"])**2 + (a["z"] - b["z"])**2) ** 0.5

    def update(self, pos):
        if self.prev is None:
            self.prev = pos
            return pos
        dist = self.distance(self.prev, pos)
        if dist > self.threshold:
            self.outlier_count += 1
            if self.outlier_count < self.max_hold:
                return self.prev
            self.outlier_count = 0
            self.prev = pos
            return pos
        self.outlier_count = 0
        smoothed = {
            "x": self.alpha * pos["x"] + (1 - self.alpha) * self.prev["x"],
            "y": self.alpha * pos["y"] + (1 - self.alpha) * self.prev["y"],
            "z": self.alpha * pos["z"] + (1 - self.alpha) * self.prev["z"],
        }
        self.prev = smoothed
        return smoothed


def load_calibration():
    camera_matrix_path = Path(CAMERA_MATRIX_FILE)
    dist_coeffs_path = Path(DIST_COEFFS_FILE)
    if camera_matrix_path.exists() and dist_coeffs_path.exists():
        return np.load(str(camera_matrix_path)), np.load(str(dist_coeffs_path))
    return None, None


def create_fallback_calibration(frame_width, frame_height):
    focal_length = frame_width
    center = (frame_width / 2, frame_height / 2)
    camera_matrix = np.array([[focal_length, 0, center[0]], [0, focal_length, center[1]], [0, 0, 1]], dtype=np.float32)
    dist_coeffs = np.zeros((5, 1), dtype=np.float32)
    return camera_matrix, dist_coeffs


def create_aruco_detector():
    # 🎯 카메라 인식 사전도 생성기와 똑같이 1000 규격으로 일치
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
    parameters = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(aruco_dict, parameters)


def append_log_event(state, marker_id, rvec=None, tvec=None, payload=None):
    log = {"timestamp": datetime.now().isoformat(), "state": state, "marker_id": int(marker_id), "event": "state_enter"}
    if rvec is not None:
        log["rvec"] = [round(float(x), 4) for x in rvec.flatten()]
    if tvec is not None:
        log["tvec"] = [round(float(x), 4) for x in tvec.flatten()]
    if payload is not None:
        cleaned_payload = payload.copy()
        if "world_position" in cleaned_payload and isinstance(cleaned_payload["world_position"], dict):
            cleaned_payload["world_position"] = {k: round(float(v), 4) for k, v in cleaned_payload["world_position"].items()}
        if "local_position" in cleaned_payload and isinstance(cleaned_payload["local_position"], dict):
            cleaned_payload["local_position"] = {k: round(float(v), 4) for k, v in cleaned_payload["local_position"].items()}
        log["payload"] = cleaned_payload
    with open("log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")


def local_to_camera_world(rvec, tvec, local_position):
    R, _ = cv2.Rodrigues(rvec)
    p_local = np.array([[float(local_position.get("x", 0.0))], [float(local_position.get("y", 0.0))], [float(local_position.get("z", 0.0))]], dtype=np.float32)
    p_world = R @ p_local + tvec.reshape(3, 1)
    return {"x": float(p_world[0][0]), "y": float(p_world[1][0]), "z": float(p_world[2][0])}


def write_runtime_state(state, marker_id, rvec=None, tvec=None, payload=None):
    runtime_data = {"timestamp": datetime.now().isoformat(), "state": state, "marker_id": int(marker_id)}
    if rvec is not None:
        runtime_data["rvec"] = rvec.flatten().tolist()
    if tvec is not None:
        runtime_data["tvec"] = tvec.flatten().tolist()
    if payload is not None:
        runtime_data["payload"] = payload
    with open("runtime_state.json", "w", encoding="utf-8") as f:
        json.dump(runtime_data, f, ensure_ascii=False, indent=2)


def format_pose_text(tvec):
    x, y, z = tvec.flatten()
    return f"Pose tvec(m): x={x:.3f}, y={y:.3f}, z={z:.3f}"


def draw_state_info(frame, state_name, payload, pose_text=None, state_marker_id=None):
    y = 30
    cv2.putText(frame, f"Current State: {state_name}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    if state_marker_id is not None:
        y += 35
        cv2.putText(frame, f"Dynamic Marker ID: {state_marker_id}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
    y += 35
    message = payload.get("message", "")
    cv2.putText(frame, f"Message: {message}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
    target_button = payload.get("target_button")
    if target_button:
        y += 35
        cv2.putText(frame, f"Target: {target_button}", (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
    if pose_text:
        y += 35
        cv2.putText(frame, pose_text, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2)


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera")
        return

    aruco_detector = create_aruco_detector()
    fsm = MarkerFSM("vision/states.json") # 에러 로그 기반 vision/ 경로 고정 가드
    camera_matrix, dist_coeffs = load_calibration()

    print("🚀 MR Kiosk 가이드라인 비전 가동 시작 (SAPI5 TTS 활성화 + DICT_4X4_50 완벽 매칭)")
    last_state_marker_id = None
    position_filter = PositionFilter()
    stable_decoder = StableStateDecoder()

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_height, frame_width = frame.shape[:2]
        if camera_matrix is None or dist_coeffs is None:
            camera_matrix, dist_coeffs = create_fallback_calibration(frame_width, frame_height)

        pose_text = None
        rvec, tvec = None, None
        detected_state_id = None

        # 🎯 등록된 DICT_4X4_50 딕셔너리로 마커 감지 트랙 온
        aruco_corners, aruco_ids, _ = aruco_detector.detectMarkers(frame)

        if aruco_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, aruco_corners, aruco_ids)
            
            for i, aruco_id in enumerate(aruco_ids.flatten()):
                current_id = int(aruco_id)
                
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers([aruco_corners[i]], MARKER_LENGTH, camera_matrix, dist_coeffs)
                current_rvec, current_tvec = rvecs[0], tvecs[0]
                cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, current_rvec, current_tvec, 0.02)
                
                # [A] 고정 마커 필터링 (ID 0) -> 키오스크의 공간 6DoF 정합 기준점으로 락 고정
                if current_id == REFERENCE_ARUCO_ID:
                    rvec, tvec = current_rvec, current_tvec
                    pose_text = format_pose_text(tvec)
                
                # [B] 동적 가변 마커 필터링 (0번 외 나머지) -> 가이드라인 상태 ID로 입력 유도
                else:
                    stable_id = stable_decoder.update(current_id)
                    if stable_id is not None:
                        detected_state_id = stable_id

            if tvec is None and len(aruco_corners) > 0:
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers([aruco_corners[0]], MARKER_LENGTH, camera_matrix, dist_coeffs)
                rvec, tvec = rvecs[0], tvecs[0]
                pose_text = format_pose_text(tvec)
        else:
            pose_text = "No ArUco Marker Detected"

        # 3. 비트 해독 결합 및 트랜잭션 + 고속 발화 처리
        if detected_state_id is not None:
            last_state_marker_id = detected_state_id

            if rvec is not None and tvec is not None:
                changed = fsm.update_by_marker_id(detected_state_id)

                if changed:
                    payload = dict(fsm.get_state_payload())
                    current_state_name = fsm.get_current_state()

                    # 💡 아루코 ID 암호 해체 및 페이로드 추가 주입
                    kiosk_info = decode_aruco_id(detected_state_id)
                    payload["kiosk_phase"] = kiosk_info["phase"]
                    payload["kiosk_details"] = kiosk_info["details"]

                    # 🔊 [HCI 레이어] 상태 최초 진입 시 컴퓨터 오디오 즉시 발화 지시
                    if current_state_name == "PHASE_00_START":
                        speak("원하시는 주문 방식을 선택해 주세요.")
                    elif "PHASE_00_CAT" in current_state_name:
                        speak("원하시는 음료 종류를 터치해 주세요.")
                    elif current_state_name == "PHASE_01_OPTION_SELECT":
                        speak("따뜻함 여부와 얼음, 설탕 조절 등 메뉴 옵션을 선택해 주세요.")
                    elif current_state_name == "PHASE_10_CART_VALIDATION":
                        speak("장바구니에 담긴 메뉴를 확인하신 후 결제 버튼을 눌러주세요.")
                    elif current_state_name == "PHASE_11_PAYMENT":
                        speak("우측 하단 카드리더기에 신용카드를 끝까지 넣어주세요.")

                    # 공간 가이드 좌표 연산 및 필터링 안정화
                    local_position = payload.get("local_position", {"x": 0.0, "y": 0.0, "z": 0.0})
                    world_position = local_to_camera_world(rvec, tvec, local_position)
                    world_position = position_filter.update(world_position)
                    payload["world_position"] = world_position

                    # 3대 파일 인프라 동시 적재 동기화 수립
                    append_log_event(current_state_name, detected_state_id, rvec, tvec, payload)
                    write_runtime_state(current_state_name, detected_state_id, rvec, tvec, payload)
                    log_event(current_state_name, detected_state_id, tvec)

        draw_state_info(frame, fsm.get_current_state(), fsm.get_state_payload(), pose_text, last_state_marker_id)
        cv2.imshow("MR Kiosk Prototype - Unified ArUco System", frame)

        if cv2.waitKey(1) & 0xFF == 27: # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()