import os

# Model configuration
MODEL_ID = "stabilityai/stable-video-diffusion-img2vid-xt"
TORCH_DTYPE = "float16"
VARIANT = "fp16"

# Cache directories
CACHE_DIR = os.environ.get("HF_HOME", "/app/model_cache")
TEMP_DIR = "/tmp"

# Default generation parameters
DEFAULT_NUM_FRAMES = 25
DEFAULT_NUM_INFERENCE_STEPS = 25
DEFAULT_FPS = 6
DEFAULT_MOTION_BUCKET_ID = 127
DEFAULT_NOISE_AUG_STRENGTH = 0.02

# Image processing
TARGET_WIDTH = 1024
TARGET_HEIGHT = 576

# Memory management
ENABLE_MEMORY_EFFICIENT_ATTENTION = True
ENABLE_CPU_OFFLOAD = False  # Set to True if running on limited GPU memory

# Validation limits
MAX_NUM_FRAMES = 50
MIN_NUM_FRAMES = 14
MAX_INFERENCE_STEPS = 50
MIN_INFERENCE_STEPS = 1
MAX_FPS = 30
MIN_FPS = 1