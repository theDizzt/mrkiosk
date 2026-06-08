# vision/app_aruco_dual.py
# python vision/app_aruco_dual.py --reference-id 769 --show

import argparse
from pathlib import Path

import cv2
import numpy as np

import json
import socket
import threading
import time

from aruco_dual_detector import DualArucoDetector
from aruco_runtime import RuntimeStabilizer, RuntimeWriter

from marker_fsm import KioskFSM
from kiosk_geometry import build_target_payload
from kiosk_guide_model import get_quick_order_target
from kiosk_id_formula import build_expected_route, build_quick_order_route
from config import get_state_info

from udp_sender import UdpSender


# ==============================================================================
# 유니티 오퍼레이터 연동용 글로벌 변수
# ==============================================================================

live_menu_id = None
fsm_rebuild_lock = threading.Lock()


def unity_operator_receiver_loop(receive_port=5006):
    global live_menu_id

    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(("0.0.0.0", receive_port))
    print(f"[OPERATOR Backend] 유니티 신호 감시 소켓 개방 완료 (Port: {receive_port})")

    while True:
        try:
            data, addr = recv_sock.recvfrom(1024)
            message = data.decode("utf-8")

            parsed_json = json.loads(message)
            menu_id = int(parsed_json.get("selected_target_id", 1))

            with fsm_rebuild_lock:
                live_menu_id = menu_id

            print(f"\n[★ 오퍼레이터 원격 확정] 메뉴 가이드가 {live_menu_id}번으로 원격 변경되었습니다.")

        except Exception as e:
            print(f"[OPERATOR Recv Error] 데이터 수신/파싱 실패: {e}")
            time.sleep(0.1)


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
        raise FileNotFoundError(f"distortion coefficient file not found in: {calibration_dir}")

    camera_matrix = np.load(camera_matrix_path)
    dist_coeffs = np.load(dist_path)

    return camera_matrix, dist_coeffs


