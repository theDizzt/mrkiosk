# vision/generate_aruco_marker.py
# python vision/generate_aruco_marker.py --id 10 --name state_MAIN_MENU
# python vision/generate_aruco_marker.py --id 원하는_ID --name state

import argparse
from pathlib import Path

import cv2
import numpy as np


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate a single ArUco marker image"
    )

    parser.add_argument(
        "--id",
        type=int,
        required=True,
        help="ArUco marker ID",
    )

    parser.add_argument(
        "--dict",
        type=str,
        default="DICT_5X5_1000",
        help="OpenCV ArUco dictionary name",
    )

    parser.add_argument(
        "--size",
        type=int,
        default=400,
        help="Marker image size in pixels",
    )

    parser.add_argument(
        "--margin",
        type=int,
        default=80,
        help="White margin size in pixels",
    )

    parser.add_argument(
        "--name",
        type=str,
        default="marker",
        help="Output name label",
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default="vision/markers",
        help="Output directory",
    )

    return parser.parse_args()


def load_dictionary(dictionary_name: str):
    if not hasattr(cv2.aruco, dictionary_name):
        raise ValueError(f"Unknown ArUco dictionary: {dictionary_name}")

    dictionary_value = getattr(cv2.aruco, dictionary_name)
    return cv2.aruco.getPredefinedDictionary(dictionary_value)


def generate_marker(dictionary, marker_id: int, size: int):
    marker = np.zeros((size, size), dtype=np.uint8)

    if hasattr(cv2.aruco, "generateImageMarker"):
        cv2.aruco.generateImageMarker(dictionary, marker_id, size, marker, 1)
    else:
        cv2.aruco.drawMarker(dictionary, marker_id, size, marker, 1)

    return marker


def add_white_margin(marker, margin: int):
    h, w = marker.shape[:2]

    canvas = np.full(
        (h + margin * 2, w + margin * 2),
        255,
        dtype=np.uint8,
    )

    canvas[margin : margin + h, margin : margin + w] = marker

    return canvas


def main():
    args = parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dictionary = load_dictionary(args.dict)
    marker = generate_marker(dictionary, args.id, args.size)
    marker_with_margin = add_white_margin(marker, args.margin)

    output_path = output_dir / f"{args.name}_id_{args.id}.png"

    cv2.imwrite(str(output_path), marker_with_margin)

    print(f"[INFO] Marker saved: {output_path}")


if __name__ == "__main__":
    main()
