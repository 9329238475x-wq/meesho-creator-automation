import os
import smtplib
from email.message import EmailMessage
from dataclasses import dataclass

@dataclass(frozen=True)
class EmailConfig:
    host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    port: int = int(os.getenv("SMTP_PORT", "587"))
    username: str = os.getenv("SMTP_USERNAME", "")
    password: str = os.getenv("SMTP_PASSWORD", "")
    sender: str = os.getenv("SMTP_FROM", "")


def send_publish_notification(recipient: str, instagram_url: str, product_name: str, config: EmailConfig | None = None) -> None:
    """Send notification only after the publishing adapter confirms a public Instagram URL."""
    if not recipient or not instagram_url:
        raise ValueError("recipient and confirmed instagram_url are required")

    cfg = config or EmailConfig()
    if not all((cfg.username, cfg.password, cfg.sender)):
        raise RuntimeError("SMTP credentials are not configured")

    msg = EmailMessage()
    msg["Subject"] = f"Your video is live on Instagram — {product_name}"
    msg["From"] = cfg.sender
    msg["To"] = recipient
    msg.set_content(
        f"Your automated video has been published successfully.\n\n"
        f"Product: {product_name}\n"
        f"Instagram video: {instagram_url}\n\n"
        "This notification was sent after the publishing step returned a public URL."
    )

    with smtplib.SMTP(cfg.host, cfg.port, timeout=30) as server:
        server.starttls()
        server.login(cfg.username, cfg.password)
        server.send_message(msg)
