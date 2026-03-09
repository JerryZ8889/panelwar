import os
import sys
import asyncio
from fastapi import FastAPI
from fastapi.responses import JSONResponse

# Ensure api/ modules are importable
sys.path.insert(0, os.path.dirname(__file__))

from data_fetcher import fetch_market_data, fetch_history
from polymarket import fetch_ceasefire_predictions
from analyzer import analyze
from database import save_snapshot, get_latest_snapshot, get_history as get_db_history

app = FastAPI()


@app.get("/api/refresh")
async def refresh():
    loop = asyncio.get_event_loop()
    market_data = await loop.run_in_executor(None, fetch_market_data)
    polymarket = await fetch_ceasefire_predictions()
    analysis = analyze(market_data, polymarket)
    snapshot = {
        "indicators": market_data,
        "polymarket": polymarket,
        "analysis": analysis,
    }
    save_snapshot(snapshot)
    return JSONResponse(content=snapshot)


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
