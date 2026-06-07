CATEGORY_STATE = {
    "Coffee": 32,
    "Tea": 64,
    "Ade/Juice": 96,
    "Beverage": 128,
    "Blended": 160,
}

CATEGORY_ORDER = [
    "Coffee",
    "Tea",
    "Ade/Juice",
    "Beverage",
    "Blended",
]

TEMP_VALUE = {
    "ICED": 0,
    "HOT": 1,
}

SWEET_VALUE = {
    "덜 달게": 0,
    "보통": 1,
    "달게": 2,
}

ICE_VALUE = {
    "얼음 많이": 0,
    "얼음 보통": 1,
    "얼음 적게": 2,
}


def get_category_from_menu_id(menu_id):
    """
    메뉴가 카테고리별 6개씩 있다고 가정.
    menu_id: 1~30
    """

    if menu_id < 1 or menu_id > 30:
        raise ValueError(f"menu_id must be between 1 and 30: {menu_id}")

    category_index = (menu_id - 1) // 6
    return CATEGORY_ORDER[category_index]


def calc_option_state_id(menu_id, temp="ICED", sweetness="보통", ice="얼음 보통"):
    menu_hash = (menu_id - 1) % 6

    temp_value = TEMP_VALUE[temp]
    sweet_value = SWEET_VALUE[sweetness]
    ice_value = ICE_VALUE[ice]

    option_code = temp_value * 9 + sweet_value * 3 + ice_value

    return 256 + (menu_hash * 32) + option_code


def calc_receipt_state_id(menu_id):
    raw_menu_id = menu_id - 1
    return 512 + (raw_menu_id * 4)


def build_expected_route(category, menu_id, temp, sweetness, ice):
    route = []

    route.append(0)

    # 메뉴 화면 진입 시 기본 Coffee가 먼저 잡히는 구조
    route.append(32)

    category_state = CATEGORY_STATE[category]
    if category_state != 32:
        route.append(category_state)

    # 메뉴 클릭 후 기본 옵션 상태
    current_temp = "ICED"
    current_sweetness = "보통"
    current_ice = "얼음 보통"

    route.append(
        calc_option_state_id(menu_id, current_temp, current_sweetness, current_ice)
    )

    # 온도 변경
    if temp != current_temp:
        current_temp = temp
        route.append(
            calc_option_state_id(menu_id, current_temp, current_sweetness, current_ice)
        )

    # 당도 변경
    if sweetness != current_sweetness:
        current_sweetness = sweetness
        route.append(
            calc_option_state_id(menu_id, current_temp, current_sweetness, current_ice)
        )

    # 얼음 변경, ICED일 때만
    if temp == "ICED" and ice != current_ice:
        current_ice = ice
        route.append(
            calc_option_state_id(menu_id, current_temp, current_sweetness, current_ice)
        )

    # 담기 후 카테고리 상태로 복귀
    route.append(category_state)

    # 주문 확인
    route.append(calc_receipt_state_id(menu_id))

    # 결제 방식 선택
    route.append(768)

    # 결제 완료 후 초기화
    route.append(0)

    return route


def build_quick_order_route(menu_id):
    """
    데모용 Quick Order FSM Route.

    메뉴 번호만 입력받고,
    옵션 선택 없이 기본 옵션창에서 바로 담기 버튼을 누르는 흐름.

    흐름:
    HOME
    → Coffee 기본 카테고리
    → 메뉴 번호 기반 카테고리
    → 메뉴 클릭 후 옵션창 기본 상태
    → 담기 후 카테고리 화면 복귀
    → 주문 확인
    → 결제 방식 선택
    → HOME
    """

    category = get_category_from_menu_id(menu_id)
    category_state = CATEGORY_STATE[category]

    route = []

    # 1. 메인 화면
    route.append(0)

    # 2. 메뉴 화면 진입 시 기본 Coffee
    route.append(32)

    # 3. Coffee가 아니면 해당 카테고리로 이동
    if category_state != 32:
        route.append(category_state)

    # 4. 메뉴 클릭 후 기본 옵션창 상태
    default_option_state = calc_option_state_id(
        menu_id=menu_id,
        temp="ICED",
        sweetness="보통",
        ice="얼음 보통",
    )
    route.append(default_option_state)

    # 5. 옵션 선택 없이 담기 버튼 선택 후 카테고리 화면 복귀
    route.append(category_state)

    # 6. 주문 확인 화면
    route.append(calc_receipt_state_id(menu_id))

    # 7. 결제 방식 선택
    route.append(768)

    # 8. 결제 완료 후 HOME
    route.append(0)

    return route
