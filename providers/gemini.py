from __future__ import annotations

import httpx


class GeminiProvider:
    """Minimal Gemini REST adapter.

    Text generation is implemented; video generation remains an explicit
    provider boundary because video APIs and operation polling can change.
    """

    def __init__(self, api_key: str, text_model: str):
        self.api_key = api_key
        self.text_model = text_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("GEMINI_API_KEY is not configured")
        response = httpx.post(
            f"{self.base_url}/models/{self.text_model}:generateContent",
            params={"key": self.api_key},
            json={"contents": [{"parts": [{"text": prompt}]}]},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
