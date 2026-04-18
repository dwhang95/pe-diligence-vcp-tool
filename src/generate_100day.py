#!/usr/bin/env python3
"""
PE Ops 100-Day Plan Generator

Accepts deal inputs and generates 5 sections in parallel:
  workstreams, resource_plan, csuite_assessment, org_chart, ebitda_bridge
"""

import asyncio
import os
import sys
from pathlib import Path

import anthropic

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass

sys.path.insert(0, str(Path(__file__).parent))
from tier import STANDARD_MODEL, PREMIUM_MODEL

BASE_DIR = Path(__file__).parent.parent
SECTION_PROMPTS_DIR = BASE_DIR / "prompts" / "section_prompts"

SECTIONS = ["workstreams", "resource_plan", "csuite_assessment", "org_chart", "ebitda_bridge"]

# Maps internal section key → prompt filename (without .md)
_PROMPT_FILENAMES = {
    "workstreams":      "100day_workstreams",
    "resource_plan":    "resource_plan",
    "csuite_assessment":"csuite_assessment",
    "org_chart":        "org_chart_18mo",
    "ebitda_bridge":    "ebitda_bridge_100day",
}


def build_100day_context(
    company_name: str,
    industry: str,
    deal_type: str,
    entry_ebitda: float,
    target_ebitda: float,
    hold_period_years: int,
    pe_thesis: str,
    key_challenges: str,
    mgmt_assessment: str,
    top_value_levers: list[str],
) -> dict:
    """Format all deal inputs into a context dict injected into every section prompt."""
    levers_md = "\n".join(f"- {lever}" for lever in top_value_levers)
    ebitda_delta = target_ebitda - entry_ebitda
    ebitda_growth_pct = (ebitda_delta / entry_ebitda * 100) if entry_ebitda else 0

    context_block = f"""**Company:** {company_name}
**Industry:** {industry}
**Deal Type:** {deal_type}
**Hold Period:** {hold_period_years} years

**EBITDA at Entry:** ${entry_ebitda:,.0f}K
**Target EBITDA:** ${target_ebitda:,.0f}K
**Required EBITDA Lift:** ${ebitda_delta:,.0f}K ({ebitda_growth_pct:.1f}% growth)

**Investment Thesis:**
{pe_thesis}

**Key Challenges:**
{key_challenges}

**Management Assessment:**
{mgmt_assessment}

**Top Value Levers:**
{levers_md}"""

    return {
        "company_name": company_name,
        "industry": industry,
        "deal_type": deal_type,
        "entry_ebitda": entry_ebitda,
        "target_ebitda": target_ebitda,
        "ebitda_delta": ebitda_delta,
        "ebitda_growth_pct": round(ebitda_growth_pct, 1),
        "hold_period_years": hold_period_years,
        "pe_thesis": pe_thesis,
        "key_challenges": key_challenges,
        "mgmt_assessment": mgmt_assessment,
        "top_value_levers": levers_md,
        "context_block": context_block,
    }


def _load_section_prompt(section_name: str) -> str:
    filename = _PROMPT_FILENAMES.get(section_name, section_name)
    path = SECTION_PROMPTS_DIR / f"{filename}.md"
    if not path.exists():
        raise FileNotFoundError(f"Section prompt not found: {path}")
    return path.read_text()


async def _generate_section(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    section_name: str,
    context: dict,
    model: str = STANDARD_MODEL,
    max_retries: int = 6,
) -> str:
    print(f"  [100day] Writing: {section_name}...")

    template = _load_section_prompt(section_name)

    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    user_prompt = template.format_map(SafeDict(context))

    wait = 15
    for attempt in range(max_retries):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            return response.content[0].text.strip()
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            print(f"  [100day] Rate limit on {section_name} — waiting {wait}s...")
            await asyncio.sleep(wait)
            wait = min(wait * 2, 120)


async def generate_100day_plan(
    company_name: str,
    industry: str,
    deal_type: str,
    entry_ebitda: float,
    target_ebitda: float,
    hold_period_years: int,
    pe_thesis: str,
    key_challenges: str,
    mgmt_assessment: str,
    top_value_levers: list[str],
    model_mode: str = "standard",
) -> dict[str, str]:
    """
    Generate all 5 sections of a 100-day plan in parallel.

    Returns a dict keyed by section name:
      workstreams, resource_plan, csuite_assessment, org_chart, ebitda_bridge
    """
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    model = PREMIUM_MODEL if model_mode == "premium" else STANDARD_MODEL

    context = build_100day_context(
        company_name=company_name,
        industry=industry,
        deal_type=deal_type,
        entry_ebitda=entry_ebitda,
        target_ebitda=target_ebitda,
        hold_period_years=hold_period_years,
        pe_thesis=pe_thesis,
        key_challenges=key_challenges,
        mgmt_assessment=mgmt_assessment,
        top_value_levers=top_value_levers,
    )

    system_prompt = (
        "You are a senior PE operating partner with 15+ years of middle market buyout experience. "
        "You write precise, actionable 100-day plans grounded in operational reality. "
        "Use PE vocabulary naturally (VCP, PortCo, EBITDA bridge, cadence, governance, KPI, BI layer). "
        "Never use: 'synergies', 'leverage our learnings', 'circle back', 'best-in-class'. "
        "Be directional and specific. Flag uncertainty explicitly. "
        "Days 1–30 are for listening. Quick wins live in Days 30–60. "
        "Never promise deliverables that require systems or data that don't exist yet."
    )

    print(f"\n[100-Day Plan] Generating 5 sections in parallel for {company_name}...")

    tasks = [
        _generate_section(client, system_prompt, section, context, model=model)
        for section in SECTIONS
    ]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    output: dict[str, str] = {}
    for section, result in zip(SECTIONS, results):
        if isinstance(result, Exception):
            print(f"  [100day] ERROR on {section}: {result}")
            output[section] = f"_Error generating section: {result}_"
        else:
            output[section] = result

    print(f"[100-Day Plan] Complete. {sum(1 for v in output.values() if not v.startswith('_Error'))} / {len(SECTIONS)} sections generated.")
    return output
