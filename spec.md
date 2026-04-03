# PE Ops Due Diligence Brief Generator — Spec

## Overview

A CLI tool that generates structured operational due diligence briefs for middle market buyout targets ($50M–$500M EV). Given a company name, description, and industry, the tool researches the company via web search and produces a markdown brief covering operational risk flags, IT/systems maturity, value creation opportunities, and a 100-day plan outline starter.

---

## Target Use Case

**Who uses this:** PE operations professionals, value creation teams, deal teams preparing for IC or early-stage diligence.

**When they use it:** Before management meetings, during early-stage diligence, or when prepping an ops angle for an IC memo.

**What they need:** A structured, opinionated brief — not a data dump. The output should read like something a senior ops partner would hand to the deal team, not a generic report.

---

## Input Schema

| Field | Type | Required | Description |
|---|---|---|---|
| `company_name` | string | Yes | Legal or common name of the target company |
| `description` | string | Yes | 2–5 sentence description of the business (what they do, how they make money) |
| `industry` | string | Yes | Primary industry vertical (e.g., "industrial packaging", "healthcare services") |
| `ev_range` | string | No | Estimated EV range (default: "$50M–$500M") |
| `context_notes` | string | No | Optional deal context: ownership history, known issues, investment thesis hooks |

---

## Output Structure

Output is a single `.md` file saved to `output/` named `{company_name_slug}_{YYYY-MM-DD}.md`.

### Sections

#### 1. Executive Summary
- 3–5 sentence snapshot of the company
- Key operational profile (asset-heavy vs. light, labor intensity, tech dependency)
- Overall ops risk rating: **Low / Medium / High / Critical**

#### 2. Operational Risk Flags
Flag categories (score each Low/Medium/High):
- **People & Org:** Key-man dependency, management depth, union exposure, turnover indicators
- **Operational Infrastructure:** Capacity utilization, facility condition signals, capex overhang risk
- **Supply Chain & Procurement:** Concentration risk, input cost exposure, vendor dependency
- **Quality & Compliance:** Regulatory exposure, customer quality requirements, certifications at risk
- **Customer Concentration:** Top customer dependency, contract structure, churn signals

For each flag: brief explanation + directional risk level + suggested diligence question.

#### 3. IT & Systems Maturity
- ERP/core systems assessment (based on company size, industry, ownership history)
- Data and reporting maturity hypothesis
- Tech debt risk
- Digital/AI enablement potential
- Suggested systems diligence checklist (5–8 questions)

#### 4. Value Creation Opportunities
Structured as a prioritized list of operational levers:

| Priority | Lever | Category | Est. Timeline | Confidence |
|---|---|---|---|---|
| 1 | [description] | [Revenue / Cost / Working Capital / Org] | [0–12 / 12–24 / 24–36 mo] | [High/Med/Low] |

Categories: Revenue Growth, Cost Reduction, Working Capital, Organizational Effectiveness, Digital/AI Transformation

Minimum 4, maximum 8 levers. Each includes a 1–2 sentence rationale.

#### 5. 100-Day Plan Outline Starter
Phase structure:
- **Days 1–30: Listen & Diagnose** — Key listening tour priorities, data requests, stakeholder mapping
- **Days 31–60: Align & Plan** — Priority workstreams to launch, governance setup, quick wins to target
- **Days 61–100: Execute & Report** — First deliverables, KPI baseline, board reporting cadence

Each phase: 3–5 bullet points. Tailored to the company's specific profile, not generic.

#### 6. Key Diligence Questions
Master list of 10–15 ops-specific questions the deal team should ask management, organized by theme.

#### 7. Data Sources Consulted
List of web sources searched and used to inform the brief.

---

## Technical Architecture

### Stack
- **Runtime:** Python 3.11+
- **LLM:** Claude API (claude-sonnet-4-6 or claude-opus-4-6)
- **Web Search:** Claude's web search tool or SerpAPI / Tavily
- **Output:** Markdown file written to `output/`
- **CLI:** Simple argparse or `click`-based interface

### File Structure
```
pe-diligence-tool/
├── spec.md                  # This document
├── CLAUDE.md                # PE ops framework + project context
├── README.md                # Setup and usage
├── requirements.txt         # Python dependencies
├── src/
│   ├── main.py              # CLI entrypoint
│   ├── researcher.py        # Web search + company research logic
│   ├── brief_generator.py   # LLM prompt construction + output generation
│   └── formatter.py         # Markdown rendering and file output
├── prompts/
│   ├── system_prompt.md     # Master system prompt for LLM
│   ├── research_prompt.md   # Web research guidance prompt
│   └── section_prompts/     # Per-section prompt templates
│       ├── exec_summary.md
│       ├── risk_flags.md
│       ├── it_systems.md
│       ├── value_creation.md
│       ├── 100_day_plan.md
│       └── diligence_questions.md
├── templates/
│   └── brief_template.md    # Output markdown structure template
└── output/                  # Generated briefs (gitignored)
```

### Data Flow
1. User runs CLI with company inputs
2. `researcher.py` runs web searches: company news, financials, Glassdoor signals, industry context
3. Research results + user inputs passed to `brief_generator.py`
4. LLM generates each section using section-specific prompts
5. `formatter.py` assembles final markdown, writes to `output/`

---

## Quality Standards

**The brief must:**
- Sound like it was written by a senior PE ops professional, not a consultant
- Include specific, directional insights — not hedged generalities
- Flag what we don't know and why it matters
- Use PE vocabulary naturally (VCP, PortCo, EBITDA, IC, 100-day, cadence, governance)
- Never produce a section that looks copy-pasted from a generic framework

**Red flags in output (must avoid):**
- "This company may have opportunities to improve operational efficiency" (too vague)
- Generic 100-day plans that could apply to any company
- IT sections that just say "assess ERP systems" without company-specific context
- Risk flags with no directional hypothesis

---

## Future Enhancements (v2+)
- PDF export with formatting
- Comparable company benchmarking (pull comps from public data)
- Integration with Pitchbook / CapIQ for financial data
- Multi-company batch mode for portfolio screening
- IC memo integration — export ops section directly into memo template
- Sector-specific modules (healthcare, industrials, services, consumer)

---

*Spec version: 1.0 | Created: 2026-03-09*
