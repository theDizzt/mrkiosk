import cv2
import numpy as np
from pathlib import Path
import json
from datetime import datetime
from collections import deque, Counter
import threading
import pyttsx3 # Windows SAPI5 TTS Engine
from config import STATE_MAP

from config import (
    CAMERA_INDEX,
    MARKER_LENGTH,
    CAMERA_MATRIX_FILE,
    DIST_COEFFS_FILE,
    REFERENCE_ARUCO_ID,
)

from marker_fsm import MarkerFSM

def decode_aruco_id(marker_id):
    """
    최종 가이드라인 규칙에 의거하여 아루코 ID로부터 키오스크 상태 분석
    """
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

def _speak_worker(text):
    """
    백그라운드 스레드에서 SAPI5 엔진을 구동하여 TTS 음성을 출력하는 함수
    """
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # 고령층 피실험자를 배려한 발화 속도 저하
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Speech Failed: {e}")

def speak(text):
    """
    비전 연산 메인 루프 프레임 저하 방지를 위한 비동기 발화 인터페이스
    """
    print(f"TTS Active User Guide: \"{text}\"")
    threading.Thread(target=_speak_worker, args=(text,), daemon=True).start()

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

def estimate_pose_modern(corners, marker_length, camera_matrix, dist_coeffs):
    """
    OpenCV 4.7+ 버전용 estimatePoseSingleMarkers 대체 구동 구현 함수
    """
    obj_points = np.array([
        [-marker_length / 2,  marker_length / 2, 0],
        [ marker_length / 2,  marker_length / 2, 0],
        [ marker_length / 2, -marker_length / 2, 0],
        [-marker_length / 2, -marker_length / 2, 0]
    ], dtype=np.float32)
    
    valid, rvec, tvec = cv2.solvePnP(obj_points, corners, camera_matrix, dist_coeffs, flags=cv2.SOLVEPNP_ITERATIVE)
    if valid:
        return rvec.reshape(1, 3), tvec.reshape(1, 3)
    return None, None

def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera")
        return

    aruco_detector = create_aruco_detector()
    fsm = MarkerFSM("vision/states.json")
    camera_matrix, dist_coeffs = load_calibration()

    print("MR Kiosk Guideline Vision Engine Started (SAPI5 TTS Active + DICT_4X4_1000 Sync)")
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

        aruco_corners, aruco_ids, _ = aruco_detector.detectMarkers(frame)

        if aruco_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, aruco_corners, aruco_ids)
            
            for i, aruco_id in enumerate(aruco_ids.flatten()):
                current_id = int(aruco_id)
                
                # 최신 OpenCV 버전 대응용 포즈 연산 우회 호출
                current_rvec, current_tvec = estimate_pose_modern(aruco_corners[i][0], MARKER_LENGTH, camera_matrix, dist_coeffs)
                
                if current_rvec is not None and current_tvec is not None:
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, current_rvec, current_tvec, 0.02)
                    
                    # 0번 고정 마커: 키오스크 기준 좌표계 획득
                    if current_id == REFERENCE_ARUCO_ID:
                        rvec, tvec = current_rvec, current_tvec
                        pose_text = format_pose_text(tvec)
                    
                    # 가변 마커: 과업 상태 전이 트리거

                    else:
                        # 0번 고정 마커가 인식되어 tvec(기준 좌표)이 먼저 확보된 경우에만 상태 마커를 연산함
                        if tvec is not None: 
                            stable_id = stable_decoder.update(current_id)
                            if stable_id is not None:
                                detected_state_id = stable_id       

            if tvec is None and len(aruco_corners) > 0:
                current_rvec, current_tvec = estimate_pose_modern(aruco_corners[0][0], MARKER_LENGTH, camera_matrix, dist_coeffs)
                if current_rvec is not None and current_tvec is not None:
                    rvec, tvec = current_rvec, current_tvec
                    pose_text = format_pose_text(tvec)
        else:
            pose_text = "No ArUco Marker Detected"

        # FSM 트랜잭션 수립 및 비동기 발화 구역

        if detected_state_id is not None:
            last_state_marker_id = detected_state_id

            if rvec is not None and tvec is not None:
                changed = fsm.update_by_marker_id(detected_state_id)

                if changed:
                    payload = dict(fsm.get_state_payload())
                    current_state_name = fsm.get_current_state()

                    kiosk_info = decode_aruco_id(detected_state_id)
                    payload["kiosk_phase"] = kiosk_info["phase"]
                    payload["kiosk_details"] = kiosk_info["details"]

                    # -----------------------------------------------------------
                    # 최적화된 가이드라인 TTS 발화 설계
                    # -----------------------------------------------------------
                    if current_state_name == "IDLE":
                        speak("원하시는 주문 방식을 선택해 주세요.")
                    elif current_state_name == "CATEGORY_SELECT":
                        speak("원하시는 음료 종류를 터치해 주세요.")
                    elif current_state_name == "ITEM_SELECT":
                        speak("원하시는 상세 메뉴와 옵션을 선택하신 후 장바구니에 담아주세요.")
                    elif current_state_name == "PAYMENT_SELECT":
                        speak("장바구니에 담긴 메뉴를 확인하신 후 결제 버튼을 눌러주세요.")
                    elif current_state_name == "CONFIRM":
                        speak("우측 하단 카드리더기에 신용카드를 끝까지 넣어주세요.")
                    elif current_state_name == "ERROR_RECOVERY":
                        speak("잘못된 입력이 감지되었습니다. 뒤로 가기 버튼을 눌러주세요.")
                    # -----------------------------------------------------------

                    local_position = payload.get("local_position", {"x": 0.0, "y": 0.0, "z": 0.0})
                    world_position = local_to_camera_world(rvec, tvec, local_position)
                    world_position = position_filter.update(world_position)
                    payload["world_position"] = world_position

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