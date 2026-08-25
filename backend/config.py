import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()

@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    veo3_api_key: str = os.getenv("VEO3_API_KEY", "")
    google_search_api_key: str = os.getenv("GOOGLE_SEARCH_API_KEY", "")
    google_search_engine_id: str = os.getenv("GOOGLE_SEARCH_ENGINE_ID", "")
    api_base_url: str = os.getenv("API_BASE_URL", "http://localhost:8000")
    timezone: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    meesho_session_dir: str = os.getenv("MEESHO_SESSION_DIR", "./data/browser/meesho")
    instagram_session_dir: str = os.getenv("INSTAGRAM_SESSION_DIR", "./data/browser/instagram")
    meesho_allow_publish: bool = os.getenv("MEESHO_ALLOW_PUBLISH", "false").lower() == "true"
    instagram_allow_publish: bool = os.getenv("INSTAGRAM_ALLOW_PUBLISH", "false").lower() == "true"

settings = Settings()
