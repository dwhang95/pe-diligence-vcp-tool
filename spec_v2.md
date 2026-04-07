# PE Ops Tool Suite — v2 Spec

**Version:** 2.0
**Author:** Derek Whang
**Date:** 2026-04-04
**Status:** Draft

---

## Overview

v2 expands the original single-module CLI into a two-module PE ops tool suite:

| Module | Who Uses It | When | Output |
|---|---|---|---|
| **Module 1: Deal Diligence Brief** | Deal team, ops partner | Pre-IC, early diligence | Ops risk brief with real comp data |
| **Module 2: Value Creation Planner** | PortCo CEO/CFO, ops partner | Day 1–100, annual planning | Structured VCP with KPI benchmarks |

Both modules share the same research infrastructure, data sources, and LLM pipeline.

---

## What's New in v2

### Module 1 Enhancements (Deal Diligence Brief)
- **Real data integration:** Comparable company benchmarks pulled from SEC EDGAR, BLS, and NewsAPI
- **Comp table:** Automatically generated with 3–5 public comps (revenue, EBITDA margin, EV/EBITDA, EV/Revenue)
- **Labor benchmarking:** BLS wage and headcount data by NAICS code surfaced in People & Org risk section
- **News sweep:** Automated news pull flags recent leadership changes, regulatory issues, customer signals
- **New section:** Comparable Companies & Benchmarks (Section 3, pushed IT to Section 4)

### Module 2 (Value Creation Planner) — Net New
Full spec below.

---

## Module 1: Deal Diligence Brief (v2)

### What Changes from v1

#### New: Section 3 — Comparable Companies & Benchmarks

Replaces the static "Data Sources Consulted" section (moved to an appendix). Auto-generated using real data pulls.

**Structure:**
```
### 3. Comparable Companies & Benchmarks

**Public Comps (SIC: [code])**

| Company | Revenue | EBITDA Margin | EV/EBITDA | EV/Revenue | Source |
|---|---|---|---|---|---|
| [Name] | $XXXm | XX% | Xx | Xx | SEC 10-K (FY24) |

**Industry Benchmarks (NAICS: [code])**
- Median EBITDA margin: XX%
- Labor cost as % of revenue: XX%
- CapEx as % of revenue: XX%
- Avg. revenue per employee: $XXXk
- Source: SEC EDGAR public comps + BLS NAICS data

**Wage Benchmarks (Key Roles)**
- Production/operations workers: $XX–$XX/hr (national median: $XX)
- Engineering/technical: $XXk–$XXk/yr
- Management: $XXk–$XXk/yr
- Source: BLS OES survey, [year]

**Implication for Thesis:**
[1–2 sentences: how the target's profile compares to benchmarks — above/below median margins, labor cost risk, etc.]
```

#### Enhanced: Section 2 — Operational Risk Flags

People & Org risk now incorporates BLS wage benchmarks to flag compensation risk. Customer Concentration pulls any named customers from news sweep.

#### Enhanced: Section 7 — Data Sources Consulted (Appendix)

Moves to appendix. Now includes structured listing of all API calls made, URLs fetched, and any data gaps.

---

### Data Source Integration (Top 3)

#### Source 1: SEC EDGAR — Public Comp Benchmarks

**What we pull:**
- 3–5 public companies in the same SIC code as the target
- Latest 10-K financial data: revenue, COGS, operating income, CapEx, headcount (if disclosed)
- Calculate: EBITDA margin (approx), EV/EBITDA using market cap + debt, CapEx intensity

**Access method:**
- `https://data.sec.gov/submissions/` — company lookup by CIK or name
- `https://data.sec.gov/api/xbrl/companyfacts/` — structured XBRL financial data per company
- Python: `requests` + direct API (no library required)
- SIC code lookup: `https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={code}`

**How it improves the brief:**
Replaces fully hypothetical benchmarks with real public company data. The brief can now say "Median EBITDA margin for public packaging companies is 14%; target's profile implies it is likely in the 10–16% range based on cost structure signals" rather than speaking in generalities.

