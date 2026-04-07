"""
SEC EDGAR API client — public comp financials by SIC code.

Data flow:
  1. Fetch company list for a given SIC from the EDGAR Atom feed
  2. For each company, fetch structured XBRL financial facts
  3. Return normalized comp snapshots (revenue, op margin, capex intensity)

Rate limit: 10 req/sec per SEC Fair Access Policy.
No API key required; a descriptive User-Agent is mandatory per SEC guidelines.
"""

import asyncio
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
import httpx

# SEC requires an identifying User-Agent: https://www.sec.gov/os/accessing-edgar-data
_HEADERS = {
    "User-Agent": "PE-Diligence-Tool derek.whang@kellogg.northwestern.edu",
    "Accept-Encoding": "gzip, deflate",
}
_BASE = "https://data.sec.gov"
_EDGAR = "https://www.sec.gov"
_REQUEST_DELAY = 0.12  # ~8 req/sec — stay safely under the 10/sec limit

# ---------------------------------------------------------------------------
# Industry → SIC code lookup
# ---------------------------------------------------------------------------

# Maps common middle-market PE industry descriptions to 4-digit SIC codes.
# Lookup is case-insensitive substring match; first match wins.
_SIC_MAP: list[tuple[str, str, str]] = [
    # (keyword, sic_code, label)
    ("corrugated",        "2653", "Corrugated & Solid Fiber Boxes"),
    ("packaging",         "2650", "Paperboard Containers & Boxes"),
    ("paper",             "2670", "Converted Paper & Paperboard Products"),
    ("plastics",          "3086", "Plastics Foam Products"),
    ("specialty chemical","2819", "Industrial Inorganic Chemicals"),
    ("chemical",          "2860", "Industrial Chemicals & Synthetics"),
    ("food manufactur",   "2099", "Food Preparations NEC"),
    ("food service",      "5812", "Eating Places"),
    ("consumer product",  "2090", "Food & Kindred Products"),
    ("cosmetic",          "2844", "Perfumes, Cosmetics & Other Toilet Preparations"),
    ("industrial machin", "3559", "Special Industry Machinery"),
    ("aerospace",         "3812", "Defense Electronics & Communication Equipment"),
    ("auto part",         "3714", "Motor Vehicle Parts & Accessories"),
    ("healthcare service","8099", "Health Services NEC"),
    ("hospital",          "8062", "General Medical & Surgical Hospitals"),
    ("physician",         "8011", "Offices & Clinics of Doctors of Medicine"),
    ("dental",            "8021", "Offices & Clinics of Dentists"),
    ("home health",       "8082", "Home Health Care Services"),
    ("staffing",          "7363", "Help Supply Services"),
    ("professional serv", "7389", "Services — Misc Business Services NEC"),
    ("business serv",     "7389", "Services — Misc Business Services NEC"),
    ("accounting",        "7389", "Services — Misc Business Services NEC"),
    ("consulting",        "8742", "Management Consulting Services"),
    ("software",          "7372", "Prepackaged Software"),
    ("it service",        "7371", "Computer Programming, Data Processing"),
    ("tech",              "7372", "Prepackaged Software"),
    ("distribution",      "5040", "Professional & Commercial Equipment"),
    ("wholesale",         "5000", "Durable Goods — Wholesale"),
    ("logistics",         "4215", "Courier Services (No Air)"),
    ("trucking",          "4213", "Trucking, Except Local"),
    ("warehouse",         "4220", "Public Warehousing & Storage"),
    ("real estate",       "6500", "Real Estate"),
    ("insurance",         "6311", "Life Insurance"),
    ("retail",            "5900", "Retail Stores"),
    ("restaurant",        "5812", "Eating Places"),
    ("hotel",             "7011", "Hotels & Motels"),
    ("education",         "8200", "Educational Services"),
    ("media",             "7812", "Motion Picture Production"),
    ("printing",          "2750", "Commercial Printing"),
    ("construction",      "1731", "Electrical Work"),
    ("building product",  "3442", "Metal Doors, Sash, Frames & Trim"),
    ("hvac",              "3585", "Air-Conditioning & Warm Air Heating Equipment"),
]


