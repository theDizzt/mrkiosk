# vision/kiosk_geometry.py

import cv2
import numpy as np

from kiosk_guide_model import (
    POSE_MARKER_CENTER,
    STATE_MARKER_CENTER,
    MARKER_SIZE_PX,
)


KIOSK_WIDTH = 1024
KIOSK_HEIGHT = 720

POSE_MARKER_CENTER = (36, 36)
STATE_MARKER_CENTER = (988, 684)
MARKER_SIZE_PX = 64

TARGET_RECTS = {
    "tea_category_button": {
        "label": "Tea 카테고리",
        "rect": {"x": 164, "y": 90, "w": 122, "h": 56},
    },
    "peach_ice_tea_button": {
        "label": "복숭아아이스티",
        "rect": {"x": 36, "y": 164, "w": 196, "h": 230},
    },
    "less_sweet_button": {
        "label": "덜 달게",
        "rect": {"x": 304, "y": 440, "w": 150, "h": 48},
    },
    "more_ice_button": {
        "label": "얼음 많이",
        "rect": {"x": 304, "y": 525, "w": 150, "h": 48},
    },
    "add_to_cart_button": {
        "label": "담기",
        "rect": {"x": 528, "y": 615, "w": 220, "h": 64},
    },
    "receipt_payment_button": {
        "label": "결제하기",
        "rect": {"x": 520, "y": 630, "w": 460, "h": 64},
    },
    "card_payment_button": {
        "label": "카드",
        "rect": {"x": 252, "y": 310, "w": 520, "h": 84},
    },
}


def rect_center(rect):
    return {
        "x": rect["x"] + rect["w"] / 2,
        "y": rect["y"] + rect["h"] / 2
    }


def estimate_pixel_to_meter(rvec_ref, tvec_ref, rvec_state=None, tvec_state=None, marker_length=0.05):
    """
    기본값: 64px 마커가 실제 marker_length(m)에 대응한다고 가정.
    우하단 state marker pose도 있으면 보정 가능.
    """
    default_scale = marker_length / MARKER_SIZE_PX

    if rvec_state is None or tvec_state is None:
        return default_scale, default_scale

    R_ref, _ = cv2.Rodrigues(rvec_ref)

    x_axis = R_ref[:, 0].reshape(3)
    y_axis = R_ref[:, 1].reshape(3)

    delta_world = (tvec_state.reshape(3) - tvec_ref.reshape(3))

    dx_px = STATE_MARKER_CENTER[0] - POSE_MARKER_CENTER[0]
    dy_px = STATE_MARKER_CENTER[1] - POSE_MARKER_CENTER[1]

    scale_x = abs(np.dot(delta_world, x_axis)) / abs(dx_px) if dx_px != 0 else default_scale
    scale_y = abs(np.dot(delta_world, y_axis)) / abs(dy_px) if dy_px != 0 else default_scale

    if scale_x <= 0 or scale_x > 0.01:
        scale_x = default_scale

    if scale_y <= 0 or scale_y > 0.01:
        scale_y = default_scale

    return scale_x, scale_y


def kiosk_pixel_to_world(rvec_ref, tvec_ref, point_px, scale_x, scale_y):
    """
    키오스크 내부 픽셀 좌표를 769번 ArUco 기준 world_position으로 변환.
    """
    R_ref, _ = cv2.Rodrigues(rvec_ref)

    dx_px = point_px["x"] - POSE_MARKER_CENTER[0]
    dy_px = point_px["y"] - POSE_MARKER_CENTER[1]

    local = np.array([
        [dx_px * scale_x],
        [dy_px * scale_y],
        [0.0]
    ], dtype=np.float32)

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
    rect = target["rect"]
    center = rect_center(rect)

    scale_x, scale_y = estimate_pixel_to_meter(
        rvec_ref,
        tvec_ref,
        rvec_state,
        tvec_state,
        marker_length
    )

    world_position = kiosk_pixel_to_world(
        rvec_ref,
        tvec_ref,
        center,
        scale_x,
        scale_y
    )

    world_size = rect_size_to_world_size(rect, scale_x, scale_y)

    return {
        "name": target["name"],
        "label": target["label"],
        "rect_px": rect,
        "center_px": center,
        "world_position": world_position,
        "world_size": world_size
    }
