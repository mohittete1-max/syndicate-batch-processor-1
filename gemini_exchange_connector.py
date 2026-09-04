import hashlib
import hmac
import json
import time
import requests
import base64

# Your Gemini sandbox/live credentials
GEMINI_API_KEY = "your_api_key"
GEMINI_API_SECRET = "your_api_secret"
BASE_URL = "https://api.gemini.com"          # live
# BASE_URL = "https://api.sandbox.gemini.com" # sandbox

def _auth_headers(payload: str):
    b64_payload = base64.b64encode(payload.encode("utf-8")).decode("utf-8")
    signature = hmac.new(
        GEMINI_API_SECRET.encode("utf-8"),
        b64_payload.encode("utf-8"),
        hashlib.sha384,
    ).hexdigest()
    return {
        "Content-Type": "text/plain",
        "X-GEMINI-APIKEY": GEMINI_API_KEY,
        "X-GEMINI-PAYLOAD": b64_payload,
        "X-GEMINI-SIGNATURE": signature,
    }

def get_balances():
    payload = {"request": "/v1/balances", "nonce": int(time.time() * 1000)}
    resp = requests.post(
        f"{BASE_URL}/v1/balances",
        headers=_auth_headers(json.dumps(payload)),
        data=None,
    )
    return resp.json()

def get_ticker(symbol="btcusd"):
    return requests.get(f"{BASE_URL}/v1/pubticker/{symbol}").json()

if __name__ == "__main__":
    print("BTC ticker:", get_ticker("btcusd"))
    # print("Balances:", get_balances())  # uncomment after adding valid keys
