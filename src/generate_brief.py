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
SECTION_PROMPTS_BULLET_DIR = SECTION_PROMPTS_DIR / "bullet"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

# Default data sources (non-premium)
DEFAULT_DATA_SOURCES = ["sec_edgar", "yahoo_finance", "bls", "news"]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def load_template(name: str, section: bool = False, section_dir: Path | None = None) -> str:
    if section:
        directory = section_dir if section_dir is not None else SECTION_PROMPTS_DIR
    else:
        directory = PROMPTS_DIR
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
    section_dir: Path | None = None,
) -> str:
    """
    Generate a single section of the brief via a single Claude call.
    Auto-retries on 429 rate-limit errors with exponential backoff (15s, 30s, 60s...).
    """
    model_tag = " [Opus]" if model == PREMIUM_MODEL else ""
    print(f"  [generate] Writing: {section_name}{model_tag}...")

    section_template = load_template(section_name, section=True, section_dir=section_dir)

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

# Optional modules — off by default, appended after core sections when selected
OPTIONAL_MODULES = [
    "transaction_structure",
    "change_my_view",
    "synergy_analysis",
    "investment_recommendation",
    "credit_metrics",
    "saas_metrics",
    "functional_scorecards",
]

CORE_SECTION_TITLES = {
    "exec_summary":        "Executive Summary",
    "risk_flags":          "Operational Risk Flags",
    "comps_benchmarks":    "Comparable Companies & Benchmarks",
    "it_systems":          "IT & Systems Maturity",
    "value_creation":      "Value Creation Opportunities",
    "100_day_plan":        "100-Day Plan Outline Starter",
    "diligence_questions": "Key Diligence Questions",
}

