import cv2
import numpy as np
from pathlib import Path
import json # 로그/연동용 JSON 저장을 위해 추가
from datetime import datetime # 타임스탬프 기록용 추가
from collections import deque, Counter
from config import STATE_MAP

from config import (
    CAMERA_INDEX,
    MARKER_LENGTH,
    CAMERA_MATRIX_FILE,
    DIST_COEFFS_FILE,
    REFERENCE_ARUCO_ID,
)

from marker_fsm import MarkerFSM


class StableStateDecoder:
    def __init__(self, window_size=7, min_count=4):
        self.history = deque(maxlen=window_size)
        self.min_count = min_count

    def update(self, state_id):
        # STATE_MAP에 없는 ID는 무시
        if state_id not in STATE_MAP:
            return None

        self.history.append(state_id)

        counter = Counter(self.history)
        most_common_id, count = counter.most_common(1)[0]

        if count >= self.min_count:
            return most_common_id

        return None


def load_calibration():
    camera_matrix_path = Path(CAMERA_MATRIX_FILE)
    dist_coeffs_path = Path(DIST_COEFFS_FILE)

    if camera_matrix_path.exists() and dist_coeffs_path.exists():
        camera_matrix = np.load(str(camera_matrix_path))
        dist_coeffs = np.load(str(dist_coeffs_path))
        print("Calibration files loaded successfully.")
        return camera_matrix, dist_coeffs

    print("Calibration files not found.")
    print("Using temporary fake calibration for prototype test only.")
    return None, None


def create_fallback_calibration(frame_width, frame_height):
    focal_length = frame_width
    center = (frame_width / 2, frame_height / 2)

    camera_matrix = np.array([
        [focal_length, 0, center[0]],
        [0, focal_length, center[1]],
        [0, 0, 1]
    ], dtype=np.float32)

    dist_coeffs = np.zeros((5, 1), dtype=np.float32)
    return camera_matrix, dist_coeffs


# ArUco Pose 감지
def create_aruco_detector():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    return cv2.aruco.ArucoDetector(aruco_dict, parameters)


# contour approx points를 좌상, 우상, 우하, 좌하 순서로 정렬
def order_corners(points):
    pts = points.reshape(4, 2).astype(np.float32)

    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    ordered = np.zeros((4, 2), dtype=np.float32)
    ordered[0] = pts[np.argmin(s)]       # top-left
    ordered[2] = pts[np.argmax(s)]       # bottom-right
    ordered[1] = pts[np.argmin(diff)]    # top-right
    ordered[3] = pts[np.argmax(diff)]    # bottom-left

    return ordered


# 2x5 비트 마커 디코딩
def decode_2x5_marker(gray, corners):
    # corners: (4,2) 형태 (marker 영역)
    # return: int marker_id (0~1023) or None

    # perspective transform → 정사각형 정렬
    size = 200

    src_pts = order_corners(corners)
    dst_pts = np.array([
        [0, 0],
        [size, 0],
        [size, size],
        [0, size]
    ], dtype=np.float32)

    matrix = cv2.getPerspectiveTransform(src_pts, dst_pts)
    warped = cv2.warpPerspective(gray, matrix, (size, size))

    warped = cv2.GaussianBlur(warped, (3, 3), 0)
    _, binary = cv2.threshold(
        warped,
        100,
        255,
        cv2.THRESH_BINARY
    )

    rows, cols = 2, 5
    cell_h = size // rows
    cell_w = size // cols

    bits = []

    for r in range(rows):
        for c in range(cols):
            y1 = r * cell_h
            y2 = (r + 1) * cell_h
            x1 = c * cell_w
            x2 = (c + 1) * cell_w

            margin_y = int(cell_h * 0.1)
            margin_x = int(cell_w * 0.1)

            cell = binary[
                y1 + margin_y:y2 - margin_y,
                x1 + margin_x:x2 - margin_x
            ]

            mean_val = np.mean(cell)

            # 검정이면 1, 흰색이면 0
            bit = 1 if mean_val < 128 else 0
            bits.append(bit)

    # bit → int
    marker_id = 0
    for bit in bits:
        marker_id = (marker_id << 1) | bit

    return marker_id, bits



