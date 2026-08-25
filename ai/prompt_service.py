from __future__ import annotations

import json
from ai.video_prompt import build_prompt_request
from providers.meesho import Product


class PromptService:
    def __init__(self, openai_provider):
        self.openai = openai_provider

    def create_video_package(self, product: Product, max_seconds: int = 10) -> dict:
        raw = self.openai.generate_text(build_prompt_request(product, max_seconds))
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.replace("```json", "", 1).replace("```", "", 1).strip()
        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as exc:
            raise RuntimeError(f"OpenAI did not return valid JSON: {exc}") from exc

        required = {"title", "voiceover", "video_prompt", "negative_prompt", "caption"}
        missing = required - set(data)
        if missing:
            raise RuntimeError(f"Prompt response missing fields: {sorted(missing)}")
        return data