class SICLookup:
    """Maps a free-text industry description to a SIC code."""

    @staticmethod
    def lookup(industry: str) -> tuple[str, str]:
        """
        Returns (sic_code, label). Falls back to ("7389", "Misc Business Services")
        if no keyword matches.
        """
        lower = industry.lower()
        for keyword, code, label in _SIC_MAP:
            if keyword in lower:
                return code, label
        return "7389", "Services — Misc Business Services NEC"


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------

@dataclass
class CompSnapshot:
    name: str
    cik: str
    sic: str
    revenue_m: Optional[float] = None        # Most recent annual revenue, $M
    op_income_m: Optional[float] = None      # Most recent annual operating income, $M
    op_margin_pct: Optional[float] = None    # op_income / revenue * 100
    capex_m: Optional[float] = None          # Most recent annual CapEx, $M
    capex_intensity_pct: Optional[float] = None  # capex / revenue * 100
    employees: Optional[int] = None
    fiscal_year: Optional[str] = None
    error: Optional[str] = None              # Set if fetch failed

    def revenue_str(self) -> str:
        return f"${self.revenue_m:.0f}M" if self.revenue_m is not None else "N/A"

    def op_margin_str(self) -> str:
        return f"{self.op_margin_pct:.1f}%" if self.op_margin_pct is not None else "N/A"

    def capex_intensity_str(self) -> str:
        return f"{self.capex_intensity_pct:.1f}%" if self.capex_intensity_pct is not None else "N/A"


@dataclass
class CompsResult:
    sic_code: str
    sic_label: str
    comps: list[CompSnapshot] = field(default_factory=list)
    error: Optional[str] = None

    def median_op_margin(self) -> Optional[float]:
        vals = [c.op_margin_pct for c in self.comps if c.op_margin_pct is not None]
        if not vals:
            return None
        vals.sort()
        mid = len(vals) // 2
        return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2

    def median_capex_intensity(self) -> Optional[float]:
        vals = [c.capex_intensity_pct for c in self.comps if c.capex_intensity_pct is not None]
        if not vals:
            return None
        vals.sort()
        mid = len(vals) // 2
        return vals[mid] if len(vals) % 2 else (vals[mid - 1] + vals[mid]) / 2

    def to_markdown_table(self) -> str:
        if not self.comps:
            return "_No public comp data available for this SIC code._"
        rows = ["| Company | Revenue | Op Margin | CapEx Intensity | Fiscal Year |",
                "|---|---|---|---|---|"]
        for c in self.comps:
            rows.append(
                f"| {c.name} | {c.revenue_str()} | {c.op_margin_str()} "
                f"| {c.capex_intensity_str()} | {c.fiscal_year or 'N/A'} |"
            )
        # Benchmark row
        med_margin = self.median_op_margin()
        med_capex = self.median_capex_intensity()
        rows.append(
            f"| **Median** | — | "
            f"**{f'{med_margin:.1f}%' if med_margin is not None else 'N/A'}** | "
            f"**{f'{med_capex:.1f}%' if med_capex is not None else 'N/A'}** | — |"
        )
        return "\n".join(rows)


# ---------------------------------------------------------------------------
# EDGAR Atom feed — company list by SIC
# ---------------------------------------------------------------------------

