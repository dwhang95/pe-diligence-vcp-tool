# PE Ops Due Diligence Brief Generator

Generates structured operational due diligence briefs for middle-market PE buyout targets ($50M–$500M+ EV). Feed it a company name, description, and industry. It runs live data pulls, web research, and LLM-powered analysis in parallel, then assembles a 7-section brief covering ops risk, IT maturity, value creation levers, and a 100-day plan starter.

Built for PE ops professionals who need a rigorous, research-backed brief before the first management meeting — not a template with blanks to fill in.

---

## What It Produces

**Input:** Company name + 2–5 sentence description + industry vertical

**Output:** A markdown brief covering:

| Section | What It Contains |
|---|---|
| 1. Executive Summary | Ops profile, labor intensity, tech dependency, overall risk rating |
| 2. Operational Risk Flags | 5 categories rated Low/Medium/High/Critical with diligence questions |
| 3. Comps & Benchmarks | Real SEC EDGAR public comp table + BLS labor data + news sweep signals |
| 4. IT & Systems Maturity | ERP/BI hypothesis, tech debt risk, digital enablement roadmap |
| 5. Value Creation Opportunities | Prioritized levers with timeline, confidence, and EBITDA framing |
| 6. 100-Day Plan Outline | Phased sprint plan with quick wins and board reporting milestones |
| 7. Key Diligence Questions | Targeted questions for management meetings, organized by risk category |

Briefs are saved to `output/` as `{company-slug}_ops_brief_{YYYY-MM-DD}.md`.

---

## Real Data Sources (v2)

Three live data sources run in parallel with the web research phase:

### SEC EDGAR (no key required)
Pulls public comp financials — revenue, operating income, CapEx intensity — for companies in the same SIC code as the target. Uses the EDGAR XBRL API (`data.sec.gov/api/xbrl/companyfacts/`). Automatically selects the closest SIC code from a 40-entry industry lookup table. Returns a markdown comp table with median benchmarks baked in.

### Bureau of Labor Statistics (free key recommended)
Pulls CES (Current Employment Statistics) data: average hourly earnings, total sector employment, and 5-year employment trend. Maps industry descriptions to BLS CES series IDs. A free API key from `data.bls.gov/registrationApi` increases the rate limit from 25 to 500 requests/day — worth getting.

### News Sweep (Puppeteer + Google RSS fallback)
Scrapes Google News via headless browser for recent articles on the target. Articles are automatically categorized into PE-relevant buckets — leadership changes, regulatory/legal, workforce signals, M&A activity, financial distress, customer events — and negative signals are flagged. Falls back to Google News RSS if Node.js isn't available.

---

## Setup

**Prerequisites:** Python 3.12, Node.js 18+

```bash
# Python environment
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Node (for Puppeteer news scraper)
npm install

# Environment variables
cp .env.example .env
# Edit .env — add ANTHROPIC_API_KEY at minimum
```

**.env variables:**
```
ANTHROPIC_API_KEY=sk-ant-...        # Required
BLS_API_KEY=                        # Optional — free at data.bls.gov/registrationApi
NEWS_API_KEY=                       # Not used in v2 (Puppeteer handles news)
```

---

## Usage

```bash
python src/generate_brief.py \
  --company "Acme Packaging" \
  --description "Mid-sized corrugated packaging manufacturer serving consumer goods and food companies in the Midwest. ~$180M revenue, founder-led, two plants in Kansas and Illinois." \
  --industry "industrial packaging" \
  --ev "$180M" \
  --notes "Founder-owned, first institutional capital. Key-man risk on founder/CEO. Plant 2 is 30 years old."
```

**Arguments:**

| Flag | Required | Description |
|---|---|---|
| `--company` | Yes | Company name |
| `--description` | Yes | 2–5 sentence business description |
| `--industry` | Yes | Industry vertical (drives SIC + BLS series selection) |
| `--ev` | No | EV range, e.g. `$120M` or `$50M–$200M` |
| `--notes` | No | Deal context: ownership history, known issues, thesis hooks |

