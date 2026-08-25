from __future__ import annotations

import httpx


class OpenAIProvider:
    """OpenAI Responses API adapter used specifically for prompt writing."""

    def __init__(self, api_key: str, model: str = "gpt-5.6-luna"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.openai.com/v1/responses"

    def generate_text(self, prompt: str) -> str:
        if not self.api_key:
            raise RuntimeError("OPENAI_API_KEY is not configured")

        response = httpx.post(
            self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            json={"model": self.model, "input": prompt},
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()

        # Responses API returns output items; collect text parts robustly.
        chunks: list[str] = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                text = content.get("text")
                if text:
                    chunks.append(text)
        if not chunks and data.get("output_text"):
            return data["output_text"]
        if not chunks:
            raise RuntimeError("OpenAI response contained no text output")
        return "\n".join(chunks)
