# Meesho Creator Automation

Automation foundation for creating affiliate/creator marketing reels from product data and publishing through supported official APIs.

## Status

Phase 1: project foundation, configuration, scheduler, database, AI provider interface, video provider interface, and Instagram publishing interface.

**Important:** No Meesho private API, login scraping, password automation, or undocumented endpoint is included. The Meesho integration is intentionally an adapter so an officially permitted data/export mechanism can be connected later.

## Daily workflow

The default schedule is **06:00 Asia/Kolkata**. The pipeline can:

1. Load candidate products from the configured provider.
2. Select a product using commission/price/quality filters.
3. Generate a short Hindi promotional script.
4. Generate a video prompt.
5. Generate a video through the configured provider.
6. Build caption/hashtags.
7. Publish through the official Instagram Graph API when configured.
8. Record job status and errors in SQLite.

## Configuration

Copy `.env.example` to `.env` and fill only the services you actually use. Never commit secrets.

## Local run

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py --run-once
```

To run the scheduler continuously:

```bash
python app.py
```

## Safety / compliance

Use only APIs and product/link mechanisms that your account and the respective provider explicitly permit. Affiliate earnings are not guaranteed. Generated marketing content should not make false claims about having personally purchased or tested a product unless that is true.
