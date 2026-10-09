import os
import sys
from datetime import datetime, timedelta, timezone

import requests

CLIENT_ID = os.environ.get("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.environ.get("DHAN_ACCESS_TOKEN")
if not CLIENT_ID or not ACCESS_TOKEN:
    sys.exit("Missing DHAN_CLIENT_ID or DHAN_ACCESS_TOKEN")

URL = "https://api.dhan.co/v2/charts/rollingoption"
HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
}

# ~6 months back; 4-day window so weekends/holidays still return data
start = datetime.now() - timedelta(days=183)
end = start + timedelta(days=4)

payload = {
    "exchangeSegment": "NSE_FNO",
    "interval": "1",              # 1-minute candles
    "securityId": 13,             # NIFTY underlying
    "instrument": "OPTIDX",
    "expiryFlag": "MONTH",
    "expiryCode": 1,
    "strike": "ATM",
    "drvOptionType": "CALL",
    "requiredData": ["open", "high", "low", "close", "volume", "oi", "strike", "spot"],
    "fromDate": start.strftime("%Y-%m-%d"),
    "toDate": end.strftime("%Y-%m-%d"),   # non-inclusive
}

print("Request:", payload["fromDate"], "->", payload["toDate"])
r = requests.post(URL, json=payload, headers=HEADERS, timeout=30)
print("HTTP", r.status_code)
if r.status_code != 200:
    sys.exit(r.text)

ce = (r.json().get("data") or {}).get("ce")
if not ce or not ce.get("timestamp"):
    sys.exit("No candles returned (try another date or expiryCode)")

ist = timezone(timedelta(hours=5, minutes=30))
print(f"Candles received: {len(ce['timestamp'])}\nFirst candle:")
print("  time  :", datetime.fromtimestamp(ce["timestamp"][0], ist))
for k in ("open", "high", "low", "close", "volume", "oi", "strike", "spot"):
    if ce.get(k):
        print(f"  {k:6}:", ce[k][0])
