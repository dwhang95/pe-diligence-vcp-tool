#!/usr/bin/env python3
"""
PE Ops Value Creation Planner — Module 2

Generates a structured VCP from portco inputs: EBITDA bridge, workstreams,
quick wins, KPI dashboard, 100-day sprint, and org capability gaps.
"""

import asyncio
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

BASE_DIR = Path(__file__).parent.parent
OUTPUT_DIR = BASE_DIR / "output"

MODEL = "claude-sonnet-4-6"

VCP_SYSTEM_PROMPT = """You are a senior PE value creation professional with 15 years of experience \
across middle-market buyouts. You build VCPs that portco operators actually use — not consultant \
decks that collect dust by Month 3.

Your output is:
- Specific and quantified (real KPI targets, dollar ranges, owner types)
- Grounded in operational reality (flag when an initiative requires systems or capabilities \
that may not yet exist)
- Written for the CEO/CFO — not the IC committee

Use naturally: VCP, PortCo, EBITDA bridge, working capital unlock, operating cadence, \
DSO/DIO/DPO, KPI, board reporting, value creation workstream, 100-day plan.
Never use: "synergies," "best-in-class," "world-class," "leverage our learnings," \
"low-hanging fruit," "circle back."

Mark LLM-estimated numbers with * to distinguish from user-supplied actuals."""


def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def _build_context_block(
    company_name: str,
    description: str,
    industry: str,
    current_revenue: float,
    current_ebitda: float,
    investment_thesis: str,
    operational_challenges: str,
    hold_period: int,
    target_ebitda: float,
) -> str:
    ebitda_margin = (current_ebitda / current_revenue * 100) if current_revenue > 0 else 0
    ebitda_uplift = target_ebitda - current_ebitda
    return f"""\
**Company:** {company_name}
**Description:** {description}
**Industry:** {industry}
**Current Revenue:** ${current_revenue:.1f}M
**Current EBITDA:** ${current_ebitda:.1f}M ({ebitda_margin:.1f}% margin)
**Target EBITDA at Exit:** ${target_ebitda:.1f}M
**Total EBITDA Uplift Required:** ${ebitda_uplift:.1f}M over {hold_period} years
**Investment Thesis:** {investment_thesis}
**Known Operational Challenges:** {operational_challenges}"""


def _part1_prompt(context: str, current_ebitda: float, target_ebitda: float, hold_period: int) -> str:
    ebitda_uplift = target_ebitda - current_ebitda
    return f"""\
{context}

Generate three sections for this Value Creation Plan. Be specific, quantified, and operator-ready.

---

## 1. EBITDA Bridge — Entry to Exit

Build an EBITDA bridge from ${current_ebitda:.1f}M to ${target_ebitda:.1f}M over {hold_period} years.
Allocate the ${ebitda_uplift:.1f}M uplift across:
- Revenue growth (pricing, volume, mix shift, new customer acquisition)
- Margin improvement (gross margin levers, COGS reduction)
- Cost reduction (G&A, overhead, procurement, labor efficiency)
- Working capital (note: DSO/DIO unlock is a cash benefit, not direct EBITDA — flag this)

Use this exact format for the bridge:
```
Entry EBITDA:          $XXm  (XX.X% margin)
+ Revenue growth:      +$Xm  (describe the lever in parentheses)
+ Margin improvement:  +$Xm
+ Cost reduction:      +$Xm
─────────────────────────────────────────
Target EBITDA:         $XXm  (XX.X% margin)
```

Follow with 2–3 sentences on the top execution risk to this bridge.

---

## 2. Top 5 Value Creation Workstreams

For each of the 5 workstreams (prioritized by EBITDA impact × execution confidence), provide:

### Workstream: [Name]
**Category:** Revenue / Cost / Working Capital / Org
**EBITDA Impact:** $Xm–$Xm
**Timeline:** Months X–XX
**Confidence:** High / Medium / Low
**Owner:** [Role type — e.g., "CFO + VP Ops"]
**Prerequisite:** [Any data, systems, or headcount required before launch]

**Current State Baseline:**
- [KPI 1]: [current value or "unknown — establish Month 1"]
- [KPI 2]: [current value]

**Target State (Month {hold_period * 12}):**
- [KPI 1]: [target with rationale]
- [KPI 2]: [target]

**Key Milestones:**
| Milestone | Due | Owner | Status |
|---|---|---|---|
| [M1] | Month X | [Role] | Not started |
| [M2] | Month X | [Role] | Not started |
| [M3] | Month X | [Role] | Not started |

**Execution Risk:** [1–2 sentences on what could prevent this workstream from delivering]

---

## 3. Quick Win Tracker — First 90 Days

List 10 specific initiatives achievable in 90 days. Quick wins must be: achievable without \
major capital, visible to the organization, and measurable within 90 days.

| # | Initiative | Category | Est. Value | Owner | Month | Effort | Impact |
|---|---|---|---|---|---|---|---|
| 1 | [Specific action] | Cost/Revenue/WC | $Xm or X% | [Role] | M1–M2 | Low/Med/High | Low/Med/High |

After the table, flag the 2–3 quick wins that will have the highest organizational visibility \
(i.e., the ones that will tell the frontline "this team is serious").
"""


