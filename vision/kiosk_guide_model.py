# vision/kiosk_guide_model.py

KIOSK_WIDTH = 1024
KIOSK_HEIGHT = 720

POSE_MARKER_ID = 769

# CSS 기준: marker 64px, top/left/right/bottom 4px
POSE_MARKER_CENTER = (36, 36)
STATE_MARKER_CENTER = (988, 684)
MARKER_SIZE_PX = 64

STATE_MAP = {
    0: "HOME",
    32: "CATEGORY_COFFEE",
    64: "CATEGORY_TEA",
    260: "PEACH_ICE_TEA_DEFAULT",
    257: "PEACH_ICE_TEA_LESS_SWEET",
    256: "PEACH_ICE_TEA_MORE_ICE",
    536: "RECEIPT_CONFIRM",
    768: "PAYMENT_SELECT"
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
    0
]

# 키오스크 CSS 1024x720 기준의 버튼 rect
# x, y, w, h는 .device-frame 내부 좌표
# 값은 1차 추정값이므로 실제 화면에서 약간 조정 필요
TARGET_RECTS = {
    0: {
        "name": "dine_in_button",
        "label": "매장에서 먹고 갈게요",
        "rect": {"x": 252, "y": 345, "w": 520, "h": 84}
    },

    32: {
    "name": "coffee_category_button",
    "label": "Coffee 카테고리",
    "rect": {"x": 36, "y": 90, "w": 122, "h": 56}
    },
    64: {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 164, "y": 90, "w": 122, "h": 56}
    },
    96: {
        "name": "ade_juice_category_button",
        "label": "Ade/Juice 카테고리",
        "rect": {"x": 292, "y": 90, "w": 122, "h": 56}
    },
    128: {
        "name": "beverage_category_button",
        "label": "Beverage 카테고리",
        "rect": {"x": 420, "y": 90, "w": 122, "h": 56}
    },
    160: {
        "name": "blended_category_button",
        "label": "Blended 카테고리",
        "rect": {"x": 548, "y": 90, "w": 122, "h": 56}
    },

    260: {
        "name": "less_sweet_button",
        "label": "덜 달게",
        "rect": {"x": 304, "y": 440, "w": 150, "h": 48}
    },

    257: {
        "name": "more_ice_button",
        "label": "얼음 많이",
        "rect": {"x": 304, "y": 525, "w": 150, "h": 48}
    },

    256: {
        "name": "add_to_cart_button",
        "label": "담기",
        "rect": {"x": 528, "y": 615, "w": 220, "h": 64}
    },

    536: {
        "name": "receipt_payment_button",
        "label": "결제하기",
        "rect": {"x": 520, "y": 630, "w": 460, "h": 64}
    },

    768: {
        "name": "card_payment_button",
        "label": "카드",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84}
    }
}


TARGET_RECTS.update({
    # 카테고리 버튼
    32: {
        "name": "coffee_category_button",
        "label": "Coffee 카테고리",
        "rect": {"x": 18, "y": 90, "w": 123, "h": 56}
    },
    64: {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 149, "y": 90, "w": 123, "h": 56}
    },
    96: {
        "name": "ade_juice_category_button",
        "label": "Ade/Juice 카테고리",
        "rect": {"x": 280, "y": 90, "w": 123, "h": 56}
    },
    128: {
        "name": "beverage_category_button",
        "label": "Beverage 카테고리",
        "rect": {"x": 411, "y": 90, "w": 123, "h": 56}
    },
    160: {
        "name": "blended_category_button",
        "label": "Blended 카테고리",
        "rect": {"x": 542, "y": 90, "w": 123, "h": 56}
    },

    # 메뉴 카드 6개, menu_hash 0~5
    "menu_item_0": {
        "name": "menu_item_0",
        "label": "1번째 메뉴",
        "rect": {"x": 18, "y": 162, "w": 204, "h": 261}
    },
    "menu_item_1": {
        "name": "menu_item_1",
        "label": "2번째 메뉴",
        "rect": {"x": 240, "y": 162, "w": 204, "h": 261}
    },
    "menu_item_2": {
        "name": "menu_item_2",
        "label": "3번째 메뉴",
        "rect": {"x": 461, "y": 162, "w": 204, "h": 261}
    },
    "menu_item_3": {
        "name": "menu_item_3",
        "label": "4번째 메뉴",
        "rect": {"x": 18, "y": 441, "w": 204, "h": 261}
    },
    "menu_item_4": {
        "name": "menu_item_4",
        "label": "5번째 메뉴",
        "rect": {"x": 240, "y": 441, "w": 204, "h": 261}
    },
    "menu_item_5": {
        "name": "menu_item_5",
        "label": "6번째 메뉴",
        "rect": {"x": 461, "y": 441, "w": 204, "h": 261}
    },

    # 옵션 모달의 담기 버튼
    "add_to_cart_button": {
        "name": "add_to_cart_button",
        "label": "담기",
        "rect": {"x": 518, "y": 520, "w": 230, "h": 64}
    },

    # 메뉴 화면 우측 결제하기 버튼
    "order_payment_button": {
        "name": "order_payment_button",
        "label": "결제하기",
        "rect": {"x": 705, "y": 630, "w": 297, "h": 68}
    },

    # 주문 확인 화면 결제하기 버튼
    "receipt_payment_button": {
        "name": "receipt_payment_button",
        "label": "주문 확인 결제하기",
        "rect": {"x": 526, "y": 629, "w": 470, "h": 64}
    },

    # 카드 결제 버튼
    "card_payment_button": {
        "name": "card_payment_button",
        "label": "카드 결제",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84}
    },
})


