# vision/kiosk_guide_model.py

KIOSK_WIDTH = 1024
KIOSK_HEIGHT = 720

POSE_MARKER_ID = 769

# CSS 기준: marker 64px, top/left/right/bottom 4px
POSE_MARKER_CENTER = (36, 36)
STATE_MARKER_CENTER = (988, 684)
MARKER_SIZE_PX = 64

CATEGORY_IDS = [32, 64, 96, 128, 160]

STATE_MAP = {
    0: "HOME",
    32: "CATEGORY_COFFEE",
    64: "CATEGORY_TEA",
    96: "CATEGORY_ADE_JUICE",
    128: "CATEGORY_BEVERAGE",
    160: "CATEGORY_BLENDED",
    260: "PEACH_ICE_TEA_DEFAULT",
    257: "PEACH_ICE_TEA_LESS_SWEET",
    256: "PEACH_ICE_TEA_MORE_ICE",
    536: "RECEIPT_CONFIRM",
    768: "PAYMENT_SELECT",
}


# ==============================================================================
# 1024 x 720 키오스크 CSS 기준 버튼 좌표
# x, y, w, h는 .device-frame 내부 좌표
# ==============================================================================

TARGET_RECTS = {
    # 홈 화면
    0: {
        "name": "dine_in_button",
        "label": "매장에서 먹고 갈게요",
        "rect": {"x": 252, "y": 345, "w": 520, "h": 84},
    },
    "dine_in_button": {
        "name": "dine_in_button",
        "label": "매장에서 먹고 갈게요",
        "rect": {"x": 252, "y": 345, "w": 520, "h": 84},
    },

    # 카테고리 버튼
    32: {
        "name": "coffee_category_button",
        "label": "Coffee 카테고리",
        "rect": {"x": 18, "y": 90, "w": 123, "h": 56},
    },
    "coffee_category_button": {
        "name": "coffee_category_button",
        "label": "Coffee 카테고리",
        "rect": {"x": 18, "y": 90, "w": 123, "h": 56},
    },

    64: {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 149, "y": 90, "w": 123, "h": 56},
    },
    "tea_category_button": {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 149, "y": 90, "w": 123, "h": 56},
    },

    96: {
        "name": "ade_juice_category_button",
        "label": "Ade/Juice 카테고리",
        "rect": {"x": 280, "y": 90, "w": 123, "h": 56},
    },
    "ade_juice_category_button": {
        "name": "ade_juice_category_button",
        "label": "Ade/Juice 카테고리",
        "rect": {"x": 280, "y": 90, "w": 123, "h": 56},
    },

    128: {
        "name": "beverage_category_button",
        "label": "Beverage 카테고리",
        "rect": {"x": 411, "y": 90, "w": 123, "h": 56},
    },
    "beverage_category_button": {
        "name": "beverage_category_button",
        "label": "Beverage 카테고리",
        "rect": {"x": 411, "y": 90, "w": 123, "h": 56},
    },

    160: {
        "name": "blended_category_button",
        "label": "Blended 카테고리",
        "rect": {"x": 542, "y": 90, "w": 123, "h": 56},
    },
    "blended_category_button": {
        "name": "blended_category_button",
        "label": "Blended 카테고리",
        "rect": {"x": 542, "y": 90, "w": 123, "h": 56},
    },

    # 메뉴 카드 6개, menu_hash 0~5
    "menu_item_0": {
        "name": "menu_item_0",
        "label": "1번째 메뉴",
        "rect": {"x": 18, "y": 162, "w": 204, "h": 261},
    },
    "menu_item_1": {
        "name": "menu_item_1",
        "label": "2번째 메뉴",
        "rect": {"x": 240, "y": 162, "w": 204, "h": 261},
    },
    "menu_item_2": {
        "name": "menu_item_2",
        "label": "3번째 메뉴",
        "rect": {"x": 461, "y": 162, "w": 204, "h": 261},
    },
    "menu_item_3": {
        "name": "menu_item_3",
        "label": "4번째 메뉴",
        "rect": {"x": 18, "y": 441, "w": 204, "h": 261},
    },
    "menu_item_4": {
        "name": "menu_item_4",
        "label": "5번째 메뉴",
        "rect": {"x": 240, "y": 441, "w": 204, "h": 261},
    },
    "menu_item_5": {
        "name": "menu_item_5",
        "label": "6번째 메뉴",
        "rect": {"x": 461, "y": 441, "w": 204, "h": 261},
    },

    # 옵션 모달 버튼
    # 지금 단계에서는 옵션 선택을 사용하지 않지만,
    # 나중에 옵션 기능 붙일 때 재사용 가능.
    "less_sweet_button": {
        "name": "less_sweet_button",
        "label": "덜 달게",
        "rect": {"x": 304, "y": 440, "w": 150, "h": 48},
    },
    "more_ice_button": {
        "name": "more_ice_button",
        "label": "얼음 많이",
        "rect": {"x": 304, "y": 525, "w": 150, "h": 48},
    },
    "add_to_cart_button": {
        "name": "add_to_cart_button",
        "label": "담기",
        "rect": {"x": 518, "y": 520, "w": 230, "h": 64},
    },

    # 메뉴 화면 우측 결제하기 버튼
    "order_payment_button": {
        "name": "order_payment_button",
        "label": "결제하기",
        "rect": {"x": 705, "y": 630, "w": 297, "h": 68},
    },

    # 주문 확인 화면 결제하기 버튼
    "receipt_payment_button": {
        "name": "receipt_payment_button",
        "label": "주문 확인 결제하기",
        "rect": {"x": 526, "y": 629, "w": 470, "h": 64},
    },

    # 카드 결제 버튼
    "card_payment_button": {
        "name": "card_payment_button",
        "label": "카드 결제",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84},
    },
}


