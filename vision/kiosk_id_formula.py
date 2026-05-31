CATEGORY_STATE = {
    "Coffee": 32,
    "Tea": 64,
    "Ade/Juice": 96,
    "Beverage": 128,
    "Blended": 160,
}

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