def _parse_atom_feed(xml_text: str) -> list[tuple[str, str]]:
    """
    Parse EDGAR Atom feed. Returns list of ("", cik) tuples.
    Company names are fetched from XBRL facts (Atom titles are corrupted in EDGAR's output).
    CIK is zero-padded to 10 digits for API calls.

    EDGAR Atom <id> format: urn:tag:www.sec.gov:cik=0001161343
    """
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []

    ns = {"atom": "http://www.w3.org/2005/Atom"}
    results = []
    for entry in root.findall("atom:entry", ns):
        id_el = entry.find("atom:id", ns)
        if id_el is None or not id_el.text:
            continue
        # Format: urn:tag:www.sec.gov:cik=0001161343
        cik_match = re.search(r"cik=(\d+)", id_el.text, re.IGNORECASE)
        if not cik_match:
            # Fallback: CIK in link href
            link_el = entry.find("atom:link", ns)
            href = (link_el.get("href") or "") if link_el is not None else ""
            cik_match = re.search(r"CIK=(\d+)", href)
        if cik_match:
            cik = cik_match.group(1).zfill(10)
            results.append(("", cik))  # name resolved from XBRL entityName
    return results


# ---------------------------------------------------------------------------
# XBRL facts — financial data for a single company
# ---------------------------------------------------------------------------

_REVENUE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
    "SalesRevenueGoodsNet",
    "NetRevenues",
]

_OP_INCOME_TAGS = [
    "OperatingIncomeLoss",
]

_CAPEX_TAGS = [
    "PaymentsToAcquirePropertyPlantAndEquipment",
    "CapitalExpendituresIncurringObligation",
    "PaymentsForCapitalImprovements",
]

_EMPLOYEE_TAGS = [
    "EntityNumberOfEmployees",
]


def _latest_annual_value(facts_usgaap: dict, tags: list[str]) -> tuple[Optional[float], Optional[str]]:
    """
    For a list of candidate GAAP tags, return the most recent annual (10-K) value
    and fiscal year. Values are in raw dollars; we convert to $M.
    """
    for tag in tags:
        tag_data = facts_usgaap.get(tag)
        if not tag_data:
            continue
        units = tag_data.get("units", {})
        usd_entries = units.get("USD", [])
        if not usd_entries:
            continue
        # Filter to annual 10-K filings only (form == "10-K"), pick most recent end date
        annual = [e for e in usd_entries if e.get("form") == "10-K"]
        if not annual:
            # Fall back to any entry if no 10-K found
            annual = usd_entries
        # Sort by end date descending, take most recent
        annual.sort(key=lambda e: e.get("end", ""), reverse=True)
        best = annual[0]
        val = best.get("val")
        fy = best.get("end", "")[:4] if best.get("end") else None
        if val is not None:
            return float(val) / 1_000_000, fy  # convert to $M
    return None, None


def _latest_employee_count(facts_dei: dict) -> Optional[int]:
    for tag in _EMPLOYEE_TAGS:
        tag_data = facts_dei.get(tag)
        if not tag_data:
            continue
        entries = tag_data.get("units", {}).get("pure", [])
        if not entries:
            continue
        entries.sort(key=lambda e: e.get("end", ""), reverse=True)
        val = entries[0].get("val")
        if val is not None:
            return int(val)
    return None