def get_bbox_from_points(points):
    pts = points.reshape(-1, 2)
    x, y, w, h = cv2.boundingRect(pts.astype(np.int32))
    return x, y, w, h


def bbox_intersection_ratio(box_a, box_b):
    ax, ay, aw, ah = box_a
    bx, by, bw, bh = box_b

    ax2, ay2 = ax + aw, ay + ah
    bx2, by2 = bx + bw, by + bh

    ix1 = max(ax, bx)
    iy1 = max(ay, by)
    ix2 = min(ax2, bx2)
    iy2 = min(ay2, by2)

    iw = max(0, ix2 - ix1)
    ih = max(0, iy2 - iy1)

    inter_area = iw * ih
    area_a = aw * ah

    if area_a <= 0:
        return 0.0

    return inter_area / float(area_a)


def detect_state_markers(gray, aruco_corners=None):
    # 2x5 상태 마커 전체 영역을 찾음
    # ArUco 마커와 겹치는 후보는 제외

    aruco_boxes = []
    if aruco_corners is not None:
        for c in aruco_corners:
            aruco_boxes.append(get_bbox_from_points(c))

    blurred = cv2.GaussianBlur(gray, (5, 5), 0)

    _, binary = cv2.threshold(
        blurred,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 작은 칸들이 하나의 2x5 블록으로 붙도록 함
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 9))
    merged = cv2.dilate(binary, kernel, iterations=2)

    contours, _ = cv2.findContours(
        merged,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )

    state_markers = []

    for contour in contours:
        area = cv2.contourArea(contour)

        if area < 2000:
            continue

        rect = cv2.minAreaRect(contour)
        box = cv2.boxPoints(rect).astype(np.int32)

        x, y, w, h = cv2.boundingRect(box)
        if h == 0:
            continue

        aspect_ratio = w / float(h)

        if not (1.8 <= aspect_ratio <= 3.5):
            continue

        candidate_box = (x, y, w, h)

        # ArUco와 겹치면 상태 마커 후보에서 제외
        overlapped_with_aruco = False
        for aruco_box in aruco_boxes:
            if bbox_intersection_ratio(candidate_box, aruco_box) > 0.2:
                overlapped_with_aruco = True
                break

        if overlapped_with_aruco:
            continue

        state_markers.append(box)

    return state_markers


class PositionFilter:
    def __init__(self, alpha=0.35, threshold=0.08, max_hold=5):
        self.prev = None
        self.alpha = alpha
        self.threshold = threshold  # 튐 기준 (미터)
        self.outlier_count = 0
        self.max_hold = max_hold  # 계속 튀면 허용

    def distance(self, a, b):
        return ((a["x"] - b["x"])**2 +
                (a["y"] - b["y"])**2 +
                (a["z"] - b["z"])**2) ** 0.5

    def update(self, pos):
        # 첫 프레임
        if self.prev is None:
            self.prev = pos
            return pos

        dist = self.distance(self.prev, pos)

        # 이상치 감지
        if dist > self.threshold:
            self.outlier_count += 1

            print(f"[OUTLIER] jump={dist:.3f}m count={self.outlier_count}")

            # 일정 횟수까진 무시
            if self.outlier_count < self.max_hold:
                return self.prev

            # 환경 변화
            print("[OUTLIER] accepted due to persistence")
            self.outlier_count = 0
            self.prev = pos
            return pos

        # 정상 값 → EMA 적용
        self.outlier_count = 0

        smoothed = {
            "x": self.alpha * pos["x"] + (1 - self.alpha) * self.prev["x"],
            "y": self.alpha * pos["y"] + (1 - self.alpha) * self.prev["y"],
            "z": self.alpha * pos["z"] + (1 - self.alpha) * self.prev["z"],
        }

        self.prev = smoothed
        return smoothed


