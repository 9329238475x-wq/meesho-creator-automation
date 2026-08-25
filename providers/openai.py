from __future__ import annotations

import httpx


class OpenAIProvider:
    """OpenAI Responses API adapter for multimodal prompt generation."""

    def __init__(self, api_key: str, model: str = "gpt-5.6-luna"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/responses"

    def generate_text(self, prompt: str, image_urls: list[str] | None = None) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        content: list[dict] = [{"type": "input_text", "text": prompt}]
        for url in image_urls or []:
            if url.startswith(("http://", "https://")):
                content.append({"type": "input_image", "image_url": url})

        response = httpx.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": self.model,
                "input": [{"role": "user", "content": content}],
            },
            timeout=180,
        )
        response.raise_for_status()
        data = response.json()

        chunks: list[str] = []
        for item in data.get("output", []):
            for part in item.get("content", []):
                text = part.get("text")
                if text:
                    chunks.append(text)
        if data.get("output_text") and not chunks:
            return data["output_text"]
        if not chunks:
            raise RuntimeError("OpenAI response contained no text output")
        return "\n".join(chunks)