def _part2_prompt(context: str, industry: str, hold_period: int) -> str:
    return f"""\
{context}

Generate three more sections for this Value Creation Plan.

---

## 4. KPI Dashboard Design

Design an 8–10 metric board reporting dashboard for this business. This will be the core \
of the monthly board package.

For each KPI:
- KPI name
- Category (Revenue / Working Capital / Operations / Org)
- Current baseline (use input numbers where available; "TBD — assess Month 1" where not)
- Target (at exit or at specific milestone)
- Reporting frequency (Monthly / Quarterly)
- Owner role

Include at least 2 industry-specific operational KPIs for {industry} \
(e.g., for packaging: OEE, scrap rate; for healthcare: utilization, payer mix).

Format as a markdown table. After the table, add:
**Operating Cadence:** [Recommended board report frequency and format — 2–3 sentences]

---

## 5. 100-Day Sprint Plan

Execution-level plan written for the CEO/CFO to own and execute — not for the deal team to review.
Each action needs: owner, success metric, and any key dependency.

**Days 1–30: Listen, map, and build trust**
5–7 specific actions. Examples of the right level of specificity:
- "Conduct 1:1s with all direct reports by Day 15 — CEO, no agenda pushed, listening only"
- "Walk every facility by Day 10 — meet supervisors, not just plant managers"
- "Map all customer contracts by tier and renewal date — identify top-10 customer concentration risk"

**Days 31–60: Quick wins and baseline-setting**
5–7 specific actions. First visible wins land here. KPI baselines get locked. \
Board reporting format agreed.

**Days 61–100: Workstream launch and accountability**
5–7 specific actions. Workstreams formally kicked off, owners named, first board report delivered, \
progress against quick win tracker reviewed.

---

## 6. Organizational Capability Gaps

Identify the top 3 capability gaps that will constrain VCP execution if not addressed.

For each gap:

### Gap [#]: [Gap Name]
**Why it matters:** [Specific EBITDA or execution impact if this gap isn't filled]
**Recommended solution:** Hire / Promote from within / Fractional resource
**Hire profile:**
- Title:
- Key experience: [3–4 specific requirements, not generic]
- Comp range: $XXXk–$XXXk base + [bonus structure]
- Report to: [CEO/CFO/COO]
**Fill timeline:** [Month X — must be in seat before workstream Y launches]
**Risk of delay:** [What specifically breaks if this hire slips 3 months]
"""


