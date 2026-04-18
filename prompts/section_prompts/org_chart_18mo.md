## Deal Context

{context_block}

---

## Task

Generate an 18-month target org structure for **{company_name}**, a **{deal_type}** in **{industry}**.

---

## Output Rules

**1. Format — Markdown Indented Hierarchy**
Use indented markdown to represent the org structure. Do not attempt a visual chart. Do not use ASCII box-drawing characters. Use this convention:

```
CEO
  CFO
    Controller
    FP&A Manager [NEW HIRE]
  COO
    VP Operations
      Plant Manager — Site A
      Plant Manager — Site B [RESTRUCTURE]
    Supply Chain Manager [ELIMINATE]
  CRO
    VP Sales
      Regional Sales Manager — East
      Regional Sales Manager — West [NEW HIRE]
    VP Marketing [VACANT — HIRE BY MONTH 6]
```

Tag every role with one of these markers where the state differs from today:
- **[NEW HIRE]** — role does not exist today; needs to be filled
- **[ELIMINATE]** — role exists today and will be removed
- **[RESTRUCTURE]** — role exists but scope, title, or reporting line changes materially
- **[INTERIM]** — filled by interim or fractional resource while permanent hire is sourced
- **[VACANT — HIRE BY MONTH X]** — open role with a target fill date
- No tag = role exists today and carries forward unchanged

**2. Current State vs. 18-Month Target — Side by Side**
For any part of the org where the structure changes materially, show both states. Use this format:

```
### [Function Name]

**Current State**
[indented hierarchy]

**18-Month Target**
[indented hierarchy with change tags]
```

Only show the current vs. target comparison where there is a difference. Functions that remain unchanged do not need a current state section — just show the target.

**3. Scope of Coverage**
Show the full leadership layer (CEO direct reports and one level down). Do not go deeper than two levels below CEO unless a specific function requires it (e.g., a manufacturing business where Plant Manager → Supervisor → Line Lead matters for headcount planning).

For individual contributor layers, use a headcount placeholder rather than individual roles:
- "Field Sales Representatives (12 FTE)" not a list of 12 names
- "Warehouse Associates (28 FTE)" not individual roles

**4. Deal Type Emphasis**
Structure the org to reflect the priorities of this specific deal type:

**Carve-out:** The current state will have shared service dependencies (IT, HR, Finance, Legal) that must become standalone functions. Show these explicitly — mark shared service roles as [CARVE-OUT: STANDALONE REQUIRED] and show what the standalone version looks like in the 18-month target.

**Platform:** The org should be built for scale — show where new layers are being added to support future tuck-ins or geographic expansion. Flag roles that are being "right-sized up" to platform-grade capability.

**Tuck-in:** Show the combined org, not just the acquiree. Where there are duplicate roles between acquirer and acquiree, show which role survives and which is eliminated. Flag the integration decision explicitly.

**5. Value Lever Alignment**
The org structure must visibly support the top value levers provided. If pricing power is a lever, there should be a CRO or VP Revenue with appropriate commercial infrastructure. If working capital is a lever, the CFO should have a Controller and treasury function visible. If operational efficiency is a lever, the COO/VP Ops layer should reflect where decision rights will live.

Do not build a generic org chart. Every structural choice should be traceable to the thesis.

---

## After the Org Chart

Add a **"Headcount Delta Summary"** section immediately after the org chart.

Format it as a table:

| Category | Count |
|---|---|
| Roles retained (no change) | X |
| New hires required | X |
| Roles eliminated | X |
| Roles restructured | X |
| Interims / fractional | X |
| **Net headcount change (leadership layer)** | **+X / -X** |

Then add 2–3 sentences of commentary: what is driving the largest change, what the hiring sequencing priority is (which hire must happen first and why), and whether the org as designed is realistically executable in 18 months given the deal complexity.

---

## Tone

Structural and specific. This is an operating plan artifact, not an HR diagram. Every role in the 18-month target should have a reason to exist that connects back to the VCP. If a role is being added, say why it's needed now. If a role is being eliminated, say what happens to the work.
