STATE_MAP = {
    # 000~099: System
    0: "IDLE",
    1: "LISTENING",

    # 100~199: Category
    100: "CATEGORY_SELECT",

    # 200~399: Item
    200: "ITEM_SELECT",

    # 400~499: Option
    400: "OPTION_SELECT",

    # 600~699: Payment
    600: "PAYMENT_SELECT",

    # 700~799: Complete
    700: "CONFIRM",

    # 800~899: Recovery
    800: "ERROR_RECOVERY",

    # 900~1023: Exception
    900: "FAIL_SAFE"
}

CAMERA_INDEX = 0
MARKER_LENGTH = 0.05  # 5 cm

CALIBRATION_DIR = "calibration"
CAMERA_MATRIX_FILE = "calibration/camera_matrix.npy"
DIST_COEFFS_FILE = "calibration/dist_coeffs.npy"
