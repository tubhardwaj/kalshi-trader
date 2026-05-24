import asyncio
import json
import ssl
import base64
import time
import certifi
import websockets
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
import os
import sys
sys.path.append(str(Path(__file__).resolve().parents[2]))
from src.ingestion.kalshi_auth import get

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "config" / ".env")

WS_URL   = os.getenv("KALSHI_WS_URL")
KEY_ID   = os.getenv("KALSHI_API_KEY_ID")
KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")

SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())


def get_ws_headers() -> dict:
    """Sign exactly /trade-api/ws/v2 — not prefixed with REST base URL."""
    with open(ROOT / KEY_PATH, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )
    timestamp_ms = str(int(time.time() * 1000))
    path         = "/trade-api/ws/v2"
    message      = f"{timestamp_ms}GET{path}".encode("utf-8")

    signature = private_key.sign(
        message,
        padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.DIGEST_LENGTH),
        hashes.SHA256()
    )
    return {
        "KALSHI-ACCESS-KEY":       KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        "KALSHI-ACCESS-SIGNATURE": base64.b64encode(signature).decode("utf-8"),
        "Content-Type":            "application/json",
    }


def get_current_ticker() -> str:
    result  = get("/markets?limit=5&series_ticker=KXBTC15M&status=open")
    markets = result.get("markets", [])
    if not markets:
        raise Exception("No open KXBTC15M market found")
    ticker = markets[0]["ticker"]
    logger.info(f"Active market: {ticker} | closes: {markets[0]['close_time']}")
    return ticker


async def stream_market(ticker: str):
    headers   = get_ws_headers()
    msg_count = 0

    logger.info(f"Connecting to {WS_URL}")
    async with websockets.connect(WS_URL, additional_headers=headers, ssl=SSL_CONTEXT) as ws:
        logger.info("Connected!")

        for cmd_id, channel in [(1, "orderbook_delta"), (2, "ticker"), (3, "trade")]:
            await ws.send(json.dumps({
                "id": cmd_id, "cmd": "subscribe",
                "params": {"channels": [channel], "market_tickers": [ticker]}
            }))

        logger.info(f"Subscribed to orderbook_delta, ticker, trade for {ticker}")

        async for message in ws:
            data      = json.loads(message)
            msg_count += 1
            logger.info(f"[{msg_count}] {data.get('type')}: {json.dumps(data)}")
            if msg_count >= 30:
                logger.info("30 messages received — test complete")
                break


async def main():
    ticker = get_current_ticker()
    await stream_market(ticker)


if __name__ == "__main__":
    asyncio.run(main())
