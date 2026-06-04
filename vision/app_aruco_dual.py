# vision/app_aruco_dual.py
# python vision/app_aruco_dual.py --reference-id 769 --show

import argparse
from pathlib import Path

import cv2
import numpy as np

<<<<<<< Updated upstream
=======
import json
import socket
import threading
import time

>>>>>>> Stashed changes
from aruco_dual_detector import DualArucoDetector
from aruco_runtime import RuntimeStabilizer, RuntimeWriter

# 키오스크 FSM / 좌표 계산 모듈
from marker_fsm import KioskFSM
from kiosk_geometry import build_target_payload
from kiosk_guide_model import get_target_for_state
from kiosk_id_formula import build_expected_route
from config import get_state_info

from udp_sender import UdpSender

<<<<<<< Updated upstream
=======
# ==============================================================================
# [오퍼레이터 연동용 글로벌 변수 및 백그라운드 수신 스레드]
# ==============================================================================
# 유니티 타겟 셀렉터가 전송할 실시간 라이브 메뉴 ID (기본값 None)
live_menu_id = None
fsm_rebuild_lock = threading.Lock()
>>>>>>> Stashed changes


def unity_operator_receiver_loop(receive_port=5006):
    global live_menu_id

    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    recv_sock.bind(("0.0.0.0", receive_port))
    print(
        f"[OPERATOR Backend] 유니티 신호 감시 소켓 개방 완료 (Port: {receive_port})"
    )

    while True:
        try:
            data, addr = recv_sock.recvfrom(1024)
            message = data.decode("utf-8")

            # 유니티 TargetSelector가 보낸 JSON 파싱 -> {"selected_target_id": 3}
            parsed_json = json.loads(message)
            menu_id = int(parsed_json.get("selected_target_id", 1))

            with fsm_rebuild_lock:
                live_menu_id = menu_id

            print(
                f"\n[★ 오퍼레이터 원격 확정] 메뉴 가이드가 {live_menu_id}번으로 원격 변경되었습니다."
            )

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
    
    parser.add_argument("--quick-order", action="store_true", help="Quick order mode")

    return parser.parse_args()


def main():
    args = parse_args()
<<<<<<< Updated upstream
=======

    # --------------------------------------------------------------------------
    # [1단계] 유니티 오퍼레이터 수신 백엔드 서버 스레드 가동
    # --------------------------------------------------------------------------
    operator_thread = threading.Thread(
        target=unity_operator_receiver_loop, args=(5006,), daemon=True
    )
    operator_thread.start()
>>>>>>> Stashed changes

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

<<<<<<< Updated upstream
    # 키오스크 상태 전이 FSM
    expected_route = build_expected_route(
        category=args.category,
        menu_id=args.menu_id,
        temp=args.temp,
        sweetness=args.sweetness,
        ice=args.ice,
    )
=======
    # 초기 가이드라인 분기 경로 생성
    if args.quick_order:
        expected_route = build_quick_order_route(
            category=args.category,
            menu_id=args.menu_id,
        )
    else:
        expected_route = build_expected_route(
            category=args.category,
            menu_id=args.menu_id,
            temp=args.temp,
            sweetness=args.sweetness,
            ice=args.ice,
        )
>>>>>>> Stashed changes
    
    print(f"[INFO] Expected route: {expected_route}")

    kiosk_fsm = KioskFSM(route=expected_route)

    cap = cv2.VideoCapture(args.camera)

    if not cap.isOpened():
        raise RuntimeError(f"Cannot open camera index: {args.camera}")

    print("[INFO] Dual ArUco detector started")
    print(f"[INFO] Reference ID: {args.reference_id}")
    print(f"[INFO] Output: {output_path}")
    print("[INFO] Press ESC or Q to quit")

    # 실시간 메뉴 상태 변화 트래킹을 위한 로컬 스냅샷 변수
    current_active_menu_id = args.menu_id
    
    # 🚨 [해결] 로그 폭주 제어용 타이머 타임스탬프 변수 위치 재지정 및 초기화
    last_print_time = 0.0

    while True:
