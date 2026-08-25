"""Daily trend-driven product research engine.

Start with fresh India trend signals, translate them into fashion intents, then
cross-check candidates against authorized Meesho product data. Random products
are not eligible for automatic publishing.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

@dataclass
class TrendSignal:
    query: str
    rank: int = 0
    traffic_label: str = ""
    status: str = "unknown"
    started: str = ""
    source: str = "google_trends"

@dataclass
class ProductCandidate:
    product_id: str
    title: str
    price_inr: float
    commission_percent: float
    product_url: str
    image_count: int
    description: str = ""
    rating: float | None = None
    review_count: int = 0
    trend_queries: list[str] | None = None
    trend_score: float = 0.0
    final_score: float = 0.0

class GoogleTrendsResearcher:
    """Configurable India Trends source.

    Use GOOGLE_TRENDS_URL only with a source/access method you are permitted to use.
    The public page is useful for discovery; production should prefer structured/approved data.
    """
    def __init__(self, url: str | None = None, timeout: int = 20):
        self.url = url or "https://trends.google.com/trending?geo=IN&hl=en-US"
        self.timeout = timeout

    def fetch(self) -> str:
        req = Request(self.url, headers={"User-Agent": "Mozilla/5.0"})
        with urlopen(req, timeout=self.timeout) as response:
            return response.read().decode("utf-8", errors="ignore")

    def extract_queries(self, html: str, limit: int = 50) -> list[TrendSignal]:
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        patterns = re.findall(r"([A-Za-z][A-Za-z0-9 &'\-]{2,80})\s+(?:[0-9]+K\+|[0-9]+M\+)", text)
        seen: set[str] = set()
        results: list[TrendSignal] = []
        for i, query in enumerate(patterns, 1):
            q = query.strip(" -")
            key = q.lower()
            if key in seen or len(q) < 3:
                continue
            seen.add(key)
            results.append(TrendSignal(query=q, rank=i))
            if len(results) >= limit:
                break
        return results

FASHION_TERMS = {
    "kurti", "kurta", "saree", "sari", "suit", "salwar", "dress", "top", "tshirt",
    "jeans", "cargo", "co-ord", "coord", "lehenga", "anarkali", "palazzo", "gown",
    "ethnic", "fashion", "outfit", "women", "men", "wear", "clothing", "fashion trend",
}

def fashion_relevance(query: str) -> float:
    q = query.lower()
    hits = sum(1 for term in FASHION_TERMS if term in q)
    return min(1.0, hits / 2.0)

def trend_score(signal: TrendSignal) -> float:
    score = 0.0
    if signal.status == "active":
        score += 0.35
    if signal.rank:
        score += max(0.0, 0.35 - signal.rank * 0.005)
    score += 0.30 * fashion_relevance(signal.query)
    return min(1.0, score)

def score_candidate(candidate: ProductCandidate, trend_matches: list[TrendSignal]) -> float:
    """Score evidence-backed candidates; random products should not pass."""
    trend = max((trend_score(x) for x in trend_matches), default=0.0)
    image_score = min(candidate.image_count / 6.0, 1.0)
    rating_score = min((candidate.rating or 0.0) / 5.0, 1.0)
    review_score = min(candidate.review_count / 1000.0, 1.0)
    commission_score = min(candidate.commission_percent / 20.0, 1.0)
    price_score = 1.0 if 199 <= candidate.price_inr <= 999 else 0.5
    score = (
        trend * 0.40 + image_score * 0.15 + rating_score * 0.12
        + review_score * 0.10 + commission_score * 0.10
        + price_score * 0.08 + (0.05 if candidate.description else 0.0)
    )
    candidate.trend_score = trend
    candidate.final_score = score
    candidate.trend_queries = [x.query for x in trend_matches]
    return score

def choose_daily_product(candidates: list[ProductCandidate], trends: list[TrendSignal], min_score: float = 0.55) -> ProductCandidate | None:
    eligible: list[ProductCandidate] = []
    relevant = [t for t in trends if fashion_relevance(t.query) > 0]
    for candidate in candidates:
        if score_candidate(candidate, relevant) >= min_score:
            eligible.append(candidate)
    return max(eligible, key=lambda x: x.final_score) if eligible else None

def save_research_result(candidate: ProductCandidate | None, path: str = "output/daily_product.json") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "selected": asdict(candidate) if candidate else None}
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    researcher = GoogleTrendsResearcher()
    trends = researcher.extract_queries(researcher.fetch())
    print(json.dumps([asdict(x) for x in trends], ensure_ascii=False, indent=2))
