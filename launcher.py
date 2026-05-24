import cv2
import numpy as np
from pathlib import Path
from datetime import datetime

# 1. 팀원들이 만든 config 설정값 및 FSM 모듈 그대로 로드
from config import (
    CAMERA_INDEX, MARKER_LENGTH, CAMERA_MATRIX_FILE,
    DIST_COEFFS_FILE, REFERENCE_ARUCO_ID, STATE_MAP
)
from marker_fsm import MarkerFSM

# 2. app_pose.py 내부의 팀원들 연산 클래스 및 캘리브레이션 함수 로드
from app_pose import (
    StableStateDecoder, 
    PositionFilter, 
    load_calibration,
    append_log_event,       # 기존 log.jsonl 기록 함수
    write_runtime_state     # 유니티 연동용 runtime_state.json 기록 함수
)

def main():
    # 카메라 장치 오픈
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print(f"[ERROR] 카메라(Index: {CAMERA_INDEX})를 열 수 없습니다.")
        return

    # ArUco 마커 디텍터 초기화
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_50)
    detector = cv2.aruco.ArucoDetector(aruco_dict, cv2.aruco.DetectorParameters())
    
    # 팀원들의 핵심 로직 객체 생성
    fsm = MarkerFSM("vision/states.json")
    decoder = StableStateDecoder()
    position_filter = PositionFilter(alpha=0.2)
    
    # 왜곡 보정 행렬 파일 로드
    camera_matrix, dist_coeffs = load_calibration()
    if camera_matrix is None:
        print("[Warning] 캘리브레이션 파일이 없어 가상 매트릭스를 생성합니다.")
        ret, frame = cap.read()
        h, w = frame.shape[:2]
        camera_matrix = np.array([[w, 0, w/2], [0, w, h/2], [0, 0, 1]], dtype=np.float32)
        dist_coeffs = np.zeros((5, 1), dtype=np.float32)

    print("========================================================")
    print("[통합 실행기] 가이드 링 연산을 제외한 코어 시스템 가동 중...")
    print(" - 마커 감지 시 실시간으로 FSM 상태가 전이됩니다.")
    print(" - 유니티 연동용 파일(runtime_state.json)이 실시간 갱신됩니다.")
    print(" - 종료하려면 카메라 창 화면에서 [ESC]를 누르세요.")
    print("========================================================")

    while True:
        ret, frame = cap.read()
        if not ret: 
            print("[ERROR] 카메라 프레임을 읽을 수 없습니다.")
            break

        # 3. 실시간 마커 추적 연산
        corners, ids, _ = detector.detectMarkers(frame)
        detected_state_id = None
        rvec, tvec = None, None

        if ids is not None:
            # 화면에 감지된 마커 테두리 및 ID 디버그 표시
            cv2.aruco.drawDetectedMarkers(frame, corners, ids)
            
            # 기준 마커(0번) 포즈 추정 (rvec, tvec 계산)
            for i, marker_id in enumerate(ids.flatten()):
                if int(marker_id) == REFERENCE_ARUCO_ID:
                    rvecs, tvecs, _ = cv2.aruco.estimatePoseSingleMarkers([corners[i]], MARKER_LENGTH, camera_matrix, dist_coeffs)
                    rvec, tvec = rvecs[0], tvecs[0]
                    break
            
            # 상태 변환 제어용 마커 인식
            for marker_id in ids.flatten():
                if int(marker_id) in STATE_MAP and int(marker_id) != REFERENCE_ARUCO_ID:
                    detected_state_id = int(marker_id)
                    break

        # 4. 팀원들의 FSM 상태 전이 및 파일 출력 로직 통합 연동
        if detected_state_id is not None:
            stable_id = decoder.update(detected_state_id)
            if stable_id is not None:
                changed = fsm.update_by_marker_id(stable_id)
                
                if changed:
                    print(f"[상태 전이] 변경 감지 -> 현재 FSM 상태: {fsm.get_current_state()}")
                    
                    # 현재 상태의 페이로드 데이터 추출 및 좌표 필터링
                    payload = fsm.get_state_payload()
                    local_pos = payload.get("local_position", {"x": 0.0, "y": 0.0, "z": 0.0})
                    world_position = position_filter.update(local_pos)
                    payload["world_position"] = world_position

                    # 팀원들이 작성했던 기존 원본 파일 기록 함수 호출 (UI 연동 및 아카이빙)
                    append_log_event(fsm.get_current_state(), stable_id, rvec, tvec, payload)
                    write_runtime_state(fsm.get_current_state(), stable_id, rvec, tvec, payload)

        # 5. 잡다한 그래픽 오버레이를 전부 뺀 깔끔한 원본 영상만 표출
        cv2.putText(frame, f"CURRENT FSM STATE: {fsm.get_current_state()}", (15, 30), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        cv2.imshow("MR Kiosk Core Integrated System", frame)

        # ESC 키 입력 시 안전하게 루프 종료
        if cv2.waitKey(1) & 0xFF == 27:
            print("[SYSTEM] 사용자에 의해 통합 프로그램이 종료되었습니다.")
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()