<<<<<<< Updated upstream
=======
        # ----------------------------------------------------------------------
        # [2단계] 유니티가 보낸 라이브 메뉴 변경 요청을 실시간으로 캐치하여 리빌드
        # ----------------------------------------------------------------------
        global live_menu_id
        if live_menu_id is not None and live_menu_id != current_active_menu_id:
            with fsm_rebuild_lock:
                current_active_menu_id = live_menu_id
                live_menu_id = None  # 신호 가로채기 완료 후 버퍼 초기화

            print(
                f"\n[FSM DYNAMIC REBUILD] 오퍼레이터의 선택에 맞춰 {current_active_menu_id}번 메뉴 경로로 즉시 갱신합니다."
            )

            if args.quick_order:
                expected_route = build_quick_order_route(
                    category=args.category,
                    menu_id=current_active_menu_id,
                )
            else:
                expected_route = build_expected_route(
                    category=args.category,
                    menu_id=current_active_menu_id,
                    temp=args.temp,
                    sweetness=args.sweetness,
                    ice=args.ice,
                )
            print(f"[FSM DYNAMIC REBUILD] 새로 설계된 가이드 블루프린트: {expected_route}")
            kiosk_fsm = KioskFSM(route=expected_route)

>>>>>>> Stashed changes
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

        target_state_id = fsm_result.get("expected_id") or guide_state_id

        if args.quick_order:
            target = get_quick_order_target(detected_state_id, target_state_id)
        else:
            target = get_target_for_state(target_state_id)

        target_payload = None
        reference_pose = runtime_state["reference"]["pose"]

<<<<<<< Updated upstream
        if reference_pose is not None:
            target = get_target_for_state(target_state_id)

            if target is not None:
                rvec_ref = np.array(reference_pose["rvec"], dtype=np.float32)
                tvec_ref = np.array(reference_pose["tvec"], dtype=np.float32)

                target_payload = build_target_payload(
                    rvec_ref=rvec_ref,
                    tvec_ref=tvec_ref,
                    target=target,
                    marker_length=args.marker_length,
                )

        # fsm 결과 확장
=======
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
                rvec_ref=rvec_ref, tvec_ref=tvec_ref, target=target,
                rvec_state=rvec_state, tvec_state=tvec_state, marker_length=args.marker_length
            )

>>>>>>> Stashed changes
        runtime_state["fsm"] = {
            "state": state_info["name"], "label": state_info["label"], "state_id": guide_state_id,
            "detected_state_id": detected_state_id, "target_state_id": target_state_id,
            "expected_id": fsm_result.get("expected_id"), "recovery": fsm_result["recovery"],
            "message": fsm_result["message"], "target": target_payload,
        }

        writer.write(runtime_state)

        if udp_sender is not None:
            udp_sender.send(runtime_state)

        # ----------------------------------------------------------------------
        # [3단계] 고성능 로직 분리: 비전은 제한 없이 최고 성능, 터미널 로그만 1초 주기 제한
        # ----------------------------------------------------------------------
# ----------------------------------------------------------------------
        # [최종 패치] 터미널 화면을 고정하고, 0.5초마다 제자리에서 값만 리프레시
        # ----------------------------------------------------------------------
        current_time = time.time()
        if current_time - last_print_time >= 0.5:  # 주기를 0.5초로 조금 더 여유 있게 조정
            import os
            # 이전 글자들을 싹 지워서 스크롤이 위로 올라가는 현상을 원천 차단합니다.
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("="*60)
            print(f" [MR Kiosk 비전 엔지니어링 실시간 모니터링 공정]")
            print("="*60)
            print(f" ▷ 현재 가동 모드      : {'퀵 오더 데모 모드' if args.quick_order else '일반 인터랙션 모드'}")
            print(f" ▷ 원격 제어 메뉴 번호  : {current_active_menu_id}번 메뉴")
            print(f" ▷ 현재 UI 페이지 ID   : {guide_state_id} ({state_info['name']})")
            print(f" ▷ 카메라 인식 마커 ID  : {detected_state_id if detected_state_id != -1 else '미감지 (-1)'}")
            print(f" ▷ 다음 가이드 타겟 ID  : {target_state_id} ({state_info['label']})")
            print("-"*60)
            
            if target_payload is not None:
                pos = target_payload["world_position"]
                print(f" 🎯 [정밀 연동 중] 유니티 전송 3D 월드 좌표계 (미터법)")
                print(f"   - X축 (좌우) : {pos['x']:+.3f}m")
                print(f"   - Y축 (상하) : {pos['y']:+.3f}m")
                print(f"   - Z축 (깊이) : {pos['z']:+.3f}m")
            else:
                print(f" ⚠️ [좌표 유실] 레퍼런스 마커(769번)를 카메라 정면에 완전히 비춰주세요.")
                
            print("="*60)
            print(" ※ 종료하려면 카메라 창을 클릭하고 [ESC] 또는 [Q]를 누르세요.")
            
            last_print_time = current_time

        # OpenCV 윈도우 화면 리프레시 및 키 입력 대기 (지연 시간 1ms 유지로 인식 속도 최상)
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