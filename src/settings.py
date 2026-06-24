WIDTH, HEIGHT = 1600, 900
FPS = 60
TITLE = "WorldSpot"

MAX_SCORE = 5000
ROUNDS_PER_GAME = 5
SUCCESS_KM = 50
SUCCESS_SCORE = 4500
# GeoGuessr exponential decay constant (meters)
SCORE_DECAY_M = 1492.07

PANORAMA_RECT = (0, 0, WIDTH, HEIGHT)

# Mini-map — bottom-right above GUESS button (GeoGuessr layout)
MAP_W, MAP_H = 400, 280
MAP_MARGIN_X, MAP_MARGIN_BOTTOM = 32, 108
MAP_RECT = (WIDTH - MAP_W - MAP_MARGIN_X, HEIGHT - MAP_H - MAP_MARGIN_BOTTOM, MAP_W, MAP_H)

# Expanded map modal
MAP_EXPANDED_W, MAP_EXPANDED_H = 1200, 720

# Results — full-screen map
RESULT_MAP_RECT = (0, 56, WIDTH, HEIGHT - 120)

PANEL_RADIUS = 8

COLORS = {
    "bg": (16, 18, 22),
    "bg_dark": (10, 12, 16),
    "panel": (22, 26, 32),
    "accent": (16, 172, 132),
    "accent_dark": (13, 140, 108),
    "accent_light": (52, 211, 163),
    "text": (255, 255, 255),
    "text_dim": (160, 170, 185),
    "guess": (234, 67, 53),
    "guess_pin": (234, 67, 53),
    "truth": (52, 168, 83),
    "line": (255, 193, 7),
    "map_border": (255, 255, 255),
    "btn_guess": (16, 172, 132),
    "btn_guess_hover": (20, 195, 150),
    "btn_disabled": (74, 85, 104),
    "hud_bar": (10, 12, 16),
    "muted": (140, 150, 165),
    "accent_hot": (20, 195, 150),
    "button_guess": (16, 172, 132),
    "button_guess_hover": (20, 195, 150),
    "button_guess_disabled": (74, 85, 104),
    "button_guess_glow": (16, 172, 132),
    "ocean": (180, 210, 230),
    "land": (200, 220, 190),
    "panel_border": (55, 60, 70),
    "brand": (121, 85, 242),
}
