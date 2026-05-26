import cv2
import numpy as np
import sys
import os

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# config에서 STATE_MAP import
from config import STATE_MAP


OUTPUT_DIR = "../data/state_markers"
CELL_SIZE = 80
MARGIN = 20


def id_to_bits(marker_id):
    return format(marker_id, "010b")


def bits_to_grid(bits):
    return [
        list(bits[:5]),
        list(bits[5:])
    ]


def draw_marker(grid):
    rows = 2
    cols = 5

    BORDER = 2  # 테두리 두께 (픽셀)

    height = rows * CELL_SIZE + 2 * MARGIN
    width = cols * CELL_SIZE + 2 * MARGIN

    img = np.ones((height, width), dtype=np.uint8) * 255

    for r in range(rows):
        for c in range(cols):
            bit = int(grid[r][c])

            x1 = MARGIN + c * CELL_SIZE
            y1 = MARGIN + r * CELL_SIZE
            x2 = x1 + CELL_SIZE
            y2 = y1 + CELL_SIZE

            # 내부 색
            color = 0 if bit == 1 else 255
            cv2.rectangle(img, (x1, y1), (x2, y2), color, -1)

            # 테두리 추가 (항상 검정)
            cv2.rectangle(
                img,
                (x1, y1),
                (x2, y2),
                0,          # black border
                BORDER
            )

            cv2.rectangle(
                img,
                (MARGIN//2, MARGIN//2),
                (width - MARGIN//2, height - MARGIN//2),
                0,
                3
            )

    return img


def save_marker(marker_id):
    bits = id_to_bits(marker_id)
    grid = bits_to_grid(bits)

    img = draw_marker(grid)

    filename = f"{OUTPUT_DIR}/marker_{marker_id}.png"
    cv2.imwrite(filename, img)

    print(f"[SAVE] {filename} → {bits}")


def generate_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for marker_id in STATE_MAP.keys():
        save_marker(marker_id)


if __name__ == "__main__":
    generate_all()
