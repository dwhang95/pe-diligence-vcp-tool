"""
News sweep client — recent articles and signals for a company.

Source priority:
  1. Puppeteer (news_scraper.js subprocess) — real per-article timestamps, deduplicated
  2. Cache file (output/news_cache/{slug}_{date}.json) — written by Puppeteer or MCP scrape
  3. Google News RSS — no key, no browser, ~100 articles but encoded redirect URLs

All three paths return the same NewsResult structure.

Categorization is keyword-based — fast, no LLM call required.
Categories map to PE due diligence risk flag buckets:
  leadership   → key-man / management change risk
  regulatory   → compliance / legal risk
  workforce    → labor / retention risk
  customer     → concentration / revenue risk
  ma           → deal activity / ownership change
  financial    → earnings / distress signals
  operational  → plant / product / quality issues
"""

import asyncio
import json
import os
import re
import subprocess
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx

# Paths
_SRC_DIR = Path(__file__).parent
_SCRAPER_JS = _SRC_DIR / "news_scraper.js"
_PROJECT_ROOT = _SRC_DIR.parent.parent
_CACHE_DIR = _PROJECT_ROOT / "output" / "news_cache"

_GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

# ---------------------------------------------------------------------------
# Accredited sources whitelist
# Only these outlets are included when accredited_only=True.
# ---------------------------------------------------------------------------

_ACCREDITED_SOURCES: set[str] = {
    "pr newswire", "prnewswire",
    "business wire", "businesswire",
    "reuters",
    "associated press", "ap news", "ap",
    "wall street journal", "wsj",
    "financial times", "ft",
    "bloomberg",
    "barron's", "barrons",
    "new york times", "nyt", "nytimes",
    "forbes",
    "fortune",
    "korea economic daily", "한국경제",
    "korea herald", "코리아헤럴드",
}


def _is_accredited(source: str) -> bool:
    """Return True if the source matches any whitelisted outlet."""
    lower = source.lower().strip()
    return any(acc in lower for acc in _ACCREDITED_SOURCES)

# ---------------------------------------------------------------------------
# Categorization
# ---------------------------------------------------------------------------

_CATEGORY_KEYWORDS: dict[str, list[str]] = {
    "leadership": [
        "ceo", "cfo", "coo", "president", "resign", "appoint", "hire",
        "depart", "step down", "named", "promoted", "leadership change",
        "executive", "board", "director", "chief",
    ],
    "regulatory": [
        "lawsuit", "litigation", "sued", "fine", "penalty", "epa", "osha",
        "fda", "recall", "violation", "settlement", "investigation",
        "regulatory", "compliance", "ftc", "doj", "probe", "trial",
    ],
    "workforce": [
        "layoff", "lay off", "laid off", "hiring freeze", "union",
        "strike", "walkout", "headcount", "workforce reduction",
        "restructuring", "severance", "furlough",
    ],
    "customer": [
        "contract", "customer", "client", "partnership", "won", "lost",
        "renewal", "churn", "revenue", "account", "deal signed",
    ],
    "ma": [
        "acqui", "merger", "acquisition", "takeover", "buyout",
        "private equity", "investment", "stake", "joint venture",
        "spac", "transaction",
    ],
    "financial": [
        "earnings", "ebitda", "loss", "debt", "bankruptcy", "default",
        "credit", "downgrade", "profit warning", "guidance", "quarterly",
        "share price", "stock", "slump", "slide", "trade below", "insider sale",
        "analyst", "brokerages", "hold", "buy", "sell",
    ],
    "operational": [
        "plant", "facility", "factory", "recall", "quality", "supply chain",
        "shortage", "outage", "expansion", "new location", "capacity",
        "erp", "cloud", "ai platform", "digital", "technology",
    ],
}

_NEGATIVE_SIGNALS = [
    "resign", "fired", "fraud", "investigation", "bankrupt",
    "default", "layoff", "recall", "violation", "fine", "penalty",
    "sued", "lawsuit", "loss", "decline", "warning", "downgrade",
    "strike", "walkout", "probe", "scandal", "misconduct",
    "slump", "slide", "below target", "insider sale", "warning sign",
    "moves closer to trial", "continues to slide",
]


def _categorize(text: str) -> str:
    lower = text.lower()
    scores = {
        cat: sum(1 for kw in kws if kw in lower)
        for cat, kws in _CATEGORY_KEYWORDS.items()
    }
    best = max(scores, key=lambda c: scores[c])
    return best if scores[best] > 0 else "general"


