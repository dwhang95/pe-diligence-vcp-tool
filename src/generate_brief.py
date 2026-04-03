#!/usr/bin/env python3
"""
PE Ops Due Diligence Brief Generator

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

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
PROMPTS_DIR = BASE_DIR / "prompts"
SECTION_PROMPTS_DIR = PROMPTS_DIR / "section_prompts"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"

MODEL = "claude-sonnet-4-6"


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
) -> tuple[str, list[str]]:
    """
    Use Claude + web_search tool to gather operational intelligence.
    Implements a standard agentic loop; web_search is server-side so
    we never need to execute the tool ourselves.
    """
    print(f"  [research] Starting web research for {company_name}...")

    prompt = load_template("research_prompt").format(
        company_name=company_name,
        description=description,
        industry=industry,
    )

    messages: list[dict] = [{"role": "user", "content": prompt}]
    all_sources: list[str] = []

    for iteration in range(10):  # safety cap
        response = await client.messages.create(
            model=MODEL,
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
) -> str:
    """Generate a single section of the brief via a single Claude call."""
    print(f"  [generate] Writing: {section_name}...")

    section_template = load_template(section_name, section=True)

    # .format_map with a defaultdict-style fallback so missing keys don't crash
    class SafeDict(dict):
        def __missing__(self, key):
            return f"{{{key}}}"

    user_prompt = section_template.format_map(SafeDict(context))

    response = await client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=system_prompt,
        messages=[{"role": "user", "content": user_prompt}],
    )

    raw = response.content[0].text
    return strip_leading_section_header(raw)


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------

async def generate_brief(
    company_name: str,
    description: str,
    industry: str,
    ev_range: str = "$50M–$500M",
    context_notes: str = "",
) -> str:

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        sys.exit("Error: ANTHROPIC_API_KEY environment variable not set.")

    client = anthropic.AsyncAnthropic(api_key=api_key)

    # -----------------------------------------------------------------------
    # Phase 1: Web research + template loading in parallel
    # -----------------------------------------------------------------------
    print("\n[Phase 1] Web research + loading templates in parallel...")

    async def load_static_templates() -> tuple[str, str]:
        system_prompt = load_template("system_prompt")
        brief_template = (TEMPLATES_DIR / "brief_template.md").read_text()
        return system_prompt, brief_template

    (research_text, sources), (system_prompt, brief_template) = await asyncio.gather(
        run_research_agent(client, company_name, description, industry),
        load_static_templates(),
    )

    research_summary = research_text.strip() if research_text.strip() else (
        "No public research data found — assess all hypotheses in management diligence."
    )

    base_context = {
        "company_name": company_name,
        "description": description,
        "industry": industry,
        "ev_range": ev_range,
        "context_notes": context_notes or "None provided.",
        "research_summary": research_summary,
    }

    # -----------------------------------------------------------------------
    # Phase 2: Sections 1–4 in parallel (no cross-section dependencies)
    # -----------------------------------------------------------------------
    print("\n[Phase 2] Generating sections 1–4 in parallel...")

    exec_summary, risk_flags, it_systems, value_creation = await asyncio.gather(
        generate_section(client, system_prompt, "exec_summary", base_context),
        generate_section(client, system_prompt, "risk_flags", base_context),
        generate_section(client, system_prompt, "it_systems", base_context),
        generate_section(client, system_prompt, "value_creation", base_context),
    )

    # -----------------------------------------------------------------------
    # Phase 3: Sections 5–6 in parallel (depend on risk_flags + value_creation)
    # -----------------------------------------------------------------------
    print("\n[Phase 3] Generating sections 5–6 in parallel...")

    extended_context = {
        **base_context,
        "risk_flags_summary": risk_flags,
        "vc_levers_summary": value_creation,
    }

    day_plan, diligence_questions = await asyncio.gather(
        generate_section(client, system_prompt, "100_day_plan", extended_context),
        generate_section(client, system_prompt, "diligence_questions", extended_context),
    )

    # -----------------------------------------------------------------------
    # Phase 4: Assemble and write output
    # -----------------------------------------------------------------------
    print("\n[Phase 4] Assembling brief...")

    today = date.today().strftime("%Y-%m-%d")

    sources_md = (
        "\n".join(f"- {url}" for url in dict.fromkeys(sources))  # deduplicate, preserve order
        if sources
        else "- Desk research based on LLM training data (no live URLs captured)"
    )

    brief = brief_template.format_map({
        "company_name": company_name,
        "date": today,
        "industry": industry,
        "ev_range": ev_range,
        "exec_summary": exec_summary,
        "risk_flags": risk_flags,
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
