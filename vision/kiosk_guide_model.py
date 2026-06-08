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

EXPECTED_ROUTE = [
    0,
    32,
    64,
    260,
    257,
    256,
    64,
    536,
    768,
    0,
]


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
    # 복숭아 아이스티가 menu_id 7이라면 Tea 카테고리의 첫 번째 메뉴이므로 menu_hash = 0
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


def get_option_change_target(current_state_id: int, expected_state_id: int):
    """
    옵션창 내부에서 current option state -> expected option state로 갈 때
    실제로 눌러야 하는 옵션 버튼을 반환한다.

    예시:
    260 -> 257 : 덜 달게
    257 -> 256 : 얼음 많이
    """

    if not (is_option_state(current_state_id) and is_option_state(expected_state_id)):
        return None

    current = parse_option_state(current_state_id)
    expected = parse_option_state(expected_state_id)

    # 메뉴가 바뀌는 경우는 옵션창 내부 전이로 보지 않음
    if current["menu_hash"] != expected["menu_hash"]:
        return get_menu_card_target_from_option_state(expected_state_id)

    # 당도 변경
    if current["sweet"] != expected["sweet"]:
        if expected["sweet"] == 0:
            return TARGET_RECTS.get("less_sweet_button")

        # 아직 좌표를 등록하지 않았다면 fallback
        if expected["sweet"] == 1:
            return TARGET_RECTS.get("normal_sweet_button")
        if expected["sweet"] == 2:
            return TARGET_RECTS.get("more_sweet_button")

    # 얼음 변경
    if current["ice"] != expected["ice"]:
        if expected["ice"] == 0:
            return TARGET_RECTS.get("more_ice_button")

        # 아직 좌표를 등록하지 않았다면 fallback
        if expected["ice"] == 1:
            return TARGET_RECTS.get("normal_ice_button")
        if expected["ice"] == 2:
            return TARGET_RECTS.get("less_ice_button")

    # 온도 변경 좌표를 나중에 추가할 경우 사용
    if current["temp"] != expected["temp"]:
        if expected["temp"] == 0:
            return TARGET_RECTS.get("iced_button")
        if expected["temp"] == 1:
            return TARGET_RECTS.get("hot_button")

    return None


def get_target_for_state(state_id: int):
    """
    단일 state_id만 보고 target을 반환하는 fallback 함수.
    정확한 시나리오 안내는 get_quick_order_target(current, expected)을 사용해야 한다.
    """

    if state_id == 0:
        return TARGET_RECTS.get(0)

    if state_id in CATEGORY_IDS:
        return TARGET_RECTS.get(state_id)

    if is_option_state(state_id):
        # 단일 state_id만으로는 메뉴 클릭인지 옵션 변경인지 구분 불가
        return get_menu_card_target_from_option_state(state_id)

    if is_receipt_state(state_id):
        return TARGET_RECTS.get("order_payment_button")

    if state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button")

    return TARGET_RECTS.get(state_id)


def get_dynamic_target_for_state(state_id: int):
    return get_target_for_state(state_id)


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

    # 상태 마커가 아직 없거나 target을 만들 수 없는 경우
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
    if is_option_state(current_state_id) and is_category_state(expected_state_id):
        return TARGET_RECTS.get("add_to_cart_button")

    # 5. 옵션창 내부에서 옵션을 변경하는 경우
    if is_option_state(current_state_id) and is_option_state(expected_state_id):
        option_target = get_option_change_target(current_state_id, expected_state_id)
        if option_target is not None:
            return option_target

    # 6. 카테고리 화면에서 메뉴 카드를 눌러 옵션창으로 들어가는 경우
    if is_category_state(current_state_id) and is_option_state(expected_state_id):
        return get_menu_card_target_from_option_state(expected_state_id)

    # 7. 카테고리 이동
    # 예: current 32, expected 64 -> Tea 버튼
    if is_category_state(expected_state_id):
        return TARGET_RECTS.get(expected_state_id)

    # 8. fallback
    return get_target_for_state(expected_state_id)