**Implementation in `researcher.py`:**
```python
def fetch_sec_comps(sic_code: str, n=5) -> list[dict]:
    """
    Pull n public companies from SEC EDGAR by SIC code.
    Returns list of dicts: {name, cik, revenue, op_income, capex, employees}
    """
    # 1. GET https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&SIC={sic_code}
    # 2. Extract CIK numbers for top n companies
    # 3. For each CIK: GET https://data.sec.gov/api/xbrl/companyfacts/{cik}.json
    # 4. Parse: us-gaap/Revenues, us-gaap/OperatingIncomeLoss, us-gaap/CapitalExpenditureDiscontinuedOperation
    # 5. Return normalized dict
```

**Rate limits:** Max 10 req/sec; no auth required.
**Cost:** Free.
**Latency:** ~5–15 sec for 5 comps.

---

#### Source 2: Bureau of Labor Statistics (BLS) — Labor & Wage Benchmarks

**What we pull:**
- Employment level by NAICS code (2-digit and 4-digit)
- Average hourly wages for key occupation groups relevant to the industry
- 5-year employment trend (hiring velocity signal for the sector)

**Access method:**
- `https://api.bls.gov/publicAPI/v2/timeseries/data/`
- Series IDs constructed from NAICS code + data type prefix (e.g., `CEU3200000001` = employment in manufacturing)
- Free API key from `https://data.bls.gov/registrationApi` (unlocks higher rate limits)

**How it improves the brief:**
People & Org risk section gains real numbers: "BLS data shows average hourly wages for packaging production workers in the Midwest at $22.40/hr. If the target is paying below this, expect retention risk post-close and budget for ~8–12% wage inflation in the VCP."

**Implementation in `researcher.py`:**
```python
def fetch_bls_labor_benchmarks(naics_code: str) -> dict:
    """
    Returns labor benchmarks for the industry.
    Dict: {avg_hourly_wage, employment_level, 5yr_employment_trend, key_roles: [...]}
    """
    # Series mapping: CEU + industry prefix + data type
    # Data type: 01=employees, 03=avg weekly hours, 08=avg hourly earnings
    # POST https://api.bls.gov/publicAPI/v2/timeseries/data/
    # Body: {"seriesid": ["CEU{naics_prefix}0000001", "CEU{naics_prefix}0000008"], "startyear": "2019", "endyear": "2024"}
```

**Rate limits:** 25 req/day without key, 500 req/day with free key.
**Cost:** Free.
**Latency:** ~2–3 sec per query.

---

#### Source 3: NewsAPI — Recent Company News Sweep

**What we pull:**
- Last 90 days of news for the company name
- Categorized: leadership changes, customer wins/losses, regulatory/legal, M&A, layoffs/hiring
- Negative signal extraction (risk flags)

**Access method:**
- `https://newsapi.org/v2/everything?q={company_name}&from={90_days_ago}&sortBy=relevancy`
- Free tier: 100 req/day, 30-day lookback
- Developer plan (~$30/mo): 500 req/day, unlimited history
- Fallback: Google News RSS `https://news.google.com/rss/search?q={company_name}`

**How it improves the brief:**
The research phase currently relies on the LLM's web search (slow, inconsistent). NewsAPI gives a structured, fast, reproducible news pull that feeds directly into risk flags. A CEO departure 3 months ago that the LLM missed is now surfaced automatically.

**Implementation in `researcher.py`:**
```python
def fetch_recent_news(company_name: str, days_back=90) -> list[dict]:
    """
    Returns structured news items, pre-categorized.
    Each item: {headline, date, url, category, sentiment}
    Category: one of [leadership, customer, regulatory, ma, workforce, other]
    """
    # GET https://newsapi.org/v2/everything?q={company_name}&from={date}&apiKey={key}
    # For each article: classify category via simple keyword matching
    # leadership: [CEO, CFO, COO, president, resign, appoint, hire, depart]
    # regulatory: [lawsuit, fine, EPA, OSHA, FDA, recall, violation, settlement]
    # workforce: [layoff, hiring freeze, union, strike, headcount]
```

**Rate limits:** 100 req/day (free), sufficient for dev; upgrade for production.
**Cost:** Free for dev; ~$30/mo for production use.
**Latency:** ~1–2 sec per query.

---

### Updated v2 Architecture (Module 1)

