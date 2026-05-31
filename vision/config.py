# ==============================================================================
# [HCI 평가 및 비전 연계] 키오스크 상태별 ArUco ID 매핑 및 자동 등록
# ==============================================================================

REFERENCE_ARUCO_ID = 769

ARUCO_DICT_NAME = "DICT_5X5_1000"

MARKER_LENGTH_M = 0.05

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

# 하드웨어 및 카메라 기본 설정값
CAMERA_INDEX = 0
MARKER_LENGTH = 0.05
CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"


# ==============================================================================
# 상태 정보 맵
# - app_aruco_dual.py의 get_state_info()에서 사용
# - target은 실제 좌표가 아니라 kiosk_guide_model.py에서 해석할 target key
# ==============================================================================

STATE_MAP = {
    0: {
        "name": "HOME",
        "label": "메인 화면",
        "target": None,
    },

    # 카테고리 탭
    32: {
        "name": "CATEGORY_COFFEE",
        "label": "Coffee 카테고리",
        "target": "tea_category_button",
    },
    64: {
        "name": "CATEGORY_TEA",
        "label": "Tea 카테고리",
        "target": "peach_ice_tea_button",
    },
    96: {
        "name": "CATEGORY_ADE_JUICE",
        "label": "Ade/Juice 카테고리",
        "target": "menu_item_button",
    },
    128: {
        "name": "CATEGORY_BEVERAGE",
        "label": "Beverage 카테고리",
        "target": "menu_item_button",
    },
    160: {
        "name": "CATEGORY_BLENDED",
        "label": "Blended 카테고리",
        "target": "menu_item_button",
    },

    # 결제 / 예외
    768: {
        "name": "PAYMENT_SELECT",
        "label": "결제 방식 선택",
        "target": "card_payment_button",
    },
    800: {
        "name": "ERROR_RECOVERY",
        "label": "오류 복구",
        "target": None,
    },
    900: {
        "name": "FAIL_SAFE",
        "label": "안전 모드",
        "target": None,
    },
}


# ==============================================================================
# 옵션 선택 구간 자동 등록
# script.js 공식:
# markerId = 256 + (menuHash * 32) + optionCode
# optionCode = temp * 9 + sugar * 3 + ice
# ==============================================================================

for menu_hash in range(6):
    for temp in [0, 1]:          # ICED(0), HOT(1)
        for sugar in [0, 1, 2]:  # 덜 달게(0), 보통(1), 달게(2)
            for ice in [0, 1, 2]:  # 얼음 많이(0), 얼음 보통(1), 얼음 적게(2)
                option_code = (temp * 9) + (sugar * 3) + ice
                marker_id = 256 + (menu_hash * 32) + option_code

                STATE_MAP[marker_id] = {
                    "name": "OPTION_SELECT",
                    "label": "옵션 선택",
                    "target": "option_button",
                }


# ==============================================================================
# 장바구니 / 주문 확인 구간 자동 등록
# script.js 공식:
# markerId = 512 + ((menuId - 1) * 4)
# menuId: 1~30
# ==============================================================================

for raw_menu_id in range(30):
    marker_id = 512 + (raw_menu_id * 4)

    STATE_MAP[marker_id] = {
        "name": "RECEIPT_CONFIRM",
        "label": "주문 확인",
        "target": "receipt_payment_button",
    }


# ==============================================================================
# get_state_info
# ==============================================================================

def get_state_info(marker_id):
    if marker_id is None or marker_id < 0:
        return {
            "name": "UNKNOWN",
            "label": "상태 마커 없음",
            "target": None,
        }

    return STATE_MAP.get(
        marker_id,
        {
            "name": "UNMAPPED",
            "label": "매핑되지 않은 상태",
            "target": None,
        },
    )
