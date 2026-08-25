"""Daily trend-driven product research engine.

Policy:
- Never randomly choose a product just because a fresh trend match is missing.
- Prefer today's fashion trends; if insufficient, fall back through recent trend history.
- Always select a product when an eligible candidate exists, so a scheduled run does not
  silently stop merely because today's trend feed is sparse.
- Target price is <= INR 700; INR 800 is an absolute fallback ceiling.
- Price urgency copy must be factual: never claim a future price increase unless a verified
  price-change signal supports it.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta
import json
import re
from pathlib import Path
from urllib.request import Request, urlopen

TARGET_PRICE_MAX = 700.0
ABSOLUTE_PRICE_MAX = 800.0
RECENT_TREND_DAYS = 7

@dataclass
class TrendSignal:
    query: str
    rank: int = 0
    traffic_label: str = ""
    status: str = "unknown"
    started: str = ""
    source: str = "google_trends"
    observed_at: str = ""

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
    price_tier: str = ""

class GoogleTrendsResearcher:
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
        now = datetime.now(timezone.utc).isoformat()
        for i, query in enumerate(patterns, 1):
            q = query.strip(" -")
            key = q.lower()
            if key in seen or len(q) < 3:
                continue
            seen.add(key)
            results.append(TrendSignal(query=q, rank=i, observed_at=now))
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

def trend_score(signal: TrendSignal, age_days: float = 0.0) -> float:
    freshness = max(0.0, 1.0 - (age_days / RECENT_TREND_DAYS))
    score = 0.45 * freshness
    if signal.status == "active":
        score += 0.25
    if signal.rank:
        score += max(0.0, 0.20 - signal.rank * 0.004)
    score += 0.10 * fashion_relevance(signal.query)
    return min(1.0, score)

def price_score(price: float) -> float:
    if price <= TARGET_PRICE_MAX:
        # Best score around the user's desired <=700 range.
        return 1.0
    if price <= ABSOLUTE_PRICE_MAX:
        return 0.55
    return 0.0

def score_candidate(candidate: ProductCandidate, trend_matches: list[TrendSignal]) -> float:
    now = datetime.now(timezone.utc)
    trend = 0.0
    for signal in trend_matches:
        age_days = 0.0
        if signal.observed_at:
            try:
                age_days = max(0.0, (now - datetime.fromisoformat(signal.observed_at)).total_seconds() / 86400)
            except ValueError:
                pass
        trend = max(trend, trend_score(signal, age_days))

    image_score = min(candidate.image_count / 6.0, 1.0)
    rating_score = min((candidate.rating or 0.0) / 5.0, 1.0)
    review_score = min(candidate.review_count / 1000.0, 1.0)
    commission_score = min(candidate.commission_percent / 20.0, 1.0)
    pscore = price_score(candidate.price_inr)

    if candidate.price_inr <= TARGET_PRICE_MAX:
        candidate.price_tier = "preferred"
    elif candidate.price_inr <= ABSOLUTE_PRICE_MAX:
        candidate.price_tier = "fallback"
    else:
        candidate.price_tier = "rejected"

    if pscore == 0.0:
        candidate.final_score = 0.0
        return 0.0

    score = (
        trend * 0.42 + image_score * 0.15 + rating_score * 0.12
        + review_score * 0.10 + commission_score * 0.08
        + pscore * 0.08 + (0.05 if candidate.description else 0.0)
    )
    candidate.trend_score = trend
    candidate.final_score = score
    candidate.trend_queries = [x.query for x in trend_matches]
    return score

def load_recent_trends(path: str = "output/trend_history.json", days: int = RECENT_TREND_DAYS) -> list[TrendSignal]:
    """Load recent persisted trend observations for the scheduled fallback."""
    p = Path(path)
    if not p.exists():
        return []
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    result: list[TrendSignal] = []
    for item in data if isinstance(data, list) else []:
        try:
            signal = TrendSignal(**item)
            observed = datetime.fromisoformat(signal.observed_at) if signal.observed_at else cutoff
            if observed >= cutoff:
                result.append(signal)
        except (TypeError, ValueError):
            continue
    return result

def save_trend_history(trends: list[TrendSignal], path: str = "output/trend_history.json") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    existing = load_recent_trends(path)
    merged = existing + trends
    # Deduplicate by query + observation day.
    seen: set[tuple[str, str]] = set()
    clean: list[TrendSignal] = []
    for item in sorted(merged, key=lambda x: x.observed_at, reverse=True):
        day = item.observed_at[:10] if item.observed_at else ""
        key = (item.query.lower(), day)
        if key in seen:
            continue
        seen.add(key)
        clean.append(item)
    Path(path).write_text(json.dumps([asdict(x) for x in clean], ensure_ascii=False, indent=2), encoding="utf-8")

def choose_daily_product(
    candidates: list[ProductCandidate],
    todays_trends: list[TrendSignal],
    recent_trends: list[TrendSignal] | None = None,
    min_score: float = 0.45,
) -> ProductCandidate | None:
    """Always try a recent trend fallback before returning None.

    Priority: today's fashion trends -> recent 7-day fashion trends -> broader recent
    fashion signals. Price remains <=700 preferred and <=800 absolute maximum.
    """
    recent = recent_trends or []
    today_relevant = [t for t in todays_trends if fashion_relevance(t.query) > 0]
    recent_relevant = [t for t in recent if fashion_relevance(t.query) > 0]

    # Prefer <=700 products first. Only use 701-800 when no suitable <=700 candidate exists.
    for pool in (candidates,):
        preferred = [c for c in pool if c.price_inr <= TARGET_PRICE_MAX]
        fallback = [c for c in pool if TARGET_PRICE_MAX < c.price_inr <= ABSOLUTE_PRICE_MAX]
        for candidate_pool in (preferred, fallback):
            scored: list[ProductCandidate] = []
            for candidate in candidate_pool:
                matches = today_relevant or recent_relevant
                if not matches:
                    continue
                if score_candidate(candidate, matches) >= min_score:
                    scored.append(candidate)
            if scored:
                return max(scored, key=lambda x: x.final_score)

    # No trend match at all: do NOT randomize. The caller should run research again or
    # provide an approved recent candidate pool. This keeps the scheduled system honest.
    return None

def build_price_copy(candidate: ProductCandidate, verified_price_history: list[float] | None = None) -> str:
    """Create truthful price language; never fabricate a future price increase."""
    price = int(candidate.price_inr)
    history = verified_price_history or []
    if history and min(history) < price:
        return f"Abhi listed price ₹{price} hai; price change ho sakta hai, isliye current price check kar lena."
    return f"Abhi listed price ₹{price} hai; latest price dekhne ke liye product page check kar lena."

def save_research_result(candidate: ProductCandidate | None, path: str = "output/daily_product.json") -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    payload = {"generated_at": datetime.now(timezone.utc).isoformat(), "selected": asdict(candidate) if candidate else None}
    Path(path).write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    researcher = GoogleTrendsResearcher()
    trends = researcher.extract_queries(researcher.fetch())
    save_trend_history(trends)
    print(json.dumps([asdict(x) for x in trends], ensure_ascii=False, indent=2))
