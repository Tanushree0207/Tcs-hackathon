import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent

# Load environment variables from .env file if present
load_dotenv(BASE_DIR / ".env")


class Config:
    """Application configuration."""

    # Server settings (default 5001 on macOS to avoid AirPlay Receiver conflict on 5000)
    PORT = int(os.getenv("PORT", 5001))
    DEBUG = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "t")

    # Security: Limit maximum request payload to 1MB to prevent DoS attacks
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 1 * 1024 * 1024))

    # Database settings
    DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "tcs_hackathon.db"))

    # Grok API key (for Phase 2 AI service integration)
    XAI_API_KEY = os.getenv("XAI_API_KEY", "")
