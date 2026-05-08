from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import httpx
from typing import Optional

app = FastAPI(title="CoinGecko Wrapper")

# CoinGecko API base URL
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"

# Symbol to CoinGecko ID mapping for top cryptocurrencies
SYMBOL_TO_ID = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
    "ADA": "cardano",
    "DOT": "polkadot",
    "AVAX": "avalanche-2",
    "MATIC": "matic-network",
    "LINK": "chainlink",
    "UNI": "uniswap",
    "DOGE": "dogecoin",
    "SHIB": "shiba-inu",
    "XRP": "ripple",
    "BNB": "binancecoin",
    "LTC": "litecoin",
    "ATOM": "cosmos",
    "NEAR": "near",
    "FTM": "fantom",
    "ALGO": "algorand",
    "APT": "aptos",
    "ARB": "arbitrum",
    "OP": "optimism",
    "SUI": "sui",
    "SEI": "sei-network",
    "TIA": "celestia",
    "INJ": "injective-protocol",
    "PEPE": "pepe",
    "WIF": "dogwifcoin",
    "BONK": "bonk",
    "RENDER": "render-token",
    "FET": "fetch-ai",
    "TAO": "bittensor",
    "AAVE": "aave",
    "MKR": "maker",
    "CRV": "curve-dao-token",
    "RUNE": "thorchain",
    "STX": "blockstack",
    "ICP": "internet-computer",
    "FIL": "filecoin",
    "GRT": "the-graph",
    "IMX": "immutable-x",
    "MANA": "decentraland",
    "SAND": "the-sandbox",
}


@app.get("/")
async def root():
    """API overview"""
    return {
        "name": "CoinGecko Wrapper",
        "description": "Cryptocurrency prices, historical data, and trending coins from CoinGecko",
        "endpoints": [
            {"path": "/price?symbol=BTC", "description": "Get current crypto price"},
            {"path": "/history?symbol=BTC&days=30", "description": "Get historical price data"},
            {"path": "/trending", "description": "Get trending coins"},
            {"path": "/health", "description": "Health check"}
        ],
        "supported_symbols": sorted(SYMBOL_TO_ID.keys())
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/price")
async def get_price(symbol: str):
    """
    Get current crypto price for a symbol
    Example: /price?symbol=BTC
    """
    symbol_upper = symbol.upper()

    # Map symbol to CoinGecko ID
    if symbol_upper not in SYMBOL_TO_ID:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol '{symbol}' not found. Supported symbols: {', '.join(SYMBOL_TO_ID.keys())}"
        )

    coin_id = SYMBOL_TO_ID[symbol_upper]

    # Call CoinGecko API
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_market_cap": "true",
                    "include_24hr_vol": "true"
                }
            )

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            response.raise_for_status()
            data = response.json()

            if coin_id not in data:
                raise HTTPException(status_code=404, detail=f"No data found for symbol '{symbol}'")

            coin_data = data[coin_id]

            return {
                "symbol": symbol_upper,
                "price": coin_data.get("usd"),
                "currency": "USD",
                "change_24h_pct": coin_data.get("usd_24h_change"),
                "market_cap": coin_data.get("usd_market_cap"),
                "volume_24h": coin_data.get("usd_24h_vol"),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            raise HTTPException(status_code=503, detail="CoinGecko API error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Network error connecting to CoinGecko")


@app.get("/history")
async def get_history(symbol: str, days: int = 30):
    """
    Get historical price data for a symbol
    Example: /history?symbol=BTC&days=30
    Supported days: 1, 7, 14, 30, 90, 180, 365, max
    """
    symbol_upper = symbol.upper()

    # Map symbol to CoinGecko ID
    if symbol_upper not in SYMBOL_TO_ID:
        raise HTTPException(
            status_code=404,
            detail=f"Symbol '{symbol}' not found. Supported symbols: {', '.join(SYMBOL_TO_ID.keys())}"
        )

    coin_id = SYMBOL_TO_ID[symbol_upper]

    # Validate days parameter
    valid_days = [1, 7, 14, 30, 90, 180, 365, "max"]
    days_param = "max" if days == "max" or str(days).lower() == "max" else days

    # Call CoinGecko API
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(
                f"{COINGECKO_BASE_URL}/coins/{coin_id}/market_chart",
                params={
                    "vs_currency": "usd",
                    "days": days_param
                }
            )

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            response.raise_for_status()
            data = response.json()

            # Transform data into cleaner format
            prices = data.get("prices", [])
            market_caps = data.get("market_caps", [])
            total_volumes = data.get("total_volumes", [])

            history = []
            for i, price_point in enumerate(prices):
                timestamp_ms, price = price_point
                market_cap = market_caps[i][1] if i < len(market_caps) else None
                volume = total_volumes[i][1] if i < len(total_volumes) else None

                history.append({
                    "date": datetime.fromtimestamp(timestamp_ms / 1000, tz=timezone.utc).isoformat(),
                    "price": price,
                    "market_cap": market_cap,
                    "volume": volume
                })

            return {
                "symbol": symbol_upper,
                "days": days_param,
                "history": history,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            raise HTTPException(status_code=503, detail="CoinGecko API error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Network error connecting to CoinGecko")


@app.get("/trending")
async def get_trending():
    """
    Get trending coins
    Example: /trending
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{COINGECKO_BASE_URL}/search/trending")

            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")

            response.raise_for_status()
            data = response.json()

            # Extract trending coins
            coins = data.get("coins", [])
            trending = []

            for item in coins:
                coin = item.get("item", {})
                trending.append({
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc")
                })

            return {
                "trending": trending,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            raise HTTPException(status_code=503, detail="CoinGecko API error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Network error connecting to CoinGecko")
