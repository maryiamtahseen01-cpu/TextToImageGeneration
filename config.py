# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ---------------- SECURITY ----------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-secret")

    # ---------------- DATABASE ----------------
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/imaginify_db")

    # ---------------- AI IMAGE API (IMAGINE.ART / VYRO) ----------------
    AI_API_KEY = os.getenv("AI_API_KEY")
    AI_API_URL = os.getenv("AI_API_URL")
    AI_API_MODEL = os.getenv("AI_API_MODEL")  # turbo | pro | ultimate

    # ---------------- IMAGE SETTINGS ----------------
    MAX_IMAGE_SIZE = 1024
    DEFAULT_IMAGE_STYLE = os.getenv("DEFAULT_IMAGE_STYLE", "realistic")
config = Config()
# ---------------- CLIPDROP ----------------
CLIPDROP_API_KEY = os.getenv("AI_API_KEY")
