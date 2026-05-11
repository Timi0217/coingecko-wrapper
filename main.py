from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
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


HOME_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoinGecko · Chekk</title>
<style>
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
body{background:#0a0a0a;color:#e0e0e0;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;display:flex;justify-content:center;padding:32px 16px}
.w{max-width:640px;width:100%;background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.07);border-radius:16px;padding:32px;height:fit-content}
.hd{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
.t{font-family:'Courier New',monospace;font-style:italic;font-size:28px;font-weight:700;color:#8DC63F}
.st{font-family:'Courier New',monospace;font-size:13px;color:#555;display:flex;align-items:center;gap:6px}
.st .d{width:8px;height:8px;border-radius:50%;background:#555;transition:background .3s}
.st .d.on{background:#4CAF50}
.sub{color:#666;font-size:14px;margin-bottom:24px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.06)}
.g{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.pc{background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:14px 16px;display:flex;align-items:center;gap:12px;opacity:0;animation:fi .4s ease forwards}
.pc:nth-child(1){animation-delay:.1s}.pc:nth-child(2){animation-delay:.15s}.pc:nth-child(3){animation-delay:.2s}.pc:nth-child(4){animation-delay:.25s}
.ci{width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:15px;flex-shrink:0;color:#fff}
.cn .nm{font-weight:600;font-size:14px;line-height:1.3}.cn .sy{color:#666;font-size:11px;text-transform:uppercase}
.cr{margin-left:auto;text-align:right}
.cr .pr{font-family:'Courier New',monospace;font-size:16px;font-weight:700;white-space:nowrap}
.cr .ch{font-family:'Courier New',monospace;font-size:12px;margin-top:2px}
.up{color:#4CAF50}.dn{color:#ef5350}
.sc{background:rgba(255,255,255,.03);border:1px solid rgba(255,255,255,.06);border-radius:12px;padding:16px 18px;margin-bottom:14px;opacity:0;animation:fi .4s ease .35s forwards}
.sl{color:#8DC63F;font-size:10px;font-weight:700;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px}
.tr{display:flex;justify-content:space-between;align-items:center;padding:5px 0}
.tr .nm{font-size:13px}.tr .ch{font-family:'Courier New',monospace;font-size:13px}
.dm{margin:14px 0;opacity:0;animation:fi .4s ease .45s forwards}
.db{height:4px;background:rgba(255,255,255,.06);border-radius:2px;margin-bottom:6px;overflow:hidden}
.df{height:100%;background:linear-gradient(90deg,#8DC63F,#6fa030);border-radius:2px;transition:width .8s cubic-bezier(.4,0,.2,1);width:0}
.dr{display:flex;justify-content:space-between}.dl{color:#555;font-size:12px}.dv{color:#8DC63F;font-family:'Courier New',monospace;font-size:13px;font-weight:600}
hr.dv2{border:none;border-top:1px solid rgba(255,255,255,.06);margin:18px 0}
.fm{display:flex;gap:10px;margin-bottom:8px}
.ip{flex:1;background:rgba(255,255,255,.05);border:1px solid rgba(255,255,255,.1);border-radius:10px;padding:13px 16px;color:#fff;font-family:'Courier New',monospace;font-size:15px;outline:none;transition:border-color .2s}
.ip:focus{border-color:rgba(141,198,63,.5)}
.bt{background:#8DC63F;color:#000;border:none;border-radius:10px;padding:13px 22px;font-weight:700;font-size:14px;cursor:pointer;font-family:'Courier New',monospace;white-space:nowrap;transition:opacity .15s}
.bt:hover{opacity:.85}
.try{color:#555;font-size:12px}.try a{color:#666;text-decoration:none;cursor:pointer;transition:color .15s}.try a:hover{color:#8DC63F}
.ld{color:#444;font-family:'Courier New',monospace;font-size:14px}
#res{margin-top:14px;padding:14px 16px;background:rgba(141,198,63,.06);border:1px solid rgba(141,198,63,.15);border-radius:10px;display:none;font-family:'Courier New',monospace;font-size:13px;line-height:1.6}
@keyframes fi{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:translateY(0)}}
@media(max-width:480px){.g{grid-template-columns:1fr}.w{padding:20px}}
</style>
</head>
<body>
<div class="w">
 <div class="hd"><div class="t">CoinGecko</div><div class="st"><span class="d" id="dot"></span><span id="stx">connecting...</span></div></div>
 <div class="sub">Crypto prices, market caps, trends, and history</div>
 <div class="g" id="grid"></div>
 <div class="sc" id="tsec" style="display:none"><div class="sl">TRENDING</div><div id="tlist"></div></div>
 <div class="dm" id="dsec" style="display:none">
  <div class="db"><div class="df" id="dfill"></div></div>
  <div class="dr"><span class="dl">BTC dominance</span><span class="dv" id="dval">&mdash;</span></div>
 </div>
 <hr class="dv2">
 <div class="fm"><input class="ip" id="sym" placeholder="BTC" value="BTC" onkeydown="if(event.key==='Enter')fetchP()"><button class="bt" onclick="fetchP()">&rarr; price</button></div>
 <div class="try">Try: <a onclick="ts('ETH')">ETH</a> &middot; <a onclick="ts('SOL')">SOL</a> &middot; <a onclick="ts('DOGE')">DOGE</a> &middot; <a onclick="ts('ADA')">ADA</a> &middot; <a onclick="ts('AVAX')">AVAX</a></div>
 <div id="res"></div>
</div>
<script>
const COINS={BTC:{name:'Bitcoin',bg:'#F7931A',icon:'\\u20BF'},ETH:{name:'Ethereum',bg:'#627EEA',icon:'\\u039E'},SOL:{name:'Solana',bg:'#00D18C',icon:'\\u25CE'},DOGE:{name:'Dogecoin',bg:'#C2A633',icon:'D'}};
function fmt(n){if(n==null)return'--';if(n>=1e9)return'$'+(n/1e9).toFixed(2)+'B';if(n>=1e6)return'$'+(n/1e6).toFixed(2)+'M';if(n>=1)return'$'+n.toLocaleString('en-US',{minimumFractionDigits:2,maximumFractionDigits:2});return'$'+n.toFixed(4)}
function chg(v){if(v==null)return'<span class="ld">--</span>';const c=v>=0?'up':'dn';const a=v>=0?'\\u25B2':'\\u25BC';return'<span class="ch '+c+'">'+a+' '+Math.abs(v).toFixed(1)+'%</span>'}
async function init(){
 const t0=Date.now();
 // Health
 try{await fetch('/health');const ms=Date.now()-t0;document.getElementById('dot').classList.add('on');document.getElementById('stx').textContent='online \\u00B7 '+ms+'ms'}catch(e){document.getElementById('stx').textContent='offline'}
 // Prices
 const grid=document.getElementById('grid');
 const syms=Object.keys(COINS);
 const results=await Promise.allSettled(syms.map(s=>fetch('/price?symbol='+s).then(r=>r.json())));
 results.forEach((r,i)=>{
  const s=syms[i],c=COINS[s];
  const card=document.createElement('div');card.className='pc';
  if(r.status==='fulfilled'){const d=r.value;card.innerHTML='<div class="ci" style="background:'+c.bg+'">'+c.icon+'</div><div class="cn"><div class="nm">'+c.name+'</div><div class="sy">'+s+'</div></div><div class="cr"><div class="pr">'+fmt(d.price)+'</div>'+chg(d.change_24h_pct)+'</div>'}
  else{card.innerHTML='<div class="ci" style="background:'+c.bg+'">'+c.icon+'</div><div class="cn"><div class="nm">'+c.name+'</div><div class="sy">'+s+'</div></div><div class="cr"><div class="pr ld">--</div></div>'}
  grid.appendChild(card)
 });
 // Trending
 try{const t=await fetch('/trending').then(r=>r.json());const coins=t.trending||[];if(coins.length){const sec=document.getElementById('tsec');sec.style.display='';const list=document.getElementById('tlist');coins.slice(0,4).forEach(c=>{const row=document.createElement('div');row.className='tr';const ch=c.change_24h_pct;const chStr=ch!=null?chg(ch):'<span class="ch" style="color:#666">#'+(c.market_cap_rank||'--')+'</span>';row.innerHTML='<span class="nm">'+c.name+'</span>'+chStr;list.appendChild(row)})}}catch(e){}
 // Global / dominance
 try{const g=await fetch('/global').then(r=>r.json());if(g.btc_dominance){const sec=document.getElementById('dsec');sec.style.display='';const pct=g.btc_dominance.toFixed(1);document.getElementById('dval').textContent=pct+'%';setTimeout(()=>{document.getElementById('dfill').style.width=pct+'%'},100)}}catch(e){}
}
function ts(s){document.getElementById('sym').value=s;fetchP()}
async function fetchP(){
 const s=document.getElementById('sym').value.trim().toUpperCase();if(!s)return;
 const res=document.getElementById('res');res.style.display='block';res.innerHTML='<span class="ld">Fetching '+s+'...</span>';
 try{const d=await fetch('/price?symbol='+s).then(r=>{if(!r.ok)throw new Error(r.status);return r.json()});
  const ch=d.change_24h_pct;const cls=ch>=0?'up':'dn';const arrow=ch>=0?'\\u25B2':'\\u25BC';
  res.innerHTML='<strong>'+d.symbol+'</strong> '+fmt(d.price)+' <span class="'+cls+'">'+arrow+' '+Math.abs(ch||0).toFixed(2)+'%</span><br><span style="color:#666">Market cap: '+fmt(d.market_cap)+'&ensp;|&ensp;24h vol: '+fmt(d.volume_24h)+'</span>'}
 catch(e){res.innerHTML='<span class="dn">Error fetching '+s+'</span>'}
}
init();
</script>
</body></html>"""


@app.get("/")
async def root():
    """Live data home page"""
    return HTMLResponse(content=HOME_HTML)


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
    Get trending coins with 24h price change
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
                # Newer CoinGecko API includes data.price_change_percentage_24h
                coin_data = coin.get("data", {})
                change_24h = coin_data.get("price_change_percentage_24h", {})
                change_usd = change_24h.get("usd") if isinstance(change_24h, dict) else change_24h
                trending.append({
                    "name": coin.get("name"),
                    "symbol": coin.get("symbol"),
                    "market_cap_rank": coin.get("market_cap_rank"),
                    "price_btc": coin.get("price_btc"),
                    "change_24h_pct": change_usd,
                    "price_usd": coin_data.get("price"),
                    "thumb": coin.get("thumb"),
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


@app.get("/global")
async def get_global():
    """Global crypto market stats including BTC dominance."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{COINGECKO_BASE_URL}/global")
            if response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            response.raise_for_status()
            data = response.json().get("data", {})
            return {
                "total_market_cap_usd": data.get("total_market_cap", {}).get("usd"),
                "total_volume_usd": data.get("total_volume", {}).get("usd"),
                "btc_dominance": data.get("market_cap_percentage", {}).get("btc"),
                "eth_dominance": data.get("market_cap_percentage", {}).get("eth"),
                "active_coins": data.get("active_cryptocurrencies"),
                "market_cap_change_24h_pct": data.get("market_cap_change_percentage_24h_usd"),
                "timestamp": datetime.now(timezone.utc).isoformat(),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            raise HTTPException(status_code=503, detail="CoinGecko API error")
        except httpx.RequestError:
            raise HTTPException(status_code=503, detail="Network error connecting to CoinGecko")
