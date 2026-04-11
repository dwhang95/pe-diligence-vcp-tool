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
) -> str:
    """
    Generate a Value Creation Plan. Saves output to output/ and returns the file path.
    style_reference: extracted text from an uploaded doc to mirror in tone/format.
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

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

    print("  [vcp] Running Part 1 (EBITDA bridge, workstreams, quick wins) and Part 2 (KPIs, 100-day, org gaps) in parallel...")

    part1_text, part2_text = await asyncio.gather(
        _generate_with_retry(client, p1, "Part 1 (sections 1–3)", system_prompt=system_prompt),
        _generate_with_retry(client, p2, "Part 2 (sections 4–6)", system_prompt=system_prompt),
    )

    today = date.today().strftime("%Y-%m-%d")
    ebitda_margin = (current_ebitda / current_revenue * 100) if current_revenue > 0 else 0
    ebitda_uplift = target_ebitda - current_ebitda

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
