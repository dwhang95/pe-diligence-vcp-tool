#!/usr/bin/env python3
"""
PE Ops Due Diligence Brief Generator — v2

Usage:
    python src/generate_brief.py \
        --company "Acme Packaging" \
        --description "..." \
        --industry "industrial packaging" \
        --ev "$120M" \
        --notes "Founder-owned, first institutional capital"
"""

import argparse
import asyncio
import os
import re
import sys
from datetime import date
from pathlib import Path

import anthropic

# Load .env from project root if it exists (optional dependency)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent.parent / ".env")
except ImportError:
    pass  # dotenv not installed — fall through to os.environ

# Data source clients (v2)
sys.path.insert(0, str(Path(__file__).parent))
from data_sources.sec_edgar import fetch_sec_comps, SICLookup
from data_sources.news import fetch_recent_news, NewsResult
from data_sources.bls import fetch_bls_benchmarks
from data_sources.yahoo_finance import fetch_yahoo_finance_comps
from data_sources.damodaran import fetch_damodaran_multiples
from data_sources.naver_finance import fetch_naver_finance

from tier import STANDARD_MODEL, PREMIUM_MODEL, get_model_for_section, get_research_model

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
SECTION_PROMPTS_DIR = PROMPTS_DIR / "section_prompts"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Default data sources (non-premium)
DEFAULT_DATA_SOURCES = ["sec_edgar", "yahoo_finance", "bls", "news"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_template(name: str, section: bool = False) -> str:
    directory = SECTION_PROMPTS_DIR if section else PROMPTS_DIR
    return (directory / f"{name}.md").read_text()


def strip_leading_section_header(text: str) -> str:
    """
    Models often echo back the '## N. Section Name' header from the format spec.
    Strip it so the brief_template's own headers aren't duplicated.
    """
    lines = text.strip().splitlines()
    if lines and re.match(r"^##\s+\d+\.", lines[0]):
        # Drop the header line and any immediately-following blank lines
        start = 1
        while start < len(lines) and not lines[start].strip():
            start += 1
        return "\n".join(lines[start:])
    return text.strip()


def extract_sources(response_content: list) -> list[str]:
    """Pull URLs out of web_search tool_result blocks."""
    urls = []
    for block in response_content:
        btype = getattr(block, "type", None)
        if btype == "tool_result":
            items = getattr(block, "content", [])
            if isinstance(items, list):
                for item in items:
                    if isinstance(item, dict):
                        url = item.get("url") or item.get("source", "")
                        if url:
                            urls.append(url)
    return urls


# ---------------------------------------------------------------------------
# Phase 1: Web research agent
# ---------------------------------------------------------------------------

async def run_research_agent(
    client: anthropic.AsyncAnthropic,
    company_name: str,
    description: str,
    industry: str,
    model: str = STANDARD_MODEL,
) -> tuple[str, list[str]]:
    """
    Use Claude + web_search tool to gather operational intelligence.
    Implements a standard agentic loop; web_search is server-side so
    we never need to execute the tool ourselves.
    """
    print(f"  [research] Starting web research for {company_name}...")

    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    prompt = load_template("research_prompt").format_map(SafeDict(
        company_name=company_name,
        description=description,
        industry=industry,
    ))

    messages: list[dict] = [{"role": "user", "content": prompt}]
    all_sources: list[str] = []

    for iteration in range(10):  # safety cap
        response = await client.messages.create(
            model=model,
            max_tokens=8096,
            tools=[{"type": "web_search_20250305", "name": "web_search", "max_uses": 8}],
            messages=messages,
        )

        all_sources.extend(extract_sources(response.content))

        if response.stop_reason == "end_turn":
            text = "\n".join(
                block.text
                for block in response.content
                if getattr(block, "type", None) == "text" and getattr(block, "text", None)
            )
            print(f"  [research] Complete. {len(all_sources)} sources found.")
            return text, all_sources

        # stop_reason == "tool_use" — add assistant turn and continue loop
        messages.append({"role": "assistant", "content": response.content})
        print(f"  [research] Iteration {iteration + 1}: continuing search...")

    # Fallback if loop exhausted
    final_text = "\n".join(
        block.text
        for block in response.content
        if getattr(block, "type", None) == "text" and getattr(block, "text", None)
    )
    return final_text, all_sources


# ---------------------------------------------------------------------------
# Phase 2–3: Section generation
# ---------------------------------------------------------------------------

async def generate_section(
    client: anthropic.AsyncAnthropic,
    system_prompt: str,
    section_name: str,
    context: dict,
    model: str = STANDARD_MODEL,
    max_retries: int = 6,
) -> str:
    """
    Generate a single section of the brief via a single Claude call.
    Auto-retries on 429 rate-limit errors with exponential backoff (15s, 30s, 60s...).
    """
    model_tag = " [Opus]" if model == PREMIUM_MODEL else ""
    print(f"  [generate] Writing: {section_name}{model_tag}...")

    section_template = load_template(section_name, section=True)

    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    user_prompt = section_template.format_map(SafeDict(context))

    wait = 15  # initial retry wait, seconds
    for attempt in range(max_retries):
        try:
            response = await client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            raw = response.content[0].text
            return strip_leading_section_header(raw)
        except anthropic.RateLimitError:
            if attempt == max_retries - 1:
                raise
            print(f"  [generate] Rate limit hit on {section_name} — waiting {wait}s...")
            await asyncio.sleep(wait)
            wait = min(wait * 2, 120)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

ALL_MODULES = [
    "exec_summary",
    "risk_flags",
    "comps_benchmarks",
    "it_systems",
    "value_creation",
    "100_day_plan",
    "diligence_questions",
]

SECTION_HEADERS = {
    "exec_summary":        "## 1. Executive Summary",
    "risk_flags":          "## 2. Operational Risk Flags",
    "comps_benchmarks":    "## 3. Comparable Companies & Benchmarks",
    "it_systems":          "## 4. IT & Systems Maturity",
    "value_creation":      "## 5. Value Creation Opportunities",
    "100_day_plan":        "## 6. 100-Day Plan Outline Starter",
    "diligence_questions": "## 7. Key Diligence Questions",
}


async def generate_brief(
    company_name: str,
    description: str,
    industry: str,
    ev_range: str = "$50M–$500M",
    context_notes: str = "",
    modules: list[str] | None = None,
    style_reference: str = "",
    data_sources: list[str] | None = None,
    model_mode: str = "standard",
) -> str:
    """
    modules:      list of section keys to generate (default: all).
    style_reference: extracted text from an uploaded document to mirror.
    data_sources: list of enabled data source keys, e.g. ["sec_edgar", "bls", "news"].
                  Defaults to all non-premium sources.
    model_mode:   "standard" (Sonnet for all) or "premium" (Opus for key sections).
    """
    if modules is None:
        modules = ALL_MODULES
    if data_sources is None:
        data_sources = DEFAULT_DATA_SOURCES

    ds = set(data_sources)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    research_model = get_research_model(model_mode)
    print(f"\n[Mode] {'Premium (Opus for key sections)' if model_mode == 'premium' else 'Standard (Sonnet)'}")
    print(f"[Sources] {sorted(ds)}")

    # -----------------------------------------------------------------------
    # Phase 1: Web research + real data fetches + template loading — all parallel
    # -----------------------------------------------------------------------
    print("\n[Phase 1] Web research, data pulls, and template loading in parallel...")

    async def load_static_templates() -> tuple[str, str]:
        base_system = load_template("system_prompt")
        if style_reference.strip():
            style_addendum = (
                "\n\n---\n\n"
                "**STYLE REFERENCE DOCUMENT (uploaded by user)**\n"
                "Mirror the structure, tone, and formatting style of this document "
                "when generating each section. Adapt content but match the voice and layout:\n\n"
                f"{style_reference[:6000]}"
            )
            system_prompt = base_system + style_addendum
        else:
            system_prompt = base_system
        brief_template = (TEMPLATES_DIR / "brief_template.md").read_text()
        return system_prompt, brief_template

    async def fetch_real_data():
        """Conditionally fetch enabled data sources concurrently."""
        tasks = {}

        if "sec_edgar" in ds:
            tasks["sec_edgar"] = fetch_sec_comps(industry)
        if "news" in ds:
            tasks["news"] = fetch_recent_news(company_name, accredited_only=True)
        if "bls" in ds:
            tasks["bls"] = fetch_bls_benchmarks(industry)
        if "yahoo_finance" in ds:
            tasks["yahoo_finance"] = fetch_yahoo_finance_comps(industry)
        if "damodaran" in ds:
            tasks["damodaran"] = fetch_damodaran_multiples(industry)
        if "naver_finance" in ds:
            tasks["naver_finance"] = fetch_naver_finance(company_name)

        if not tasks:
            return {}

        keys = list(tasks.keys())
        results_list = await asyncio.gather(*tasks.values(), return_exceptions=True)
        return dict(zip(keys, results_list))

    (research_text, sources), (system_prompt, brief_template), data_results = (
        await asyncio.gather(
            run_research_agent(client, company_name, description, industry, model=research_model),
            load_static_templates(),
            fetch_real_data(),
        )
    )

    # Unpack results with graceful fallback for each source
    sec_comps     = data_results.get("sec_edgar")
    news_result   = data_results.get("news")
    bls_bench     = data_results.get("bls")
    yf_result     = data_results.get("yahoo_finance")
    damo_result   = data_results.get("damodaran")
    naver_result  = data_results.get("naver_finance")

    # Log data pull results
    if sec_comps and not isinstance(sec_comps, Exception):
        print(f"  [data] SEC EDGAR: {len(sec_comps.comps)} comps (SIC {sec_comps.sic_code})"
              + (f" — {sec_comps.error}" if sec_comps.error else ""))
    if news_result and not isinstance(news_result, Exception):
        print(f"  [data] News: {len(news_result.articles)} articles via {news_result.source_used}")
    if bls_bench and not isinstance(bls_bench, Exception):
        print(f"  [data] BLS: {bls_bench.industry_label}")
    if yf_result and not isinstance(yf_result, Exception):
        valid_snaps = [s for s in yf_result.snapshots if not s.error]
        print(f"  [data] Yahoo Finance: {len(valid_snaps)} valid comp snapshots")
    if damo_result and not isinstance(damo_result, Exception):
        print(f"  [data] Damodaran: {damo_result.industry_label} — EV/EBITDA {damo_result.ev_ebitda}x ({damo_result.source})")
    if naver_result and not isinstance(naver_result, Exception):
        if naver_result.error:
            print(f"  [data] Naver Finance: {naver_result.error}")
        else:
            print(f"  [data] Naver Finance: {naver_result.company_name} ({naver_result.stock_code})")

    research_summary = research_text.strip() if research_text.strip() else (
        "No public research data found — assess all hypotheses in management diligence."
    )

    # Build context blocks for the comps section prompt
    sec_comps_markdown = "_SEC EDGAR not enabled._"
    if sec_comps and not isinstance(sec_comps, Exception):
        sec_comps_markdown = (
            f"**SIC {sec_comps.sic_code} — {sec_comps.sic_label}**\n\n"
            + sec_comps.to_markdown_table()
            if not sec_comps.error
            else f"_SEC EDGAR data unavailable: {sec_comps.error}_"
        )

    bls_benchmark_markdown = "_BLS labor data not enabled._"
    if bls_bench and not isinstance(bls_bench, Exception):
        bls_benchmark_markdown = (
            bls_bench.to_markdown()
            if not bls_bench.error
            else f"_BLS data unavailable: {bls_bench.error}_"
        )

    yf_markdown = ""
    if yf_result and not isinstance(yf_result, Exception):
        yf_markdown = "\n\n" + yf_result.to_markdown()

    damo_markdown = ""
    if damo_result and not isinstance(damo_result, Exception):
        damo_markdown = "\n\n" + damo_result.to_markdown()

    naver_markdown = ""
    if naver_result and not isinstance(naver_result, Exception) and not naver_result.error:
        naver_markdown = "\n\n" + naver_result.to_markdown()

    # Cap news context to stay under token budget
    news_summary_markdown = "_News sweep not enabled._"
    if news_result and not isinstance(news_result, Exception):
        top_articles = sorted(
            news_result.articles,
            key=lambda a: (not a.is_risk_flag, a.date),
            reverse=False,
        )[:12]
        news_trimmed = NewsResult(
            company_name=news_result.company_name,
            days_searched=news_result.days_searched,
            articles=top_articles,
            source_used=news_result.source_used,
            error=news_result.error,
        )
        news_summary_markdown = news_trimmed.to_summary_markdown()

    base_context = {
        "company_name": company_name,
        "description": description,
        "industry": industry,
        "ev_range": ev_range,
        "context_notes": context_notes or "None provided.",
        "research_summary": research_summary,
        # Data source context for Section 3 (comps & benchmarks)
        "sec_comps_markdown":     sec_comps_markdown,
        "bls_benchmark_markdown": bls_benchmark_markdown + yf_markdown + damo_markdown + naver_markdown,
        "news_summary_markdown":  news_summary_markdown,
    }

    async def gen(section_key: str, ctx: dict) -> str:
        if section_key not in modules:
            print(f"  [generate] Skipping (disabled): {section_key}")
            return "_Section excluded from this brief._"
        section_model = get_model_for_section(section_key, model_mode)
        return await generate_section(client, system_prompt, section_key, ctx, model=section_model)

    # -----------------------------------------------------------------------
    # Phase 2: Sections 1–5 sequentially
    # -----------------------------------------------------------------------
    print("\n[Phase 2] Generating sections 1–5 sequentially...")
    exec_summary     = await gen("exec_summary",     base_context)
    risk_flags       = await gen("risk_flags",       base_context)
    comps_benchmarks = await gen("comps_benchmarks", base_context)
    it_systems       = await gen("it_systems",       base_context)
    value_creation   = await gen("value_creation",   base_context)

    # -----------------------------------------------------------------------
    # Phase 3: Sections 6–7 (depend on risk_flags + value_creation)
    # -----------------------------------------------------------------------
    print("\n[Phase 3] Generating sections 6–7...")

    extended_context = {
        **base_context,
        "risk_flags_summary": risk_flags,
        "vc_levers_summary": value_creation,
    }

    day_plan            = await gen("100_day_plan",        extended_context)
    diligence_questions = await gen("diligence_questions", extended_context)

    # -----------------------------------------------------------------------
    # Phase 4: Assemble and write output
    # -----------------------------------------------------------------------
    print("\n[Phase 4] Assembling brief...")

    today = date.today().strftime("%Y-%m-%d")

    # Merge web search sources with data source attributions
    source_lines = list(dict.fromkeys(f"- {url}" for url in sources)) if sources else [
        "- Desk research based on LLM training data (no live URLs captured)"
    ]
    if sec_comps and not isinstance(sec_comps, Exception) and not sec_comps.error:
        source_lines.append(f"- SEC EDGAR XBRL API — SIC {sec_comps.sic_code} public comp financials")
    if bls_bench and not isinstance(bls_bench, Exception) and not bls_bench.error:
        source_lines.append(f"- BLS CES API — {bls_bench.industry_label} labor benchmarks")
    if news_result and not isinstance(news_result, Exception):
        source_lines.append(f"- News sweep: {news_result.source_used} ({len(news_result.articles)} articles, accredited sources)")
    if yf_result and not isinstance(yf_result, Exception):
        source_lines.append(f"- Yahoo Finance — {yf_result.industry_label} public comp proxies")
    if damo_result and not isinstance(damo_result, Exception):
        source_lines.append(f"- Damodaran (NYU) — {damo_result.industry_label} industry multiples ({damo_result.source})")
    if naver_result and not isinstance(naver_result, Exception) and not naver_result.error:
        source_lines.append(f"- Naver Finance — {naver_result.company_name} ({naver_result.exchange})")

    sources_md = "\n".join(source_lines)

    brief = brief_template.format_map({
        "company_name": company_name,
        "date": today,
        "industry": industry,
        "ev_range": ev_range,
        "exec_summary": exec_summary,
        "risk_flags": risk_flags,
        "comps_benchmarks": comps_benchmarks,
        "it_systems": it_systems,
        "value_creation": value_creation,
        "100_day_plan": day_plan,
        "diligence_questions": diligence_questions,
        "data_sources": sources_md,
    })

    OUTPUT_DIR.mkdir(exist_ok=True)
    output_path = OUTPUT_DIR / f"{slugify(company_name)}_ops_brief_{today}.md"
    output_path.write_text(brief, encoding="utf-8")

    print(f"\nBrief saved to: {output_path}")
    return str(output_path)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Generate a PE ops diligence brief for a buyout target.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Example:
  python src/generate_brief.py \\
    --company "Acme Packaging" \\
    --description "Mid-sized corrugated packaging manufacturer." \\
    --industry "industrial packaging" \\
    --ev "$120M" \\
    --notes "Founder-owned, first institutional capital"
""",
    )
    parser.add_argument("--company", required=True, help="Company name")
    parser.add_argument(
        "--description", required=True,
        help="2–5 sentence description of the business",
    )
    parser.add_argument("--industry", required=True, help="Primary industry vertical")
    parser.add_argument(
        "--ev", default="$50M–$500M",
        dest="ev_range",
        help="EV range (default: $50M–$500M)",
    )
    parser.add_argument(
        "--notes", default="", dest="context_notes",
        help="Optional deal context (ownership history, known issues, thesis hooks)",
    )

    args = parser.parse_args()

    asyncio.run(generate_brief(
        company_name=args.company,
        description=args.description,
        industry=args.industry,
        ev_range=args.ev_range,
        context_notes=args.context_notes,
    ))


if __name__ == "__main__":
    main()
