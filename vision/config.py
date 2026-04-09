STATE_MAP = {
    0: "IDLE",
    1: "LISTENING",
    10: "MENU_GUIDE",
    20: "OPTION_GUIDE",
    30: "PAYMENT_GUIDE",
    40: "CONFIRM",
    90: "ERROR_RECOVERY",
    99: "FAIL_SAFE"
}

CAMERA_INDEX = 0
MARKER_LENGTH = 0.05  # 5 cm

CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"