def get_state_name(state_id: int) -> str:
    return STATE_MAP.get(state_id, "UNKNOWN")


def is_category_state(state_id: int) -> bool:
    return state_id in CATEGORY_IDS


def is_option_state(state_id: int) -> bool:
    return 256 <= state_id < 448


def is_receipt_state(state_id: int) -> bool:
    return 512 <= state_id < 632


def parse_option_state(state_id: int):
    """
    script.js 공식:
    state_id = 256 + menu_hash * 32 + option_code
    option_code = temp * 9 + sugar * 3 + ice

    temp: 0=ICED, 1=HOT
    sugar: 0=덜 달게, 1=보통, 2=달게
    ice: 0=얼음 많이, 1=얼음 보통, 2=얼음 적게
    """

    option_area = state_id - 256
    menu_hash = option_area // 32
    option_code = option_area % 32

    temp_value = option_code // 9
    remain = option_code % 9
    sweet_value = remain // 3
    ice_value = remain % 3

    return {
        "menu_hash": menu_hash,
        "option_code": option_code,
        "temp": temp_value,
        "sweet": sweet_value,
        "ice": ice_value,
    }


def get_menu_card_target_from_option_state(expected_state_id: int):
    """
    카테고리 화면에서 메뉴를 눌러 옵션창으로 들어갈 때,
    expected_state_id의 menu_hash를 이용해 메뉴 카드 위치를 찾는다.
    """

    if not is_option_state(expected_state_id):
        return None

    parsed = parse_option_state(expected_state_id)
    menu_hash = parsed["menu_hash"]

    if 0 <= menu_hash <= 5:
        return TARGET_RECTS.get(f"menu_item_{menu_hash}")

    return None


def get_target_for_state(state_id: int):
    """
    단일 state_id만 보고 target을 반환하는 fallback 함수.
    정확한 안내는 get_quick_order_target(current, expected)을 사용해야 한다.
    """

    if state_id == 0:
        return TARGET_RECTS.get(0)

    if is_category_state(state_id):
        return TARGET_RECTS.get(state_id)

    if is_option_state(state_id):
        return get_menu_card_target_from_option_state(state_id)

    if is_receipt_state(state_id):
        return TARGET_RECTS.get("order_payment_button")

    if state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button")

    return TARGET_RECTS.get(state_id)


