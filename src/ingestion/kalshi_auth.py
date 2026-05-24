import base64
import time
import httpx
from pathlib import Path
from urllib.parse import urlparse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parents[2]
load_dotenv(ROOT / "config" / ".env")

API_KEY_ID = os.getenv("KALSHI_API_KEY_ID")
PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH")
BASE_URL = os.getenv("KALSHI_BASE_URL")


def load_private_key():
    with open(ROOT / PRIVATE_KEY_PATH, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None, backend=default_backend())


def sign_request(method: str, path: str) -> dict:
    timestamp_ms = str(int(time.time() * 1000))

    # Must sign the FULL path from root e.g. /trade-api/v2/portfolio/balance
    full_path = urlparse(BASE_URL + path).path
    # Strip query params before signing
    sign_path = full_path.split('?')[0]

    message = f"{timestamp_ms}{method.upper()}{sign_path}".encode("utf-8")

    private_key = load_private_key()
    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH
        ),
        hashes.SHA256()
    )
    signature_b64 = base64.b64encode(signature).decode("utf-8")

    return {
        "KALSHI-ACCESS-KEY": API_KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        "KALSHI-ACCESS-SIGNATURE": signature_b64,
        "Content-Type": "application/json",
    }


def get(path: str) -> dict:
    headers = sign_request("GET", path)
    response = httpx.get(f"{BASE_URL}{path}", headers=headers)
    response.raise_for_status()
    return response.json()
