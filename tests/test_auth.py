import sys
sys.path.append(".")

from src.ingestion.kalshi_auth import get

# Test 1: Fetch your account balance
print("Testing auth — fetching account balance...")
result = get("/portfolio/balance")
print(result)