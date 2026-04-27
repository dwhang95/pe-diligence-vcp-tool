# Prompt: What Would Change My View (Bullet Mode)

Generate the "What Would Change My View" section for the PE ops diligence brief.

## Input Context
- Company: {company_name}
- Description: {description}
- Industry: {industry}
- EV range: {ev_range}
- Context notes: {context_notes}
- Research findings: {research_summary}
- Executive summary: {exec_summary_text}
- Risk flags: {risk_flags_summary}
- Value creation opportunities: {value_creation_summary}

## Format Rules — STRICTLY ENFORCE
- Maximum 3 upgrades + 3 downgrades. Each = exactly 1 line.
- Every item maximum 25 words.
- No hedging. No prose paragraphs. No introductory sentences.
- Items must be specific and falsifiable — not generic ("management is strong").
- Do not restate context already in the input.

## Instructions

Write 3 upgrade triggers and 3 downgrade triggers. These are IC-level conviction signals — specific, falsifiable conditions that would materially change the view.

Upgrades: confirmed in diligence → deal becomes more attractive.
Downgrades: confirmed in diligence → thesis impaired or deal breaks.

## Format
```
## What Would Change My View

### Upgrades
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}

### Downgrades
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}
- {{Specific falsifiable condition → what it means for the thesis — max 25 words}}
```