def get_dynamic_target_for_state(state_id: int):
    return get_target_for_state(state_id)

def get_recovery_target(current_state_id: int, detected_state_id: int = None):
    """
    잘못된 상태 마커가 인식되었을 때,
    FSM이 인정한 현재 상태로 돌아가기 위한 버튼을 반환한다.

    예:
    current_state_id = 32, detected_state_id = 128
    → Coffee 버튼을 눌러 32 상태로 복귀해야 함
    """

    if current_state_id is None or current_state_id < 0:
        return None

    # HOME으로 복구
    if current_state_id == 0:
        return TARGET_RECTS.get(0)

    # 카테고리 상태로 복구
    # 예: 현재 FSM은 Coffee(32)인데 사용자가 Beverage(128)를 눌렀다면
    # 다시 Coffee 버튼을 안내
    if is_category_state(current_state_id):
        return TARGET_RECTS.get(current_state_id)

    # 옵션 상태로 복구
    # 옵션창 상태를 다시 만들려면 해당 메뉴 카드를 다시 누르게 안내
    if is_option_state(current_state_id):
        return get_menu_card_target_from_option_state(current_state_id)

    # 주문 확인 상태로 복구
    if is_receipt_state(current_state_id):
        return TARGET_RECTS.get("order_payment_button")

    # 결제 방식 선택 상태로 복구
    if current_state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button")

    return get_target_for_state(current_state_id)

def get_quick_order_target(current_state_id: int, expected_state_id: int):
    """
    FSM 전이 기반 target 결정 함수.

    current_state_id:
        현재 FSM이 인정한 상태

    expected_state_id:
        다음에 도달해야 하는 상태

    핵심:
        expected_state_id는 '도착할 상태'이고,
        target은 '그 상태로 가기 위해 지금 눌러야 하는 버튼'이다.
    """

    if current_state_id is None or current_state_id < 0:
        return None

    if expected_state_id is None:
        return get_target_for_state(current_state_id)

    # 0. HOME 화면에서는 32로 가기 위해 Coffee가 아니라 매장 주문 버튼을 눌러야 함
    if current_state_id == 0:
        return TARGET_RECTS.get(0)

    # 1. 결제 방식 선택 화면에서 HOME으로 돌아가는 경우: 카드 결제 버튼
    if current_state_id == 768 and expected_state_id == 0:
        return TARGET_RECTS.get("card_payment_button")

    # 2. 주문 확인 화면에서 결제 방식 선택 화면으로 가는 경우: 주문 확인 결제하기 버튼
    if is_receipt_state(current_state_id) and expected_state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button")

    # 3. 메뉴/카테고리 화면에서 주문 확인 화면으로 가는 경우: 메뉴 화면 우측 결제하기 버튼
    if is_receipt_state(expected_state_id):
        return TARGET_RECTS.get("order_payment_button")

    # 4. 옵션창에서 카테고리 화면으로 돌아가는 경우: 담기 버튼
    # 현재 quick route에서는 기본 옵션창 진입 후 바로 이 조건으로 담기 안내
    if is_option_state(current_state_id) and is_category_state(expected_state_id):
        return TARGET_RECTS.get("add_to_cart_button")

    # 5. 카테고리 화면에서 메뉴 카드를 눌러 옵션창으로 들어가는 경우
    if is_category_state(current_state_id) and is_option_state(expected_state_id):
        return get_menu_card_target_from_option_state(expected_state_id)

    # 6. 카테고리 이동
    # 예: current 32, expected 64 -> Tea 버튼
    if is_category_state(expected_state_id):
        return TARGET_RECTS.get(expected_state_id)

    # 7. fallback
    return get_target_for_state(expected_state_id)