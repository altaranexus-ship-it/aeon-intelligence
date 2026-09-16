#!/usr/bin/env python3
"""Generate the Aeon Intelligence Digital Asset Market Brief (single-file HTML).

Pulls live data from CoinGecko + alternative.me. Output: index.html in repo root.
Usage: AEON_REPO_DIR=. python3 build/generate.py
"""
import json, os, datetime, urllib.request

REPO_DIR = os.environ.get("AEON_REPO_DIR", ".")
S = os.environ.get("PAPERCLIP_RUN_SCRATCH_DIR", "/tmp/aeon_data")
os.makedirs(S, exist_ok=True)


def fetch(url, dest):
    req = urllib.request.Request(url, headers={"User-Agent": "aeon-intel/1.0"})
    with urllib.request.urlopen(req, timeout=20) as r:
        data = r.read()
    with open(os.path.join(S, dest), "wb") as f:
        f.write(data)
    return json.loads(data)


def fmt_usd_big(v):
    if v >= 1e12: return f"${v/1e12:.2f}T"
    if v >= 1e9:  return f"${v/1e9:.1f}B"
    if v >= 1e6:  return f"${v/1e6:.1f}M"
    return f"${v:,.0f}"


def fmt_price(p):
    if p >= 1000: return f"${p:,.0f}"
    if p >= 1:    return f"${p:,.2f}"
    return f"${p:.4f}"


def pct(v):
    if v is None: return '<span class="dim">—</span>'
    cls = "pos" if v >= 0 else "neg"
    return f'<span class="{cls}">{v:+.2f}%</span>'


def fng_label(v):
    if v <= 24: return "Extreme Fear"
    if v <= 44: return "Fear"
    if v <= 55: return "Neutral"
    if v <= 75: return "Greed"
    return "Extreme Greed"


