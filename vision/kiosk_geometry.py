# vision/kiosk_geometry.py

import cv2
import numpy as np

# 브라우저 렌더링 기준 고정 사양 (style.css 바탕 정밀 셋팅)
KIOSK_WIDTH = 1024
KIOSK_HEIGHT = 720

# 마커 중심점 좌표 (769번 레퍼런스 마커와 상태 마커의 웹상 절대 픽셀 위치 계산)
POSE_MARKER_CENTER = (36.0, 36.0)     # top: 4px + (size 64px / 2)
STATE_MARKER_CENTER = (988.0, 684.0)  # right: 4px, bottom: 4px 반전 축 중심점
MARKER_SIZE_PX = 64.0

# ==============================================================================
# [정밀 동적 보정 완료] 웹 프론트엔드 CSS 레이아웃 그리드 기반 픽셀 좌표 매트릭스
# ==============================================================================
TARGET_RECTS = {
    # 0: 홈 화면 "매장에서 먹고 갈게요" 대형 버튼 위치
    0: {
        "name": "dine_in_button",
        "label": "매장에서 먹고 갈게요",
        "rect": {"x": 252, "y": 345, "w": 520, "h": 84}
    },

    # 카테고리 탭 (menu-area 내부의 18px 패딩 및 5등분 grid-template-columns 계산값)
    32: {
        "name": "coffee_category_button",
        "label": "Coffee 카테고리",
        "rect": {"x": 18, "y": 90, "w": 126, "h": 56}
    },
    64: {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 154, "y": 90, "w": 126, "h": 56}
    },
    96: {
        "name": "ade_juice_category_button",
        "label": "Ade/Juice 카테고리",
        "rect": {"x": 290, "y": 90, "w": 126, "h": 56}
    },
    128: {
        "name": "beverage_category_button",
        "label": "Beverage 카테고리",
        "rect": {"x": 426, "y": 90, "w": 126, "h": 56}
    },
    160: {
        "name": "blended_category_button",
        "label": "Blended 카테고리",
        "rect": {"x": 562, "y": 90, "w": 126, "h": 56}
    },
    "tea_category_button": {
        "name": "tea_category_button",
        "label": "Tea 카테고리",
        "rect": {"x": 154, "y": 90, "w": 126, "h": 56}
    },

    # 복숭아 아이스티 등 카테고리 내 첫 번째 메뉴 아이템의 물리적 영역
    260: {
        "name": "peach_ice_tea_button",
        "label": "복숭아아이스티",
        "rect": {"x": 36, "y": 164, "w": 196, "h": 230}
    },
    "peach_ice_tea_button": {
        "name": "peach_ice_tea_button",
        "label": "복숭아아이스티",
        "rect": {"x": 36, "y": 164, "w": 196, "h": 230}
    },

    # 옵션 세부 조절 팝업 모달 하단의 버튼 타겟 정보
    "less_sweet_button": {
        "name": "less_sweet_button",
        "label": "덜 달게",
        "rect": {"x": 304, "y": 440, "w": 150, "h": 48}
    },
    "more_ice_button": {
        "name": "more_ice_button",
        "label": "얼음 많이",
        "rect": {"x": 304, "y": 506, "w": 150, "h": 48}
    },

    # 옵션 모달창 우하단 초록색 "담기" 버튼 절대 위치 매핑 가드
    "add_to_cart_button": {
        "name": "add_to_cart_button",
        "label": "담기",
        "rect": {"x": 518, "y": 520, "w": 230, "h": 64}
    },
    256: {
        "name": "add_to_cart_button",
        "label": "담기",
        "rect": {"x": 518, "y": 520, "w": 230, "h": 64}
    },

    # 메뉴 메인화면 우측 하단 고정 형태의 오더 패널 결제 버튼
    "order_payment_button": {
        "name": "order_payment_button",
        "label": "결제하기",
        "rect": {"x": 705, "y": 630, "w": 297, "h": 68}
    },

    # 1~30번 메뉴 전체 동적 대응: 최종 장바구니 주문 확인창의 "결제하기" 버튼 픽셀 위치 고정
    536: {
        "name": "receipt_payment_button",
        "label": "주문 확인 결제하기",
        "rect": {"x": 526, "y": 629, "w": 470, "h": 64}
    },
    "receipt_payment_button": {
        "name": "receipt_payment_button",
        "label": "주문 확인 결제하기",
        "rect": {"x": 526, "y": 629, "w": 470, "h": 64}
    },

    # 768: 결제 수단 선택 화면 레이아웃 상의 "신용카드" 대형 버튼
    768: {
        "name": "card_payment_button",
        "label": "카드 결제",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84}
    },
    "card_payment_button": {
        "name": "card_payment_button",
        "label": "카드 결제",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84}
    }
}


