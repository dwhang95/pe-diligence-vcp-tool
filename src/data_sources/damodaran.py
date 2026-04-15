"""
damodaran.py — NYU Damodaran Industry Multiples.

Fetches EV/EBITDA and operating margin benchmarks from Aswath Damodaran's
publicly available annual dataset (pages.stern.nyu.edu/~adamodar/).

Data is updated every January. We fetch live and parse the HTML table.
Falls back to a cached set of representative multiples if the fetch fails.
"""

import asyncio
import re
from dataclasses import dataclass
from typing import Optional

import httpx

# ---------------------------------------------------------------------------
# Damodaran dataset URL — EV multiples by industry
# ---------------------------------------------------------------------------

_DAMODARAN_URL = (
    "https://pages.stern.nyu.edu/~adamodar/New_Home_Page/datafile/vebitda.html"
)
_HEADERS = {"User-Agent": "PE-Diligence-Tool derek.whang@kellogg.northwestern.edu"}


# ---------------------------------------------------------------------------
# Industry keyword → Damodaran industry name mapping
# Damodaran uses his own classification; we fuzzy-match our PE industry terms
# ---------------------------------------------------------------------------

_DAMO_MAP: list[tuple[str, str]] = [
    # (our_keyword, damodaran_industry_substring)
    ("packaging",        "Paper/Forest"),
    ("corrugated",       "Paper/Forest"),
    ("paper",            "Paper/Forest"),
    ("plastics",         "Chemical (Specialty)"),
    ("chemical",         "Chemical"),
    ("cosmetic",         "Household Products"),
    ("beauty",           "Household Products"),
    ("baby",             "Household Products"),
    ("consumer product", "Consumer Products"),
    ("food manufactur",  "Food Processing"),
    ("food service",     "Restaurant/Dining"),
    ("restaurant",       "Restaurant/Dining"),
    ("hotel",            "Hotel/Gaming"),
    ("healthcare serv",  "Healthcare Support"),
    ("hospital",         "Hospitals/Healthcare"),
    ("physician",        "Healthcare Support"),
    ("home health",      "Healthcare Support"),
    ("staffing",         "Human Resources"),
    ("professional",     "Information Services"),
    ("business serv",    "Business & Consumer Services"),
    ("consulting",       "Business & Consumer Services"),
    ("accounting",       "Business & Consumer Services"),
    ("software",         "Software (System & Application)"),
    ("it service",       "IT Services"),
    ("tech",             "Electronics"),
    ("distribution",     "Distributors"),
    ("wholesale",        "Distributors"),
    ("logistics",        "Transportation"),
    ("trucking",         "Trucking"),
    ("construction",     "Engineering/Construction"),
    ("building",         "Building Materials"),
    ("hvac",             "Machinery"),
    ("industrial",       "Machinery"),
    ("aerospace",        "Aerospace/Defense"),
    ("auto part",        "Auto Parts"),
    ("retail",           "Retail (General)"),
    ("education",        "Education"),
    ("media",            "Broadcasting"),
    ("printing",         "Publishing & Newspapers"),
    ("real estate",      "Real Estate (Services)"),
]


def _match_damodaran_industry(industry: str) -> str:
    lower = industry.lower()
    for keyword, damo_label in _DAMO_MAP:
        if keyword in lower:
            return damo_label
    return "Business & Consumer Services"


# ---------------------------------------------------------------------------
# Fallback multiples (2024 Damodaran dataset approximations)
# Used when live fetch fails.
# ---------------------------------------------------------------------------