OPTIONAL_SECTION_TITLES = {
    "transaction_structure":    "Transaction Structure Analysis",
    "change_my_view":           "What Would Change My View",
    "synergy_analysis":         "Synergy Analysis",
    "investment_recommendation":"Investment Recommendation",
    "credit_metrics":           "Credit & Financial Metrics",
    "saas_metrics":             "SaaS & Technology Metrics",
    "functional_scorecards":    "Functional Scorecards",
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
    deal_type: str = "Standard (Mfg / Services / Retail)",
    brief_style: str = "long_form",
) -> str:
    """
    modules:      list of section keys to generate (default: all core modules).
                  Optional module keys (transaction_structure, change_my_view, etc.)
                  are only generated when explicitly included.
    style_reference: extracted text from an uploaded document to mirror.
    data_sources: list of enabled data source keys, e.g. ["sec_edgar", "bls", "news"].
                  Defaults to all non-premium sources.
    model_mode:   "standard" (Sonnet for all) or "premium" (Opus for key sections).
    deal_type:    deal type label (e.g. "Financial Services / Fintech", "Technology / SaaS").
    brief_style:  "bullet" (concise ~5k words) or "long_form" (full ~10k words).
    """
    if modules is None:
        modules = ALL_MODULES
    if data_sources is None:
        data_sources = DEFAULT_DATA_SOURCES

    # Resolve prompt directory based on style
    _section_dir = SECTION_PROMPTS_BULLET_DIR if brief_style == "bullet" else SECTION_PROMPTS_DIR

    ds = set(data_sources)

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.AsyncAnthropic(api_key=api_key)
    research_model = get_research_model(model_mode)
    print(f"\n[Mode] {'Premium (Opus for key sections)' if model_mode == 'premium' else 'Standard (Sonnet)'}")
    print(f"[Style] {brief_style}")
    print(f"[Sources] {sorted(ds)}")

    # -----------------------------------------------------------------------
    # Phase 1: Web research + real data fetches + template loading — all parallel
    # -----------------------------------------------------------------------
    print("\n[Phase 1] Web research, data pulls, and template loading in parallel...")

    async def load_static_templates() -> str:
        base_system = load_template("system_prompt")
        if style_reference.strip():
            style_addendum = (
                "\n\n---\n\n"
                "**STYLE REFERENCE DOCUMENT (uploaded by user)**\n"
                "Mirror the structure, tone, and formatting style of this document "
                "when generating each section. Adapt content but match the voice and layout:\n\n"
                f"{style_reference[:6000]}"
            )
            return base_system + style_addendum
        return base_system

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

    (research_text, sources), system_prompt, data_results = (
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
        "deal_type": deal_type,
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
        # Use bullet dir only if prompt file exists there; otherwise fall back to long_form
        resolved_dir = _section_dir
        if brief_style == "bullet" and not (_section_dir / f"{section_key}.md").exists():
            resolved_dir = SECTION_PROMPTS_DIR
        return await generate_section(
            client, system_prompt, section_key, ctx,
            model=section_model, section_dir=resolved_dir,
        )

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
    # Phase 3: Sections 6–7 + optional sections that need Phase 2 outputs
    # -----------------------------------------------------------------------
    print("\n[Phase 3] Generating sections 6–7 and optional sections...")

    extended_context = {
        **base_context,
        "risk_flags_summary": risk_flags,
        "vc_levers_summary": value_creation,
    }

    day_plan            = await gen("100_day_plan",        extended_context)
    diligence_questions = await gen("diligence_questions", extended_context)

    # Optional sections that depend only on base_context
    transaction_structure = await gen("transaction_structure", base_context)
    synergy_analysis      = await gen("synergy_analysis",      base_context)
    credit_metrics        = await gen("credit_metrics",        base_context)
    saas_metrics          = await gen("saas_metrics",          base_context)
    functional_scorecards = await gen("functional_scorecards", base_context)

    # change_my_view needs exec_summary + risk_flags + value_creation
    cmv_context = {
        **base_context,
        "exec_summary_text":      exec_summary,
        "risk_flags_summary":     risk_flags,
        "value_creation_summary": value_creation,
    }
    change_my_view = await gen("change_my_view", cmv_context)

    # investment_recommendation needs all key prior outputs
    ir_context = {
        **base_context,
        "exec_summary_text":      exec_summary,
        "risk_flags_summary":     risk_flags,
        "value_creation_summary": value_creation,
    }
    investment_recommendation = await gen("investment_recommendation", ir_context)

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

    _EXCLUDED = "_Section excluded from this brief._"

    # Build brief programmatically so optional sections get correct numbering
    brief_lines = [
        f"# PE Ops Diligence Brief: {company_name}",
        "",
        f"**Generated:** {today}",
        f"**Industry:** {industry}",
        f"**EV Range:** {ev_range}",
        f"**Deal Type:** {deal_type}",
        "**Brief Version:** 2.1 (Pre-Diligence / Desk Research + Real Data)",
        f"**Brief Style:** {'Bullet (~5,000 words)' if brief_style == 'bullet' else 'Long Form (~10,000 words)'}",
        "",
        "> *This brief combines publicly available data (SEC EDGAR, BLS, news) with LLM analysis. "
        "It is intended to inform diligence priorities and management meeting preparation — not to "
        "replace direct diligence. Public comp benchmarks skew larger than typical middle-market "
        "targets; treat as directional context.*",
        "",
        "---",
        "",
    ]

    section_num = 1

    core_results = [
        ("exec_summary",        exec_summary),
        ("risk_flags",          risk_flags),
        ("comps_benchmarks",    comps_benchmarks),
        ("it_systems",          it_systems),
        ("value_creation",      value_creation),
        ("100_day_plan",        day_plan),
        ("diligence_questions", diligence_questions),
    ]

    for key, content in core_results:
        if key in modules and content != _EXCLUDED:
            title = CORE_SECTION_TITLES[key]
            brief_lines += [f"## {section_num}. {title}", "", content, "", "---", ""]
            section_num += 1

    optional_results = [
        ("transaction_structure",    transaction_structure),
        ("change_my_view",           change_my_view),
        ("synergy_analysis",         synergy_analysis),
        ("investment_recommendation",investment_recommendation),
        ("credit_metrics",           credit_metrics),
        ("saas_metrics",             saas_metrics),
        ("functional_scorecards",    functional_scorecards),
    ]

    for key, content in optional_results:
        if key in modules and content != _EXCLUDED:
            title = OPTIONAL_SECTION_TITLES[key]
            brief_lines += [f"## {section_num}. {title}", "", content, "", "---", ""]
            section_num += 1

    brief_lines += [
        f"## {section_num}. Data Sources Consulted",
        "",
        sources_md,
        "",
        "---",
        "",
        f"*Generated by PE Ops Due Diligence Brief Generator v2.1 | {today}*",
    ]

    brief = "\n".join(brief_lines)

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
        deal_type="Standard (Mfg / Services / Retail)",
    ))


if __name__ == "__main__":
    main()
