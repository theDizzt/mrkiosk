import cv2
from config import CAMERA_INDEX, MARKER_LENGTH
from marker_fsm import MarkerFSM


def get_aruco_dictionary():
    return cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)


def create_detector():
    aruco_dict = get_aruco_dictionary()
    parameters = cv2.aruco.DetectorParameters()
    detector = cv2.aruco.ArucoDetector(aruco_dict, parameters)
    return detector


def draw_state_info(frame, state_name, payload):
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
        pos_text = f"Position: ({position['x']}, {position['y']})"
        cv2.putText(
            frame,
            pos_text,
            (20, y),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (0, 200, 255),
            2
        )


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera")
        return

    detector = create_detector()
    fsm = MarkerFSM("states.json")

    print("Press ESC to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame")
            break

        corners, ids, _ = detector.detectMarkers(frame)

        if ids is not None:
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)

            for marker_id in ids.flatten():
                changed = fsm.update_by_marker_id(int(marker_id))
                if changed:
                    payload = fsm.get_state_payload()
                    print("=" * 50)
                    print(f"Marker ID: {marker_id}")
                    print(f"New State: {fsm.get_current_state()}")
                    print(f"Payload: {payload}")

        current_state = fsm.get_current_state()
        payload = fsm.get_state_payload()
        draw_state_info(frame, current_state, payload)

        cv2.imshow("MR Kiosk Prototype - Marker FSM", frame)

        key = cv2.waitKey(1) & 0xFF
        if key == 27:  # ESC
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()