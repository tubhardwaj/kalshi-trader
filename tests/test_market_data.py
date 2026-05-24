import sys
sys.path.append(".")
from src.ingestion.kalshi_auth import get

result = get("/markets?limit=5&series_ticker=KXBTC15M&status=open")
markets = result.get("markets", [])
if not markets:
    print("No open markets right now")
    sys.exit(0)

TICKER = markets[0]["ticker"]
print(f"Current market: {TICKER}\n")

# Market detail
print("=== Market Detail ===")
detail = get(f"/markets/{TICKER}")
m = detail.get("market", {})
print(f"yes_bid:   {m.get('yes_bid')}")
print(f"yes_ask:   {m.get('yes_ask')}")
print(f"volume:    {m.get('volume')}")
print(f"open_time: {m.get('open_time')}")
print(f"close_time:{m.get('close_time')}")

# Trades - correct path
print("\n=== Recent Trades ===")
trades = get(f"/markets/{TICKER}/trades?limit=10")
for t in trades.get("trades", []):
    print(t)
