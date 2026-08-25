from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.blocking import BlockingScheduler
from config import settings
from database.db import SessionLocal, Job, init_db
from providers.meesho import MeeshoProvider
from providers.openai import OpenAIProvider
from ai.prompt_service import PromptService

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
log = logging.getLogger(__name__)


def choose_product(products):
    eligible = [
        p for p in products
        if settings.min_price_inr <= p.price_inr <= settings.max_price_inr
        and p.commission_percent >= settings.min_commission_percent
    ]
    return max(eligible, key=lambda p: (p.commission_percent, -p.price_inr), default=None)


def run_daily_job() -> None:
    init_db()
    log.info("Starting daily creator automation at %s", datetime.now(ZoneInfo(settings.timezone)).isoformat())
    provider = MeeshoProvider(settings.meesho_provider_enabled, settings.meesho_product_feed_url)

    try:
        products = provider.list_products()
        product = choose_product(products)
        if product is None:
            log.warning("No eligible product found; stopping cleanly")
            return

        if not settings.openai_api_key:
            raise RuntimeError("OPENAI_API_KEY is required for the ChatGPT video-prompt stage")

        prompt_service = PromptService(OpenAIProvider(settings.openai_api_key, settings.openai_prompt_model))
        package = prompt_service.create_video_package(product, settings.max_video_seconds)
        log.info("Generated video package for %s", product.title)

        # Persistence is optional. If no database is configured, continue without it.
        if SessionLocal is not None:
            with SessionLocal() as session:
                job = Job(status="prompt_ready", product_id=product.product_id)
                session.add(job)
                session.commit()
                log.info("Saved job %s", job.id)

        # The returned package contains the exact video_prompt, voiceover,
        # negative_prompt and caption that the next video/publishing stages consume.
        log.info("Video prompt length=%d, voiceover length=%d", len(package["video_prompt"]), len(package["voiceover"]))
        return package

    except Exception as exc:
        log.exception("Daily job failed: %s", exc)
        return None


def start_scheduler() -> None:
    hour, minute = map(int, settings.daily_run_time.split(":", 1))
    scheduler = BlockingScheduler(timezone=ZoneInfo(settings.timezone))
    scheduler.add_job(run_daily_job, "cron", hour=hour, minute=minute, id="daily_creator_job", replace_existing=True)
    log.info("Scheduler started: daily at %s %s", settings.daily_run_time, settings.timezone)
    scheduler.start()