_FALLBACK_MULTIPLES: dict[str, dict] = {
    "Paper/Forest":                 {"ev_ebitda": 8.5,  "ev_revenue": 1.1, "op_margin": 10.2},
    "Chemical":                     {"ev_ebitda": 9.2,  "ev_revenue": 1.4, "op_margin": 11.5},
    "Chemical (Specialty)":         {"ev_ebitda": 10.1, "ev_revenue": 1.8, "op_margin": 13.4},
    "Household Products":           {"ev_ebitda": 12.4, "ev_revenue": 2.1, "op_margin": 14.8},
    "Consumer Products":            {"ev_ebitda": 11.2, "ev_revenue": 1.6, "op_margin": 12.1},
    "Food Processing":              {"ev_ebitda": 10.8, "ev_revenue": 1.2, "op_margin": 10.4},
    "Restaurant/Dining":            {"ev_ebitda": 12.7, "ev_revenue": 1.8, "op_margin": 12.9},
    "Hotel/Gaming":                 {"ev_ebitda": 11.4, "ev_revenue": 2.2, "op_margin": 14.1},
    "Healthcare Support":           {"ev_ebitda": 13.5, "ev_revenue": 1.4, "op_margin": 9.8},
    "Hospitals/Healthcare":         {"ev_ebitda": 10.9, "ev_revenue": 0.8, "op_margin": 7.2},
    "Human Resources":              {"ev_ebitda": 10.3, "ev_revenue": 0.5, "op_margin": 5.4},
    "Business & Consumer Services": {"ev_ebitda": 12.1, "ev_revenue": 1.8, "op_margin": 11.2},
    "Information Services":         {"ev_ebitda": 14.3, "ev_revenue": 3.2, "op_margin": 18.1},
    "Software (System & Application)": {"ev_ebitda": 22.4, "ev_revenue": 6.8, "op_margin": 17.6},
    "IT Services":                  {"ev_ebitda": 13.8, "ev_revenue": 1.6, "op_margin": 10.1},
    "Electronics":                  {"ev_ebitda": 11.6, "ev_revenue": 1.4, "op_margin": 9.8},
    "Distributors":                 {"ev_ebitda": 9.4,  "ev_revenue": 0.4, "op_margin": 4.8},
    "Transportation":               {"ev_ebitda": 8.7,  "ev_revenue": 1.1, "op_margin": 9.4},
    "Trucking":                     {"ev_ebitda": 7.9,  "ev_revenue": 0.8, "op_margin": 8.6},
    "Engineering/Construction":     {"ev_ebitda": 8.2,  "ev_revenue": 0.5, "op_margin": 5.1},
    "Building Materials":           {"ev_ebitda": 10.4, "ev_revenue": 1.4, "op_margin": 11.8},
    "Machinery":                    {"ev_ebitda": 11.3, "ev_revenue": 1.7, "op_margin": 12.4},
    "Aerospace/Defense":            {"ev_ebitda": 14.2, "ev_revenue": 1.8, "op_margin": 11.3},
    "Auto Parts":                   {"ev_ebitda": 6.8,  "ev_revenue": 0.5, "op_margin": 5.9},
    "Retail (General)":             {"ev_ebitda": 9.8,  "ev_revenue": 0.6, "op_margin": 5.2},
    "Education":                    {"ev_ebitda": 9.1,  "ev_revenue": 1.4, "op_margin": 10.3},
    "Broadcasting":                 {"ev_ebitda": 10.2, "ev_revenue": 2.1, "op_margin": 15.6},
    "Publishing & Newspapers":      {"ev_ebitda": 7.4,  "ev_revenue": 1.0, "op_margin": 8.4},
    "Real Estate (Services)":       {"ev_ebitda": 13.6, "ev_revenue": 1.1, "op_margin": 7.8},
}


# ---------------------------------------------------------------------------
# Data structure
# ---------------------------------------------------------------------------

@dataclass
class DamodaranResult:
    industry_label: str          # Matched Damodaran industry name
    ev_ebitda: Optional[float] = None
    ev_revenue: Optional[float] = None
    op_margin_pct: Optional[float] = None
    n_firms: Optional[int] = None
    data_year: Optional[str] = None
    source: str = "fallback"     # "live" or "fallback"
    error: Optional[str] = None

    def to_markdown(self) -> str:
        if self.error and self.ev_ebitda is None:
            return f"_Damodaran data unavailable: {self.error}_"

        def x(v): return f"{v:.1f}x" if v is not None else "N/A"
        def p(v): return f"{v:.1f}%" if v is not None else "N/A"
        n_str = f" (n={self.n_firms} firms)" if self.n_firms else ""

        lines = [
            f"**Damodaran Industry Benchmarks — {self.industry_label}{n_str}**",
            f"_(Source: NYU Damodaran, {self.data_year or 'latest'} — {self.source} data)_",
            "",
            f"| Metric | Value |",
            f"|---|---|",
            f"| EV/EBITDA | {x(self.ev_ebitda)} |",
            f"| EV/Revenue | {x(self.ev_revenue)} |",
            f"| Operating Margin | {p(self.op_margin_pct)} |",
        ]
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML parsing helpers
# ---------------------------------------------------------------------------

def _parse_float(text: str) -> Optional[float]:
    """Parse a cell value like '12.34' or '12.34%' or 'NA'."""
    clean = re.sub(r"[%,$\s]", "", text.strip())
    if not clean or clean.upper() in ("NA", "N/A", "-", ""):
        return None
    try:
        return float(clean)
    except ValueError:
        return None


