import sys
sys.path.append(".")

from pathlib import Path
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "config" / ".env")

print("=== ENV CHECK ===")
print(f"API_KEY_ID: {os.getenv('KALSHI_API_KEY_ID')}")
print(f"PRIVATE_KEY_PATH: {os.getenv('KALSHI_PRIVATE_KEY_PATH')}")
print(f"BASE_URL: {os.getenv('KALSHI_BASE_URL')}")

print("\n=== KEY FILE CHECK ===")
key_path = ROOT / os.getenv("KALSHI_PRIVATE_KEY_PATH")
print(f"Looking for key at: {key_path}")
print(f"File exists: {key_path.exists()}")

print("\n=== SIGNATURE CHECK ===")
import base64, time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

with open(key_path, "rb") as f:
    private_key = serialization.load_pem_private_key(f.read(), password=None)

timestamp_ms = str(int(time.time() * 1000))
path = "/portfolio/balance"
message = f"{timestamp_ms}GET{path}"
print(f"Message to sign: {message}")

signature = private_key.sign(message.encode("utf-8"), padding.PKCS1v15(), hashes.SHA256())
signature_b64 = base64.b64encode(signature).decode("utf-8")
print(f"Signature (first 40 chars): {signature_b64[:40]}...")

print("\n=== RAW REQUEST CHECK ===")
import httpx
headers = {
    "KALSHI-ACCESS-KEY": os.getenv("KALSHI_API_KEY_ID"),
    "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
    "KALSHI-ACCESS-SIGNATURE": signature_b64,
    "Content-Type": "application/json",
}
print(f"Headers: {headers}")
response = httpx.get(f"https://trading-api.kalshi.com/trade-api/v2{path}", headers=headers)
print(f"Status: {response.status_code}")
print(f"Response body: {response.text}")