```
pe-diligence-tool/
├── spec_v2.md               # This document
├── src/
│   ├── main.py              # CLI entrypoint (unchanged interface)
│   ├── researcher.py        # + SEC EDGAR, BLS, NewsAPI integrations
│   ├── data_sources/        # NEW
│   │   ├── sec_edgar.py     # SEC EDGAR API client
│   │   ├── bls.py           # BLS API client
│   │   └── news.py          # NewsAPI + RSS fallback client
│   ├── brief_generator.py   # + comp table generation
│   └── formatter.py         # + appendix rendering
├── prompts/
│   ├── section_prompts/
│   │   └── comps_benchmarks.md  # NEW section prompt
│   └── ...
```

### New .env Variables Required

```
# Existing
ANTHROPIC_API_KEY=

# New
NEWS_API_KEY=           # newsapi.org (free signup)
BLS_API_KEY=            # data.bls.gov (free signup)
# SEC EDGAR needs no key
```

### SIC / NAICS Mapping

Middle-market PE deals mostly fall into these codes. The tool will need an industry-to-SIC/NAICS lookup table:

| Industry Input | SIC | NAICS |
|---|---|---|
| industrial packaging | 2650–2679 | 322200 |
| healthcare services | 8000–8099 | 621000 |
| business services | 7370–7379 | 541500 |
| consumer products | 2000–2099 | 311000 |
| distribution/logistics | 5000–5199 | 423000 |
| specialty chemicals | 2800–2899 | 325000 |

Implementation: simple dict lookup in `researcher.py`, fallback to user-specified SIC if industry not matched.

---

## Module 2: Value Creation Planner

### Purpose

The Deal Diligence Brief is built for the deal team. The Value Creation Planner is built for the portco operator — the CFO or CEO sitting across the table from the PE sponsor in the first board meeting. It takes the investment thesis and turns it into a living operational roadmap.

**Who uses it:** PortCo CEO, CFO, PE ops partner, value creation leads
**When:** Day 1–30 (initial build), Day 60 (refinement), quarterly (progress tracking)
**Output:** Structured VCP with KPIs, EBITDA bridge, workstream assignments, and milestone tracking

### Design Philosophy

Most VCP templates fail because they were built by consultants who've never run a plant. They look great on slides and collect dust by Month 3. This planner is:
- **Operator-first:** Written for the CEO/CFO, not the IC committee
- **Grounded in baselines:** No initiative without a current-state KPI baseline
- **Honest about timelines:** Flags when a lever requires systems or capabilities that don't exist yet
- **Accountability-ready:** Assigns owners and links to board reporting cadence

### Input Schema (Module 2)

| Field | Type | Required | Description |
|---|---|---|---|
| `company_name` | string | Yes | Portfolio company name |
| `description` | string | Yes | Business description (same as diligence input) |
| `industry` | string | Yes | Industry vertical |
| `ev` | number | No | Deal EV at close ($M) |
| `entry_ebitda` | number | No | EBITDA at close ($M) |
| `entry_multiple` | number | No | EV/EBITDA at entry |
| `target_multiple` | number | No | Target exit EV/EBITDA |
| `hold_period_yrs` | number | No | Target hold period (default: 5) |
| `key_levers` | list[string] | No | Sponsor's priority value creation levers (free text) |
| `known_issues` | string | No | Known operational gaps from diligence |
| `diligence_brief_path` | string | No | Path to existing diligence brief (Module 1 output) — if provided, VCP auto-ingests it |

### Output Structure (Module 2)

Output is a single `.md` file saved to `output/` named `{company_slug}_vcp_{YYYY-MM-DD}.md`.

#### Section 1: Investment Thesis & Value Creation Summary

- Sponsor's thesis (derived from inputs or diligence brief)
- EBITDA bridge: entry → target (by lever category)
- Total value creation potential ($M EBITDA uplift, MOIC implication)
- Top 3 risks to thesis execution

```
**EBITDA Bridge (Entry to Target)**
Entry EBITDA:          $XXm  (XX.X% margin)
+ Revenue initiatives: +$Xm  (pricing, mix, cross-sell)
+ Cost reduction:      +$Xm  (procurement, overhead)
+ Working capital:     +$Xm  (DSO/DIO unlock, noted as cash, not EBITDA)
+ Org effectiveness:   +$Xm  (right-sizing, capability builds)
─────────────────────────────
Target EBITDA:         $XXm  (XX.X% margin)
Implied exit EV:       $XXXm (Xx EV/EBITDA)
```

