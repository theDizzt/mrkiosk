REFERENCE_ARUCO_ID = 0

ARUCO_DICT_NAME = "DICT_5X5_1000"

MARKER_LENGTH_M = 0.05

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

STATE_MAP = {
    10: {
        "name": "MAIN_MENU",
        "label": "메인 화면",
        "target": {
            "x": 960,
            "y": 540,
            "width": 700,
            "height": 500,
        },
    },
    20: {
        "name": "ORDER_START",
        "label": "주문 시작",
        "target": {
            "x": 960,
            "y": 860,
            "width": 420,
            "height": 110,
        },
    },
    30: {
        "name": "MENU_SELECT",
        "label": "메뉴 선택",
        "target": {
            "x": 520,
            "y": 420,
            "width": 260,
            "height": 220,
        },
    },
    40: {
        "name": "OPTION_SELECT",
        "label": "옵션 선택",
        "target": {
            "x": 1420,
            "y": 520,
            "width": 360,
            "height": 180,
        },
    },
    50: {
        "name": "CART_CONFIRM",
        "label": "장바구니 확인",
        "target": {
            "x": 1600,
            "y": 900,
            "width": 360,
            "height": 120,
        },
    },
    60: {
        "name": "PAYMENT_GUIDE",
        "label": "결제 안내",
        "target": {
            "x": 1700,
            "y": 930,
            "width": 320,
            "height": 110,
        },
    },
    70: {
        "name": "PAYMENT_PROCESSING",
        "label": "결제 진행 중",
        "target": {
            "x": 960,
            "y": 540,
            "width": 500,
            "height": 180,
        },
    },
    80: {
        "name": "PAYMENT_COMPLETE",
        "label": "결제 완료",
        "target": {
            "x": 960,
            "y": 540,
            "width": 500,
            "height": 180,
        },
    },
    90: {
        "name": "ERROR_HELP",
        "label": "오류 / 도움말",
        "target": {
            "x": 960,
            "y": 900,
            "width": 700,
            "height": 140,
        },
    },
}


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
