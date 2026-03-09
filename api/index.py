import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

sys.path.insert(0, os.path.dirname(__file__))

from data_fetcher import fetch_market_data, fetch_batch, fetch_history
from polymarket import fetch_ceasefire_predictions
from analyzer import analyze
from database import save_snapshot, get_latest_snapshot, get_history as get_db_history

app = FastAPI()


# ── Batch endpoints (5 batches, ~5-6 symbols each) ──

@app.get("/api/batch/{batch_id}")
async def batch(batch_id: int):
    """Fetch a single batch of indicators (1-5)."""
    if batch_id < 1 or batch_id > 5:
        return JSONResponse(content={"error": "batch_id must be 1-5"}, status_code=400)
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_batch, batch_id)
    return JSONResponse(content=data)


@app.get("/api/polymarket")
async def polymarket():
    """Fetch Polymarket ceasefire predictions."""
    data = await fetch_ceasefire_predictions()
    return JSONResponse(content=data)


@app.get("/api/analyze")
async def analyze_endpoint(indicators: str = ""):
    """Run analysis on provided indicator data (POST-style via query isn't ideal,
    but keeping GET for simplicity - frontend sends data as JSON body)."""
    # This endpoint is called by frontend after all batches complete
    # Frontend sends merged indicators as POST body
    pass


# ── Keep the full refresh for local dev ──

@app.get("/api/refresh")
async def refresh():
    loop = asyncio.get_event_loop()
    market_data = await loop.run_in_executor(None, fetch_market_data)
    polymarket_data = await fetch_ceasefire_predictions()
    analysis = analyze(market_data, polymarket_data)
    snapshot = {
        "indicators": market_data,
        "polymarket": polymarket_data,
        "analysis": analysis,
    }
    save_snapshot(snapshot)
    return JSONResponse(content=snapshot)


# ── Analysis via POST (frontend sends merged data) ──

from fastapi import Request

@app.post("/api/analyze")
async def analyze_post(request: Request):
    """Receive merged indicators + polymarket, return analysis."""
    body = await request.json()
    indicators = body.get("indicators", {})
    polymarket_data = body.get("polymarket", [])
    analysis = analyze(indicators, polymarket_data)
    # Save snapshot
    snapshot = {
        "indicators": indicators,
        "polymarket": polymarket_data,
        "analysis": analysis,
    }
    save_snapshot(snapshot)
    return JSONResponse(content={"analysis": analysis})


@app.get("/api/latest")
async def latest():
    snap = get_latest_snapshot()
    if snap:
        return JSONResponse(content=snap)
    return JSONResponse(content={"error": "No data yet. Click refresh."}, status_code=404)


@app.get("/api/history/{symbol}")
async def history(symbol: str, period: str = "1mo"):
    loop = asyncio.get_event_loop()
    data = await loop.run_in_executor(None, fetch_history, symbol, period)
    return JSONResponse(content=data)


@app.get("/api/snapshots")
async def snapshots(limit: int = 50):
    data = get_db_history(limit)
    return JSONResponse(content=data)
