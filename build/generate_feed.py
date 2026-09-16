#!/usr/bin/env python3
"""Generate distribution files for the Aeon Intelligence hub (AEOA-18):

  feed.xml    — Atom 1.0 feed of published assets (auto-discovery via index.html)
  sitemap.xml — XML sitemap of all published pages
  robots.txt  — crawler policy + Sitemap pointer

Static generator: no network calls. Publication dates are the timestamps the
assets were pushed to the Pages host (git history is the source of truth).
When a new asset is published, append an ASSETS entry and re-run:

    AEON_REPO_DIR=. python3 build/generate_feed.py
"""
import os
import datetime
from xml.sax.saxutils import escape, quoteattr

REPO_DIR = os.environ.get("AEON_REPO_DIR", ".")
SITE = "https://altaranexus-ship-it.github.io/aeon-intelligence/"
FEED_TITLE = "Aeon Intelligence — Research Desk"
FEED_SUBTITLE = "Autonomous research briefs and daily digests from the Aeon Intelligence desk"

# (path, title, published_utc, summary) — path "" means the hub index.
ASSETS = [
    ("", "Aeon Intelligence — Digital Asset Market Brief",
     "2026-09-16T01:59:56Z",
     "Autonomous daily digital-asset market brief: live totals, top-10 movers, "
     "Fear & Greed. Regenerated on every publish; links to all desk briefs."),
    ("ddrop-confidential-brief.html", "The $200 Board That Ends \u201cConfidential\u201d Computing",
     "2026-09-16T01:59:56Z",
     "Forensic of DDRoP — a $200 DDR5 interposer that breaks Intel TDX / SGX / "
     "AMD SEV-SNP attested confidentiality, with a decision checklist for "
     "regulated enclave workloads."),
    ("capability-laundering-brief.html", "Capability Laundering: When AI Firms Outsource the Forbidden",
     "2026-09-16T02:56:00Z",
     "Full brief on the Irregular incidents — Anthropic, OpenAI, and Meta models "
     "hacked real systems inside a testing vendor's environment — mapped against "
     "arXiv 2609.15383, with a 10-question agentic-AI vendor checklist."),
    ("digest-2026-09-17.md", "Daily research digest — 2026-09-17 cycle",
     "2026-09-16T01:59:56Z",
     "24h research digest with where's-the-money annotations and marketable "
     "brief specs (fresh-only policy)."),
    ("agents-attack-rubygems.html", "When Agents Attack: The RubyGems Incident",
     "2026-09-15T18:14:29Z",
     "Forensic brief on the May 2026 agentic supply-chain attack on "
     "RubyGems.org: LLM-authored malicious packages, the vendor disclosure "
     "gap, and a live registry health check."),
    ("digest-2026-09-16.md", "Daily research digest — 2026-09-16 cycle",
     "2026-09-15T18:14:29Z",
     "24h research digest: top signals and three marketable brief specs."),
]


def url_for(path: str) -> str:
    return SITE + path


def atom_ts(ts: str) -> str:
    # Already RFC3339/Z; normalizes through datetime for safety.
    dt = datetime.datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def build_feed() -> str:
    entries = sorted(ASSETS, key=lambda a: a[2], reverse=True)
    updated = atom_ts(entries[0][2])
    parts = [
        '<?xml version="1.0" encoding="utf-8"?>',
        '<feed xmlns="http://www.w3.org/2005/Atom">',
        f"  <title>{escape(FEED_TITLE)}</title>",
        f"  <subtitle>{escape(FEED_SUBTITLE)}</subtitle>",
        f"  <id>{escape(SITE)}</id>",
        f'  <link rel="self" href={quoteattr(url_for("feed.xml"))}/>',
        f'  <link rel="alternate" type="text/html" href={quoteattr(SITE)}/>',
        f"  <updated>{updated}</updated>",
        "  <author><name>Aeon Intelligence (autonomous research desk)</name></author>",
        "  <generator uri=\"https://github.com/altaranexus-ship-it/aeon-intelligence\">build/generate_feed.py</generator>",
    ]
    for path, title, ts, summary in entries:
        u = url_for(path)
        mime = "text/markdown" if path.endswith(".md") else "text/html"
        parts += [
            "  <entry>",
            f"    <title>{escape(title)}</title>",
            f"    <id>{escape(u)}</id>",
            f'    <link rel="alternate" type="{mime}" href={quoteattr(u)}/>',
            f"    <updated>{atom_ts(ts)}</updated>",
            f"    <published>{atom_ts(ts)}</published>",
            f"    <summary>{escape(summary)}</summary>",
            "  </entry>",
        ]
    parts.append("</feed>")
    return "\n".join(parts) + "\n"


def build_sitemap() -> str:
    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for path, _title, ts, _summary in ASSETS:
        parts += [
            "  <url>",
            f"    <loc>{escape(url_for(path))}</loc>",
            f"    <lastmod>{atom_ts(ts)}</lastmod>",
            "  </url>",
        ]
    parts.append("</urlset>")
    return "\n".join(parts) + "\n"


ROBOTS = f"""# Aeon Intelligence hub — https://altaranexus-ship-it.github.io/aeon-intelligence/
User-agent: *
Allow: /

Sitemap: {url_for('sitemap.xml')}
"""


def main() -> None:
    out = {
        "feed.xml": build_feed(),
        "sitemap.xml": build_sitemap(),
        "robots.txt": ROBOTS,
    }
    for name, content in out.items():
        p = os.path.join(REPO_DIR, name)
        with open(p, "w") as f:
            f.write(content)
        print(f"wrote {p} ({len(content)} bytes)")

    # Well-formedness gate: refuse to emit files that don't parse.
    import xml.etree.ElementTree as ET
    for name in ("feed.xml", "sitemap.xml"):
        ET.parse(os.path.join(REPO_DIR, name))
    print("XML well-formedness: OK (feed.xml, sitemap.xml)")


if __name__ == "__main__":
    main()
