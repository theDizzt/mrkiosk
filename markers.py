import cv2
import os

# 저장 폴더
output_dir = "markers"
os.makedirs(output_dir, exist_ok=True)

# ArUco Dictionary
aruco_dict = cv2.aruco.getPredefinedDictionary(
    cv2.aruco.DICT_5X5_1000
)

# 마커 이미지 크기(px)
marker_size = 300

# 0 ~ 768 생성
for marker_id in range(769):

    marker_img = cv2.aruco.generateImageMarker(
        aruco_dict,
        marker_id,
        marker_size
    )

    save_path = os.path.join(
        output_dir,
        f"marker_{marker_id}.png"
    )

    cv2.imwrite(save_path, marker_img)

print("0~768 ArUco 마커 생성 완료")