"""Meesho Creator Club browser automation scaffold.

This module uses Playwright for a user-authorized browser session. It intentionally
DOES NOT automate credential entry, bypass CAPTCHA/2FA, evade anti-bot controls, or
call private/undocumented Meesho endpoints.

Expected first-run flow:
1. Run with --login and complete the official login manually in the opened browser.
2. The authenticated browser profile is persisted locally (keep it private).
3. Scheduled runs reuse that profile and navigate the Creator Club UI.
4. UI selectors are configurable because websites can change their markup.

The exact Creator Club URLs/selectors should be verified against the user's current
account UI before enabling unattended publishing.
"""
from __future__ import annotations

import argparse
import os
import time
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

BASE_URL = os.getenv("MEESHO_CREATOR_URL", "https://www.meesho.com/")
PROFILE_DIR = Path(os.getenv("MEESHO_BROWSER_PROFILE", "./data/meesho_browser_profile"))
HEADLESS = os.getenv("MEESHO_HEADLESS", "false").lower() == "true"


def launch_context(playwright, headless: bool = HEADLESS):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        viewport={"width": 1440, "height": 900},
    )


def manual_login():
    """Open a persistent browser so the user can log in manually."""
    with sync_playwright() as p:
        context = launch_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(BASE_URL, wait_until="domcontentloaded")
        print("Complete Meesho login/verification manually in the browser.")
        input("After login is complete, press ENTER here to save the session... ")
        context.close()


def open_creator_club(page: Page):
    """Navigate to the configured Creator Club URL.

    Set MEESHO_CREATOR_CLUB_URL after verifying the official URL in the account UI.
    """
    url = os.getenv("MEESHO_CREATOR_CLUB_URL")
    if not url:
        raise RuntimeError("Set MEESHO_CREATOR_CLUB_URL to the verified Creator Club URL")
    page.goto(url, wait_until="domcontentloaded")
    page.wait_for_load_state("networkidle")


def click_by_text(page: Page, text: str, timeout: int = 10_000):
    """Click visible UI text; selectors should be replaced with stable selectors once verified."""
    locator = page.get_by_text(text, exact=True)
    locator.first.wait_for(state="visible", timeout=timeout)
    locator.first.click()


def prepare_creator_upload(page: Page):
    """Navigate to the Creator upload UI without submitting a post.

    The final selectors/text must be verified against the live account UI. This function
    deliberately stops before publishing so an incorrect selector cannot accidentally post.
    """
    # Examples only; do not assume these labels are permanent.
    profile_text = os.getenv("MEESHO_PROFILE_MENU_TEXT", "Profile")
    upload_text = os.getenv("MEESHO_UPLOAD_MENU_TEXT", "Upload Video")
    click_by_text(page, profile_text)
    click_by_text(page, upload_text)
    print("Creator upload screen reached. Publishing is intentionally not automated yet.")


def run_navigation_only():
    with sync_playwright() as p:
        context = launch_context(p)
        page = context.pages[0] if context.pages else context.new_page()
        open_creator_club(page)
        prepare_creator_upload(page)
        time.sleep(3)
        context.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true", help="Open browser for manual official login")
    parser.add_argument("--navigate", action="store_true", help="Navigate to Creator upload UI without publishing")
    args = parser.parse_args()

    if args.login:
        manual_login()
    elif args.navigate:
        run_navigation_only()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
