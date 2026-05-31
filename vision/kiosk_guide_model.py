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
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 164, "y": 90, "w": 122, "h": 56}
    },

    64: {
        "name": "peach_ice_tea_button",
        "label": "복숭아아이스티",
        "rect": {"x": 36, "y": 164, "w": 196, "h": 230}
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