# 상태 변경 이력을 누적 저장하는 함수 추가
def append_log_event(state, marker_id, rvec=None, tvec=None, payload=None):
    log = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "marker_id": marker_id,
        "event": "state_enter"
    }

    if rvec is not None:
        log["rvec"] = rvec.flatten().tolist()

    if tvec is not None:
        log["tvec"] = tvec.flatten().tolist()

    if payload is not None:
        log["payload"] = payload

    with open("log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(log, ensure_ascii=False) + "\n")


# 죄표 변환
def local_to_camera_world(rvec, tvec, local_position):
    # 문서 구조 기준:
    # P_camera = R * P_local + t

    # rvec, tvec: ArUco 6DoF pose
    # local_position: 마커 기준 로컬 좌표

    R, _ = cv2.Rodrigues(rvec)

    p_local = np.array([
        [float(local_position.get("x", 0.0))],
        [float(local_position.get("y", 0.0))],
        [float(local_position.get("z", 0.0))]
    ], dtype=np.float32)

    p_world = R @ p_local + tvec.reshape(3, 1)

    return {
        "x": float(p_world[0][0]),
        "y": float(p_world[1][0]),
        "z": float(p_world[2][0])
    }


def log_event(state, marker_id, tvec=None):
    log = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "marker_id": marker_id,
        "event": "state_enter"
    }

    if tvec is not None:
        log["tvec"] = tvec.flatten().tolist()

    with open("log.json", "a", encoding="utf-8") as f:
        f.write(json.dumps(log) + "\n")


# Unity가 읽기 쉬운 최신 상태 파일 저장 함수 추가
def write_runtime_state(state, marker_id, rvec=None, tvec=None, payload=None):
    runtime_data = {
        "timestamp": datetime.now().isoformat(),
        "state": state,
        "marker_id": marker_id
    }

    if rvec is not None:
        runtime_data["rvec"] = rvec.flatten().tolist()

    if tvec is not None:
        runtime_data["tvec"] = tvec.flatten().tolist()

    if payload is not None:
        runtime_data["payload"] = payload

    with open("runtime_state.json", "w", encoding="utf-8") as f:
        json.dump(runtime_data, f, ensure_ascii=False, indent=2)


# Drawing
def format_pose_text(tvec):
    x, y, z = tvec.flatten()
    return f"Pose tvec(m): x={x:.3f}, y={y:.3f}, z={z:.3f}"


