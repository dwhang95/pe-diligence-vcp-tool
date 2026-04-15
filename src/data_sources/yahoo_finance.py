"""
yahoo_finance.py — Public comp metrics and market context via yfinance.

For PE diligence:
  - Pull EV/EBITDA, EV/Revenue, market cap for industry proxy comps
  - If company is publicly traded: pull current metrics directly

yfinance is synchronous; we run it in a thread executor to stay async-friendly.
"""

import asyncio
from dataclasses import dataclass, field
from typing import Optional

try:
    import yfinance as yf
    _YF_AVAILABLE = True
except ImportError:
    _YF_AVAILABLE = False


# ---------------------------------------------------------------------------
# Industry → proxy comp tickers
# Maps PE industry keywords to a small set of representative public comps.
# Not exhaustive — used as market context, not a full comps set.
# ---------------------------------------------------------------------------

_INDUSTRY_TICKERS: list[tuple[str, str, list[str]]] = [
    # (keyword, industry_label, [tickers])
    ("packaging",       "Packaging",                 ["PKG", "SEE", "SLGN", "IP", "ATR"]),
    ("corrugated",      "Corrugated/Paper",           ["PKG", "IP", "SLGN", "SEE"]),
    ("cosmetic",        "Beauty / Personal Care",     ["ELF", "ULTA", "COTY", "RGS"]),
    ("baby",            "Consumer / Baby Products",   ["CHD", "PG", "KMB", "ENR"]),
    ("consumer product","Consumer Products",          ["PG", "KMB", "CHD", "NWL"]),
    ("food manufactur", "Food Manufacturing",         ["CAG", "SJM", "MKC", "GIS"]),
    ("food service",    "Food Service",               ["MCD", "QSR", "YUM", "SBUX"]),
    ("healthcare serv", "Healthcare Services",        ["UNH", "HUM", "CNC", "MOH"]),
    ("physician",       "Physician Practice Mgmt",    ["AMSF", "OPCH", "LHCG", "AMEDISYS"]),
    ("dental",          "Dental Services",            ["DFIN", "XRAY", "PDCO"]),
    ("home health",     "Home Health",                ["AMSF", "OPCH", "LHCG"]),
    ("staffing",        "Staffing / HR Services",     ["MAN", "KELYA", "KFRC", "RHI"]),
    ("professional",    "Professional Services",      ["ACN", "CBRE", "MAN", "KFY"]),
    ("business serv",   "Business Services",          ["CBRE", "RRX", "FLT", "WEX"]),
    ("accounting",      "Accounting / Business Svcs", ["CBIZ", "MHK", "BDO"]),
    ("consulting",      "Management Consulting",      ["ACN", "ICF", "CACI", "BAH"]),
    ("software",        "Software / SaaS",            ["NOW", "CRM", "HUBS", "VEEV"]),
    ("it service",      "IT Services",                ["CTSH", "EPAM", "GLOB", "DXC"]),
    ("tech",            "Technology",                 ["AAPL", "MSFT", "GOOGL", "META"]),
    ("distribution",    "Distribution",               ["GWW", "MSM", "FAST", "NVENT"]),
    ("wholesale",       "Wholesale / Distribution",   ["SYSCO", "US FD", "PFG", "CHEF"]),
    ("logistics",       "Logistics / Transport",      ["UPS", "FDX", "XPO", "R"]),
    ("trucking",        "Trucking",                   ["WERN", "HTLD", "ODFL", "SAIA"]),
    ("warehouse",       "Warehousing / 3PL",          ["XPO", "GXO", "RXYL", "CHRW"]),
    ("construction",    "Construction Services",      ["PWR", "STRL", "TPC", "PRIM"]),
    ("building",        "Building Products",          ["MAS", "FBHS", "DOOR", "JELD"]),
    ("hvac",            "HVAC / Climate",             ["TT", "CARR", "LII", "AAON"]),
    ("industrial mach", "Industrial Machinery",       ["ITT", "RXN", "ESCO", "FLOW"]),
    ("aerospace",       "Aerospace / Defense",        ["LMT", "RTX", "GD", "NOC"]),
    ("auto part",       "Auto Parts",                 ["LKQ", "AAP", "BWA", "DAN"]),
    ("retail",          "Retail",                     ["HD", "LOW", "TGT", "COST"]),
    ("restaurant",      "Restaurants",                ["MCD", "QSR", "YUM", "TXRH"]),
    ("hotel",           "Hospitality",                ["HLT", "MAR", "H", "CHH"]),
    ("real estate",     "Real Estate Services",       ["CBRE", "JLL", "RMAX", "EXPI"]),
    ("education",       "Education Services",         ["STRA", "PRDO", "GHC", "BRT"]),
    ("media",           "Media / Entertainment",      ["DIS", "WBD", "NFLX", "PARA"]),
    ("printing",        "Printing / Publishing",      ["RRD", "QUAD", "LSC", "NN"]),
]

_FALLBACK_TICKERS = ["SPY", "MDY"]  # Market proxies


