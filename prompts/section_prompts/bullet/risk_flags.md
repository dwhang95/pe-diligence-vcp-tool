# Prompt: Operational Risk Flags (Bullet Mode)

Generate the Operational Risk Flags section for the PE ops diligence brief.

## Input Context
- Company: {company_name} | Industry: {industry} | EV: {ev_range}
- Description: {description}
- Research findings: {research_summary}

## Format Rules — STRICTLY ENFORCE
- Bullets only. No prose paragraphs whatsoever.
- Every bullet maximum 25 words.
- Do not restate context already in the input.
- No hedging language ("it appears", "it seems", "may potentially").
- State the finding, then the implication. Nothing else.
- Maximum 5 risks total. Only flag what is genuinely material.

## Instructions

Identify the 5 most material operational risks. Draw from: People & Organization, Operational Infrastructure, Supply Chain & Procurement, Quality & Compliance, Customer Concentration.

For each risk:
- One header line: risk name + rating (Low / Medium / High / Critical)
- Exactly 2 sub-bullets only:
  - Bullet 1: the finding (what the risk is, max 25 words)
  - Bullet 2: the thesis implication (what it means for the deal, max 25 words)

No diligence questions in this section.

## Format
```
## 2. Operational Risk Flags

### {{Risk Name}} — {{Low/Medium/High/Critical}}
- {{Finding: what the risk is — max 25 words}}
- {{Implication: what this means for the thesis or close conditions — max 25 words}}

### {{Risk Name}} — {{Low/Medium/High/Critical}}
- {{Finding}}
- {{Implication}}

[Repeat — max 5 risks]
```
