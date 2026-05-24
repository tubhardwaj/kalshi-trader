import sys
sys.path.append(".")
from src.ingestion.kalshi_auth import get

# BTC 15-min markets
print("=== BTC 15-min Markets ===")
result = get("/markets?limit=20&series_ticker=KXBTC15M&status=open")
markets = result.get("markets", [])
print(f"Found {len(markets)} open markets\n")
for m in markets:
    print(f"ticker:     {m['ticker']}")
    print(f"title:      {m['title']}")
    print(f"yes_bid:    {m.get('yes_bid')}")
    print(f"yes_ask:    {m.get('yes_ask')}")
    print(f"volume:     {m.get('volume')}")
    print(f"close_time: {m.get('close_time')}")
    print()

# Also fetch the series info
print("=== KXBTC15M Series Info ===")
series = get("/series/KXBTC15M")
print(series)
