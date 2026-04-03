# PE Ops Due Diligence Brief Generator

Generates structured operational due diligence briefs for middle market PE buyout targets ($50M–$500M EV).

## What it produces

Given a company name, description, and industry, the tool researches the company and generates a markdown brief covering:

1. Executive summary + overall ops risk rating
2. Operational risk flags (People, Ops Infrastructure, Supply Chain, Quality, Customer Concentration)
3. IT & systems maturity assessment
4. Value creation opportunities (prioritized)
5. 100-day plan outline starter
6. Key diligence questions for management

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env  # Add your ANTHROPIC_API_KEY
```

## Usage

```bash
python src/main.py \
  --company "Acme Packaging" \
  --description "Mid-sized corrugated packaging manufacturer serving food & beverage customers in the Midwest. 3 facilities, ~400 employees." \
  --industry "industrial packaging" \
  --ev "$120M" \
  --notes "Founder-owned, first institutional capital"
```

Output saved to `output/acme-packaging_2026-03-09.md`.

## Project Structure

```
pe-diligence-tool/
├── spec.md              # Full product specification
├── CLAUDE.md            # PE ops framework + AI context
├── README.md            # This file
├── src/                 # Source code
├── prompts/             # LLM prompt templates
├── templates/           # Output templates
└── output/              # Generated briefs (gitignored)
```

See `spec.md` for full architecture and output format details.