def parse_args():
    parser = argparse.ArgumentParser(description="Dual ArUco detector for MR Kiosk")

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
        default=0.0125,
        help="Reference marker side length in meters. Tablet CSS 64px marker is usually around 0.012~0.013m.",
    )

    parser.add_argument(
        "--dict",
        type=str,
        default="DICT_4X4_1000",
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

    parser.add_argument(
        "--category",
        type=str,
        default="Tea",
        help="Order category: Coffee, Tea, Ade/Juice, Beverage, Blended",
    )

    parser.add_argument(
        "--menu-id",
        type=int,
        default=7,
        help="Menu ID from kiosk menu data",
    )

    parser.add_argument(
        "--temp",
        type=str,
        default="ICED",
        choices=["ICED", "HOT"],
        help="Temperature option",
    )

    parser.add_argument(
        "--sweetness",
        type=str,
        default="보통",
        choices=["덜 달게", "보통", "달게"],
        help="Sweetness option",
    )

    parser.add_argument(
        "--ice",
        type=str,
        default="얼음 보통",
        choices=["얼음 많이", "얼음 보통", "얼음 적게"],
        help="Ice amount option",
    )

    parser.add_argument("--udp-host", type=str, default=None)
    parser.add_argument("--udp-port", type=int, default=5005)

    parser.add_argument(
        "--quick-order",
        action="store_true",
        help="Quick order mode. 옵션 변경 없이 기본 옵션으로 바로 담는 데모 모드.",
    )

    return parser.parse_args()


def build_route_from_args(args, menu_id):
    if args.quick_order:
        return build_quick_order_route(menu_id=menu_id)

    return build_expected_route(
        category=args.category,
        menu_id=menu_id,
        temp=args.temp,
        sweetness=args.sweetness,
        ice=args.ice,
    )


def main():
    args = parse_args()

    operator_thread = threading.Thread(
        target=unity_operator_receiver_loop,
        args=(5006,),
        daemon=True,
    )
    operator_thread.start()

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

    udp_sender = None

    if args.udp_host is not None:
        udp_sender = UdpSender(args.udp_host, args.udp_port)
        print(f"[INFO] UDP enabled: {args.udp_host}:{args.udp_port}")

    expected_route = build_route_from_args(args, args.menu_id)
    print(f"[INFO] Expected route: {expected_route}")

    kiosk_fsm = KioskFSM(route=expected_route)

    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index: {args.camera}")

    print("[INFO] Dual ArUco detector started")
    print(f"[INFO] Reference ID: {args.reference_id}")
    print(f"[INFO] Marker length: {args.marker_length} m")
    print(f"[INFO] Output: {output_path}")
    print("[INFO] Press ESC or Q to quit")

    current_active_menu_id = args.menu_id
    last_print_time = 0.0

    global live_menu_id

    while True:
        # ----------------------------------------------------------------------
        # 유니티 오퍼레이터가 메뉴를 바꾼 경우 FSM route 재생성
        # ----------------------------------------------------------------------
        if live_menu_id is not None and live_menu_id != current_active_menu_id:
            with fsm_rebuild_lock:
                current_active_menu_id = live_menu_id
                live_menu_id = None

            print(f"\n[FSM DYNAMIC REBUILD] 메뉴 경로를 {current_active_menu_id}번 메뉴 기준으로 갱신합니다.")

            expected_route = build_route_from_args(args, current_active_menu_id)
            print(f"[FSM DYNAMIC REBUILD] 새 route: {expected_route}")

            kiosk_fsm = KioskFSM(route=expected_route)

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

        detected_state_id = runtime_state["state_marker"]["id"]

        fsm_result = kiosk_fsm.update(detected_state_id)

        guide_state_id = fsm_result["current_id"]
        state_info = get_state_info(guide_state_id)

        # 중요:
        # expected_id가 0이면 Python에서 False로 취급되므로 "or guide_state_id"를 쓰면 안 됨.
        expected_id = fsm_result.get("expected_id")
        target_state_id = expected_id if expected_id is not None else guide_state_id

        # 중요:
        # detected_state_id는 순간 인식값이고,
        # guide_state_id는 FSM이 인정한 현재 상태다.
        # target 선택은 guide_state_id 기준으로 해야 안정적이다.
        target = get_quick_order_target(
            current_state_id=guide_state_id,
            expected_state_id=target_state_id,
        )

        target_payload = None
        reference_pose = runtime_state["reference"]["pose"]

        if reference_pose is not None and target is not None:
            rvec_ref = np.array(reference_pose["rvec"], dtype=np.float32)
            tvec_ref = np.array(reference_pose["tvec"], dtype=np.float32)

            state_pose = result.get("state_pose")
            rvec_state = None
            tvec_state = None

            if state_pose is not None and runtime_state["tracking"]["state_status"] == "TRACKING":
                rvec_state = np.array(state_pose["rvec"], dtype=np.float32)
                tvec_state = np.array(state_pose["tvec"], dtype=np.float32)

            target_payload = build_target_payload(
                rvec_ref=rvec_ref,
                tvec_ref=tvec_ref,
                target=target,
                rvec_state=rvec_state,
                tvec_state=tvec_state,
                marker_length=args.marker_length,
            )

        runtime_state["fsm"] = {
            "state": state_info["name"],
            "label": state_info["label"],
            "state_id": guide_state_id,
            "detected_state_id": detected_state_id,
            "target_state_id": target_state_id,
            "expected_id": expected_id,
            "recovery": fsm_result["recovery"],
            "message": fsm_result["message"],
            "target_name": target.get("name") if target is not None else None,
            "target_label": target.get("label") if target is not None else None,
            "target_rect": target.get("rect") if target is not None else None,
            "target": target_payload,
        }

        writer.write(runtime_state)

        if udp_sender is not None:
            udp_sender.send(runtime_state)

        # ----------------------------------------------------------------------
        # 터미널 모니터링
        # ----------------------------------------------------------------------
        current_time = time.time()

        if current_time - last_print_time >= 0.5:
            import os

            os.system("cls" if os.name == "nt" else "clear")

            print("=" * 64)
            print(" [MR Kiosk 비전 엔지니어링 실시간 모니터링]")
            print("=" * 64)
            print(f" ▷ 현재 가동 모드      : {'퀵 오더 데모 모드' if args.quick_order else '일반 인터랙션 모드'}")
            print(f" ▷ 현재 메뉴 번호      : {current_active_menu_id}번")
            print(f" ▷ 현재 FSM 상태 ID    : {guide_state_id} ({state_info['name']})")
            print(f" ▷ 카메라 인식 마커 ID : {detected_state_id if detected_state_id != -1 else '미감지 (-1)'}")
            print(f" ▷ 다음 목표 상태 ID   : {target_state_id}")
            print(f" ▷ 선택된 타겟 버튼    : {target.get('name') if target else None}")
            print(f" ▷ 타겟 라벨           : {target.get('label') if target else None}")
            print(f" ▷ 타겟 rect           : {target.get('rect') if target else None}")
            print("-" * 64)

            if target_payload is not None:
                pos = target_payload["world_position"]
                size = target_payload["world_size"]

                print(" 🎯 [정밀 연동 중] 유니티 전송 3D 월드 좌표계")
                print(f"   - X축 좌우 : {pos['x']:+.3f} m")
                print(f"   - Y축 상하 : {pos['y']:+.3f} m")
                print(f"   - Z축 깊이 : {pos['z']:+.3f} m")
                print(f"   - W 크기   : {size['w']:+.3f} m")
                print(f"   - H 크기   : {size['h']:+.3f} m")
            else:
                print(" ⚠️ [좌표 유실] reference marker 또는 target이 없습니다.")

            print("=" * 64)
            print(" ※ 종료하려면 카메라 창을 클릭하고 [ESC] 또는 [Q]를 누르세요.")

            last_print_time = current_time

        if args.show:
            debug_frame = detector.draw_debug(frame, result)
            cv2.imshow("Dual ArUco Detector", debug_frame)

        key = cv2.waitKey(1) & 0xFF

        if key == 27 or key == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()