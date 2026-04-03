"""
formatter.py — Assemble generated sections into the final brief markdown.
"""

from pathlib import Path
from datetime import date


def assemble_brief(
    company_name: str,
    industry: str,
    ev_range: str,
    sections: dict,
    research_summary: str,
) -> str:
    template = Path("templates/brief_template.md").read_text()

    today = date.today().strftime("%Y-%m-%d")
    slug = company_name.lower().replace(" ", "_").replace(",", "").replace(".", "")

    # Extract source URLs from research summary (lines starting with http)
    source_lines = [
        line.strip()
        for line in research_summary.splitlines()
        if line.strip().startswith("http")
    ]
    data_sources = "\n".join(f"- {s}" for s in source_lines) if source_lines else (
        "- Claude API training data (company public information as of knowledge cutoff)\n"
        "- Note: No live web search was performed. Validate against current sources."
    )

    brief = template.replace("{company_name}", company_name)
    brief = brief.replace("{date}", today)
    brief = brief.replace("{industry}", industry)
    brief = brief.replace("{ev_range}", ev_range)
    brief = brief.replace("{exec_summary}", sections["exec_summary"])
    brief = brief.replace("{risk_flags}", sections["risk_flags"])
    brief = brief.replace("{it_systems}", sections["it_systems"])
    brief = brief.replace("{value_creation}", sections["value_creation"])
    brief = brief.replace("{100_day_plan}", sections["100_day_plan"])
    brief = brief.replace("{diligence_questions}", sections["diligence_questions"])
    brief = brief.replace("{data_sources}", data_sources)

    return brief, slug, today


def save_brief(brief: str, slug: str, today: str) -> Path:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    output_path = output_dir / f"{slug}_{today}.md"
    output_path.write_text(brief)
    return output_path
