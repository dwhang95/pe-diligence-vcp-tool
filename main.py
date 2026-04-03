"""
main.py — CLI entry point for the PE Ops Due Diligence Brief Generator.

Usage:
    python main.py <company_name> <description> <industry> [ev_range] [context_notes]

Example:
    python main.py "CBIZ" \
        "Professional business services company providing accounting, tax, insurance, and employee benefits to mid-market companies" \
        "Business Services / Professional Services" \
        "$4.7B EV" \
        "Take-private scenario; 2+ prior PE sponsors; aggressive M&A roll-up of CPA firms"
"""

import sys
import os
from dotenv import load_dotenv
import anthropic

from researcher import gather_research
from brief_generator import generate_brief_sections
from formatter import assemble_brief, save_brief


def main():
    load_dotenv()

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set in .env")
        sys.exit(1)

    if len(sys.argv) < 4:
        print("Usage: python main.py <company_name> <description> <industry> [ev_range] [context_notes]")
        sys.exit(1)

    company_name = sys.argv[1]
    description = sys.argv[2]
    industry = sys.argv[3]
    ev_range = sys.argv[4] if len(sys.argv) > 4 else "Not specified"
    context_notes = sys.argv[5] if len(sys.argv) > 5 else "No additional context provided."

    client = anthropic.Anthropic(api_key=api_key)

    print(f"\n=== PE Ops Diligence Brief Generator ===")
    print(f"Target: {company_name}")
    print(f"Industry: {industry}")
    print(f"EV: {ev_range}")
    print()

    print("Step 1/3: Gathering research intelligence...")
    research_summary = gather_research(company_name, description, industry, client)
    print("  Done.\n")

    print("Step 2/3: Generating brief sections...")
    sections = generate_brief_sections(
        company_name=company_name,
        description=description,
        industry=industry,
        ev_range=ev_range,
        context_notes=context_notes,
        research_summary=research_summary,
        client=client,
    )
    print("  Done.\n")

    print("Step 3/3: Assembling and saving brief...")
    brief, slug, today = assemble_brief(
        company_name=company_name,
        industry=industry,
        ev_range=ev_range,
        sections=sections,
        research_summary=research_summary,
    )
    output_path = save_brief(brief, slug, today)
    print(f"  Saved to: {output_path}\n")

    print(f"=== Brief complete: {output_path} ===\n")
    print(brief)


if __name__ == "__main__":
    main()
