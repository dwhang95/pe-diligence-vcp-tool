"""
naver_finance.py — Naver Finance data for Korean/Asian companies.

Calls naver_finance.js (Puppeteer subprocess) to scrape finance.naver.com.
Returns structured company financial data in Korean Won (KRW).

Best used when:
  - Target is a Korean KOSPI/KOSDAQ listed company
  - Need Korean market context for a transaction (Widus-style deals)
  - Comparable Korean listed companies for an M&A transaction

USD conversion uses a hardcoded approximate rate; real-time FX is not fetched
(add yfinance USDKRW=X call if precision matters).
"""

import asyncio
import json
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

_SCRAPER_JS = Path(__file__).parent / "naver_finance.js"
_PROJECT_ROOT = Path(__file__).parent.parent.parent

# Approximate USD/KRW rate — update periodically or fetch dynamically
_USD_KRW_APPROX = 1_350.0


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class NaverFinanceResult:
    company_name: str
    stock_code: str = ""
    exchange: str = "KOSPI/KOSDAQ"
    current_price_krw: Optional[int] = None
    page_url: str = ""
    metrics: dict = field(default_factory=dict)  # raw metrics dict from JS
    error: Optional[str] = None

    def current_price_usd(self) -> Optional[float]:
        if self.current_price_krw is None:
            return None
        return self.current_price_krw / _USD_KRW_APPROX

    def to_markdown(self) -> str:
        if self.error:
            return f"_Naver Finance: {self.error}_"

        lines = [
            f"**Naver Finance — {self.company_name}** "
            f"({'KOSPI/KOSDAQ'} · {self.stock_code})",
            "",
        ]

        if self.current_price_krw:
            usd = self.current_price_usd()
            usd_str = f" (~${usd:,.2f} USD)" if usd else ""
            lines.append(f"**Current Price:** ₩{self.current_price_krw:,}{usd_str}")

        # Key metrics
        metric_labels = {
            "per":                    "PER (P/E)",
            "pbr":                    "PBR (P/B)",
            "roe_pct":                "ROE",
            "market_cap_display":     "Market Cap",
            "revenue_display":        "Revenue (TTM)",
            "operating_income_display": "Operating Income",
            "net_income_display":     "Net Income",
            "debt_ratio_pct":         "Debt Ratio",
            "dividend_yield_pct":     "Dividend Yield",
            "eps_krw":                "EPS (KRW)",
        }

        for key, label in metric_labels.items():
            val = self.metrics.get(key)
            if val:
                lines.append(f"**{label}:** {val}")

        if self.page_url:
            lines.append(f"\n_Source: {self.page_url}_")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Subprocess call
# ---------------------------------------------------------------------------

async def fetch_naver_finance(company_name: str) -> NaverFinanceResult:
    """
    Fetch company financial data from Naver Finance via Puppeteer.

    Args:
        company_name: Company name in Korean or English (Korean works better
                      for KOSPI/KOSDAQ lookups)

    Returns:
        NaverFinanceResult with stock metrics and KRW pricing
    """
    result = NaverFinanceResult(company_name=company_name)

    if not _SCRAPER_JS.exists():
        result.error = f"Scraper not found: {_SCRAPER_JS}"
        return result

    node_modules = _PROJECT_ROOT / "node_modules" / "puppeteer"
    if not node_modules.exists():
        result.error = "puppeteer not installed — run: npm install (in pe-diligence-tool/)"
        return result

    loop = asyncio.get_event_loop()
    try:
        proc = await loop.run_in_executor(
            None,
            lambda: subprocess.run(
                ["node", str(_SCRAPER_JS), company_name],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(_PROJECT_ROOT),
            ),
        )
    except subprocess.TimeoutExpired:
        result.error = "Naver Finance scrape timed out (60s)"
        return result
    except Exception as exc:
        result.error = f"Subprocess error: {exc}"
        return result

    if proc.returncode != 0:
        result.error = (
            proc.stderr.strip()[:200] if proc.stderr.strip()
            else f"Scraper exited {proc.returncode}"
        )
        return result

    try:
        data = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        result.error = f"Invalid JSON from scraper: {exc}"
        return result

    result.stock_code         = data.get("stock_code", "")
    result.company_name       = data.get("company_name", company_name)
    result.exchange           = data.get("exchange", "KOSPI/KOSDAQ")
    result.current_price_krw  = data.get("current_price_krw")
    result.page_url           = data.get("page_url", "")
    result.metrics            = data.get("metrics", {})

    return result


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else "삼성전자"
    print(f"=== Naver Finance: {company} ===\n")
    r = await fetch_naver_finance(company)
    if r.error:
        print(f"Error: {r.error}")
    else:
        print(r.to_markdown())


if __name__ == "__main__":
    asyncio.run(_test())
