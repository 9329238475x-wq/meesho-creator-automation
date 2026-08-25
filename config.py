from __future__ import annotations

import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    timezone: str = os.getenv("TIMEZONE", "Asia/Kolkata")
    daily_run_time: str = os.getenv("DAILY_RUN_TIME", "06:00")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///data/meesho_automation.db")

    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    gemini_text_model: str = os.getenv("GEMINI_TEXT_MODEL", "gemini-2.5-flash")
    gemini_video_model: str = os.getenv("GEMINI_VIDEO_MODEL", "veo-3.1-generate-preview")

    instagram_access_token: str = os.getenv("INSTAGRAM_ACCESS_TOKEN", "")
    instagram_business_account_id: str = os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID", "")

    meesho_provider_enabled: bool = os.getenv("MEESHO_PROVIDER_ENABLED", "false").lower() == "true"
    meesho_product_feed_url: str = os.getenv("MEESHO_PRODUCT_FEED_URL", "")

    target_language: str = os.getenv("TARGET_LANGUAGE", "Hindi")
    reel_aspect_ratio: str = os.getenv("REEL_ASPECT_RATIO", "9:16")
    max_video_seconds: int = int(os.getenv("MAX_VIDEO_SECONDS", "10"))
    min_price_inr: int = int(os.getenv("MIN_PRICE_INR", "199"))
    max_price_inr: int = int(os.getenv("MAX_PRICE_INR", "999"))
    min_commission_percent: float = float(os.getenv("MIN_COMMISSION_PERCENT", "5"))


settings = Settings()
