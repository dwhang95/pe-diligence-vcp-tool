## Deal Context

{context_block}

---

## Task

Generate an action-linked EBITDA bridge for **{company_name}**, a **{deal_type}** in **{industry}**, covering the 100-day window and Year 1 trajectory.

Output a single markdown table with these exact columns:

| Initiative | Category | Entry Run-Rate Impact ($K) | 100-Day Target Impact ($K) | Confidence | Owner |
|---|---|---|---|---|---|

---

## Output Rules

**1. Link Every Row to a Specific Initiative**
Each row must name a concrete action — not a generic lever. The initiative column must describe what is actually being done, not what outcome is hoped for.

Not acceptable:
- "Pricing improvement"
- "Cost reduction"
- "Working capital optimization"

Acceptable:
- "Implement list price increase of 3–5% across Product Line A (excluding top 3 accounts)"
- "Eliminate 2 redundant middle management roles in operations following org assessment"
- "Reduce DSO from ~52 days to ~40 days via AR collections process redesign and early pay incentive"
- "Consolidate 3 regional warehouses into 2, reducing occupancy and logistics cost"
- "Renegotiate top 5 supplier contracts using combined volume leverage post-close"

Draw the initiative names from the top value levers and key challenges in the deal context. If a value lever is too vague to generate a specific initiative, flag it as "Requires further diligence to specify."

**2. Category — Four Options Only**
Assign each initiative to exactly one:
- **Revenue** — top-line growth, pricing, volume, mix improvement
- **COGS** — direct material, direct labor, manufacturing overhead, freight
- **SG&A** — indirect headcount, rent, professional fees, marketing spend, IT costs
- **Other** — working capital, one-time items, or cross-category (explain in initiative name)

Note: Working capital improvements (DSO, DIO, DPO) affect cash flow, not EBITDA directly. If including a working capital initiative, categorize as "Other" and note that the EBITDA impact is indirect (e.g., freed cash reduces revolver draw and interest expense). Do not conflate cash and EBITDA.

**3. Entry Run-Rate Impact ($K)**
This is the estimated annualized EBITDA impact if the initiative were already fully implemented at close — i.e., the full-run-rate opportunity. This is the "size of the prize," not what will be captured in 100 days. It is an estimate. It requires validation. Say so.

**4. 100-Day Target Impact ($K)**
This is what can realistically be captured or contracted within the first 100 days. This is almost always less than the entry run-rate impact, because:
- Pricing changes take time to take effect (contract cycles, customer pushback)
- Cost reductions require notice periods, org decisions, and severance
- Procurement savings require renegotiation lead time
- Systems-dependent initiatives cannot close until systems are in place

Be realistic. A pricing initiative with a $500K run-rate opportunity might only yield $80K in the first 100 days if it's being implemented mid-cycle. Do not pad the 100-day column to make the bridge look better.

**5. Confidence — Three Levels Only**
- **H (High):** Initiative is well-defined, owner is identified, no systems or dependencies blocking execution, and comparable initiatives have succeeded in similar portcos. Expect >80% of stated impact to be realized.
- **M (Medium):** Initiative is plausible but requires validation in diligence, management buy-in is uncertain, or execution complexity is real. Expect 50–80% of stated impact.
- **L (Low):** Initiative depends on assumptions not yet validated, requires significant change management, or has meaningful execution risk. Treat as upside, not base case. Expect <50% of stated impact.

No more than 40% of rows should be H. If everything is high confidence, the bridge is not credible.

**6. Owner — Specific Role**
Same rules as the workstreams prompt: specific role only (CEO, CFO, VP Operations, CRO, CHRO, Operating Partner). Never "management" or "TBD."

If the right owner doesn't exist yet (Vacant or Replace from the C-suite assessment), flag as "Interim [Role] / Hire Required."

---

## After the Table

Add a **"Bridge Summary"** section immediately after the table.

Format it as:

### EBITDA Bridge Summary

| Milestone | EBITDA ($K) | Notes |
|---|---|---|
| Entry EBITDA (at close) | ${entry_ebitda:,.0f} | As-reported or adjusted per QofE |
| Quick Win Run-Rate EBITDA | $[sum of H-confidence 100-day impacts + entry] | Achievable within 100 days, high confidence only |
| Year 1 Target EBITDA | ${target_ebitda:,.0f} | Per deal model; includes medium-confidence initiatives |
| Full Run-Rate EBITDA (all levers) | $[sum of all entry run-rate impacts + entry] | Theoretical maximum; requires full execution |

Then add a **"Validation Requirements"** note — 3–5 bullet points listing the specific assumptions in this bridge that must be confirmed during diligence or in the first 30 days before committing to the Year 1 target. Examples:
- "Pricing power assumption requires customer interview validation — top 5 accounts represent 60% of revenue"
- "Headcount reduction impact assumes no retention bonuses or severance costs that offset savings"
- "Procurement savings assume supplier concentration is sufficient for renegotiation leverage — confirm spend data"

These are not caveats to bury the bridge. They are the diligence checklist that makes the bridge actionable.

---

## Disclaimer Line

End the entire section with this line, verbatim:

> *All EBITDA impact figures are pre-diligence estimates based on deal context and industry benchmarks. They require validation through management interviews, financial data room review, and operational diligence before being incorporated into the investment model.*

---

## Tone

Operator-grade precision. This bridge will be reviewed by an IC. Every number needs a story and every story needs an owner. Do not write a bridge that requires heroic assumptions to close — if the math doesn't work cleanly, say so explicitly in the bridge summary rather than obscuring the gap with optimistic run-rates.
