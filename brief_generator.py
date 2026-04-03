"""
brief_generator.py — Generate each section of the ops diligence brief using Claude API.
"""

import time
import anthropic
from pathlib import Path


def load_system_prompt() -> str:
    return Path("prompts/system_prompt.md").read_text()


def load_section_prompt(section: str, **kwargs) -> str:
    text = Path(f"prompts/section_prompts/{section}.md").read_text()
    for k, v in kwargs.items():
        text = text.replace(f"{{{k}}}", str(v))
    return text


def generate_section(
    section_prompt: str,
    system_prompt: str,
    client: anthropic.Anthropic,
    max_tokens: int = 4096,
    retries: int = 3,
) -> str:
    for attempt in range(retries):
        try:
            message = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=max_tokens,
                system=system_prompt,
                messages=[{"role": "user", "content": section_prompt}],
            )
            return message.content[0].text
        except (anthropic.APIConnectionError, anthropic.APIStatusError) as e:
            if attempt < retries - 1:
                wait = 2 ** attempt
                print(f"    Connection error, retrying in {wait}s... ({e})")
                time.sleep(wait)
            else:
                raise


def generate_brief_sections(
    company_name: str,
    description: str,
    industry: str,
    ev_range: str,
    context_notes: str,
    research_summary: str,
    client: anthropic.Anthropic,
) -> dict:
    system = load_system_prompt()

    common = dict(
        company_name=company_name,
        description=description,
        industry=industry,
        ev_range=ev_range,
        research_summary=research_summary,
    )

    print("  Generating executive summary...")
    exec_summary = generate_section(
        load_section_prompt("exec_summary", context_notes=context_notes, **common),
        system, client,
    )

    print("  Generating risk flags...")
    risk_flags = generate_section(
        load_section_prompt("risk_flags", **common),
        system, client,
    )

    print("  Generating IT & systems maturity...")
    it_systems = generate_section(
        load_section_prompt("it_systems", **common),
        system, client,
    )

    print("  Generating value creation opportunities...")
    value_creation = generate_section(
        load_section_prompt("value_creation", context_notes=context_notes, **common),
        system, client, max_tokens=4096,
    )

    # Pass summaries of prior sections into the 100-day and diligence Q sections
    risk_flags_summary = risk_flags[:800]
    vc_levers_summary = value_creation[:800]

    print("  Generating 100-day plan...")
    plan_100_day = generate_section(
        load_section_prompt(
            "100_day_plan",
            risk_flags_summary=risk_flags_summary,
            vc_levers_summary=vc_levers_summary,
            **common,
        ),
        system, client,
    )

    print("  Generating diligence questions...")
    diligence_questions = generate_section(
        load_section_prompt(
            "diligence_questions",
            risk_flags_summary=risk_flags_summary,
            **common,
        ),
        system, client,
    )

    return {
        "exec_summary": exec_summary,
        "risk_flags": risk_flags,
        "it_systems": it_systems,
        "value_creation": value_creation,
        "100_day_plan": plan_100_day,
        "diligence_questions": diligence_questions,
    }
