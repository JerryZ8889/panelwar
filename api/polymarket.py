import httpx
from datetime import datetime, timezone, timedelta

GAMMA_API = "https://gamma-api.polymarket.com"

# Known ceasefire market slugs
CEASEFIRE_SLUGS = [
    "us-x-iran-ceasefire-by-march-15",
    "us-x-iran-ceasefire-by-march-31",
    "us-x-iran-ceasefire-by-april-30",
    "us-x-iran-ceasefire-by-may-31",
    "us-x-iran-ceasefire-by-june-30",
]

# Slug to deadline date mapping for filtering expired markets
_SLUG_DATES = {
    "march-2": (2026, 3, 2), "march-6": (2026, 3, 6),
    "march-15": (2026, 3, 15), "march-31": (2026, 3, 31),
    "april-30": (2026, 4, 30), "may-31": (2026, 5, 31),
    "june-30": (2026, 6, 30), "july-31": (2026, 7, 31),
    "august-31": (2026, 8, 31),
}


def _is_expired(slug: str) -> bool:
    """Check if a market's deadline has already passed."""
    for key, (y, m, d) in _SLUG_DATES.items():
        if key in slug:
            return datetime.now(timezone(timedelta(hours=8))).date() > datetime(y, m, d).date()
    return False


async def fetch_ceasefire_predictions() -> list[dict]:
    """Fetch ceasefire prediction probabilities from Polymarket."""
    results = []

    async with httpx.AsyncClient(timeout=15) as client:
        # Try fetching the parent event first
        try:
            resp = await client.get(
                f"{GAMMA_API}/events",
                params={"slug": "us-x-iran-ceasefire-by", "closed": "false"},
            )
            if resp.status_code == 200:
                events = resp.json()
                if events and len(events) > 0:
                    event = events[0]
                    markets = event.get("markets", [])
                    for market in markets:
                        outcome_prices = market.get("outcomePrices", "[]")
                        if isinstance(outcome_prices, str):
                            import json
                            outcome_prices = json.loads(outcome_prices)
                        yes_price = float(outcome_prices[0]) if outcome_prices else 0

                        results.append({
                            "slug": market.get("slug", ""),
                            "question": market.get("question", ""),
                            "probability": round(yes_price * 100, 1),
                            "volume": market.get("volume", 0),
                            "liquidity": market.get("liquidity", 0),
                        })

                    if results:
                        results = [r for r in results if not _is_expired(r["slug"])]
                        return sorted(results, key=lambda x: x["probability"])
        except Exception:
            pass

        # Fallback: fetch each market individually
        for slug in CEASEFIRE_SLUGS:
            try:
                resp = await client.get(
                    f"{GAMMA_API}/markets",
                    params={"slug": slug},
                )
                if resp.status_code == 200:
                    markets = resp.json()
                    if markets and len(markets) > 0:
                        market = markets[0]
                        outcome_prices = market.get("outcomePrices", "[]")
                        if isinstance(outcome_prices, str):
                            import json
                            outcome_prices = json.loads(outcome_prices)
                        yes_price = float(outcome_prices[0]) if outcome_prices else 0

                        results.append({
                            "slug": slug,
                            "question": market.get("question", slug),
                            "probability": round(yes_price * 100, 1),
                            "volume": market.get("volume", 0),
                            "liquidity": market.get("liquidity", 0),
                        })
            except Exception:
                results.append({
                    "slug": slug,
                    "question": slug,
                    "probability": None,
                    "error": "Failed to fetch",
                })

    return sorted(
        [r for r in results if r.get("probability") is not None and not _is_expired(r["slug"])],
        key=lambda x: x["probability"],
    )