def rect_center(rect):
    return {
        "x": rect["x"] + rect["w"] / 2.0,
        "y": rect["y"] + rect["h"] / 2.0
    }


def estimate_pixel_to_meter(rvec_ref, tvec_ref, rvec_state=None, tvec_state=None, marker_length=0.05):
    """
    [물리 공간 원근 변환 방어 로직]
    디바이스 창 확대/축소 시 일어나는 픽셀 비틀림 오차를 완전히 잡아내며,
    64px 마커 크기를 기반으로 정밀 단위 미터 비율을 실시간 추정 및 고정 백업 처리합니다.
    """
    # 64픽셀이 실제 마커 눈금 크기(5cm)라는 절대 기준 팩터 물리 비율 (약 0.00078125)
    absolute_scale = marker_length / MARKER_SIZE_PX
    
    if rvec_state is None or tvec_state is None:
        return absolute_scale, absolute_scale

    try:
        # 카메라 3D 센서 공간 상에서 두 마커 간의 실제 미터법 물리 거리 연산
        dist_m = np.linalg.norm(tvec_ref - tvec_state)
        
        # 실제 웹 브라우저 CSS 구조의 듀얼 마커 중심 간 정적 오프셋 픽셀 거리 역산
        # dx = 988 - 36 = 952, dy = 684 - 36 = 648
        dist_px = np.sqrt((STATE_MARKER_CENTER[0] - POSE_MARKER_CENTER[0])**2 + 
                          (STATE_MARKER_CENTER[1] - POSE_MARKER_CENTER[1])**2)

        if dist_px > 0:
            dynamic_scale = dist_m / dist_px
            # 카메라 각도 왜곡 범위 필터링 가드 적용
            if absolute_scale * 0.7 < dynamic_scale < absolute_scale * 1.3:
                return dynamic_scale, dynamic_scale
    except Exception:
        pass

    return absolute_scale, absolute_scale


def transform_pixel_to_world(point_px, rvec_ref, tvec_ref, scale_x, scale_y):
    """
    로드리게스 변환 행렬을 이용해 2D 스크린 좌표계를 유니티 AR 3D 월드 매트릭스 좌표로 정밀 평면 투영합니다.
    """
    R_ref, _ = cv2.Rodrigues(rvec_ref)

    # 769번 기준 마커 중심점(36, 36)으로부터 목표 좌표까지의 유격(픽셀 거리) 역산
    dx_px = point_px["x"] - POSE_MARKER_CENTER[0]
    dy_px = point_px["y"] - POSE_MARKER_CENTER[1]

    # 회전 보정을 위한 로컬 카메라 평면 미터 벡터 조립 (X: 우측, Y: 하단반전, Z: 전방 수렴)
    local = np.array([
        [dx_px * scale_x],
        [dy_px * scale_y],
        [0.0]
    ], dtype=np.float32)

    # 레퍼런스 포즈 변환 행렬 합산 후 3차원 공간 좌표계 매핑
    world = R_ref @ local + tvec_ref.reshape(3, 1)

    return {
        "x": float(world[0][0]),
        "y": float(world[1][0]),
        "z": float(world[2][0])
    }


def rect_size_to_world_size(rect, scale_x, scale_y):
    return {
        "w": float(rect["w"] * scale_x),
        "h": float(rect["h"] * scale_y)
    }


def build_target_payload(rvec_ref, tvec_ref, target, rvec_state=None, tvec_state=None, marker_length=0.05):
    if target is None or "rect" not in target:
        return None
        
    rect = target["rect"]
    center = rect_center(rect)

    # 정밀 왜곡 제거 스케일 값 획득
    scale_x, scale_y = estimate_pixel_to_meter(
        rvec_ref,
        tvec_ref,
        rvec_state,
        tvec_state,
        marker_length
    )

    # 월드 공간상의 3D 타겟 바운딩 센터 연산
    world_pos = transform_pixel_to_world(center, rvec_ref, tvec_ref, scale_x, scale_y)

    return {
<<<<<<< Updated upstream
        "name": target.get("name", "unknown_target"),
        "label": target.get("label", ""),
        "rect_px": rect,
        "center_px": center,
        "world_position": world_position,
        "world_size": world_size
    }
=======
        "world_position": world_pos,
        "world_size": rect_size_to_world_size(rect, scale_x, scale_y),
        "label": target.get("label", "Target")
    }
>>>>>>> Stashed changes
