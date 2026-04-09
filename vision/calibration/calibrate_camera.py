import cv2
import numpy as np
from pathlib import Path

# 체스보드 내부 코너 개수
CHESSBOARD_SIZE = (9, 6)

# 한 칸의 실제 크기 (예: 0.025m = 2.5cm)
SQUARE_SIZE = 0.025

IMAGE_DIR = Path("calibration/images")
OUTPUT_CAMERA_MATRIX = Path("calibration/camera_matrix.npy")
OUTPUT_DIST_COEFFS = Path("calibration/dist_coeffs.npy")


def main():
    image_paths = sorted(IMAGE_DIR.glob("*.jpg"))

    if not image_paths:
        print("No calibration images found.")
        return

    # 3D object points 준비
    objp = np.zeros((CHESSBOARD_SIZE[0] * CHESSBOARD_SIZE[1], 3), np.float32)
    objp[:, :2] = np.mgrid[0:CHESSBOARD_SIZE[0], 0:CHESSBOARD_SIZE[1]].T.reshape(-1, 2)
    objp *= SQUARE_SIZE

    objpoints = []
    imgpoints = []

    image_size = None

    # 코너 정밀화 조건
    criteria = (
        cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER,
        30,
        0.001
    )

    success_count = 0

    for image_path in image_paths:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Failed to load: {image_path}")
            continue

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image_size = gray.shape[::-1]

        found, corners = cv2.findChessboardCorners(gray, CHESSBOARD_SIZE, None)

        if found:
            refined_corners = cv2.cornerSubPix(
                gray,
                corners,
                (11, 11),
                (-1, -1),
                criteria
            )

            objpoints.append(objp)
            imgpoints.append(refined_corners)
            success_count += 1

            preview = image.copy()
            cv2.drawChessboardCorners(preview, CHESSBOARD_SIZE, refined_corners, found)
            cv2.imshow("Detected Corners", preview)
            cv2.waitKey(300)

            print(f"[OK] Corners detected: {image_path.name}")
        else:
            print(f"[FAIL] Corners not detected: {image_path.name}")

    cv2.destroyAllWindows()

    if success_count < 5:
        print("Not enough valid images for calibration.")
        return

    ret, camera_matrix, dist_coeffs, rvecs, tvecs = cv2.calibrateCamera(
        objpoints,
        imgpoints,
        image_size,
        None,
        None
    )

    np.save(str(OUTPUT_CAMERA_MATRIX), camera_matrix)
    np.save(str(OUTPUT_DIST_COEFFS), dist_coeffs)

    print("\nCalibration complete.")
    print(f"Reprojection Error: {ret}")
    print("Camera Matrix:")
    print(camera_matrix)
    print("Distortion Coefficients:")
    print(dist_coeffs)

    print(f"\nSaved: {OUTPUT_CAMERA_MATRIX}")
    print(f"Saved: {OUTPUT_DIST_COEFFS}")


if __name__ == "__main__":
    main()
