"""
researcher.py — Gather pre-diligence intelligence on a PE buyout target.
Uses Claude API to synthesize research findings from training knowledge.
"""

import anthropic
from pathlib import Path


def load_prompt(path: str, **kwargs) -> str:
    text = Path(path).read_text()
    for k, v in kwargs.items():
        text = text.replace(f"{{{k}}}", v)
    return text


def gather_research(company_name: str, description: str, industry: str, client: anthropic.Anthropic) -> str:
    prompt = load_prompt(
        "prompts/research_prompt.md",
        company_name=company_name,
        description=description,
        industry=industry,
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2000,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text
