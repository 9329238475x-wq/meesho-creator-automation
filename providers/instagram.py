from __future__ import annotations

import httpx


class InstagramPublisher:
    """Official Instagram Graph API publisher adapter.

    Requires an eligible Instagram professional account and valid access token.
    The media URL must be publicly reachable by Meta when publishing a reel.
    """

    def __init__(self, access_token: str, account_id: str, graph_version: str = "v23.0"):
        self.access_token = access_token
        self.account_id = account_id
        self.base_url = f"https://graph.facebook.com/{graph_version}"

    def _check_config(self) -> None:
        if not self.access_token or not self.account_id:
            raise RuntimeError("Instagram API credentials are not configured")

    def create_reel_container(self, video_url: str, caption: str) -> str:
        self._check_config()
        response = httpx.post(
            f"{self.base_url}/{self.account_id}/media",
            params={
                "media_type": "REELS",
                "video_url": video_url,
                "caption": caption,
                "access_token": self.access_token,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["id"]

    def publish_container(self, creation_id: str) -> str:
        self._check_config()
        response = httpx.post(
            f"{self.base_url}/{self.account_id}/media_publish",
            params={
                "creation_id": creation_id,
                "access_token": self.access_token,
            },
            timeout=60,
        )
        response.raise_for_status()
        return response.json()["id"]
