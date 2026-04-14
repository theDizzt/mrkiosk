import cv2
import numpy as np
from pathlib import Path
import json # 로그/연동용 JSON 저장을 위해 추가
from datetime import datetime # 타임스탬프 기록용 추가

from config import (
    CAMERA_INDEX,
    MARKER_LENGTH,
    CAMERA_MATRIX_FILE,
    DIST_COEFFS_FILE,
)
from marker_fsm import MarkerFSM


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


def create_detector():
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector


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


def draw_state_info(frame, state_name, payload, pose_text=None):
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

    position = payload.get("position")
    if position:
        y += 35
        cv2.putText(
            frame,
            f"UI Position: ({position['x']}, {position['y']})",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 200, 255),
            2
        )

    # offset_from_marker 표시 추가
    offset = payload.get("offset_from_marker")
    if offset:
        y += 35
        cv2.putText(
            frame,
            f"Offset: ({offset['x']:.3f}, {offset['y']:.3f}, {offset['z']:.3f})",
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (200, 255, 200),
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


def format_pose_text(tvec):
    x, y, z = tvec.flatten()
    return f"Pose tvec(m): x={x:.3f}, y={y:.3f}, z={z:.3f}"


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    detector = create_detector()
    fsm = MarkerFSM("states.json")

    camera_matrix, dist_coeffs = load_calibration()

    print("Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        frame_height, frame_width = frame.shape[:2]

        if camera_matrix is None or dist_coeffs is None:
            camera_matrix, dist_coeffs = create_fallback_calibration(frame_width, frame_height)

        corners, ids, _ = detector.detectMarkers(frame)
        pose_text = None

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for i, marker_id in enumerate(ids.flatten()):
                marker_id = int(marker_id)

                # estimate pose
                # 포즈 계산을 먼저 수행
                rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers(
                    [corners[i]],
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
                    0.03
                )

                pose_text = format_pose_text(tvec)

                print(f"Marker {marker_id} pose:")
                print(f"  rvec: {rvec.flatten()}")
                print(f"  tvec: {tvec.flatten()}")

                # 포즈 계산 후에 상태 변경
                changed = fsm.update_by_marker_id(marker_id)

                if changed:
                    payload = fsm.get_state_payload()
                    print("=" * 60)
                    print(f"Marker ID: {marker_id}")
                    print(f"New State: {fsm.get_current_state()}")
                    print(f"Payload: {payload}")

                    """
                    # append_log_event()와 역할이 겹쳐 삭제
                    log_event(
                        state=fsm.get_current_state(),
                        marker_id=marker_id,
                        tvec=tvec
                    )
                    """

                    # 상태 변경 이력 누적 저장
                    # tvec, rvec를 안전하게 로그에 저장 가능함
                    append_log_event(
                        state=fsm.get_current_state(),
                        marker_id=marker_id,
                        rvec=rvec,
                        tvec=tvec,
                        payload=payload
                    )

                    # Unity 연동용 최신 상태 저장
                    write_runtime_state(
                        state=fsm.get_current_state(),
                        marker_id=marker_id,
                        rvec=rvec,
                        tvec=tvec,
                        payload=payload
                    )

                pose_text = format_pose_text(tvec)

                print(f"Marker {marker_id} pose:")
                print(f"  rvec: {rvec.flatten()}")
                print(f"  tvec: {tvec.flatten()}")

        current_state = fsm.get_current_state()
        payload = fsm.get_state_payload()
        draw_state_info(frame, current_state, payload, pose_text)

        cv2.imshow("MR Kiosk Prototype - Pose Estimation", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
