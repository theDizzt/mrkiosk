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
    RING_COORDINATE_MAP, # config.py의 고정 맵 바인딩
)

from marker_fsm import MarkerFSM

def decode_aruco_id(marker_id):
    """
    [완전 개정] 홀수/짝수 무관하게 웹페이지 3진법 인코딩 매커니즘을 100% 역산해내는 디코더
    """
    result = {"phase": "UNKNOWN", "details": {}}
    m_id = int(marker_id)
    
    if 0 <= m_id <= 160:
        result["phase"] = "Phase_00"
        if m_id == 0:
            result["details"]["state"] = "초기 매장/포장 선택 화면"
        elif m_id % 32 == 0:
            cat_num = m_id // 32
            cat_names = {1: "Coffee", 2: "Tea", 3: "Ade/Juice", 4: "Beverage", 5: "Blended"}
            result["details"]["state"] = f"{cat_names.get(cat_num, 'Unknown')} 카테고리 탐색"

    elif 256 <= m_id <= 447:
        result["phase"] = "Phase_01"
        temp_val = m_id - 256
        menu_hash = temp_val // 32
        option_code = temp_val % 32
        
        # 3진법 수학적 역산 (나머지 연산 안전장치 강화)
        temperature = option_code // 9
        rem = option_code % 9
        sugar = rem // 3
        ice = rem % 3
        
        result["details"]["menu_hash"] = menu_hash
        result["details"]["temperature"] = "ICED" if temperature == 0 else "HOT"
        result["details"]["sugar"] = "덜 달게" if sugar == 0 else ("보통" if sugar == 1 else "달게")
        result["details"]["ice"] = "얼음 많이" if ice == 0 else ("얼음 보통" if ice == 1 else "얼음 적게")
        
        # 피실험자의 UI 진행 상황에 맞춘 다음 링 위치 결정을 위한 스텝 플래그
        # 처음 진입해서 옵션을 하나도 변경 안 한 기본 상태 검사
        if option_code == 4: # 기본 상태 (ICED(0*9) + 보통(1*3) + 얼음보통(1) = 4)
            result["details"]["current_step"] = "TEMPERATURE"
        else:
            result["details"]["current_step"] = "PROGRESSING"

    elif 512 <= m_id <= 628:
        result["phase"] = "Phase_10"
        result["details"]["common_reference_id"] = (m_id - 512) // 4

    elif m_id in [768, 769]:
        result["phase"] = "Phase_11"
        result["details"]["state"] = "최종 카드 결제 단계"
        
    return result
    """
    [교정] script.js의 3진법 인코딩 매커니즘과 100% 일치하도록 디코딩 구조 동기화
    """
    result = {"phase": "UNKNOWN", "details": {}}
    m_id = int(marker_id)
    
    if 0 <= m_id <= 160:
        result["phase"] = "Phase_00"
        if m_id == 0:
            result["details"]["state"] = "초기 매장/포장 선택 화면"
        elif m_id % 32 == 0:
            cat_num = m_id // 32
            cat_names = {1: "Coffee", 2: "Tea", 3: "Ade/Juice", 4: "Beverage", 5: "Blended"}
            result["details"]["state"] = f"{cat_names.get(cat_num, 'Unknown')} 카테고리 탐색"

    elif 256 <= m_id <= 447:
        result["phase"] = "Phase_01"
        temp_val = m_id - 256
        menu_hash = temp_val // 32
        option_code = temp_val % 32
        
        # 3진법 역산 역추적 (script.js 동기화)
        temperature = option_code // 9
        rem = option_code % 9
        sugar = rem // 3
        ice = rem % 3
        
        result["details"]["menu_hash"] = menu_hash
        result["details"]["temperature"] = "ICED" if temperature == 0 else "HOT"
        result["details"]["sugar"] = "덜 달게" if sugar == 0 else ("보통" if sugar == 1 else "달게")
        result["details"]["ice"] = "얼음 많이" if ice == 0 else ("얼음 보통" if ice == 1 else "얼음 적게")
        
        # 유저가 조작 중인 현재 세부 단계 판별 플래그 주입
        # 초기 진입 상태 판단 가드 설정
        if option_code == 0:
            result["details"]["current_step"] = "TEMPERATURE"
        else:
            result["details"]["current_step"] = "PROGRESSING"

    elif 512 <= m_id <= 628:
        result["phase"] = "Phase_10"
        result["details"]["common_reference_id"] = (m_id - 512) // 4

    elif m_id in [768, 769]:
        result["phase"] = "Phase_11"
        result["details"]["state"] = "최종 카드 결제 단계"
        
    return result

def _speak_worker(text):
    try:
        engine = pyttsx3.init()
        engine.setProperty('rate', 150) # 고령층 피실험자용 속도 감속
        engine.say(text)
        engine.runAndWait()
    except Exception as e:
        print(f"TTS Speech Failed: {e}")