def _match_industry(industry: str) -> tuple[str, list[str]]:
    lower = industry.lower()
    for keyword, label, tickers in _INDUSTRY_TICKERS:
        if keyword in lower:
            return label, tickers
    return "Broad Market", _FALLBACK_TICKERS


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class TickerSnapshot:
    ticker: str
    name: str
    current_price: Optional[float] = None
    market_cap_b: Optional[float] = None     # $B
    ev_b: Optional[float] = None             # Enterprise Value $B
    revenue_m: Optional[float] = None        # TTM revenue $M
    ebitda_m: Optional[float] = None         # TTM EBITDA $M
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    pe_ratio: Optional[float] = None
    price_52w_change_pct: Optional[float] = None
    error: Optional[str] = None

    def row_md(self) -> str:
        def b(v):   return f"${v:.1f}B" if v is not None else "N/A"
        def x(v):   return f"{v:.1f}x"  if v is not None else "N/A"
        def pct(v): return f"{v:+.0f}%" if v is not None else "N/A"
        nm = (self.name or self.ticker)[:22]
        return (
            f"| {self.ticker} | {nm} | {b(self.market_cap_b)} | {b(self.ev_b)} "
            f"| {x(self.ev_ebitda)} | {x(self.ev_revenue)} | {pct(self.price_52w_change_pct)} |"
        )


@dataclass
class YFinanceResult:
    industry_label: str
    snapshots: list[TickerSnapshot] = field(default_factory=list)
    error: Optional[str] = None

    def to_markdown(self) -> str:
        if self.error and not self.snapshots:
            return f"_Yahoo Finance unavailable: {self.error}_"
        valid = [s for s in self.snapshots if not s.error and s.ev_b is not None]
        if not valid:
            return f"_Yahoo Finance: no valid comp data for {self.industry_label}._"
        lines = [
            f"**Public comp proxies — {self.industry_label}**",
            "",
            "| Ticker | Name | Mkt Cap | EV | EV/EBITDA | EV/Rev | 52W Chg |",
            "|---|---|---|---|---|---|---|",
        ]
        for s in valid:
            lines.append(s.row_md())
        multiples = [s.ev_ebitda for s in valid if s.ev_ebitda and 0 < s.ev_ebitda < 50]
        if multiples:
            med = sorted(multiples)[len(multiples) // 2]
            lines.append(f"\n**Median EV/EBITDA (public comps):** {med:.1f}x")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Fetch helpers (sync — run via executor)
# ---------------------------------------------------------------------------

def _fetch_ticker_sync(symbol: str) -> TickerSnapshot:
    snap = TickerSnapshot(ticker=symbol, name=symbol)
    if not _YF_AVAILABLE:
        snap.error = "yfinance not installed"
        return snap
    try:
        t = yf.Ticker(symbol)
        info = t.fast_info  # faster, fewer network calls
        full_info = t.info

        snap.name = full_info.get("shortName") or full_info.get("longName") or symbol

        # Market cap
        mc = info.market_cap if hasattr(info, "market_cap") else full_info.get("marketCap")
        if mc:
            snap.market_cap_b = mc / 1e9

        # EV
        ev = full_info.get("enterpriseValue")
        if ev:
            snap.ev_b = ev / 1e9

        # Revenue TTM
        rev = full_info.get("totalRevenue")
        if rev:
            snap.revenue_m = rev / 1e6

        # EBITDA TTM
        eb = full_info.get("ebitda")
        if eb:
            snap.ebitda_m = eb / 1e6

        # Multiples
        snap.ev_ebitda = full_info.get("enterpriseToEbitda")
        snap.ev_revenue = full_info.get("enterpriseToRevenue")
        snap.pe_ratio = full_info.get("trailingPE")

        # 52-week change
        hi52 = info.year_high if hasattr(info, "year_high") else full_info.get("fiftyTwoWeekHigh")
        lo52 = info.year_low  if hasattr(info, "year_low")  else full_info.get("fiftyTwoWeekLow")
        cur  = info.last_price if hasattr(info, "last_price") else full_info.get("currentPrice")
        snap.current_price = cur
        if cur and lo52 and hi52:
            mid52 = (hi52 + lo52) / 2
            if mid52 > 0:
                snap.price_52w_change_pct = (cur - mid52) / mid52 * 100

    except Exception as exc:
        snap.error = str(exc)[:100]
    return snap


# ---------------------------------------------------------------------------
# Public async entry point
# ---------------------------------------------------------------------------

async def fetch_yahoo_finance_comps(industry: str) -> YFinanceResult:
    """
    Fetch public comp proxies from Yahoo Finance for a given industry.
    Runs synchronous yfinance calls in a thread executor.
    """
    if not _YF_AVAILABLE:
        return YFinanceResult(
            industry_label=industry,
            error="yfinance not installed — run: pip install yfinance",
        )

    label, tickers = _match_industry(industry)
    result = YFinanceResult(industry_label=label)

    loop = asyncio.get_event_loop()
    tasks = [
        loop.run_in_executor(None, _fetch_ticker_sync, sym)
        for sym in tickers[:5]  # cap at 5 to keep latency under 10s
    ]
    result.snapshots = list(await asyncio.gather(*tasks))
    return result


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    import sys
    industry = sys.argv[1] if len(sys.argv) > 1 else "professional services"
    print(f"=== Yahoo Finance: {industry} ===\n")
    r = await fetch_yahoo_finance_comps(industry)
    print(r.to_markdown())


if __name__ == "__main__":
    asyncio.run(_test())