def _is_negative(text: str) -> bool:
    lower = text.lower()
    return any(sig in lower for sig in _NEGATIVE_SIGNALS)


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class NewsItem:
    headline: str
    date: str           # YYYY-MM-DD
    source: str
    category: str
    is_risk_flag: bool


@dataclass
class NewsResult:
    company_name: str
    days_searched: int
    articles: list[NewsItem] = field(default_factory=list)
    source_used: str = ""
    error: Optional[str] = None

    def by_category(self) -> dict[str, list[NewsItem]]:
        out: dict[str, list[NewsItem]] = {}
        for item in self.articles:
            out.setdefault(item.category, []).append(item)
        return out

    def risk_flags(self) -> list[NewsItem]:
        return [a for a in self.articles if a.is_risk_flag]

    def to_summary_markdown(self) -> str:
        if not self.articles:
            return (
                f"_No news found for {self.company_name} "
                f"(source: {self.source_used or 'none'})._"
            )
        lines = [
            f"**News sweep:** {len(self.articles)} articles "
            f"(via {self.source_used})",
            "",
        ]
        by_cat = self.by_category()
        # Show risk-relevant categories first
        priority = ["leadership", "regulatory", "financial", "workforce", "ma", "operational", "customer"]
        ordered = [(c, by_cat[c]) for c in priority if c in by_cat]
        ordered += [(c, items) for c, items in by_cat.items() if c not in priority and c != "general"]

        for cat, items in ordered:
            lines.append(f"**{cat.title()} ({len(items)})**")
            # Show up to 3 per category, risk flags first
            top = sorted(items, key=lambda x: (not x.is_risk_flag, x.date), reverse=False)[:3]
            for item in top:
                flag = " ⚠" if item.is_risk_flag else ""
                lines.append(f"- {item.date}: {item.headline} _{item.source}_{flag}")

        risk = self.risk_flags()
        if risk:
            lines += ["", f"**Risk signals identified ({len(risk)}):**"]
            for r in risk[:6]:
                lines.append(f"  - [{r.category}] {r.headline}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _items_from_raw(raw: list[dict]) -> list[NewsItem]:
    items = []
    for a in raw:
        title = a.get("title", "").strip()
        if not title:
            continue
        dt_raw = a.get("datetime", "") or ""
        date = dt_raw[:10] if dt_raw else ""
        source = a.get("source", "")
        text = title + " " + source
        items.append(NewsItem(
            headline=title,
            date=date,
            source=source,
            category=_categorize(text),
            is_risk_flag=_is_negative(text),
        ))
    return items


# ---------------------------------------------------------------------------
# Source 1: Puppeteer subprocess
# ---------------------------------------------------------------------------

async def _fetch_puppeteer(company_name: str) -> list[NewsItem]:
    """Run news_scraper.js as a subprocess. Returns empty list on any failure."""
    if not _SCRAPER_JS.exists():
        raise FileNotFoundError(f"Scraper not found: {_SCRAPER_JS}")

    # Check node_modules/puppeteer is installed
    node_modules = _PROJECT_ROOT / "node_modules" / "puppeteer"
    if not node_modules.exists():
        raise RuntimeError(
            "puppeteer not installed — run: npm install  (in pe-diligence-tool/)"
        )

    loop = asyncio.get_event_loop()
    result = await loop.run_in_executor(
        None,
        lambda: subprocess.run(
            ["node", str(_SCRAPER_JS), company_name],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(_PROJECT_ROOT),
        ),
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"news_scraper.js exited {result.returncode}: {result.stderr.strip()}"
        )

    raw = json.loads(result.stdout)
    return _items_from_raw(raw)


# ---------------------------------------------------------------------------
# Source 2: Cache file
# ---------------------------------------------------------------------------

def _load_from_cache(company_name: str) -> Optional[tuple[list[NewsItem], str]]:
    """
    Look for the most recent cache file for this company.
    Returns (items, cache_path_str) or None if not found.
    """
    slug = _slugify(company_name)
    if not _CACHE_DIR.exists():
        return None
    candidates = sorted(_CACHE_DIR.glob(f"{slug}_*.json"), reverse=True)
    if not candidates:
        return None
    latest = candidates[0]
    try:
        raw = json.loads(latest.read_text(encoding="utf-8"))
        items = _items_from_raw(raw)
        return items, str(latest.name)
    except Exception:
        return None


def _write_cache(company_name: str, raw: list[dict]) -> None:
    """Write raw article list to a dated cache file."""
    _CACHE_DIR.mkdir(parents=True, exist_ok=True)
    slug = _slugify(company_name)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    path = _CACHE_DIR / f"{slug}_{today}.json"
    path.write_text(json.dumps(raw, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Source 3: Google News RSS
# ---------------------------------------------------------------------------

def _parse_rss_date(date_str: str) -> str:
    for fmt in ("%a, %d %b %Y %H:%M:%S %Z", "%a, %d %b %Y %H:%M:%S %z"):
        try:
            return datetime.strptime(date_str, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    m = re.search(r"(\d{4}-\d{2}-\d{2})", date_str)
    return m.group(1) if m else date_str[:10]


async def _fetch_google_rss(company_name: str) -> list[NewsItem]:
    query = company_name.replace(" ", "+")
    url = _GNEWS_RSS.format(query=query)
    async with httpx.AsyncClient(headers={"User-Agent": "PE-Diligence-Tool/2.0"}) as client:
        resp = await client.get(url, timeout=12, follow_redirects=True)
        resp.raise_for_status()

    try:
        root = ET.fromstring(resp.text)
    except ET.ParseError:
        return []

    items = []
    for item in root.findall(".//item"):
        headline = (item.findtext("title") or "").strip()
        if not headline:
            continue
        source = ""
        if " - " in headline:
            headline, source = headline.rsplit(" - ", 1)
            headline, source = headline.strip(), source.strip()
        pub_raw = item.findtext("pubDate") or ""
        pub = _parse_rss_date(pub_raw) if pub_raw else ""
        desc = item.findtext("description") or ""
        text = headline + " " + desc
        items.append(NewsItem(
            headline=headline,
            date=pub,
            source=source,
            category=_categorize(text),
            is_risk_flag=_is_negative(text),
        ))
    return items


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def fetch_recent_news(
    company_name: str,
    days_back: int = 90,
    accredited_only: bool = True,
) -> NewsResult:
    """
    Fetch recent news for a company.

    Priority: Puppeteer subprocess → cache file → Google News RSS.

    Args:
        company_name:    Target company name
        days_back:       Informational only (Puppeteer/RSS return whatever Google shows)
        accredited_only: When True, filter articles to whitelisted accredited sources only

    Returns:
        NewsResult with categorized articles and risk flags
    """
    result = NewsResult(company_name=company_name, days_searched=days_back)
    errors: list[str] = []

    # --- Source 1: Puppeteer ---
    try:
        items = await _fetch_puppeteer(company_name)
        result.articles = items
        result.source_used = "puppeteer"
        if accredited_only:
            result.articles = [a for a in result.articles if _is_accredited(a.source)]
            result.source_used += " (accredited)"
        return result
    except Exception as exc:
        errors.append(f"puppeteer: {exc}")

    # --- Source 2: Cache file ---
    cached = _load_from_cache(company_name)
    if cached:
        items, cache_name = cached
        result.articles = items
        if accredited_only:
            result.articles = [a for a in result.articles if _is_accredited(a.source)]
        result.source_used = f"cache ({cache_name})" + (" (accredited)" if accredited_only else "")
        if errors:
            result.error = " | ".join(errors)
        return result

    # --- Source 3: Google News RSS ---
    try:
        result.articles = await _fetch_google_rss(company_name)
        if accredited_only:
            result.articles = [a for a in result.articles if _is_accredited(a.source)]
        result.source_used = "google_rss" + (" (accredited)" if accredited_only else "")
    except Exception as exc:
        errors.append(f"rss: {exc}")
        result.source_used = "none"

    if errors:
        result.error = " | ".join(errors)

    return result


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "CBIZ"
    print(f"=== News Sweep: {company} ===\n")
    result = await fetch_recent_news(company)
    print(f"Source:   {result.source_used}")
    print(f"Articles: {len(result.articles)}")
    if result.error:
        print(f"Warnings: {result.error}")
    print()
    by_cat = result.by_category()
    for cat, items in sorted(by_cat.items(), key=lambda x: -len(x[1])):
        flags = sum(1 for i in items if i.is_risk_flag)
        print(f"  [{cat}] {len(items)} article(s), {flags} risk flag(s)")
        for a in items[:2]:
            flag = " ⚠" if a.is_risk_flag else ""
            print(f"    {a.date}: {a.headline}{flag}")
    print()
    print("--- Summary Markdown ---")
    print(result.to_summary_markdown())


if __name__ == "__main__":
    asyncio.run(_test())
