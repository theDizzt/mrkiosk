from dataclasses import dataclass
from typing import List, Optional, Tuple

import cv2
import numpy as np


@dataclass
class DetectedMarker:
    marker_id: int
    corners: np.ndarray

    @property
    def center(self) -> Tuple[float, float]:
        pts = self.corners.reshape(4, 2)
        center = pts.mean(axis=0)
        return float(center[0]), float(center[1])

    @property
    def area(self) -> float:
        pts = self.corners.reshape(4, 2).astype(np.float32)
        return float(cv2.contourArea(pts))


class DualArucoDetector:
    def __init__(
        self,
        reference_id: int,
        camera_matrix: np.ndarray,
        dist_coeffs: np.ndarray,
        marker_length_m: float,
        dictionary_name: str = "DICT_5X5_1000",
    ):
        self.reference_id = reference_id
        self.camera_matrix = camera_matrix
        self.dist_coeffs = dist_coeffs
        self.marker_length_m = marker_length_m

        self.aruco_dict = self._load_dictionary(dictionary_name)
        self.detector_params = cv2.aruco.DetectorParameters()

        self.use_new_api = hasattr(cv2.aruco, "ArucoDetector")

        if self.use_new_api:
            self.detector = cv2.aruco.ArucoDetector(
                self.aruco_dict,
                self.detector_params,
            )
        else:
            self.detector = None

    def _load_dictionary(self, dictionary_name: str):
        if not hasattr(cv2.aruco, dictionary_name):
            raise ValueError(f"Unknown ArUco dictionary: {dictionary_name}")

        dictionary_value = getattr(cv2.aruco, dictionary_name)
        return cv2.aruco.getPredefinedDictionary(dictionary_value)

    def detect(self, frame: np.ndarray) -> List[DetectedMarker]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.use_new_api:
            corners, ids, _ = self.detector.detectMarkers(gray)
        else:
            corners, ids, _ = cv2.aruco.detectMarkers(
                gray,
                self.aruco_dict,
                parameters=self.detector_params,
            )

        if ids is None or len(ids) == 0:
            return []

        markers: List[DetectedMarker] = []

        flat_ids = ids.flatten()

        for marker_id, marker_corners in zip(flat_ids, corners):
            markers.append(
                DetectedMarker(
                    marker_id=int(marker_id),
                    corners=marker_corners.reshape(4, 2),
                )
            )

        return markers

    def split_reference_and_state(
        self,
        markers: List[DetectedMarker],
    ) -> Tuple[Optional[DetectedMarker], Optional[DetectedMarker], List[DetectedMarker]]:

        reference_marker = None
        state_candidates: List[DetectedMarker] = []

        for marker in markers:
            if marker.marker_id == self.reference_id:
                reference_marker = marker
            else:
                state_candidates.append(marker)

        # 상태 ID 정의 전이므로,
        # Reference가 아닌 마커 중 화면에서 가장 크게 보이는 마커를 State 후보로 사용한다.
        state_marker = None
        if state_candidates:
            state_marker = max(state_candidates, key=lambda marker: marker.area)

        return reference_marker, state_marker, state_candidates

    def estimate_pose(self, marker: DetectedMarker) -> Optional[dict]:
        half = self.marker_length_m / 2.0

        object_points = np.array(
            [
                [-half, half, 0.0],
                [half, half, 0.0],
                [half, -half, 0.0],
                [-half, -half, 0.0],
            ],
            dtype=np.float32,
        )

        image_points = marker.corners.astype(np.float32)

        success, rvec, tvec = cv2.solvePnP(
            object_points,
            image_points,
            self.camera_matrix,
            self.dist_coeffs,
            flags=cv2.SOLVEPNP_IPPE_SQUARE,
        )

        if not success:
            return None

        return {
            "rvec": rvec.reshape(3).astype(float).tolist(),
            "tvec": tvec.reshape(3).astype(float).tolist(),
            "marker_center": list(marker.center),
            "marker_area": marker.area,
        }

    def process(self, frame: np.ndarray) -> dict:
        markers = self.detect(frame)

        reference_marker, state_marker, state_candidates = self.split_reference_and_state(
            markers
        )

        reference_pose = None

        if reference_marker is not None:
            reference_pose = self.estimate_pose(reference_marker)

        state_marker_id = state_marker.marker_id if state_marker is not None else None

        return {
            "markers": markers,
            "reference_marker": reference_marker,
            "state_marker": state_marker,
            "state_candidates": state_candidates,
            "reference_pose": reference_pose,
            "state_marker_id": state_marker_id,
        }

    def draw_debug(self, frame: np.ndarray, result: dict) -> np.ndarray:
        output = frame.copy()

        markers: List[DetectedMarker] = result["markers"]

        for marker in markers:
            pts = marker.corners.reshape(4, 2).astype(int)

            if marker.marker_id == self.reference_id:
                color = (0, 255, 0)
                label = f"REF {marker.marker_id}"
            else:
                color = (255, 180, 0)
                label = f"STATE? {marker.marker_id}"

            cv2.polylines(output, [pts], True, color, 2)

            cx, cy = marker.center

            cv2.putText(
                output,
                label,
                (int(cx), int(cy)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
                cv2.LINE_AA,
            )

        reference_pose = result["reference_pose"]

        if reference_pose is not None:
            rvec = np.array(reference_pose["rvec"], dtype=np.float32).reshape(3, 1)
            tvec = np.array(reference_pose["tvec"], dtype=np.float32).reshape(3, 1)

            cv2.drawFrameAxes(
                output,
                self.camera_matrix,
                self.dist_coeffs,
                rvec,
                tvec,
                self.marker_length_m * 0.7,
            )

        return output