def draw_state_info(frame, state_name, payload, pose_text=None, state_marker_id=None):
    y = 30

    cv2.putText(
        frame,
        f"Current State: {state_name}",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2
    )

    if state_marker_id is not None:
        y += 35
        cv2.putText(
            frame,
            f"State Marker ID: {state_marker_id}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 255, 0),
            2
        )

    y += 35
    message = payload.get("message", "")
    cv2.putText(
        frame,
        f"Message: {message}",
        (20, y),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.6,
        (255, 255, 255),
        2
    )

    target_button = payload.get("target_button")
    if target_button:
        y += 35
        cv2.putText(
            frame,
            f"Target Button: {target_button}",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 255, 0),
            2
        )

    local_position = payload.get("local_position")
    if local_position:
        y += 35
        cv2.putText(
            frame,
            f"Local: ({local_position['x']:.3f}, {local_position['y']:.3f}, {local_position['z']:.3f})",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 255, 200),
            2
        )

    world_position = payload.get("world_position")
    if world_position:
        y += 35
        cv2.putText(
            frame,
            f"World: ({world_position['x']:.3f}, {world_position['y']:.3f}, {world_position['z']:.3f})",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 200, 255),
            2
        )

    if pose_text:
        y += 35
        cv2.putText(
            frame,
            pose_text,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 165, 255),
            2
        )


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)

    if not cap.isOpened():
        print("Failed to open camera.")
        return

    aruco_detector = create_aruco_detector()
    fsm = MarkerFSM("states.json")

    camera_matrix, dist_coeffs = load_calibration()

    print("Press ESC to quit.")
    print("ArUco: pose estimation only")
    print("2x5 marker: state ID only")

    last_state_marker_id = None

    # world_position 흔들림 완화용 EMA 필터
    position_filter = PositionFilter(
        alpha=0.35,
        threshold=0.08,   # 튐 기준 (8 cm)
        max_hold=5        # 몇 번까지 무시
    )

    stable_decoder = StableStateDecoder(window_size=7, min_count=4)

    while True:
        ret, frame = cap.read()

        if not ret:
            print("Failed to read frame.")
            break

        frame_height, frame_width = frame.shape[:2]

        if camera_matrix is None or dist_coeffs is None:
            camera_matrix, dist_coeffs = create_fallback_calibration(
                frame_width,
                frame_height
            )

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        pose_text = None
        rvec = None
        tvec = None

        # ArUco로 6DoF 포즈 추정
        aruco_corners, aruco_ids, _ = aruco_detector.detectMarkers(frame)

        if aruco_ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, aruco_corners, aruco_ids)

            reference_index = None

            # 기준 ArUco ID 찾기
            for i, aruco_id in enumerate(aruco_ids.flatten()):
                if int(aruco_id) == REFERENCE_ARUCO_ID:
                    reference_index = i
                    break

            # 기준 마커가 있을 때만 pose 계산
            if reference_index is not None:
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [aruco_corners[reference_index]],
                    MARKER_LENGTH,
                    camera_matrix,
                    dist_coeffs
                )

                rvec = rvecs[0]
                tvec = tvecs[0]

                cv2.drawFrameAxes(
                    frame,
                    camera_matrix,
                    dist_coeffs,
                    rvec,
                    tvec,
                    0.015
                )

                pose_text = format_pose_text(tvec)

            else:
                # 기준 마커 없을 때 안내 메시지
                cv2.putText(
                    frame,
                    f"Reference ArUco ID {REFERENCE_ARUCO_ID} not found",
                    (20, frame_height - 60),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )

        # 2x5 정사각형 마커로 상태 ID 인식
        detected_state_id = None
        aruco_corners, aruco_ids, _ = aruco_detector.detectMarkers(frame)
        state_markers = detect_state_markers(gray, aruco_corners)

        for marker in state_markers:
            state_id, bits = decode_2x5_marker(gray, marker)
            stable_state_id = stable_decoder.update(state_id)

            if stable_state_id is not None:
                detected_state_id = stable_state_id
            else:
                detected_state_id = None

            cv2.polylines(frame, [marker], True, (0, 255, 0), 2)

            x, y = marker[0]
            cv2.putText(
                frame,
                f"State ID: {state_id}",
                (int(x), int(y) - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (0, 255, 0),
                2
            )

            cv2.putText(
                frame,
                f"Bits: {''.join(map(str, bits))}",
                (int(x), int(y) + 20),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 255),
                2
            )

            # 첫 번째 상태 마커 사용
            break

        # 상태 ID와 ArUco pose가 둘 다 있을 때만 FSM + runtime JSON 갱신
        if detected_state_id is not None:
            last_state_marker_id = detected_state_id

            if rvec is None or tvec is None:
                cv2.putText(
                    frame,
                    "State marker detected, but ArUco pose not found",
                    (20, frame_height - 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.6,
                    (0, 0, 255),
                    2
                )
            else:
                changed = fsm.update_by_marker_id(detected_state_id)

                if changed:
                    payload = dict(fsm.get_state_payload())

                    local_position = payload.get(
                        "local_position",
                        {"x": 0.0, "y": 0.0, "z": 0.0}
                    )

                    world_position = local_to_camera_world(
                        rvec,
                        tvec,
                        local_position
                    )

                    # 좌표 스무딩 적용
                    world_position = position_filter.update(world_position)

                    payload["world_position"] = world_position

                    print("=" * 60)
                    print(f"State Marker ID: {detected_state_id}")
                    print(f"New State: {fsm.get_current_state()}")
                    print(f"Payload: {payload}")

                    append_log_event(
                        state=fsm.get_current_state(),
                        marker_id=detected_state_id,
                        rvec=rvec,
                        tvec=tvec,
                        payload=payload
                    )

                    write_runtime_state(
                        state=fsm.get_current_state(),
                        marker_id=detected_state_id,
                        rvec=rvec,
                        tvec=tvec,
                        payload=payload
                    )

        current_state = fsm.get_current_state()
        payload = fsm.get_state_payload()

        draw_state_info(
            frame,
            current_state,
            payload,
            pose_text,
            last_state_marker_id
        )

        cv2.imshow("MR Kiosk Prototype - ArUco Pose + 2x5 State Marker", frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
