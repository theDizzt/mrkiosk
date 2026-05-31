REFERENCE_ARUCO_ID = 769

ARUCO_DICT_NAME = "DICT_5X5_1000"

MARKER_LENGTH_M = 0.05

SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080

STATE_MAP = {
    0: {
        "name": "HOME",
        "label": "메인 화면",
        "target": None,
    },
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
    260: {
        "name": "PEACH_ICE_TEA_DEFAULT",
        "label": "복숭아아이스티 기본 옵션",
        "target": "less_sweet_button",
    },
    257: {
        "name": "PEACH_ICE_TEA_LESS_SWEET",
        "label": "덜 달게 선택",
        "target": "more_ice_button",
    },
    256: {
        "name": "PEACH_ICE_TEA_MORE_ICE",
        "label": "얼음 많이 선택",
        "target": "add_to_cart_button",
    },
    536: {
        "name": "RECEIPT_CONFIRM",
        "label": "주문 확인",
        "target": "receipt_payment_button",
    },
    768: {
        "name": "PAYMENT_SELECT",
        "label": "결제 방식 선택",
        "target": "card_payment_button",
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
