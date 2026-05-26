# vision/app_aruco_dual.py

import argparse
from pathlib import Path

import cv2
import numpy as np

from aruco_dual_detector import DualArucoDetector
from aruco_runtime import RuntimeStabilizer, RuntimeWriter
from config import get_state_info


def load_calibration(calibration_dir: Path):
    camera_matrix_path = calibration_dir / "camera_matrix.npy"

    dist_candidates = [
        calibration_dir / "dist_coeff.npy",
        calibration_dir / "dist_coeffs.npy",
        calibration_dir / "dist_coefficients.npy",
    ]

    if not camera_matrix_path.exists():
        raise FileNotFoundError(f"camera_matrix.npy not found: {camera_matrix_path}")

    dist_path = None

    for candidate in dist_candidates:
        if candidate.exists():
            dist_path = candidate
            break

    if dist_path is None:
        raise FileNotFoundError(
            f"distortion coefficient file not found in: {calibration_dir}"
        )

    camera_matrix = np.load(camera_matrix_path)
    dist_coeffs = np.load(dist_path)

    return camera_matrix, dist_coeffs


def parse_args():
    parser = argparse.ArgumentParser(
        description="Dual ArUco detector for MR Kiosk"
    )

    parser.add_argument(
        "--camera",
        type=int,
        default=0,
        help="OpenCV camera index",
    )

    parser.add_argument(
        "--reference-id",
        type=int,
        required=True,
        help="Reference ArUco marker ID. State IDs are not defined here.",
    )

    parser.add_argument(
        "--marker-length",
        type=float,
        default=0.05,
        help="Reference marker side length in meters",
    )

    parser.add_argument(
        "--dict",
        type=str,
        default="DICT_5X5_1000",
        help="OpenCV ArUco dictionary name",
    )

    parser.add_argument(
        "--calibration-dir",
        type=str,
        default="vision/calibration",
        help="Calibration directory path",
    )

    parser.add_argument(
        "--output",
        type=str,
        default="vision/runtime_state.json",
        help="Runtime JSON output path",
    )

    parser.add_argument(
        "--show",
        action="store_true",
        help="Show debug camera window",
    )

    return parser.parse_args()


def main():
    args = parse_args()

    calibration_dir = Path(args.calibration_dir)
    output_path = Path(args.output)

    camera_matrix, dist_coeffs = load_calibration(calibration_dir)

    detector = DualArucoDetector(
        reference_id=args.reference_id,
        camera_matrix=camera_matrix,
        dist_coeffs=dist_coeffs,
        marker_length_m=args.marker_length,
        dictionary_name=args.dict,
    )

    stabilizer = RuntimeStabilizer(
        reference_hold_frames=5,
        state_hold_frames=10,
    )

    writer = RuntimeWriter(output_path)

    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index: {args.camera}")

    print("[INFO] Dual ArUco detector started")
    print(f"[INFO] Reference ID: {args.reference_id}")
    print(f"[INFO] Output: {output_path}")
    print("[INFO] Press ESC or Q to quit")

    while True:
        ret, frame = cap.read()

        if not ret:
            print("[WARN] Failed to read camera frame")
            continue

        result = detector.process(frame)

        runtime_state = stabilizer.update(
            reference_pose=result["reference_pose"],
            state_marker_id=result["state_marker_id"],
            reference_id=args.reference_id,
        )

        state_marker_id = runtime_state["state_marker"]["id"]
        state_info = get_state_info(state_marker_id)

        runtime_state["fsm"] = {
            "state": state_info["name"],
            "label": state_info["label"],
            "state_id": state_marker_id,
            "target": state_info["target"],
        }

        writer.write(runtime_state)

        if args.show:
            debug_frame = detector.draw_debug(frame, result)

            state_id = runtime_state["state_marker"]["id"]
            ref_status = runtime_state["tracking"]["reference_status"]
            state_status = runtime_state["tracking"]["state_status"]

            cv2.putText(
                debug_frame,
                f"REF: {ref_status} | STATE: {state_status} | STATE_ID: {state_id}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                (0, 255, 255),
                2,
                cv2.LINE_AA,
            )

            cv2.imshow("Dual ArUco Detector", debug_frame)

            key = cv2.waitKey(1) & 0xFF

            if key == 27 or key == ord("q"):
                break
        else:
            key = cv2.waitKey(1) & 0xFF

            if key == 27 or key == ord("q"):
                break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