#### Section 2: Value Creation Workstreams

For each workstream:

```
### Workstream: [Name]
**Category:** Revenue / Cost / Working Capital / Org
**EBITDA Impact:** $Xm–$Xm (XX–XX% of target uplift)
**Timeline:** Months X–XX
**Confidence:** High / Medium / Low
**Owner:** [Role, not name — e.g., "CFO + VP Ops"]
**Prerequisite:** [Data, systems, or headcount required before launch]

**Current State Baseline:**
- [KPI 1]: [Current value or "unknown — establish in Month 1"]
- [KPI 2]: [Current value]

**Target State (Month 24):**
- [KPI 1]: [Target value and rationale]
- [KPI 2]: [Target value]

**Key Milestones:**
| Milestone | Due | Owner | Status |
|---|---|---|---|
| [M1] | Month X | [Role] | Not started |

**Dependencies / Risks:**
- [Risk 1]: [Mitigation approach]
```

Minimum 4 workstreams, maximum 8. Prioritized by EBITDA impact × confidence.

#### Section 3: KPI Dashboard Design

Defines the KPI set for board reporting. Structured as:

```
**Operating Cadence:** Monthly board report + quarterly deep dive

| KPI | Category | Baseline | Target | Frequency | Owner |
|---|---|---|---|---|---|
| Revenue growth (YoY) | Revenue | XX% | XX% | Monthly | CEO |
| Gross margin | Revenue | XX% | XX% | Monthly | CFO |
| DSO (days sales outstanding) | Working Capital | XX days | XX days | Monthly | CFO |
| DIO (days inventory outstanding) | Working Capital | XX days | XX days | Monthly | VP Ops |
| Headcount (FTE) | Org | XXX | XXX | Monthly | HR/CEO |
| Revenue per employee | Org | $XXXk | $XXXk | Quarterly | CEO |
| Customer retention rate | Revenue | XX% | XX% | Quarterly | CCO/CEO |
| [Industry-specific KPI] | Ops | XX | XX | Monthly | VP Ops |
```

Industry-specific KPIs are generated by the LLM based on the company's sector. Examples:
- Packaging: OEE (overall equipment effectiveness), scrap rate, on-time delivery
- Healthcare services: patient throughput, payer mix, provider utilization
- Distribution: fill rate, order cycle time, warehouse cost/unit

#### Section 4: 100-Day Operational Sprint Plan

Same structure as Module 1's 100-day outline, but more granular — written for the CEO/CFO to execute, not for the deal team to review.

Each item includes: owner, deadline, success metric, dependency.

#### Section 5: Organizational Capability Assessment

- Current leadership assessment (based on diligence inputs or brief)
- Key gaps: roles that need to be upgraded, added, or externally hired
- Change management risk: cultural resistance signals, integration complexity
- Recommended first 3 hires / promotions with rationale

#### Section 6: Quick Win Tracker (Months 1–6)

The board wants to see early proof of concept. This section defines 3–5 quick wins:

```
| Quick Win | Category | Est. Value | Owner | Month | Status |
|---|---|---|---|---|---|
| [Initiative] | [Cost/Revenue/WC] | $Xm | [Role] | M1–M3 | Not started |
```

Quick wins must be: achievable without major capital, visible to the organization, measurable within 90 days.

---

### Data Sources for Module 2

Module 2 builds on Module 1's data sources plus:

**Source 4: Damodaran Dataset (Free, Annual Download)**
- Industry-level financial benchmarks updated annually by NYU Stern Professor Damodaran
- Provides: EV/EBITDA, EV/Revenue, EBITDA margins, return on capital by sector
- Access: Direct download from `https://pages.stern.nyu.edu/~adamodar/`
- Use in VCP: Anchors the EBITDA bridge and exit multiple assumptions with real industry data
- Update cadence: Annual (January); cache locally, refresh at start of year

**Source 5: BLS Occupational Employment & Wages Survey (OES)**
- Granular wage data by occupation code (SOC) and geography
- Access: Same BLS API, different series IDs (OES data vs. CES)
- Use in VCP: Right-sizes compensation assumptions in org effectiveness workstream

---

### Module 2 File Structure Additions