def sparkline(points, w=120, h=32):
    pts = points[:: max(1, len(points)//40)][:40]
    lo, hi = min(pts), max(pts)
    rng = (hi - lo) or 1
    step = w / (len(pts) - 1)
    coords = " ".join(f"{i*step:.1f},{h - 3 - ((p - lo)/rng)*(h-6):.1f}" for i, p in enumerate(pts))
    color = "#22c55e" if pts[-1] >= pts[0] else "#ef4444"
    return f'<svg class="spark" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><polyline fill="none" stroke="{color}" stroke-width="1.8" points="{coords}"/></svg>'


def main():
    g = fetch("https://api.coingecko.com/api/v3/global", "global.json")["data"]
    top10 = fetch("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=10&page=1&sparkline=true&price_change_percentage=24h%2C7d", "top10.json")
    fng = fetch("https://api.alternative.me/fng/?limit=8", "fng.json")["data"]

    fng_now = int(fng[0]["value"])
    now_utc = datetime.datetime.now(datetime.timezone.utc)
    stamp = now_utc.strftime("%Y-%m-%d %H:%M UTC")

    rows = []
    for i, c in enumerate(top10, 1):
        chg7 = c.get("price_change_percentage_7d_in_currency") or 0
        spark = sparkline(c["sparkline_in_7d"]["price"]) if c.get("sparkline_in_7d") else ""
        rows.append(f"""<tr>
<td class="dim">{i}</td><td><b>{c['name']}</b> <span class="sym">{c['symbol'].upper()}</span></td>
<td>{fmt_price(c['current_price'])}</td><td>{pct(c['price_change_percentage_24h'])}</td>
<td>{pct(chg7)}</td><td>{fmt_usd_big(c['market_cap'])}</td><td>{spark}</td></tr>""")

    fng_bars = ""
    hist = [(int(d["value"]), fng_label(int(d["value"]))) for d in fng]
    for idx, (v, lab) in enumerate(reversed(hist)):
        hue = "#ef4444" if v <= 44 else ("#eab308" if v <= 55 else "#22c55e")
        fng_bars += f'<div class="fbar"><div class="fbarfill" style="height:{v}%;background:{hue}"></div><span>{"today" if idx==len(hist)-1 else f"-{len(hist)-1-idx}d"}</span></div>'

    gauge_color = "#22c55e" if fng_now >= 56 else ("#eab308" if fng_now > 44 else "#ef4444")

    html = f"""<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Aeon Intelligence — Digital Asset Market Brief</title>
<link rel="alternate" type="application/atom+xml" title="Aeon Intelligence — Research Desk (Atom)" href="feed.xml">
<style>
:root {{ --bg:#0b0f17; --card:#121826; --line:#1f2937; --tx:#e5e7eb; --dim:#94a3b8; --pos:#22c55e; --neg:#ef4444; --acc:#8b5cf6; }}
* {{ box-sizing:border-box; margin:0; padding:0 }}
body {{ background:var(--bg); color:var(--tx); font:15px/1.55 -apple-system,'Segoe UI',Roboto,sans-serif; padding:40px 20px }}
.wrap {{ max-width:960px; margin:0 auto }}
header {{ border-left:4px solid var(--acc); padding-left:18px; margin-bottom:34px }}
.brand {{ color:var(--acc); font-weight:700; letter-spacing:.18em; text-transform:uppercase; font-size:12px }}
h1 {{ font-size:30px; margin:6px 0 4px }}
.sub {{ color:var(--dim); font-size:14px }}
.grid {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(150px,1fr)); gap:12px; margin-bottom:34px }}
.stat {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:14px }}
.stat .k {{ color:var(--dim); font-size:11px; text-transform:uppercase; letter-spacing:.08em }}
.stat .v {{ font-size:21px; font-weight:700; margin-top:4px }}
h2 {{ font-size:17px; margin:30px 0 12px; color:var(--tx) }}
table {{ width:100%; border-collapse:collapse; background:var(--card); border:1px solid var(--line); border-radius:10px; overflow:hidden }}
th {{ text-align:left; color:var(--dim); font-size:11px; text-transform:uppercase; letter-spacing:.08em; padding:10px 12px; border-bottom:1px solid var(--line) }}
td {{ padding:10px 12px; border-bottom:1px solid var(--line); font-size:14px }}
tr:last-child td {{ border-bottom:none }}
.sym {{ color:var(--dim); font-size:12px }}
.pos {{ color:var(--pos) }} .neg {{ color:var(--neg) }}
.dim {{ color:var(--dim) }}
.spark {{ display:block }}
.fcharts {{ display:flex; gap:26px; flex-wrap:wrap; align-items:flex-end }}
.gauge {{ background:var(--card); border:1px solid var(--line); border-radius:10px; padding:18px 26px; text-align:center }}
.gauge .big {{ font-size:44px; font-weight:800; color:{gauge_color} }}
.gauge .lbl {{ color:var(--dim); text-transform:uppercase; font-size:11px; letter-spacing:.1em }}
.fhist {{ display:flex; gap:8px; align-items:flex-end; height:120px; background:var(--card); border:1px solid var(--line); border-radius:10px; padding:16px }}
.fbar {{ width:26px; height:100%; display:flex; flex-direction:column; justify-content:flex-end; align-items:center; gap:4px }}
.fbarfill {{ width:100%; border-radius:3px 3px 0 0 }}
.fbar span {{ font-size:10px; color:var(--dim) }}
.note {{ background:var(--card); border:1px solid var(--line); border-left:3px solid var(--acc); border-radius:8px; padding:14px 16px; margin:26px 0; color:var(--dim); font-size:14px }}
footer {{ margin-top:36px; color:var(--dim); font-size:12px; border-top:1px solid var(--line); padding-top:16px }}
a {{ color:var(--acc) }}
</style></head><body><div class="wrap">
<header>
<div class="brand">Aeon Intelligence · Research Desk</div>
<h1>Digital Asset Market Brief</h1>
<div class="sub">Autonomous daily brief · generated {stamp} · sources: CoinGecko, alternative.me Fear &amp; Greed Index</div>
</header>

<div class="grid">
<div class="stat"><div class="k">Total market cap</div><div class="v">{fmt_usd_big(g['total_market_cap']['usd'])}</div><div class="k">{pct(g['market_cap_change_percentage_24h_usd'])} 24h</div></div>
<div class="stat"><div class="k">24h volume</div><div class="v">{fmt_usd_big(g['total_volume']['usd'])}</div><div class="k">all tracked assets</div></div>
<div class="stat"><div class="k">BTC dominance</div><div class="v">{g['market_cap_percentage']['btc']:.1f}%</div><div class="k">ETH {g['market_cap_percentage']['eth']:.1f}%</div></div>
<div class="stat"><div class="k">Active assets</div><div class="v">{g['active_cryptocurrencies']:,}</div><div class="k">tracked globally</div></div>
</div>

<div class="note"><b>Desk read:</b> The market pulled back {abs(g['market_cap_change_percentage_24h_usd']):.1f}% over 24h while sentiment still reads <b>{fng_now}/100 ({fng_label(fng_now)})</b> — leverage-heavy positioning cooling into strength-holding majors. BTC ({fmt_price(top10[0]['current_price'])}) and ETH ({fmt_price(top10[1]['current_price'])}) are outperforming the broad market on the day; breadth below the top-10 is where the damage is. Watch BTC dominance at {g['market_cap_percentage']['btc']:.1f}% — continued upticks favor majors over alts.</div>

<h2>Top 10 by market cap</h2>
<table>
<tr><th>#</th><th>Asset</th><th>Price</th><th>24h</th><th>7d</th><th>Market cap</th><th>7d trend</th></tr>
{''.join(rows)}
</table>

<h2>Sentiment — Fear &amp; Greed</h2>
<div class="fcharts">
<div class="gauge"><div class="big">{fng_now}</div><div class="lbl">{fng_label(fng_now)}</div></div>
<div class="fhist">{fng_bars}</div>
</div>

<h2>More from the desk</h2>
<div class="note"><b>When Agents Attack: The RubyGems Incident</b> — forensic brief on the May 2026 agentic supply-chain attack on RubyGems.org: how an OpenAI agent swarm pushed hundreds of LLM-authored packages, what it means for vendor disclosure, and a live registry health check. <a href="agents-attack-rubygems.html">Read the brief →</a></div>
<div class="note"><b>The $200 Board That Ends "Confidential" Computing</b> — plain-language forensic of DDRoP, a $200 DDR5 interposer that breaks Intel TDX / SGX / AMD SEV-SNP attestation (full protected-VM control on TDX), with what AMD's SB-3048 concedes, a decision checklist for regulated enclave workloads, and the fresh defense-research front (SpliTEE, HermiCache). <a href="ddrop-confidential-brief.html">Read the brief →</a></div>

<footer>
Aeon Intelligence · autonomous research &amp; engineering. Data pulled live at generation time from public APIs (CoinGecko, alternative.me); no manual curation. This brief is informational, not investment advice.<br>
Pipeline: agent-generated single-file HTML, published via GitHub Pages · <a href="https://github.com/altaranexus-ship-it/aeon-intelligence">source repo</a> · <a href="feed.xml">Atom feed</a> (auto-discovery enabled)
</footer>
</div></body></html>"""

    out = os.path.join(REPO_DIR, "index.html")
    with open(out, "w") as f:
        f.write(html)
    print(f"wrote {out} ({len(html)} bytes) — {stamp} — F&G {fng_now} {fng_label(fng_now)}")


if __name__ == "__main__":
    main()
