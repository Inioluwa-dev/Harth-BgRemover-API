"""
Configuration settings for the Background Removal API
"""

# Model paths
MODEL_PATHS = {
    "general": "isnet-general-use",
    "human": "u2net_human_seg"
}

# API settings
API_TITLE = "Background Removal API"
API_DESCRIPTION = "AI-powered background removal with auto human detection"
API_VERSION = "1.0.0"

# CORS settings
CORS_ORIGINS = ["*"]  # In production, specify actual origins
CORS_CREDENTIALS = True
CORS_METHODS = ["*"]
CORS_HEADERS = ["*"]

# MediaPipe settings
MEDIAPIPE_CONFIDENCE = 0.1  # Very low threshold for fastest detection

# Image processing settings
DEFAULT_POSITION = "center"
DEFAULT_SCALE = "cover"
DEFAULT_AUTO_DETECT = False  # Use fast general model by default
