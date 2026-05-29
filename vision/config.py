# HCI 평가 연계:
# marker_id는 사용자가 위치한 키오스크 과업 단계 의미.
# 로그 분석 시 marker_id를 기준으로 어느 단계에서 시간이 오래 걸렸는지 어느 단계에서 오류가 자주 발생했는지 구분.

# config.py 최종본

STATE_MAP = {
    # Phase 00: 초기 화면 및 카테고리 탭 탐색 (0 ~ 160)
    0: "PHASE_00_START",
    32: "PHASE_00_CAT_COFFEE",
    64: "PHASE_00_CAT_TEA",
    96: "PHASE_00_CAT_ADE",
    128: "PHASE_00_CAT_BEV",
    160: "PHASE_00_CAT_BLEND",

    # Phase 11: 최종 결제 모듈 안내 (768 고정)
    768: "PHASE_11_PAYMENT",

    # 예외 및 시스템 기본 코드 가드
    1: "LISTENING",
    800: "ERROR_RECOVERY",
    900: "FAIL_SAFE"
}

# Phase 01 (256~447) 및 Phase 10 (512~628) 가변 ID 범위 자동 촘촘 등록
for id_01 in range(256, 448):
    STATE_MAP[id_01] = "PHASE_01_OPTION_SELECT"

for id_10 in range(512, 629):
    STATE_MAP[id_10] = "PHASE_10_CART_VALIDATION"

REFERENCE_ARUCO_ID = 0
CAMERA_INDEX = 0
MARKER_LENGTH = 0.05

CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"

REFERENCE_ARUCO_ID = 0

CAMERA_INDEX = 0
MARKER_LENGTH = 0.05  # 5 cm

CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"
