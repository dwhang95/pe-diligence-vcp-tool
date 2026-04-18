## Deal Context

{context_block}

---

## Task

Generate a 100-day workstream plan for **{company_name}**, a **{deal_type}** in **{industry}**.

Output a single markdown table with these exact columns:

| Workstream | Functional Owner | Days 1–30 Focus | Days 31–60 Focus | Days 61–100 Focus | Primary KPI | Priority |
|---|---|---|---|---|---|---|

---

## Output Rules

**1. Workstream Count**
Generate between 8 and 12 workstreams. No fewer — this is a real buyout, not a slide deck. No more — bandwidth is finite in the first 100 days.

**2. Deal Type — Required Workstreams**

If deal type is **Carve-out**, you MUST include all four of the following. These are non-negotiable — a carve-out without them fails:
- TSA Management (track dependencies, enforce exit timelines, escalate breaches)
- ERP Standup (assess current state, select platform, begin data migration planning)
- Entity Separation (legal entity setup, bank accounts, contracts novation, insurance)
- Benefits Migration (health, 401k, payroll — coordinate with CHRO and external broker)

If deal type is **Platform**, you MUST include all three of the following:
- Management Assessment (structured listening tour, capability scoring, upgrade decisions)
- Reporting Infrastructure (KPI definition, BI layer, board reporting cadence)
- Quick-Win Revenue/Cost Initiative (at least one specific lever from the value levers provided — name it explicitly)

If deal type is **Tuck-in**, you MUST include all three of the following:
- Integration Planning (Day 1 readiness, functional workstream leads, integration PMO)
- Synergy Capture (map to deal model assumptions, assign owners, set tracking cadence)
- Org Consolidation (spans and layers, role redundancies, retention of key performers)

**3. Functional Owner Rules**
- Every workstream must have a specific role: CEO, CFO, COO, VP Operations, CHRO, CRO, VP Finance, General Counsel, IT Director, Operating Partner
- Never use "Management," "Leadership Team," "TBD," or any other generic placeholder
- If a role doesn't exist at the company yet, write "Interim [Role]" — that flags it as a hiring need

**4. Pacing Discipline — Enforce This**
The three phase columns must follow this cadence. Violations of pacing undermine operator credibility:
- **Days 1–30:** Diagnostic only — assess, listen, map, interview, request data. No decisions, no announcements, no org changes
- **Days 31–60:** Design and decide — finalize structure, make upgrade decisions, launch quick wins that were identified in Days 1–30
- **Days 61–100:** Execute and track — implementations running, KPIs live, board reporting cadence established, VCP v1.0 drafted

Do not put execution work in Days 1–30. Do not put diagnostic work in Days 61–100. Be precise about what happens in each phase, not vague ("assess and improve" is not acceptable phrasing).

**5. Primary KPI**
Each workstream must have one specific, measurable KPI. Not "progress" or "completion." Examples of acceptable KPIs:
- Days to first board-ready dashboard
- TSA line items exited by Day 90
- DSO reduction vs. Day 1 baseline
- # leadership roles assessed with capability score
- ERP vendor selected Y/N
- Synergy capture $ vs. deal model assumption

**6. Priority**
Assign H / M / L. No more than 4 workstreams should be H. If everything is high priority, nothing is.

---

## After the Table

Add a **"Critical Path"** section immediately after the table. This is not optional.

Format it as:

### Critical Path — 3 Sequencing Dependencies

List exactly 3 dependencies that, if they slip, derail the plan. For each:
- **Dependency:** [what must happen first]
- **Downstream risk:** [what it blocks]
- **Owner:** [specific role]
- **Deadline:** [day number or window]

Choose dependencies that actually matter for *this deal type and these value levers* — not generic PM boilerplate.

---

## Tone

Write like a senior PE operating partner briefing a portco management team — not a McKinsey engagement manager building a slide. That means:
- Direct declarative sentences
- No passive voice ("the assessment will be conducted" → "CFO conducts assessment")
- No hedging on pacing or ownership
- Specific over vague at every turn
- If something is a risk, name it plainly
