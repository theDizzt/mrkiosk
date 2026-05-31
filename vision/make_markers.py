import os
import cv2
import numpy as np

def generate_and_save_aruco(marker_id, output_dir, image_size=400):
    """
    지정한 ArUco ID에 해당하는 마커를 생성하여 파일로 물리 저장
    """
    aruco_dict = cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_1000)
    marker_image = cv2.aruco.generateImageMarker(aruco_dict, marker_id, image_size)
    
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, f"aruco_{marker_id:04d}.png")
    cv2.imwrite(file_path, marker_image)

def main():
    print("Starting full ArUco marker generation based on specifications...\n")
    output_folder = "C:/Users/dhkim/mrkiosk/vision/kiosk_aruco_markers"

    # 1. Phase 00: 초기 화면 및 카테고리 고정 마커 (0, 32, 64, 96, 128, 160)
    print("Generating Phase 00 base markers...")
    phase_00_ids = [0, 32, 64, 96, 128, 160]
    for m_id in phase_00_ids:
        generate_and_save_aruco(m_id, output_dir=output_folder)

    # 2. Phase 01: 메뉴 상세 옵션 가변 마커 (192개 전 조합 완전 생성)
    print("Generating Phase 01 all option combination markers (192 total)...")
    # MenuHash (0~5), Temperature (0~2), Sugar (0~1), Ice (0~1)
    for menu_hash in range(6):
        for temp in range(3):
            for sugar in range(2):
                for ice in range(2):
                    m_id = 256 + (menu_hash * 32) + (temp * 8) + (sugar * 4) + (ice * 2)
                    generate_and_save_aruco(m_id, output_dir=output_folder)

    # 3. Phase 10: 장바구니 검증 마커 (512번부터 4단위로 매칭되는 범위 생성)
    print("Generating Phase 10 cart validation markers...")
    # 주요 메뉴 인덱스 범위에 맞춰 일괄 생성 (0번부터 15번 메뉴 가정 시)
    for menu_idx in range(16):
        m_id = 512 + (menu_idx * 4)
        generate_and_save_aruco(m_id, output_dir=output_folder)

    # 4. Phase 11: 최종 결제 안내 고정 마커
    print("Generating Phase 11 final payment marker...")
    generate_and_save_aruco(768, output_dir=output_folder)

    print(f"\nAll required combination markers are completely saved in '{output_folder}'")

if __name__ == "__main__":
    main()