def _parse_int(text: str) -> Optional[int]:
    clean = re.sub(r"[,\s]", "", text.strip())
    try:
        return int(clean)
    except ValueError:
        return None


def _parse_damodaran_table(html: str, target_industry: str) -> Optional[DamodaranResult]:
    """
    Parse Damodaran's vebitda.html table.
    Columns (approximate): Industry Name | # Firms | EV/EBITDA | EV/EBIT | EV/EBITDA(adj) | ...
    We look for the row whose industry name best matches target_industry.
    """
    from lxml import html as lxml_html

    try:
        tree = lxml_html.fromstring(html)
    except Exception:
        return None

    # Find all table rows
    rows = tree.xpath("//table//tr")
    if not rows:
        return None

    # Find header row to understand column positions
    header_cols: list[str] = []
    for row in rows[:5]:
        cells = row.xpath(".//th | .//td")
        texts = [c.text_content().strip().lower() for c in cells]
        if any("industry" in t for t in texts):
            header_cols = texts
            break

    # Column index detection
    idx_industry = 0
    idx_n_firms  = 1
    idx_ev_ebitda = 2
    for i, h in enumerate(header_cols):
        if "firm" in h:
            idx_n_firms = i
        elif "ev/ebitda" in h and idx_ev_ebitda == 2:
            idx_ev_ebitda = i

    target_lower = target_industry.lower()
    best_row = None
    best_score = 0

    for row in rows:
        cells = row.xpath(".//td")
        if len(cells) <= idx_ev_ebitda:
            continue
        name = cells[idx_industry].text_content().strip()
        if not name:
            continue
        name_lower = name.lower()
        # Score: count how many words from target appear in name
        score = sum(1 for w in target_lower.split("/") if w.strip() in name_lower)
        # Bonus: substring match
        if any(part in name_lower for part in target_lower.split("/")):
            score += 2
        if score > best_score:
            best_score = score
            best_row = cells

    if not best_row or best_score == 0:
        return None

    name = best_row[idx_industry].text_content().strip()
    n_firms = _parse_int(best_row[idx_n_firms].text_content()) if len(best_row) > idx_n_firms else None
    ev_ebitda = _parse_float(best_row[idx_ev_ebitda].text_content()) if len(best_row) > idx_ev_ebitda else None

    # Try to find EV/Revenue and operating margin columns
    ev_revenue = None
    op_margin = None
    for i, cell in enumerate(best_row):
        if i in (idx_industry, idx_n_firms, idx_ev_ebitda):
            continue
        val = _parse_float(cell.text_content())
        if val is None:
            continue
        # Heuristic: op margin is usually < 40%, EV/Revenue is 0.1–15x
        if op_margin is None and 0 < val < 40:
            op_margin = val
        elif ev_revenue is None and 0 < val < 15:
            ev_revenue = val

    if ev_ebitda is None:
        return None

    return DamodaranResult(
        industry_label=name,
        ev_ebitda=ev_ebitda,
        ev_revenue=ev_revenue,
        op_margin_pct=op_margin,
        n_firms=n_firms,
        source="live",
    )


# ---------------------------------------------------------------------------
# Public async entry point
# ---------------------------------------------------------------------------

async def fetch_damodaran_multiples(industry: str) -> DamodaranResult:
    """
    Fetch industry EV multiples from NYU Damodaran dataset.
    Falls back to embedded 2024 approximations if the live fetch fails.
    """
    damo_industry = _match_damodaran_industry(industry)

    # Try live fetch
    try:
        async with httpx.AsyncClient(headers=_HEADERS, timeout=15) as client:
            resp = await client.get(_DAMODARAN_URL, follow_redirects=True)
            resp.raise_for_status()
            parsed = _parse_damodaran_table(resp.text, damo_industry)
            if parsed:
                parsed.data_year = "2025"
                return parsed
    except Exception as exc:
        pass  # fall through to fallback

    # Fallback
    fallback = _FALLBACK_MULTIPLES.get(damo_industry, _FALLBACK_MULTIPLES["Business & Consumer Services"])
    return DamodaranResult(
        industry_label=damo_industry,
        ev_ebitda=fallback["ev_ebitda"],
        ev_revenue=fallback["ev_revenue"],
        op_margin_pct=fallback["op_margin"],
        data_year="2024",
        source="fallback",
    )


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    import sys
    industry = sys.argv[1] if len(sys.argv) > 1 else "professional services"
    print(f"=== Damodaran Multiples: {industry} ===\n")
    r = await fetch_damodaran_multiples(industry)
    print(r.to_markdown())


if __name__ == "__main__":
    asyncio.run(_test())
