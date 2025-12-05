import os

os.makedirs("data/output", exist_ok=True)

LOG_FILE_PATH = r"./data/logs/"
USER_FILE_PATH = r"./data/output/user_info.json"
USER_FINAL_DATA_PATH = r"./data/output/final.json"
USER_FINAL_MIN_VIB_PATH = r"./data/output/min_vib.json"

NUM_VIBRATION = 5  # Number of vibration motors
SAMPLES_BEFORE_REST = 100
REST_DURATION_SECONDS = 100
MINIMUM_VIB_TIME = 0.1

arduino_config = {
    "port": "COM10",
    "baudrate": 9600,
}

GRAPH_SIZE = (1100, 600)
radius = GRAPH_SIZE[1] * 0.90
offset = GRAPH_SIZE[1] * 0.05 / 2

# Window 1 configs
window_1_layout_config = {
    "font_large": ("Arial", 14),
    "font_medium": ("Arial", 12),
    "font_small": ("Arial", 10),
    "text_size": 40,
}
# Minimum vibration configuration
min_vibration_layout_config = {
    "font_large": ("Arial", 18),
    "font_medium": ("Arial", 16),
    "font_small": ("Arial", 14),
    "graph_size": GRAPH_SIZE,
    "radius": radius,
    "offset": offset,
    "btn_color": "#2C3E50",
}

# Window 2 configs
window_2_layout_config = {
    "font_large": ("Arial", 18),
    "font_medium": ("Arial", 16),
    "font_small": ("Arial", 14),
    "graph_size": GRAPH_SIZE,
    "radius": radius,
    "offset": offset,
    "btn_color": "#2C3E50",
}
# Window 3 configs
window_3_layout_config = {
    "font_large": ("Arial", 18),
    "font_medium": ("Arial", 16),
    "font_small": ("Arial", 14),
    "graph_size": GRAPH_SIZE,
    "radius": radius,
    "offset": offset,
    "btn_color": "#2C3E50",
}
