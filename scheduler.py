from __future__ import annotations

import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from apscheduler.schedulers.blocking import BlockingScheduler
from config import settings
from database.db import SessionLocal, Job, init_db
from providers.meesho import MeeshoProvider
from ai.content import build_script, build_video_prompt, build_caption

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

        script = build_script(product)
        prompt = build_video_prompt(product, script)
        caption = build_caption(product)

        with SessionLocal() as session:
            job = Job(status="content_ready", product_id=product.product_id)
            session.add(job)
            session.commit()
            log.info("Prepared job %s for %s", job.id, product.title)

        # Video generation and Instagram publishing are intentionally separate
        # adapters and will be enabled after their official API credentials are configured.
        log.info("Prompt ready (%d chars); caption ready (%d chars)", len(prompt), len(caption))

    except Exception as exc:
        log.exception("Daily job failed: %s", exc)


def start_scheduler() -> None:
    hour, minute = map(int, settings.daily_run_time.split(":", 1))
    scheduler = BlockingScheduler(timezone=ZoneInfo(settings.timezone))
    scheduler.add_job(run_daily_job, "cron", hour=hour, minute=minute, id="daily_creator_job", replace_existing=True)
    log.info("Scheduler started: daily at %s %s", settings.daily_run_time, settings.timezone)
    scheduler.start()