def _part3_scorecards_prompt(context: str) -> str:
    return f"""\
{context}

Generate four functional assessment scorecards. For each dimension, analyze the available \
company context, industry, investment thesis, and operational challenges to assign a maturity rating. \
When information is insufficient to assess a dimension with confidence, note \
"Insufficient data — assess in management meeting" and set Maturity to 🟡 Y.

Maturity ratings:
- 🔴 R = High/Critical risk — impairs thesis or EBITDA if unaddressed
- 🟡 Y = Medium risk — needs diligence; mitigable with planning
- 🟢 G = Low risk — unlikely to impair thesis

**100-Day Priority (Y/N):** Y if material enough to address in first 100 days; N otherwise.
**Platform vs Tuck-In Impact:** Platform = affects standalone build-and-buy; Tuck-In = affects add-on integration; Both = affects both.
**Future CIM Gap?:** Y if this dimension is likely to be missing or misrepresented in a future CIM and must be independently verified; N if likely surfaced organically.

Keep Current State Notes to 1–2 sentences. Be directional, not generic.

---

### Scorecard 1 — Operations

| Dimension | Assessment Area | Current State Notes | Maturity (R/Y/G) | 100-Day Priority (Y/N) | Platform vs Tuck-In Impact | Future CIM Gap? |
|---|---|---|---|---|---|---|
| Process Documentation | Are SOPs documented, current, and operationally embedded? | | | | | |
| End-to-End Flow | Is the full ops flow (order-to-cash, procure-to-pay, etc.) mapped and understood? | | | | | |
| Bottlenecks | Are production/service delivery bottlenecks identified and actively managed? | | | | | |
| Capacity Planning | Does the company have formal capacity planning against demand forecasts? | | | | | |
| Cost Transparency | Is unit cost, overhead allocation, and margin by product/service visible? | | | | | |
| Margin Leakage | Are pricing, scrap, returns, or rework creating untracked margin erosion? | | | | | |
| Operating KPIs | Are operational KPIs defined, tracked, and visible to leadership weekly? | | | | | |
| Continuous Improvement | Is there a culture and process for ongoing ops improvement (Lean, Kaizen, etc.)? | | | | | |
| Vendor Management | Is the vendor base rationalized with contracts, SLAs, and performance tracking? | | | | | |
| Quality Control | Are QC standards defined and defect/return rates tracked over time? | | | | | |
| Customer Satisfaction | Is customer satisfaction measured (NPS, CSAT, complaint tracking) and acted upon? | | | | | |
| M&A Readiness | Can the ops function absorb an add-on acquisition within 6–12 months? | | | | | |
| Geographic Scalability | Could the operating model replicate in a new geography without major re-engineering? | | | | | |
| Ops Leadership | Is there a capable, stable ops leader (COO/VP Ops) in seat? | | | | | |
| Capital Intensity | Are capex requirements well-understood and in line with growth plans? | | | | | |

**Key Outputs — Operations**

- **Top Risks:** [2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what ops maturity means for the EBITDA bridge]

---

### Scorecard 2 — IT & Systems

| Dimension | Assessment Area | Current State Notes | Maturity (R/Y/G) | 100-Day Priority (Y/N) | Platform vs Tuck-In Impact | Future CIM Gap? |
|---|---|---|---|---|---|---|
| Core ERP | Is the ERP modern, well-implemented, and actively used across the business? | | | | | |
| Financial Close | Is the monthly financial close timely (<10 days) and reliable? | | | | | |
| Data Integrity | Is there a single source of truth for financial and operational data? | | | | | |
| BI/Reporting | Does leadership have a real-time or near-real-time BI/reporting layer? | | | | | |
| CRM Usage | Is CRM used consistently by the sales team with clean, actionable data? | | | | | |
| Integrations | Are key systems (ERP, CRM, HRIS, etc.) integrated or siloed with manual bridges? | | | | | |
| Scalability | Can current systems support 2x revenue growth without a full replacement? | | | | | |
| M&A Readiness | Can the IT stack integrate an acquired company within 12–18 months? | | | | | |
| IT Ownership | Is there a capable IT leader (CTO/IT Director) or is IT outsourced/underresourced? | | | | | |
| Vendor Dependence | Is the company dangerously dependent on a single vendor or legacy system? | | | | | |
| Tech Debt | Is there significant deferred IT investment creating operational risk? | | | | | |
| Cybersecurity | Are basic cybersecurity controls in place (MFA, endpoint protection, incident response)? | | | | | |
| Disaster Recovery | Is there a tested DR/BCP plan covering critical systems? | | | | | |
| Access Controls | Are role-based access controls and separation of duties enforced? | | | | | |
| Roadmap Clarity | Is there a documented IT roadmap aligned to business priorities? | | | | | |

**Key Outputs — IT & Systems**

- **Top Risks:** [2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what IT maturity means for the VCP and platform build thesis]

---

### Scorecard 3 — Commercial

| Dimension | Assessment Area | Current State Notes | Maturity (R/Y/G) | 100-Day Priority (Y/N) | Platform vs Tuck-In Impact | Future CIM Gap? |
|---|---|---|---|---|---|---|
| Growth Drivers | Are revenue growth drivers clearly identified and actively managed? | | | | | |
| Sales Process | Is the sales process defined, repeatable, and consistently followed? | | | | | |
| Sales Dependency | Is revenue overly dependent on the owner, a single rep, or a small team? | | | | | |
| Pipeline Visibility | Is the sales pipeline visible, accurate, and used for forecasting? | | | | | |
| Forecast Accuracy | Are revenue forecasts within ±10% variance to actuals on a rolling basis? | | | | | |
| Lead Gen | Are lead generation channels diversified and performing predictably? | | | | | |
| Pricing Discipline | Is pricing strategic, defensible, and enforced consistently? | | | | | |
| Margin Visibility | Is gross margin tracked by customer, product line, and channel? | | | | | |
| Retention | Is customer retention/churn tracked and above industry benchmarks? | | | | | |
| Unit Economics | Are CAC, LTV, and payback period understood and healthy? | | | | | |
| GTM Scalability | Can the go-to-market motion scale to new segments or geographies without major reinvestment? | | | | | |
| Sales Enablement | Do reps have the tools, training, and collateral needed to close effectively? | | | | | |
| Incentives | Are sales incentive structures aligned with margin, not just revenue? | | | | | |
| Customer Concentration | Is revenue diversified, or does top-customer concentration create deal risk? | | | | | |
| Cross-Sell/Upsell | Is there a proven motion to expand revenue within the existing customer base? | | | | | |

**Key Outputs — Commercial**

- **Top Risks:** [2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what commercial maturity means for the revenue growth thesis]

---

### Scorecard 4 — Talent & HR

| Dimension | Assessment Area | Current State Notes | Maturity (R/Y/G) | 100-Day Priority (Y/N) | Platform vs Tuck-In Impact | Future CIM Gap? |
|---|---|---|---|---|---|---|
| CEO Capability | Does the CEO have the capability and bandwidth to lead through PE ownership and growth? | | | | | |
| CFO Capability | Does the CFO have PE-grade financial reporting, controls, and strategic finance capability? | | | | | |
| COO Capability | Is there a capable operations leader who can own the VCP execution? | | | | | |
| Leadership Bench | Is the broader leadership team (VPs, Directors) PE-ready and capable of scaling? | | | | | |
| Retention | Are key employees being retained, and is attrition at or below industry norms? | | | | | |
| Single Points of Failure | Are there individuals whose departure would materially impair operations or client relationships? | | | | | |
| Hiring Velocity | Can the company hire fast enough to support the growth plan? | | | | | |
| Org Design | Is the org structure aligned to the strategy, or are there gaps and misalignments? | | | | | |
| M&A Experience | Has the leadership team managed through acquisitions or integrations before? | | | | | |
| Incentive Alignment | Are equity/bonus structures aligned to PE value creation milestones? | | | | | |
| Performance Mgmt | Is there a consistent, documented performance management process? | | | | | |
| Culture | Is the company culture conducive to change, accountability, and PE ownership? | | | | | |
| Succession Planning | Are successors identified for critical roles? | | | | | |
| Talent Gaps | Are there open critical roles or known capability gaps that could impair the thesis? | | | | | |
| Compensation Benchmarking | Is total compensation (base + bonus + equity) benchmarked to market, and are there retention risk outliers? | | | | | |

**Key Outputs — Talent & HR**

- **Top Risks:** [2–3 highest-risk dimensions with brief rationale]
- **Top Opportunities:** [2–3 highest-upside dimensions for value creation]
- **Value Creation Implications:** [1–2 sentences on what talent/HR maturity means for the 100-day plan and platform thesis]
"""


