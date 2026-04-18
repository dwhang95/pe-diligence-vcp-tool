## Deal Context

{context_block}

---

## Task

Generate a C-suite assessment for **{company_name}**, a **{deal_type}** in **{industry}**.

Output a single markdown table with these exact columns:

| Role | Incumbent Status | Rationale | Key Gaps to Address | If Replacing: Search Timeline |
|---|---|---|---|---|

---

## Output Rules

**1. Roles to Include**
Include every functional leadership role that is material to executing the VCP for this deal. At minimum, assess: CEO, CFO. Add the following based on deal type and industry:
- **COO** — include if operations are a primary value lever or if the CEO is founder/owner with no ops deputy
- **CRO / VP Sales** — include if revenue growth is in the top value levers
- **CHRO / VP HR** — include if headcount is >100, a carve-out, or org consolidation is required
- **CTO / VP IT** — include if ERP standup, digital transformation, or IT systems maturity is a key workstream
- **VP Operations / Plant Manager** — include for industrial, manufacturing, or logistics businesses
- **General Counsel** — include for carve-outs, regulated industries, or where legal entity complexity is high

Do not include roles that don't exist and aren't needed. Do not pad the table.

**2. Incumbent Status — Four Options Only**
Use exactly one of these values per role. No other phrasing:
- **Keep** — high confidence this person can execute the VCP; PE experience or strong track record in PE-adjacent environment
- **Replace** — clear capability gap, misalignment with thesis, or prior track record that creates risk; upgrade decision should be made by Day 60
- **Assess** — insufficient information to decide; structured evaluation required in Days 1–30 with a decision checkpoint at Day 45
- **Vacant** — role does not exist and needs to be filled; note if this is a new hire or a carve-out Day 1 gap

**3. Rationale — PE-Lens Specific**
Rationale must be grounded in one or more of these lenses. Generic observations ("strong leader," "needs development") are not acceptable:
- **Thesis alignment:** Does this person's instincts and priorities match the investment thesis? A cost-optimization thesis needs a different CFO than a growth thesis.
- **PE experience:** Has this person worked in a PE-backed environment before? Do they understand board dynamics, IC cadence, and operating with leverage?
- **Change management capability:** Can this person lead their function through ownership transition, org change, and a VCP execution cycle without losing the team?
- **Reporting and data discipline:** Does this person build and use data to manage, or do they manage by intuition and relationships?
- **Speed:** Middle market PE moves faster than founder-run businesses. Can this person shift from annual planning cycles to quarterly sprints?

Write the rationale in 1–2 direct sentences. If the status is Assess, say exactly what you're assessing and what the decision criteria are.

**4. Key Gaps to Address**
Be specific to the role and the deal. Examples of acceptable gap descriptions:
- "No experience managing a BI buildout; will need IT partner and external support to stand up reporting layer"
- "Strong operator but has never managed a board relationship; will need operating partner coaching in first 90 days"
- "Sales org has operated without CRM discipline; needs to institute pipeline rigor before growth thesis can execute"

Do not write generic gaps ("needs to develop strategically," "communication skills"). If there are no material gaps for a Keep, write "None identified at this stage — validate in listening tour."

**5. Search Timeline (If Replacing)**
Only populate this column if status is **Replace** or **Vacant**. Use realistic executive search timelines:
- C-suite (CEO, CFO, COO): 90–120 days from search launch to offer acceptance; add 30–60 days notice/transition
- VP/Director level: 60–90 days
- Interim coverage: note if an interim is needed to bridge the gap
- For Vacant roles in carve-outs: flag if this is a Day 1 risk (role must be filled before close or TSA exit)

If status is Keep or Assess, write "N/A."

---

## After the Table

Add a **"Management Risk"** section immediately after the table.

Write 2–4 sentences as a plain-language paragraph — no bullet points, no headers within this section. It should answer three questions:
1. What is the overall management risk level for this deal (Low / Medium / High) and why?
2. Which single role represents the highest execution risk, and what happens to the thesis if that role underperforms?
3. What does the PE sponsor need to decide or act on in the first 30 days to de-risk the management picture?

Write it as a senior operating partner would brief an IC — direct, specific, no hedging.

---

## Tone

Blunt but fair. The purpose of this assessment is to protect the investment thesis, not to be diplomatic. If a CFO is a replace, say why clearly. If a CEO is a keep but has never worked in a PE environment, flag that as a real risk — not a footnote. Do not soften assessments to the point where they lose their utility.
