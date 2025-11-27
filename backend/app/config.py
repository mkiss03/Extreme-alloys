# backend/app/config.py
"""
Configuration settings for the Extreme Alloys API
"""

import os
import logging
from dotenv import load_dotenv

load_dotenv()

# Environment settings
ENV = os.getenv("ENV", "development")
DEBUG = ENV == "development"

# API settings
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
API_PREFIX = "/api/v1"

# Model settings
MODEL_PATH = os.getenv("MODEL_PATH", "./models/saved")
DEVICE = os.getenv("DEVICE", "cpu")  # 'cpu' or 'cuda'

# Logging configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)
