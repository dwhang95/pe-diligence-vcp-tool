"""
Bureau of Labor Statistics (BLS) API client — labor benchmarks by industry.

Uses the BLS Public Data API v2:
  https://api.bls.gov/publicAPI/v2/timeseries/data/

Data returned:
  - Employment level (total employees, thousands)
  - Average hourly earnings
  - 5-year employment trend (growth/contraction signal)

Series ID format for CES (Current Employment Statistics):
  CEU{supersector_code}{data_type_code}
  Data types: 01=all employees (thousands), 08=avg hourly earnings

No API key required, but a free key (https://data.bls.gov/registrationApi)
increases rate limits from 25 req/day to 500 req/day. Key is read from
BLS_API_KEY env var if present.

Note: BLS uses its own industry classification (CES codes), not NAICS directly.
This module maintains a mapping from common PE industry terms to CES series IDs.
"""

import asyncio
import os
from dataclasses import dataclass, field
from typing import Optional
import httpx

_BLS_API = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# ---------------------------------------------------------------------------
# CES industry series ID mapping
#
# Format: (employment_series, earnings_series, label)
# Series IDs pulled from BLS CES supercategory codes.
# ---------------------------------------------------------------------------

# Maps keyword (lowercase) → (employment_series_id, hourly_earnings_series_id, label)
_NAICS_TO_BLS: list[tuple[str, str, str, str]] = [
    # (keyword, emp_series, earnings_series, label)
    # Manufacturing subsectors
    ("packaging",          "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("corrugated",         "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("paper",              "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("food manufactur",    "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("consumer product",   "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("cosmetic",           "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("chemical",           "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("printing",           "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    ("plastics",           "CEU3200000001", "CEU3200000008", "Manufacturing — Nondurable Goods"),
    # Durable goods manufacturing
    ("industrial machin",  "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("aerospace",          "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("auto part",          "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("metal",              "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("building product",   "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("hvac",               "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    ("electronics",        "CEU3100000001", "CEU3100000008", "Manufacturing — Durable Goods"),
    # Healthcare
    ("healthcare",         "CEU6562000001", "CEU6562000008", "Health Care & Social Assistance"),
    ("hospital",           "CEU6562000001", "CEU6562000008", "Health Care & Social Assistance"),
    ("physician",          "CEU6562000001", "CEU6562000008", "Health Care & Social Assistance"),
    ("dental",             "CEU6562000001", "CEU6562000008", "Health Care & Social Assistance"),
    ("home health",        "CEU6562000001", "CEU6562000008", "Health Care & Social Assistance"),
    # Professional & Business Services
    ("professional serv",  "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("business serv",      "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("consulting",         "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("accounting",         "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("staffing",           "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("software",           "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("it service",         "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    ("tech",               "CEU6000000001", "CEU6000000008", "Professional & Business Services"),
    # Wholesale & Distribution
    ("distribution",       "CEU4200000001", "CEU4200000008", "Wholesale Trade"),
    ("wholesale",          "CEU4200000001", "CEU4200000008", "Wholesale Trade"),
    # Transportation & Warehousing
    ("logistics",          "CEU4300000001", "CEU4300000008", "Transportation & Warehousing"),
    ("trucking",           "CEU4300000001", "CEU4300000008", "Transportation & Warehousing"),
    ("warehouse",          "CEU4300000001", "CEU4300000008", "Transportation & Warehousing"),
    # Retail
    ("retail",             "CEU4200000001", "CEU4200000008", "Retail Trade"),
    ("restaurant",         "CEU7000000001", "CEU7000000008", "Leisure & Hospitality"),
    ("food service",       "CEU7000000001", "CEU7000000008", "Leisure & Hospitality"),
    ("hotel",              "CEU7000000001", "CEU7000000008", "Leisure & Hospitality"),
    # Construction
    ("construction",       "CEU2000000001", "CEU2000000008", "Construction"),
    # Education
    ("education",          "CEU6500000001", "CEU6500000008", "Education & Health Services"),
]

# Fallback — Total Private sector
_FALLBACK = ("CEU0500000001", "CEU0500000008", "Total Private Sector")


def _get_series(industry: str) -> tuple[str, str, str]:
    lower = industry.lower()
    for keyword, emp, earn, label in _NAICS_TO_BLS:
        if keyword in lower:
            return emp, earn, label
    return _FALLBACK


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class LaborBenchmark:
    industry_label: str
    emp_series_id: str
    earn_series_id: str

    # Most recent values
    employment_thousands: Optional[float] = None      # Total employed, thousands
    avg_hourly_earnings: Optional[float] = None       # $ per hour
    avg_hourly_earnings_year: Optional[str] = None    # Year of data point

    # 5-year trend
    employment_5yr_ago: Optional[float] = None        # Employment 5 years prior
    employment_trend_pct: Optional[float] = None      # % change over 5 years

    error: Optional[str] = None

    def to_markdown(self) -> str:
        lines = [f"**Industry:** {self.industry_label}"]
        if self.avg_hourly_earnings is not None:
            lines.append(
                f"**Avg. Hourly Earnings:** ${self.avg_hourly_earnings:.2f}/hr "
                f"({self.avg_hourly_earnings_year or 'recent'})"
            )
        if self.employment_thousands is not None:
            lines.append(
                f"**Sector Employment:** {self.employment_thousands:,.0f}k workers (national)"
            )
        if self.employment_trend_pct is not None:
            direction = "growth" if self.employment_trend_pct >= 0 else "contraction"
            lines.append(
                f"**5-Year Employment Trend:** {self.employment_trend_pct:+.1f}% ({direction})"
            )
        if self.error:
            lines.append(f"_Data note: {self.error}_")
        return "\n".join(lines)

    def annualized_wage(self) -> Optional[float]:
        """Rough annualized wage assuming 2,080 hrs/year."""
        if self.avg_hourly_earnings is None:
            return None
        return self.avg_hourly_earnings * 2080


# ---------------------------------------------------------------------------
# BLS API call
# ---------------------------------------------------------------------------

def _build_payload(series_ids: list[str], api_key: str) -> dict:
    payload: dict = {
        "seriesid": series_ids,
        "startyear": str(2019),
        "endyear": str(2024),
    }
    if api_key:
        payload["registrationkey"] = api_key
    return payload


def _extract_latest(series_data: dict) -> tuple[Optional[float], Optional[str]]:
    """Return (latest_value, year) from a BLS series data block."""
    data_points = series_data.get("data", [])
    if not data_points:
        return None, None
    # BLS returns most recent first
    latest = data_points[0]
    try:
        val = float(latest["value"])
    except (KeyError, ValueError, TypeError):
        return None, None
    year = latest.get("year", "")
    return val, year


def _extract_5yr_ago(series_data: dict) -> Optional[float]:
    """Return the value from ~5 years before the most recent data point."""
    data_points = series_data.get("data", [])
    if len(data_points) < 2:
        return None
    # Data is newest-first. Find point closest to 5 years back.
    try:
        latest_year = int(data_points[0].get("year", 0))
        target_year = latest_year - 5
        candidates = [
            dp for dp in data_points
            if abs(int(dp.get("year", 0)) - target_year) <= 1
            and dp.get("period", "").startswith("M")  # monthly
        ]
        if candidates:
            return float(candidates[0]["value"])
    except (ValueError, TypeError):
        pass
    # Fallback: use last available data point
    try:
        return float(data_points[-1]["value"])
    except (ValueError, TypeError):
        return None


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def fetch_bls_benchmarks(
    industry: str,
    api_key: Optional[str] = None,
) -> LaborBenchmark:
    """
    Fetch labor benchmarks for an industry from BLS.

    Args:
        industry: Free-text industry description (used to look up CES series)
        api_key:  BLS registration key (reads BLS_API_KEY from env if not passed)

    Returns:
        LaborBenchmark with employment level, hourly earnings, and trend
    """
    if api_key is None:
        api_key = os.environ.get("BLS_API_KEY", "")

    emp_series, earn_series, label = _get_series(industry)
    bench = LaborBenchmark(
        industry_label=label,
        emp_series_id=emp_series,
        earn_series_id=earn_series,
    )

    payload = _build_payload([emp_series, earn_series], api_key)

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                _BLS_API,
                json=payload,
                headers={"Content-Type": "application/json"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        bench.error = f"BLS API request failed: {exc}"
        return bench

    if data.get("status") != "REQUEST_SUCCEEDED":
        msg = data.get("message", ["Unknown BLS error"])
        bench.error = f"BLS API error: {msg[0] if isinstance(msg, list) else msg}"
        return bench

    series_results = {s["seriesID"]: s for s in data.get("Results", {}).get("series", [])}

    # Employment
    emp_data = series_results.get(emp_series, {})
    bench.employment_thousands, _ = _extract_latest(emp_data)
    prior = _extract_5yr_ago(emp_data)
    if bench.employment_thousands is not None and prior and prior > 0:
        bench.employment_5yr_ago = prior
        bench.employment_trend_pct = (bench.employment_thousands - prior) / prior * 100

    # Earnings
    earn_data = series_results.get(earn_series, {})
    bench.avg_hourly_earnings, bench.avg_hourly_earnings_year = _extract_latest(earn_data)

    return bench


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    industries = [
        "professional services",
        "industrial packaging",
        "healthcare services",
    ]
    for ind in industries:
        print(f"=== BLS Benchmarks: {ind} ===")
        result = await fetch_bls_benchmarks(ind)
        print(result.to_markdown())
        ann = result.annualized_wage()
        if ann:
            print(f"Implied annualized wage: ~${ann:,.0f}/yr")
        if result.error:
            print(f"Error: {result.error}")
        print()


if __name__ == "__main__":
    asyncio.run(_test())
