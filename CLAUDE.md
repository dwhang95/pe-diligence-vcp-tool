# CLAUDE.md — PE Ops Due Diligence Brief Generator

This file provides context for Claude Code when working on this project.

---

## What This Tool Does

Generates structured operational due diligence briefs for middle market PE buyout targets ($50M–$500M EV). Input: company name, description, industry. Output: markdown brief covering ops risk, IT maturity, value creation levers, and a 100-day plan starter.

---

## Derek's PE Ops Framework

### The Core Belief
The best PE ops work happens at the intersection of analytical rigor and relational intelligence. Spreadsheets tell you what happened. Conversations tell you why and what's possible.

### Diligence Philosophy
- **Hypothesis-driven:** Enter diligence with a point of view. Update it, don't abandon it at the first sign of noise.
- **Go to the floor:** Management presentations lie by omission. The factory floor, the CS team, the warehouse — that's where the truth lives.
- **Key-man is always the first question:** In middle market, one person leaving can unravel a thesis.
- **IT maturity = ops ceiling:** A company with a 20-year-old ERP and no reporting layer cannot execute a VCP. Assess systems early.
- **Customer concentration kills:** Top customer >20% is a flag. Top customer >40% is a potential deal-breaker without contract protection.

### Value Creation Framework (Priority Order)
1. **Revenue levers first** — Pricing power, customer mix, cross-sell. These compound.
2. **Working capital** — Often the fastest win in middle market. DSO, DIO, DPO frequently untouched.
3. **Cost structure** — Procurement consolidation, labor productivity, overhead benchmarking.
4. **Organizational effectiveness** — Right-sizing, capability gaps, leadership upgrades.
5. **Digital/AI transformation** — High potential but long cycle time. Flag early, plan realistically.

### 100-Day Plan Principles
- Days 1–30 are for listening, not fixing. Announcing changes before trust is built destroys goodwill.
- The listening tour must include non-management voices: supervisors, frontline, key customers.
- Quick wins (Days 30–60) should be visible AND impactful — not just easy.
- Board reporting cadence should be set by Day 60, not Day 90.
- Never promise a deliverable in a 100-day plan that requires systems or data that don't exist yet.

### Risk Flag Calibration
| Rating | Meaning |
|---|---|
| Low | Exists but unlikely to impair thesis |
| Medium | Needs diligence; could be mitigated with planning |
| High | Could impair thesis or EBITDA if unaddressed; needs a plan before close |
| Critical | Deal-breaker risk if confirmed; requires management discussion before IC |

### Industries Derek Knows Best
- Industrial manufacturing and packaging (Inovar Packaging, Kelso portfolio)
- Consumer products (Widus: cosmetics, baby care, infant apparel)
- Healthcare services (adjacent through L.E.K.)
- Business services / professional services (L.E.K. cross-sector)

---

## Output Voice and Standards

All generated content must sound like a senior PE ops professional wrote it — not a consultant, not a generalist analyst.

**Use naturally:** VCP, PortCo, IC memo, EBITDA bridge, cadence, governance, operating cadence, diligence, thesis, 100-day, KPI, BI layer, key-man, customer concentration, working capital unlock.

**Never use:** "synergies," "leverage our learnings," "circle back," "low-hanging fruit" (unless being ironic), "best-in-class," "world-class."

**Tone:** Confident and directional. Flag uncertainty explicitly. Short sentences when making a point. Longer when providing context.

**When we don't know something:** Say so and explain what it implies for diligence. "No public data on ERP systems — assess in management meeting. A company of this size without a documented BI layer likely has significant reporting debt."

---

## Technical Notes

- **LLM:** Use claude-sonnet-4-6 for generation (claude-opus-4-6 for complex reasoning if needed)
- **Web search:** Search for: company name + news, Glassdoor reviews, LinkedIn employee count/growth, industry trends, any press releases or customer mentions
- **Output:** All briefs saved to `output/` as `{slug}_{date}.md` — this folder is gitignored
- **Prompts:** All prompts live in `prompts/`. Modify there, not inline in code.
- **Content drafts:** LinkedIn posts and thought leadership drafts live in `content-drafts/` (previously `~/content-drafts/`, moved 2026-04-25)
- **Python style:** Prefer simple, readable code. No over-engineering. Functions should do one thing.

---

## Project Status (updated 2026-04-18)
- [x] Spec written
- [x] Folder structure created
- [x] System prompt written
- [x] Section prompts written
- [x] researcher.py / web search integrated
- [x] generate_brief.py built (async pipeline)
- [x] Streamlit UI built (src/app.py)
- [x] Functional Scorecards module added (Section 8)
- [x] Deployed to Streamlit Cloud
- [x] End-to-end test run on real companies (CBIZ, Floor & Decor)
- [ ] VCP Generator module (next)
- [ ] Widus Korea/SEA market variant

---
## Current Module Architecture (updated 2026-04-18)
- src/app.py — Streamlit UI (two-column, dark PE theme)
- src/generate_brief.py — async pipeline
- prompts/section_prompts/ — one .md per section

Optional modules (checkbox in UI, off by default):
- Functional Scorecards (Ops / IT / Commercial / Talent) → Section 8

When adding modules: update OPTIONAL_MODULES, OPTIONAL_SECTION_TITLES, 
and optional_results in generate_brief.py. Never hardcode section numbers.

## Do Not
- Change gold accent (#c9a84c) without flagging
- Add sync calls inside the async pipeline
- Commit without local Streamlit test first

*Last updated: 2026-04-18*
