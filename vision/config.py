# ==============================================================================
# [HCI 평가 및 비전 연계] 키오스크 상태별 ArUco ID 매핑 및 자동 등록 (최종본 반영)
# ==============================================================================

# 1. 고정 마커 및 기본 상태 맵 초기화
STATE_MAP = {
    # Phase 00: 초기 화면 및 카테고리 탭 (ID: 0 ~ 160)
    0: "IDLE",                  # 초기 매장/포장 선택 화면 (리셋 공통)
    32: "CATEGORY_SELECT",      # Coffee 탭 화면
    64: "CATEGORY_SELECT",      # Tea 탭 화면
    96: "CATEGORY_SELECT",      # Ade/Juice 탭 화면 (청포도 에이드 실험군)
    128: "CATEGORY_SELECT",     # Beverage 탭 화면
    160: "CATEGORY_SELECT",     # Blended 탭 화면

    # Phase 11: 최종 결제 모듈 안내 (기획 수정 반영: 768 및 769 둘 다 CONFIRM 처리)
    768: "CONFIRM",             # 기존 결제 화면 마커 가드
    769: "CONFIRM",             # 좌측 상단 고정 Reference 마커 등록 (FSM 튕김 방지)

    # 시스템 강제 코드 가드 및 예외 처리
    800: "ERROR_RECOVERY",
    900: "FAIL_SAFE"
}

# 2. Phase 01: 메뉴 상세 옵션 선택 구간 자동 등록 (ID: 256 ~ 447)
# [교정] script.js와 동일한 3진법 연산 구조로 변경하여 홀수 ID까지 완벽 등록
for menu_hash in range(6):
    for temp in [0, 1]:      # ICED(0), HOT(1)
        for sugar in [0, 1, 2]:    # 덜 달게(0), 보통(1), 달게(2)
            for ice in [0, 1, 2]:  # 얼음 많이(0), 얼음 보통(1), 얼음 적게(2)
                # 웹페이지(script.js) 정식 공식 동기화 완료
                option_code = (temp * 9) + (sugar * 3) + ice
                phase_01_id = 256 + (menu_hash * 32) + option_code
                STATE_MAP[phase_01_id] = "ITEM_SELECT"

# 3. Phase 10: 장바구니 검증 구간 자동 등록 (ID: 512 ~ 628)
for menu_id in range(30):
    phase_10_id = 512 + (menu_id * 4)
    STATE_MAP[phase_10_id] = "PAYMENT_SELECT"


# ==============================================================================
# [HCI 평가 연계] 통신 없는 마커 ID 기반 가이드 링 미터(m) 단위 상대 좌표 설정
# ==============================================================================
RING_COORDINATE_MAP = {
    32:  {"x": -0.15, "y": 0.08, "z": 0.0},  # Coffee 탭 위치
    64:  {"x": -0.08, "y": 0.08, "z": 0.0},  # Tea 탭 위치
    96:  {"x": -0.02, "y": 0.08, "z": 0.0},  # Ade/Juice 탭 위치

    # 최종 결제 단계 - 화면 왼쪽 위 고정 타겟 구역 조준
    769: {"x": -0.15, "y": 0.20, "z": 0.0} 
}

# 하드웨어 및 카메라 기본 셋팅 값
REFERENCE_ARUCO_ID = 769        
CAMERA_INDEX = 0                
MARKER_LENGTH = 0.05            
CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"