def get_state_name(state_id: int) -> str:
    return STATE_MAP.get(state_id, "UNKNOWN")


def get_target_for_state(state_id: int):
    """
    현재 FSM의 expected_id 또는 guide_state_id를 받아
    다음에 안내해야 할 버튼 rect를 반환한다.
    """

    # 홈 화면: 매장 주문 버튼
    if state_id == 0:
        return TARGET_RECTS.get(0)

    # 카테고리 상태
    if state_id == 32:
        return TARGET_RECTS.get(32)

    if state_id == 64:
        return TARGET_RECTS.get(64)

    # 옵션 선택 상태
    # 키오스크 공식:
    # state_id = 256 + menu_hash * 32 + option_code
    if 256 <= state_id < 448:
        option_code = (state_id - 256) % 32

        temp_value = option_code // 9
        remain = option_code % 9
        sweet_value = remain // 3
        ice_value = remain % 3

        # option_code가 가리키는 상태 자체를 기준으로
        # 어느 옵션 버튼을 안내할지 결정
        if sweet_value == 0:
            return TARGET_RECTS.get(260)  # 덜 달게 버튼

        if ice_value == 0:
            return TARGET_RECTS.get(257)  # 얼음 많이 버튼

        return TARGET_RECTS.get(260)

    # 주문 확인 화면
    # receipt id = 512 + (menu_id - 1) * 4
    if 512 <= state_id < 632:
        return TARGET_RECTS.get(536)

    # 결제 방식 선택
    if state_id == 768:
        return TARGET_RECTS.get(768)

    return TARGET_RECTS.get(state_id)


def get_dynamic_target_for_state(state_id: int):
    # 카테고리 상태
    if state_id == 32:
        return TARGET_RECTS[32]
    if state_id == 64:
        return TARGET_RECTS[64]

    # 옵션 상태 영역: 256~447
    if 256 <= state_id < 448:
        option_code = (state_id - 256) % 32

        temp_value = option_code // 9
        remain = option_code % 9
        sweet_value = remain // 3
        ice_value = remain % 3

        # 현재는 다음 단계 안내용으로 주로 사용
        # sweet_value / ice_value에 따라 안내 대상 선택
        if sweet_value == 0:
            return TARGET_RECTS[260]  # 덜 달게 버튼 위치
        if ice_value == 0:
            return TARGET_RECTS[257]  # 얼음 많이 버튼 위치

        return TARGET_RECTS[260]

    # 주문 확인 영역
    if 512 <= state_id < 632:
        return TARGET_RECTS[536]

    if state_id == 768:
        return TARGET_RECTS[768]

    return TARGET_RECTS.get(state_id)


# vision/kiosk_guide_model.py 내부의 get_quick_order_target 함수 교체 전문

