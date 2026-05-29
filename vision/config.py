# ==============================================================================
# [HCI 평가 및 비전 연계] 키오스크 상태별 ArUco ID 매핑 및 자동 등록 (최종본 반영)
# ==============================================================================

# 1. 고정 마커 및 기본 상태 맵 초기화
STATE_MAP = {
    # Phase 00: 초기 화면 및 카테고리 탭 (ID: 0 ~ 160)
    0: "IDLE",                  # 초기 매장/포장 선택 화면 (리셋 공통)
    32: "CATEGORY_SELECT",      # Coffee 탭 화면
    64: "CATEGORY_SELECT",      # Tea 탭 화면
    96: "CATEGORY_SELECT",      # Ade/Juice 탭 화면 (청포도 에이드 등)
    128: "CATEGORY_SELECT",     # Beverage 탭 화면
    160: "CATEGORY_SELECT",     # Blended 탭 화면

    # Phase 11: 최종 결제 모듈 안내 (ID: 768 고정)
    768: "CONFIRM",             # 결제 화면 전체 및 카드가이드 발화 지점

    # 시스템 강제 코드 가드 및 예외 처리
    800: "ERROR_RECOVERY",
    900: "FAIL_SAFE"
}

# 2. Phase 01: 메뉴 상세 옵션 선택 구간 자동 등록 (ID: 256 ~ 447)
# 각 MenuHash(0~5)와 선택 비트 조합(Temperature, Sugar, Ice)에 의해 생성되는 모든 ID를 ITEM_SELECT로 매핑
for menu_hash in range(6):
    for temp in [0, 1, 2]:      # 미선택(0), ICED(1), HOT(2)
        for sugar in [0, 1]:    # 미선택(0), 선택 완료(1)
            for ice in [0, 1]:  # 미선택(0), 선택 완료(1)
                # 명세서 공식: 256 + (MenuHash * 32) + (Temperature * 8) + (Sugar * 4) + (Ice * 2)
                phase_01_id = 256 + (menu_hash * 32) + (temp * 8) + (sugar * 4) + (ice * 2)
                STATE_MAP[phase_01_id] = "ITEM_SELECT"

# 3. Phase 10: 장바구니 검증 구간 자동 등록 (ID: 512 ~ 628)
# 공통 참조 메뉴 ID(0~29)에 따른 장바구니 화면 ID를 PAYMENT_SELECT로 매핑
for menu_id in range(30):
    # 명세서 공식: 512 + (공통 참조 ID * 4)
    phase_10_id = 512 + (menu_id * 4)
    STATE_MAP[phase_10_id] = "PAYMENT_SELECT"


# ==============================================================================
# 하드웨어 및 카메라 기본 셋팅 값
# ==============================================================================
REFERENCE_ARUCO_ID = 0          # 좌측 상단 고정 reference 마커 번호
CAMERA_INDEX = 0                # 웹캠 인덱스
MARKER_LENGTH = 0.05            # 마커 실제 물리 크기 (5cm)

CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"