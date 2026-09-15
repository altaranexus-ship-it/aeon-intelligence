# Aeon Intelligence — Public Assets

Autonomous research & engineering desk. This repo hosts Aeon's publishable assets.

## Live assets

- **Digital Asset Market Brief** — [`index.html`](index.html) · generated 2026-09-15 10:35 UTC from live CoinGecko + alternative.me data. Published via GitHub Pages (enable in repo Settings → Pages → deploy from branch `main`).

## Internal documents

- **Org Infrastructure Audit** (AEOA-4 Deliverable 1) — [`infrastructure-audit.md`](infrastructure-audit.md): verified toolset inventory for the Research/Engineering/Crypto desks, gaps blocking paid work, and the single highest-leverage fix.

## Pipeline

1. `build/generate.py` pulls global market data, top-10 with 7-day sparklines, and 8-day Fear & Greed history from public APIs.
2. Renders a dependency-free single-file HTML brief.
3. Push to `main` → GitHub Pages serves it.

Regenerate: `AEON_REPO_DIR=. python3 build/generate.py && git add -A && git commit -m "refresh brief" && git push`

## Watched repos (seed)

- `altaranexus-ship-it/aeon-intelligence` (this repo — public asset home)
- `altaranexus-ship-it/nexus-agent` (NEXUS trading/agent infrastructure)
