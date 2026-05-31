# vision/aruco_runtime.py

# vision/aruco_runtime.py

import json
import os
import time
from pathlib import Path


class RuntimeWriter:
    def __init__(self, output_path):
        self.output_path = Path(output_path)

    def write(self, data):
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        temp_path = self.output_path.with_suffix(".tmp")

        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        for _ in range(5):
            try:
                os.replace(temp_path, self.output_path)
                break
            except PermissionError:
                time.sleep(0.02)
        else:
            print(f"[WARN] Failed to replace runtime state file: {self.output_path}")


class RuntimeStabilizer:
    def __init__(self, reference_hold_frames=5, state_hold_frames=10):
        self.reference_hold_frames = reference_hold_frames
        self.state_hold_frames = state_hold_frames

        self.last_reference_pose = None
        self.last_state_marker_id = None

        self.reference_missing_count = 0
        self.state_missing_count = 0

    def update(self, reference_pose, state_marker_id, reference_id):
        now = time.time()

        if reference_pose is not None:
            self.last_reference_pose = reference_pose
            self.reference_missing_count = 0
            reference_status = "detected"
        else:
            self.reference_missing_count += 1

            if (
                self.last_reference_pose is not None
                and self.reference_missing_count <= self.reference_hold_frames
            ):
                reference_pose = self.last_reference_pose
                reference_status = "held"
            else:
                reference_pose = None
                reference_status = "lost"

        if state_marker_id is not None:
            self.last_state_marker_id = state_marker_id
            self.state_missing_count = 0
            state_status = "detected"
        else:
            self.state_missing_count += 1

            if (
                self.last_state_marker_id is not None
                and self.state_missing_count <= self.state_hold_frames
            ):
                state_marker_id = self.last_state_marker_id
                state_status = "held"
            else:
                state_marker_id = None
                state_status = "lost"

        valid = reference_pose is not None

        return {
            "valid": valid,
            "timestamp": now,
            "tracking": {
                "reference_status": reference_status,
                "state_status": state_status,
                "reference_missing_count": self.reference_missing_count,
                "state_missing_count": self.state_missing_count,
            },
            "reference": {
                "id": reference_id,
                "detected": reference_status == "detected",
                "pose": reference_pose,
            },
            "state_marker": {
                "detected": state_status == "detected",
                "id": state_marker_id if state_marker_id is not None else -1,
            },
            "fsm": {
                "state": "UNMAPPED",
                "label": "매핑되지 않은 상태",
                "state_id": state_marker_id if state_marker_id is not None else -1,
                "target": None,
            },
        }
