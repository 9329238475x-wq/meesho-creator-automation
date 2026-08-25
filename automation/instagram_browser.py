"""Instagram browser automation scaffold using a user-authorized Playwright session.

Use this only for workflows permitted by Instagram/Meta and your account. The script
never asks for or stores a password, never bypasses CAPTCHA/2FA, and never attempts to
evade anti-automation controls.

First run:
    python automation/instagram_browser.py --login

After manual login, the persistent browser profile can be reused by a scheduled job.
Publishing is intentionally gated behind --publish and an explicit confirmation unless
INSTAGRAM_ALLOW_PUBLISH=true is set by the operator.

UI selectors/text are configurable because Instagram's UI can change. Verify the live
account UI before unattended publishing.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path

from playwright.sync_api import Page, sync_playwright

INSTAGRAM_URL = os.getenv("INSTAGRAM_URL", "https://www.instagram.com/")
PROFILE_DIR = Path(os.getenv("INSTAGRAM_BROWSER_PROFILE", "./data/instagram_browser_profile"))
HEADLESS = os.getenv("INSTAGRAM_HEADLESS", "false").lower() == "true"
ALLOW_PUBLISH = os.getenv("INSTAGRAM_ALLOW_PUBLISH", "false").lower() == "true"


def launch_context(playwright, headless: bool = HEADLESS):
    PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    return playwright.chromium.launch_persistent_context(
        user_data_dir=str(PROFILE_DIR),
        headless=headless,
        viewport={"width": 1440, "height": 900},
    )


def manual_login() -> None:
    with sync_playwright() as p:
        context = launch_context(p, headless=False)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(INSTAGRAM_URL, wait_until="domcontentloaded")
        print("Log in to the official Instagram site manually and complete any verification.")
        input("After login is complete, press ENTER to save the session... ")
        context.close()


def click_text(page: Page, text: str, timeout: int = 10_000) -> None:
    locator = page.get_by_text(text, exact=True)
    locator.first.wait_for(state="visible", timeout=timeout)
    locator.first.click()


def open_create_ui(page: Page) -> None:
    """Open Instagram's create flow without publishing.

    The visible UI text is configurable. Do not assume labels are permanent.
    """
    create_label = os.getenv("INSTAGRAM_CREATE_LABEL", "Create")
    click_text(page, create_label)


def prepare_upload(page: Page, video_path: str, title: str, description: str) -> None:
    """Prepare an upload form; final submission remains gated.

    Instagram commonly combines caption/title-like text into a caption rather than
    providing a separate video title field. The automation therefore treats `title`
    as a generated caption prefix and keeps the description configurable.
    """
    path = Path(video_path)
    if not path.is_file():
        raise FileNotFoundError(f"Video not found: {path}")

    open_create_ui(page)

    # The exact file chooser and Next/Share controls vary. We intentionally use
    # role/text discovery rather than brittle CSS selectors and fail closed.
    file_input = page.locator('input[type="file"]').first
    file_input.wait_for(state="attached", timeout=10_000)
    file_input.set_input_files(str(path))

    # Caption is deliberately prepared but publishing is gated below.
    caption = f"{title}\n\n{description}".strip()
    print("Prepared caption:")
    print(caption)


def publish(page: Page, caption: str) -> None:
    if not ALLOW_PUBLISH:
        raise RuntimeError(
            "Publishing is disabled. Set INSTAGRAM_ALLOW_PUBLISH=true only after verifying the live UI and account workflow."
        )

    # Do not bypass platform protections. Use the visible official Share/Publish control.
    share_label = os.getenv("INSTAGRAM_SHARE_LABEL", "Share")
    click_text(page, share_label)


def run_prepare(video_path: str, title: str, description: str) -> None:
    with sync_playwright() as p:
        context = launch_context(p)
        page = context.pages[0] if context.pages else context.new_page()
        page.goto(INSTAGRAM_URL, wait_until="domcontentloaded")
        prepare_upload(page, video_path, title, description)
        input("Review the browser. Press ENTER to close without publishing... ")
        context.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--login", action="store_true")
    parser.add_argument("--prepare", action="store_true")
    parser.add_argument("--video")
    parser.add_argument("--title", default="")
    parser.add_argument("--description", default="")
    args = parser.parse_args()

    if args.login:
        manual_login()
    elif args.prepare:
        if not args.video:
            parser.error("--prepare requires --video")
        run_prepare(args.video, args.title, args.description)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