async def _generate_with_retry(
    client: anthropic.AsyncAnthropic,
    prompt: str,
    label: str,
    max_retries: int = 5,
    system_prompt: str = VCP_SYSTEM_PROMPT,
) -> str:
    wait = 15
    for attempt in range(max_retries):
        try:
            response = await client.messages.create(
                model=MODEL,
                max_tokens=6000,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            print(f"  [vcp] {label} complete.")
            return response.content[0].text.strip()
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            print(f"  [vcp] Rate limit on {label} — waiting {wait}s...")
            await asyncio.sleep(wait)
            wait = min(wait * 2, 120)


async def generate_vcp(
    company_name: str,
    description: str,
    industry: str,
    current_revenue: float,
    current_ebitda: float,
    investment_thesis: str,
    operational_challenges: str,
    hold_period: int,
    target_ebitda: float,
    style_reference: str = "",
    include_scorecards: bool = False,
) -> str:
    """
    Generate a Value Creation Plan. Saves output to output/ and returns the file path.
    style_reference: extracted text from an uploaded doc to mirror in tone/format.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY not set. Please configure your environment.")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    print(f"\n[VCP] Generating Value Creation Plan for {company_name}...")

    system_prompt = VCP_SYSTEM_PROMPT
    if style_reference.strip():
        system_prompt += (
            "\n\n---\n\n"
            "**STYLE REFERENCE DOCUMENT (uploaded by user)**\n"
            "Mirror the structure, tone, and formatting style of this document:\n\n"
            f"{style_reference[:6000]}"
        )

    context = _build_context_block(
        company_name, description, industry,
        current_revenue, current_ebitda,
        investment_thesis, operational_challenges,
        hold_period, target_ebitda,
    )

    p1 = _part1_prompt(context, current_ebitda, target_ebitda, hold_period)
    p2 = _part2_prompt(context, industry, hold_period)

    if include_scorecards:
        p3 = _part3_scorecards_prompt(context)
        print("  [vcp] Running Part 1, Part 2, and Functional Scorecards in parallel...")
        part1_text, part2_text, part3_text = await asyncio.gather(
            _generate_with_retry(client, p1, "Part 1 (sections 1–3)", system_prompt=system_prompt),
            _generate_with_retry(client, p2, "Part 2 (sections 4–6)", system_prompt=system_prompt),
            _generate_with_retry(client, p3, "Functional Scorecards", system_prompt=system_prompt),
        )
    else:
        print("  [vcp] Running Part 1 (EBITDA bridge, workstreams, quick wins) and Part 2 (KPIs, 100-day, org gaps) in parallel...")
        part1_text, part2_text = await asyncio.gather(
            _generate_with_retry(client, p1, "Part 1 (sections 1–3)", system_prompt=system_prompt),
            _generate_with_retry(client, p2, "Part 2 (sections 4–6)", system_prompt=system_prompt),
        )
        part3_text = None

    today = date.today().strftime("%Y-%m-%d")
    ebitda_margin = (current_ebitda / current_revenue * 100) if current_revenue > 0 else 0
    ebitda_uplift = target_ebitda - current_ebitda

    scorecards_block = f"\n---\n\n## 7. Functional Scorecards\n\n{part3_text}\n" if part3_text else ""

    vcp_doc = f"""# Value Creation Plan — {company_name}

**Generated:** {today} | **Industry:** {industry} | **Hold Period:** {hold_period} years

| | Entry | Target at Exit |
|---|---|---|
| Revenue | ${current_revenue:.1f}M | — |
| EBITDA | ${current_ebitda:.1f}M ({ebitda_margin:.1f}% margin) | ${target_ebitda:.1f}M |
| Uplift Required | | +${ebitda_uplift:.1f}M |

**Investment Thesis:** {investment_thesis}

---

{part1_text}

---

{part2_text}
{scorecards_block}
---

*Generated by PE Ops Tool Suite v2 — Module 2: Value Creation Planner*
*Numbers marked with * are LLM estimates based on comparable benchmarks, not actuals.*
*Validate all baselines in Month 1 before committing to targets.*
"""

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{slugify(company_name)}_vcp_{today}.md"
    output_path.write_text(vcp_doc, encoding="utf-8")

    print(f"\n[VCP] Saved to: {output_path}")
    return str(output_path)
