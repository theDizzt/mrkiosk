import cv2
import os

# 저장 폴더
output_dir = "kiosk_aruco_markers"
os.makedirs(output_dir, exist_ok=True)

# ArUco Dictionary: 4x4, 최대 1000개 ID 지원
aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)

# 마커 이미지 크기
marker_size = 256  # px

for marker_id in range(0, 770): # 0 - 769번
    marker_img = cv2.aruco.generateImageMarker(
        aruco_dict,
        marker_id,
        marker_size
    )

    filename = f"aruco_id_{marker_id}.png"
    filepath = os.path.join(output_dir, filename)

    cv2.imwrite(filepath, marker_img)

print("생성 완료!")
print(f"저장 위치: {output_dir}")