def speak(text):
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
                current_rvec, current_tvec = estimate_pose_modern(aruco_corners[i][0], MARKER_LENGTH, camera_matrix, dist_coeffs)
                
                if current_rvec is not None and current_tvec is not None:
                    cv2.drawFrameAxes(frame, camera_matrix, dist_coeffs, current_rvec, current_tvec, 0.02)
                    
                    if current_id == REFERENCE_ARUCO_ID:
                        rvec, tvec = current_rvec, current_tvec
                        pose_text = format_pose_text(tvec)
                    else:
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

        # ==============================================================================
        # [실시간 교정 완료] FSM 트랜잭션 수립 및 매 프레임 동적 링 좌표 연산 구역
        # ==============================================================================
        if detected_state_id is not None:
            last_state_marker_id = detected_state_id

            if rvec is not None and tvec is not None:
                # 1. FSM 상태 변경 여부 체크 및 상태 전환
                changed = fsm.update_by_marker_id(detected_state_id)
                current_state_name = fsm.get_current_state()
                kiosk_info = decode_aruco_id(detected_state_id)

                # 2. 최초 상태 변경 시에만 TTS 음성 안내 1회 출력 (프레임 마비 방지)
                if changed:
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
                    
                    print(f"[FSM 이동 성공] {fsm.previous_state} -> {current_state_name} (마커: {detected_state_id})")

                # 3. [★ 핵심 교정] changed 블록 밖으로 탈출시켜 '매 프레임' 실시간 좌표를 갱신합니다.
                local_position = {"x": 0.0, "y": 0.0, "z": 0.0}

                if kiosk_info["phase"] == "Phase_01":
                    details = kiosk_info["details"]
                    step = details.get("current_step")
                    
                    # 옵션창 상태 비트에 따른 타겟 가이드 버튼 위치 동적 매핑
                    if step == "TEMPERATURE":
                        # 기본 진입 시: 온도 선택 (ICED 버튼 구역 가이드)
                        local_position = {"x": -0.06, "y": -0.02, "z": 0.0}
                    elif details.get("temperature") == "ICED" and details.get("ice") == "얼음 보통":
                        # 온도 선택 완료 후 기본 세팅: 얼음 선택 행 가이드
                        local_position = {"x": 0.0, "y": -0.12, "z": 0.0}
                    else:
                        # 그 외 최종 상태: 장바구니 [담기] 버튼 구역 가이드
                        local_position = {"x": -0.05, "y": -0.18, "z": 0.0}
                else:
                    # Phase 01이 아닌 일반 카테고리/결제 단계는 config.py 고정 테이블 실시간 참조
                    local_position = RING_COORDINATE_MAP.get(detected_state_id, {"x": 0.0, "y": 0.0, "z": 0.0})

                # 4. 행렬 연산을 통해 3D 절대 공간 좌표로 실시간 변환
                world_position = local_to_camera_world(rvec, tvec, local_position)
                world_position = position_filter.update(world_position)
                
                # 런타임 공유 페이로드 업데이트
                payload = dict(fsm.get_state_payload()) if fsm.get_state_payload() else {}
                payload["kiosk_phase"] = kiosk_info["phase"]
                payload["kiosk_details"] = kiosk_info["details"]
                payload["local_position"] = local_position
                payload["world_position"] = world_position

                # 5. 매 프레임마다 변동되는 리얼타임 3D 좌표 콘솔 인쇄
                print(f"[트래킹 성공] 마커 ID: {detected_state_id} -> 3D World XYZ: [{world_position['x']:.4f}m, {world_position['y']:.4f}m, {world_position['z']:.4f}m]")

                # 로깅 및 상태 저장은 데이터 오버헤드를 막기 위해 상태가 바뀐 시점에만 기록
                if changed:
                    append_log_event(current_state_name, detected_state_id, rvec, tvec, payload)
                    write_runtime_state(current_state_name, detected_state_id, rvec, tvec, payload)
                    log_event(current_state_name, detected_state_id, tvec)

        # 769번 고정마커 단독 노출 예외 가드 핸들링
        if last_state_marker_id == REFERENCE_ARUCO_ID and rvec is not None and tvec is not None:
            if fsm.get_current_state() == "CONFIRM":
                local_position = RING_COORDINATE_MAP.get(REFERENCE_ARUCO_ID, {"x": -0.15, "y": 0.20, "z": 0.0})
                world_position = local_to_camera_world(rvec, tvec, local_position)
                world_position = position_filter.update(world_position)

        draw_state_info(frame, fsm.get_current_state(), fsm.get_state_payload(), pose_text, last_state_marker_id)
        cv2.imshow("MR Kiosk Prototype - Unified ArUco System", frame)

        if cv2.waitKey(1) & 0xFF == 27: # ESC
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()