async def _fetch_comp_snapshot(
    client: httpx.AsyncClient, name: str, cik: str, sic: str
) -> CompSnapshot:
    snap = CompSnapshot(name=name or f"CIK {cik}", cik=cik, sic=sic)
    url = f"{_BASE}/api/xbrl/companyfacts/CIK{cik}.json"
    try:
        await asyncio.sleep(_REQUEST_DELAY)
        resp = await client.get(url, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:
        snap.error = f"XBRL fetch failed: {exc}"
        return snap

    # Use entityName from XBRL response (Atom feed titles are corrupted)
    snap.name = data.get("entityName") or name or f"CIK {cik}"

    facts = data.get("facts", {})
    usgaap = facts.get("us-gaap", {})
    dei = facts.get("dei", {})

    snap.revenue_m, snap.fiscal_year = _latest_annual_value(usgaap, _REVENUE_TAGS)
    snap.op_income_m, _ = _latest_annual_value(usgaap, _OP_INCOME_TAGS)
    snap.capex_m, _ = _latest_annual_value(usgaap, _CAPEX_TAGS)
    snap.employees = _latest_employee_count(dei)

    if snap.revenue_m and snap.revenue_m > 0:
        if snap.op_income_m is not None:
            snap.op_margin_pct = snap.op_income_m / snap.revenue_m * 100
        if snap.capex_m is not None:
            snap.capex_intensity_pct = snap.capex_m / snap.revenue_m * 100

    return snap


# ---------------------------------------------------------------------------
# Public entry point
# ---------------------------------------------------------------------------

async def fetch_sec_comps(
    industry: str,
    sic_code: Optional[str] = None,
    n: int = 6,
    min_revenue_m: float = 50.0,
    min_fiscal_year: int = 2020,
) -> CompsResult:
    """
    Pull public comp financials from SEC EDGAR for a given industry.

    Args:
        industry:        Free-text industry description (used for SIC lookup if sic_code not given)
        sic_code:        Override SIC code (4-digit string); if None, auto-detected from industry
        n:               Max number of comps to return (default 6)
        min_revenue_m:   Filter out companies with revenue below this threshold (default $50M)
        min_fiscal_year: Filter out companies whose most recent data is older than this year

    Returns:
        CompsResult with a list of CompSnapshot objects and benchmark medians
    """
    if sic_code is None:
        sic_code, label = SICLookup.lookup(industry)
    else:
        label = f"SIC {sic_code}"

    result = CompsResult(sic_code=sic_code, sic_label=label)

    # Step 1: Get company list from EDGAR Atom feed (fetch 80 to have enough after filtering)
    atom_url = (
        f"{_EDGAR}/cgi-bin/browse-edgar"
        f"?action=getcompany&SIC={sic_code}&dateb=&owner=include&count=80"
        f"&search_text=&output=atom"
    )
    try:
        async with httpx.AsyncClient() as client:
            resp = await client.get(atom_url, headers=_HEADERS, timeout=15)
            resp.raise_for_status()
            companies = _parse_atom_feed(resp.text)
    except Exception as exc:
        result.error = f"EDGAR company list fetch failed: {exc}"
        return result

    if not companies:
        result.error = "No companies found for this SIC code in EDGAR."
        return result

    # Step 2: Fetch XBRL facts — scan up to n*5 companies to find n valid ones
    candidates = companies[: n * 5]
    valid: list[CompSnapshot] = []

    async with httpx.AsyncClient() as client:
        for name, cik in candidates:
            if len(valid) >= n:
                break
            snap = await _fetch_comp_snapshot(client, name, cik, sic_code)
            # Filter: needs revenue data, above minimum, and recent enough
            if (
                snap.error is None
                and snap.revenue_m is not None
                and snap.revenue_m >= min_revenue_m
                and snap.fiscal_year is not None
                and int(snap.fiscal_year) >= min_fiscal_year
            ):
                valid.append(snap)

    # Step 3: Rank by revenue descending
    valid.sort(key=lambda s: s.revenue_m or 0, reverse=True)
    result.comps = valid[:n]

    if not result.comps:
        result.error = (
            f"No companies in SIC {sic_code} had revenue ≥${min_revenue_m:.0f}M "
            f"with data from {min_fiscal_year} or later."
        )

    return result


# ---------------------------------------------------------------------------
# CLI test
# ---------------------------------------------------------------------------

async def _test():
    print("=== SEC EDGAR Test: Professional Services (SIC 7389) ===\n")
    result = await fetch_sec_comps("business services", n=5)
    print(f"SIC: {result.sic_code} — {result.sic_label}")
    print(f"Comps found: {len(result.comps)}")
    if result.error:
        print(f"Error: {result.error}")
    print()
    for c in result.comps:
        print(f"  {c.name} (CIK {c.cik})")
        print(f"    Revenue: {c.revenue_str()} | Op Margin: {c.op_margin_str()} "
              f"| CapEx: {c.capex_intensity_str()} | FY: {c.fiscal_year}")
    print()
    print("--- Comp Table ---")
    print(result.to_markdown_table())
    print()
    med = result.median_op_margin()
    print(f"Median Op Margin: {f'{med:.1f}%' if med is not None else 'N/A'}")


if __name__ == "__main__":
    asyncio.run(_test())