**Runtime:** 3–6 minutes depending on API rate limits. The generator auto-retries on Anthropic rate-limit errors with exponential backoff (15s → 30s → 60s). SEC EDGAR pulls take ~15–30 seconds for 5–6 comps.

---

## Architecture

```
pe-diligence-tool/
├── src/
│   ├── generate_brief.py        # Main entry point — orchestrates all phases
│   └── data_sources/
│       ├── sec_edgar.py         # SEC EDGAR XBRL API client
│       ├── bls.py               # BLS CES API client
│       ├── news.py              # News sweep (Puppeteer → cache → Google RSS)
│       └── news_scraper.js      # Puppeteer headless scraper (Node.js)
├── prompts/
│   ├── system_prompt.md         # Core persona + voice instructions for Claude
│   ├── research_prompt.md       # Web research agent instructions
│   └── section_prompts/
│       ├── exec_summary.md
│       ├── risk_flags.md
│       ├── comps_benchmarks.md  # Injects real SEC + BLS + news data
│       ├── it_systems.md
│       ├── value_creation.md
│       ├── 100_day_plan.md
│       └── diligence_questions.md
├── templates/
│   └── brief_template.md        # Final brief assembly template
├── output/                      # Generated briefs (gitignored)
├── spec_v2.md                   # v2 architecture and Module 2 design spec
├── requirements.txt             # Python dependencies
└── package.json                 # Node dependencies (Puppeteer)
```

### Pipeline

```
Phase 1 (parallel):
  ├── Web research agent (Claude + web_search, up to 8 searches)
  ├── SEC EDGAR comps fetch (async HTTP, SIC-matched)
  ├── BLS benchmarks fetch (async HTTP, CES series-matched)
  ├── News sweep (Puppeteer subprocess)
  └── Template + prompt loading

Phase 2 (sequential, auto-retry on rate limits):
  Sections 1–5: exec_summary → risk_flags → comps_benchmarks → it_systems → value_creation

Phase 3 (sequential):
  Sections 6–7: 100_day_plan → diligence_questions
  (these ingest risk_flags + value_creation as context)

Phase 4:
  Brief assembly → write to output/
```

Sections generate sequentially to stay within Anthropic's token/minute rate limits. Each call retries up to 6 times with exponential backoff before failing.

---

## Test the Data Sources

Run each source independently to verify connectivity:

```bash
# SEC EDGAR — pulls SIC 7389 (Business Services) comps
python src/data_sources/sec_edgar.py

# BLS — professional services, packaging, and healthcare benchmarks
python src/data_sources/bls.py

# News — scrape Google News for a specific company
python src/data_sources/news.py "CBIZ"
```

---

## Tested On

| Target | EV | Industry | Date |
|---|---|---|---|
| CBIZ (take-private) | $4.7B | Accounting / Professional Services | 2026-04-07 |

---

## Diligence Philosophy

This tool is built around a specific PE ops point of view:

- **Hypothesis-driven:** Enter with a thesis, update it — don't abandon it at the first sign of noise
- **Key-man first:** In middle market, one departure can unravel a thesis
- **IT maturity = ops ceiling:** A company without a BI layer cannot execute a VCP
- **Customer concentration kills:** Top customer >20% is a flag; >40% is a potential deal-breaker

The output is intended to sharpen the first management meeting agenda, not replace direct diligence. Public comp benchmarks skew larger than typical middle-market targets — treat them as directional context.

---

## What's Coming (Module 2)

A **Value Creation Planner (VCP)** module is in design. It ingests the diligence brief output and generates a structured VCP with:
- EBITDA bridge (entry → target, by lever)
- Workstream templates with KPI baselines, milestones, and owners
- KPI dashboard design for board reporting
- 100-day sprint plan written for the CEO/CFO to execute

See `spec_v2.md` for the full design.

---

## Dependencies

**Python:** `anthropic>=0.40.0`, `python-dotenv>=1.0.0`, `httpx` (via anthropic)

**Node.js:** `puppeteer` (headless Chromium for news scraping)

**APIs (all free):**
- Anthropic Claude API — requires account
- SEC EDGAR XBRL API — no key, no registration required
- BLS Public Data API — no key required; free registration unlocks higher rate limits
