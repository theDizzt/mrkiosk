import cv2
from pathlib import Path

SAVE_DIR = Path("calibration/images")
SAVE_DIR.mkdir(parents=True, exist_ok=True)

CAMERA_INDEX = 0


def main():
    cap = cv2.VideoCapture(CAMERA_INDEX)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    print("Press SPACE to save image.")
    print("Press ESC to quit.")

    image_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Failed to read frame.")
            break

        display = frame.copy()
        cv2.putText(
            display,
            f"Saved Images: {image_count}",
            (20, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (0, 255, 0),
            2
        )

        cv2.imshow("Calibration Capture", display)

        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            break
        elif key == 32:  # SPACE
            file_path = SAVE_DIR / f"calib_{image_count:02d}.jpg"
            cv2.imwrite(str(file_path), frame)
            print(f"Saved: {file_path}")
            image_count += 1

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
