import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote
from urllib.request import Request, urlopen

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

app = FastAPI()

# shortcut: Yahoo 비공식 API(키 불필요), 막히거나 상용이면 공식 유료 API로 교체
YAHOO = "https://query1.finance.yahoo.com/v8/finance/chart/{}?range=1d&interval=5m"
INDEX = Path(__file__).parent / "static" / "index.html"


@app.get("/")
def read_home():
    return FileResponse(INDEX)


@app.get("/stock/{symbol}")
def read_stock(symbol: str):
    req = Request(YAHOO.format(quote(symbol, safe="")), headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urlopen(req, timeout=5) as r:
            result = json.load(r)["chart"]["result"][0]
    except HTTPError as e:
        raise HTTPException(404 if e.code == 404 else 502, f"종목 조회 실패: {symbol}")
    meta = result["meta"]
    closes = result.get("indicators", {}).get("quote", [{}])[0].get("close", [])
    series = [(t, c) for t, c in zip(result.get("timestamp", []), closes) if c is not None]
    return {
        "times": [t for t, _ in series],
        "points": [c for _, c in series],
        "symbol": meta["symbol"],
        "name": meta.get("longName") or meta.get("shortName"),
        "price": meta["regularMarketPrice"],
        "previous_close": meta.get("chartPreviousClose"),
        "currency": meta.get("currency"),
        "day_high": meta.get("regularMarketDayHigh"),
        "day_low": meta.get("regularMarketDayLow"),
        "volume": meta.get("regularMarketVolume"),
    }