def get_quick_order_target(current_state_id: int, expected_state_id: int):
    """
    quick_order 데모용 target 결정 함수 (안전 가이드 패치 적용)
    """
    # 1. 옵션창 상태에서 카테고리 화면으로 돌아가는 경우 ('담기' 버튼 안내)
    if 256 <= current_state_id < 448 and expected_state_id in [32, 64, 96, 128, 160]:
        return TARGET_RECTS.get("add_to_cart_button") or TARGET_RECTS.get(256)

    # 2. 카테고리 선택 단계
    if expected_state_id in [32, 64, 96, 128, 160]:
        return TARGET_RECTS.get(expected_state_id) or TARGET_RECTS.get(32)

    # 3. 메뉴 클릭 후 옵션창으로 진입하는 단계 (카테고리 안의 '메뉴 카드' 버튼 안내)
    if 256 <= expected_state_id < 448:
        menu_hash = (expected_state_id - 256) // 32
        if 0 <= menu_hash <= 5:
            return TARGET_RECTS.get(f"menu_item_{menu_hash}") or TARGET_RECTS.get(260)
        return TARGET_RECTS.get(260)

    # 4. 주문 확인 화면으로 넘어가는 단계 ('결제하기' 버튼 안내)
    if 512 <= expected_state_id < 632:
        # 중요: order_payment_button이나 receipt_payment_button이 누락되었을 때 536번 기본 좌표로 자동 복구
        return TARGET_RECTS.get("order_payment_button") or TARGET_RECTS.get("receipt_payment_button") or TARGET_RECTS.get(536)

    # 5. 결제 방식 선택 화면으로 넘어가는 단계 (주문 확인창의 '결제하기' 버튼 안내)
    if expected_state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button") or TARGET_RECTS.get(768)

    # 6. 결제 완료 후 HOME 복귀 (카드 결제 버튼 안내)
    if expected_state_id == 0:
        return TARGET_RECTS.get("card_payment_button") or TARGET_RECTS.get(768) or TARGET_RECTS.get(0)

    # 7. 예외 안전장치: 위의 모든 조건에 걸리지 않으면 수치 기반 기본 타겟 리턴
    return get_target_for_state(expected_state_id)    

    # 1. 옵션창 상태에서 카테고리 화면으로 돌아가는 경우
    # 예: 260 → 64, 292 → 64, 292 → 96
    # 이 전이는 '담기' 버튼을 눌러야 발생함
    if 256 <= current_state_id < 448 and expected_state_id in [32, 64, 96, 128, 160]:
        return TARGET_RECTS.get("add_to_cart_button") or TARGET_RECTS.get(256)

    # 2. 카테고리 선택 단계
    # 예: 0 → 32, 32 → 64, 32 → 96, 32 → 128, 32 → 160
    if expected_state_id in [32, 64, 96, 128, 160]:
        return TARGET_RECTS.get(expected_state_id)

    # 3. 메뉴 클릭 후 옵션창으로 진입하는 단계
    # 예: 64 → 260, 64 → 292, 96 → 292
    # 이때는 해당 카테고리 안의 '메뉴 버튼'을 눌러야 함
    if 256 <= expected_state_id < 448:
        menu_hash = (expected_state_id - 256) // 32

        if 0 <= menu_hash <= 5:
            return TARGET_RECTS.get(f"menu_item_{menu_hash}")

        return None

    # 4. 주문 확인 화면으로 넘어가는 단계
    # 예: 64 → 536, 64 → 540, 96 → 564
    # 이때는 카테고리 화면의 '결제하기' 버튼을 눌러야 함
    if 512 <= expected_state_id < 632:
        return TARGET_RECTS.get("order_payment_button") or TARGET_RECTS.get(536)

    # 5. 결제 방식 선택 화면으로 넘어가는 단계
    # 예: 536 → 768, 540 → 768, 564 → 768
    # 이때는 주문 확인 화면의 '결제하기' 버튼 위치가 같음
    if expected_state_id == 768:
        return TARGET_RECTS.get("receipt_payment_button") or TARGET_RECTS.get(768)

    # 6. 결제 완료 후 HOME 복귀
    # 보통 카드 결제 버튼 안내
    if expected_state_id == 0:
        return TARGET_RECTS.get("card_payment_button") or TARGET_RECTS.get(0)

    return get_target_for_state(expected_state_id)