```
pe-diligence-tool/
├── src/
│   ├── vcp_generator.py         # NEW — VCP construction logic
│   ├── ebitda_bridge.py         # NEW — EBITDA bridge modeling
│   └── data_sources/
│       └── damodaran.py         # NEW — Damodaran dataset client
├── prompts/
│   └── vcp_prompts/             # NEW
│       ├── system_prompt.md
│       ├── workstream.md
│       ├── kpi_dashboard.md
│       ├── quick_wins.md
│       └── org_assessment.md
├── templates/
│   └── vcp_template.md          # NEW
```

### CLI Interface (Module 2)

```bash
# Generate diligence brief (Module 1)
python src/main.py brief \
  --company "Inovar Packaging" \
  --description "Mid-size flexible packaging manufacturer..." \
  --industry "industrial packaging" \
  --ev 150

# Generate VCP (Module 2)
python src/main.py vcp \
  --company "Inovar Packaging" \
  --industry "industrial packaging" \
  --ev 150 \
  --entry-ebitda 18 \
  --entry-multiple 8.3 \
  --target-multiple 10.0 \
  --hold-years 5 \
  --from-brief output/inovar_packaging_2026-04-04.md  # optional: ingest existing brief

# Generate both in sequence
python src/main.py full \
  --company "Inovar Packaging" \
  --description "..." \
  --industry "industrial packaging" \
  --ev 150 \
  --entry-ebitda 18
```

---

## v2 Build Sequence

| Phase | Deliverable | Priority | Estimated Scope |
|---|---|---|---|
| **Phase 1** | Data source clients (`sec_edgar.py`, `bls.py`, `news.py`) | High | 3 files, ~150 lines each |
| **Phase 2** | Updated `researcher.py` with data source integration | High | Refactor existing file |
| **Phase 3** | New Section 3 prompt + comp table generation | High | 1 prompt file, formatter update |
| **Phase 4** | `vcp_generator.py` + VCP section prompts | Medium | Core new module |
| **Phase 5** | `ebitda_bridge.py` + bridge logic | Medium | Structured modeling logic |
| **Phase 6** | CLI refactor (`main.py`) for dual-module commands | Medium | Argparse/click restructure |
| **Phase 7** | Damodaran client + OES data integration | Lower | Enhancement for VCP |
| **Phase 8** | End-to-end test on real deal (Inovar Packaging or CBIZ) | High | QA pass |

---

## Updated Project Status

**Module 1 (Deal Diligence Brief)**
- [x] Spec written (v1)
- [x] Prompts written
- [x] End-to-end test run (CBIZ, 2026-03-20)
- [ ] `sec_edgar.py` data client
- [ ] `bls.py` data client
- [ ] `news.py` data client
- [ ] `researcher.py` updated with data source calls
- [ ] Section 3 (Comps & Benchmarks) prompt + template
- [ ] End-to-end test with real data (Phase 1–3 complete)

**Module 2 (Value Creation Planner)**
- [ ] VCP prompts written
- [ ] `vcp_generator.py` built
- [ ] `ebitda_bridge.py` built
- [ ] `damodaran.py` client built
- [ ] CLI refactored for dual commands
- [ ] End-to-end VCP test

---

## Open Questions

1. **SIC vs. NAICS:** SEC EDGAR uses SIC codes; BLS uses NAICS. Need a reliable cross-walk table. Use Census Bureau's official SIC-to-NAICS mapping file.

2. **Private company benchmarking:** Most diligence targets are private. Public comp benchmarks (SEC EDGAR) are directionally useful but structurally different companies. How prominently should we caveat this? Recommendation: include a standard disclaimer in Section 3 and flag when the public comps are materially larger than the target.

3. **NewsAPI free tier (30-day lookback):** For a deal that's been in the pipeline for months, 30 days may miss important signals. Mitigation: use Google News RSS as a fallback (no lookback limit), and prompt the user to provide context notes for older events.

4. **LLM vs. structured data for EBITDA bridge:** The bridge in Module 2 is partly modeled (uses real inputs) and partly LLM-generated (uses comparable benchmarks to estimate initiative sizing). Need to clearly distinguish "actual input" from "LLM estimate" in output. Proposed: use `*` footnote notation for estimates.

5. **Damodaran dataset currency:** Updated annually in January. Need to bundle a cached version in the repo and document the manual refresh process.

---

*Spec version: 2.0 | Created: 2026-04-04*
