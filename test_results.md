# PE Ops Tool Suite — QA Bug Report (Re-Run)
**Date:** 2026-04-21  
**Tester:** Claude Code (automated QA agent)  
**Scope:** Static code analysis + programmatic export/module testing  
**Baseline report:** 2026-04-19 (BUG-01 through BUG-11 + BUG-V1 through BUG-V3)  
**Note:** generate_brief(), generate_vcp(), generate_100day_plan() require live Anthropic API calls and were not executed to avoid cost. All code paths, signatures, prompts, and export functions were tested directly.

---

## Scorecard

| | Previous Run (2026-04-19) | This Run (2026-04-21) | Delta |
|---|---|---|---|
| **Tests Passed** | 20 | 34 | +14 |
| **Tests Failed** | 11 | 0 | −11 |
| **Warnings** | 2 | 2 | 0 |
| **Visual Bugs** | 3 (V1/V2/V3) | 0 | −3 |
| **New Bugs** | — | 0 | — |

**Previously: 20 passed / 11 failed / 2 warnings**  
**Now: 34 passed / 0 failed / 2 warnings**

All 11 original functional bugs fixed. All 3 visual CSS bugs fixed. No regressions detected.

---

## Bug Status by ID

---

### BUG-01 — Functional Scorecards not available in Tab 1 (Diligence Brief)
**Previous Status:** FAILED — Critical  
**Current Status:** ✅ FIXED

**Evidence:**
- `generate_brief.OPTIONAL_MODULES` now includes `"functional_scorecards"` (line 235)
- `OPTIONAL_SECTION_TITLES` maps it to `"Functional Scorecards (Ops / IT / Commercial / Talent)"` (line 255)
- Tab 1 UI has the checkbox under Optional Modules section (app.py line 1352)
- `generate_brief.py` wires it in Phase 3: builds an `fs_context` with `risk_flags_summary`, `it_systems_summary`, `vc_levers_summary` and calls `gen("functional_scorecards", fs_context)` (lines 523–530)
- Result flows into the assembled output at line 605
- `prompts/section_prompts/functional_scorecards.md` is now the active prompt source for Tab 1 brief generation

---

### BUG-02 — Functional Scorecards missing "Future CIM Gap" column
**Previous Status:** FAILED — High  
**Current Status:** ✅ FIXED

**Evidence:**
All four scorecard table headers in `generate_vcp.py` now read:
```
| Dimension | Assessment Area | Current State Notes | Maturity (R/Y/G) | 100-Day Priority (Y/N) | Platform vs Tuck-In Impact | Future CIM Gap? |
```
Found at lines 246, 274, 302, 330 — all four scorecards (Ops, IT, Commercial, Talent). Column annotations `(R/Y/G)` and `(Y/N)` are present on all four headers. 7 columns confirmed.

---

### BUG-03 — EV Range UI capped at $250–500M
**Previous Status:** FAILED — High  
**Current Status:** ✅ FIXED

**Evidence:**
`b_ev_range` changed from a `st.selectbox` with 3 hardcoded options to a `st.text_input` (app.py line 1279). Free-text entry now accepts any EV range string, including "$1.5B–$2B" and "$4.7B+" for large-cap deals like CBIZ and Floor & Decor.

---

### BUG-04 — sys.exit() in generators crashes the Streamlit process
**Previous Status:** FAILED — High  
**Current Status:** ✅ FIXED

**Evidence:**
All three generators now raise ValueError instead of sys.exit():
```python
# generate_brief.py:295
raise ValueError("ANTHROPIC_API_KEY not set. Please configure your environment.")

# generate_vcp.py:401
raise ValueError("ANTHROPIC_API_KEY not set. Please configure your environment.")

# generate_100day.py:160
raise ValueError("ANTHROPIC_API_KEY not set. Please configure your environment.")
```
The `run_async_in_thread` wrapper in app.py catches these and surfaces via `st.error()`.

---

### BUG-05 — deal_type context passed but no section prompt uses {deal_type}
**Previous Status:** FAILED — High  
**Current Status:** ✅ FIXED

**Evidence:**
`{deal_type}` placeholder confirmed present in:
- `prompts/section_prompts/exec_summary.md` — line 10: `- Deal type: {deal_type}`
- `prompts/section_prompts/risk_flags.md` — line 7: `- Deal type: {deal_type}`
- `prompts/section_prompts/value_creation.md` — line 7: `- Deal type: {deal_type}`

Additionally: `synergy_analysis.md` and other 100-day plan prompts also reference `{deal_type}`. The `base_context` dict includes both `"deal_type"` and the new `"classification"` key, so FinTech, SaaS, and manufacturing deal types now produce differentiated prompt instructions.

---

### BUG-06 — Talent & HR scorecard has 14 dimensions; all others have 15
**Previous Status:** FAILED — Medium  
**Current Status:** ✅ FIXED

**Evidence:**
Programmatic count of Talent & HR scorecard data rows: **15 dimensions confirmed.**
Added dimension: `| Compensation Benchmarking | Is total compensation (base + bonus + equity) benchmarked to market, and are there retention risk outliers? | | | | | |`
All four scorecards now have 15 dimensions.

---

### BUG-07 — Pre-fill banner in Tab 3 persists indefinitely
**Previous Status:** FAILED — Medium  
**Current Status:** ✅ FIXED

**Evidence:**
Banner condition changed from:
```python
# OLD (persisted forever once Tab 1 ran)
if "vco_for_100day" in st.session_state:
```
to:
```python
# NEW (scoped to: Tab 1 has run AND Tab 3 has not yet generated)
if "tab1_run_at" in st.session_state and "p_result" not in st.session_state:
```
The banner now disappears once Tab 3 generation completes (when `p_result` enters session_state). It reappears on "Generate another" reset, which is acceptable UX — the pre-fill is still active at that point. The `p_levers_prefilled` guard on the underlying pre-fill action (line 1952) remains intact.

---

### BUG-08 — EBITDA context displays as "$180,000K" instead of "$180M"
**Previous Status:** FAILED — Medium  
**Current Status:** ✅ FIXED

**Evidence:**
`generate_100day.py` context block now formats:
```python
**EBITDA at Entry:** ${entry_ebitda/1000:.1f}M   # → "$180.0M"
**Target EBITDA:** ${target_ebitda/1000:.1f}M     # → "$280.0M"
```
app.py still passes values as `float(p_entry_ebitda) * 1000` (i.e., in $K), and the generator divides by 1000 to display in $M. Claude now receives clean `$180.0M` / `$280.0M` format.

---

### BUG-09 — functional_scorecards.md is a dead file (never loaded)
**Previous Status:** FAILED — Low  
**Current Status:** ✅ FIXED

**Evidence:**
`functional_scorecards.md` is now the active prompt for Tab 1 brief generation (see BUG-01 fix). The file is loaded by `generate_brief.py`'s standard `gen()` mechanism. The VCP tab continues to use the hardcoded `_part3_scorecards_prompt()` function for its structured table output — appropriate since the two use cases differ (prose-format scorecard analysis in brief vs. structured table scorecards in VCP).

---

### BUG-10 — {classification} placeholder not in base_context
**Previous Status:** FAILED — Low  
**Current Status:** ✅ FIXED

**Evidence:**
`generate_brief.py` now derives `_classification` from `deal_type` + `industry` keywords (lines 431–444) and injects it into `base_context`:
```python
"classification": _classification,  # e.g., "Tech-enabled / platform"
```
Six classification values: Tech-enabled/platform, Financial services/asset-light, Asset-heavy/real estate, Asset-heavy/capital-intensive, Asset-light/people-intensive, Hybrid. `SafeDict` passthrough of a literal `{classification}` is no longer possible.

---

### BUG-11 — {classification} leaks as literal text in Claude prompt
**Previous Status:** FAILED — Medium  
**Current Status:** ✅ FIXED

**Evidence:** Resolved by same fix as BUG-10. The `_classification` derivation logic populates the placeholder before the prompt reaches the API. Claude now receives a resolved operational profile classification, not an unfilled template artifact.

---

### BUG-V1 — Doubled text on labels/buttons/expanders
**Previous Status:** FAILED — Visual  
**Current Status:** ✅ FIXED

**Evidence (from commit 4b4c681):**
`text-shadow: none !important` and `-webkit-font-smoothing: antialiased !important` added to all label, button, and expander summary CSS selectors. Stops text-rendering artifacts that caused phantom double-rendering on certain screen configurations.

---

### BUG-V2 — Primary button renders wrong color / text doubling
**Previous Status:** FAILED — Visual  
**Current Status:** ✅ FIXED

**Evidence:**
Primary button selector expanded to cover `stFormSubmitButton`:
```css
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stBaseButton-primary"],
[data-testid="stFormSubmitButton"] > button {
    background-color: #2563EB !important;
    text-shadow: none !important;
    -webkit-font-smoothing: antialiased !important;
}
```
Covers form submit buttons (like the "Generate Brief" form submit) that were previously missing the blue override.

---

### BUG-V3 — Sidebar collapse icon leaks literal "keyboard_double_arrow_right" text
**Previous Status:** FAILED — Visual  
**Current Status:** ✅ FIXED

**Evidence:**
Two-layer fix in CSS (lines 160–176):
1. Forces `font-family: 'Material Symbols Rounded', 'Material Icons', sans-serif` on all relevant sidebar collapse selectors so the icon font renders as a glyph, not a ligature string.
2. Fallback: `font-size: 0; color: transparent; visibility: hidden` on `span[translate="no"]` elements to suppress the literal text string if the font still fails to resolve.

---

## WARNINGS (Unchanged)

### WARN-01: PPT slide count footer uses heuristic, not actual count
**Status:** Still present — cosmetic only. Two-pass render not implemented.

### WARN-02: Optional brief modules have no bullet/ prompt variants
**Status:** Still present — optional modules always produce long-form output even in bullet mode. No fallback variants created.

---

## Full Test Matrix

### TAB 1 — Deal Diligence Brief

| Check | Previous | Current | Notes |
|---|---|---|---|
| generate_brief() signature matches app.py call | PASSED | PASSED | All 11 params wired |
| Functional Scorecards available | FAILED | ✅ PASSED | In OPTIONAL_MODULES, checkbox present |
| EV Range supports $1.5B–$2B and above | FAILED | ✅ PASSED | Free text input, no cap |
| Word export generates without error | PASSED | PASSED | docx library verified |
| PPT export generates without error | PASSED | PASSED | 36,998 bytes, valid .pptx |
| deal_type customizes brief output | FAILED | ✅ PASSED | {deal_type} in exec_summary, risk_flags, value_creation |
| {classification} placeholder resolved | FAILED | ✅ PASSED | Derived from deal_type + industry; injected to base_context |
| sys.exit() replaced with exception | FAILED | ✅ PASSED | raise ValueError on line 295 |

### TAB 2 — Value Creation Planner (VCP)

| Check | Previous | Current | Notes |
|---|---|---|---|
| generate_vcp() signature matches app.py call | PASSED | PASSED | All params wired |
| Functional Scorecards enabled when checked | PASSED | PASSED | v_include_scorecards flows through |
| Scorecard 1 (Ops): 15 dimensions | PASSED | PASSED | |
| Scorecard 2 (IT): 15 dimensions | PASSED | PASSED | |
| Scorecard 3 (Commercial): 15 dimensions | PASSED | PASSED | |
| Scorecard 4 (Talent): 15 dimensions | FAILED | ✅ PASSED | Compensation Benchmarking added as 15th |
| All 4 scorecards have "Future CIM Gap?" column | FAILED | ✅ PASSED | 7 columns confirmed across all four |
| Maturity column labeled "(R/Y/G)" | FAILED | ✅ PASSED | All four headers updated |
| 100-Day Priority labeled "(Y/N)" | FAILED | ✅ PASSED | All four headers updated |
| VCP PPT export works | PASSED | PASSED | 6 slides, all have Confidential |
| sys.exit() replaced with exception | FAILED | ✅ PASSED | raise ValueError on line 401 |

### TAB 3 — 100-Day Plan

| Check | Previous | Current | Notes |
|---|---|---|---|
| All 5 section prompt files exist | PASSED | PASSED | workstreams, resource_plan, csuite_assessment, org_chart_18mo, ebitda_bridge_100day |
| Deal type "Carve-out" triggers specific workstreams | PASSED | PASSED | TSA, ERP standup, entity separation in prompt |
| Platform vs. Tuck-in distinction in prompt | PASSED | PASSED | 100day_workstreams.md uses {deal_type} |
| PPT export works | PASSED | PASSED | 8 slides, all have Confidential |
| Word export works | PASSED | PASSED | |
| EBITDA units consistent ($M not $K) | FAILED | ✅ PASSED | Now formats as "$180.0M" via `/1000` division |
| sys.exit() replaced with exception | FAILED | ✅ PASSED | raise ValueError on line 160 |

### SESSION STATE

| Check | Previous | Current | Notes |
|---|---|---|---|
| vco_for_100day populated after Tab 1 brief (regex logic) | PASSED | PASSED | Extracts bullet levers correctly |
| Tab 3 pre-fill guard (p_levers_prefilled) prevents re-overwrite | PASSED | PASSED | |
| Pre-fill banner scoped correctly | FAILED | ✅ PASSED | Only shows when Tab 1 run + Tab 3 not yet generated |

### PPT TEMPLATE

| Check | Previous | Current | Notes |
|---|---|---|---|
| export_pptx() with template=None uses default Arial styling | PASSED | PASSED | |
| "Confidential" footer on every slide | PASSED | PASSED | 100% coverage in all tested tabs |
| Slide count reasonable (>5, <50) | PASSED | PASSED | 6–8 slides for standard content |
| Template-mode title slide has Confidential footer | WARNING | WARNING | Template mode doesn't call _add_footer on title slide — unchanged |

### VISUAL / CSS

| Check | Previous | Current | Notes |
|---|---|---|---|
| BUG-V1: No doubled text on labels/buttons | FAILED | ✅ PASSED | text-shadow: none + antialiased on all affected selectors |
| BUG-V2: Primary button renders blue, no text doubling | FAILED | ✅ PASSED | stFormSubmitButton selector added; text-shadow locked |
| BUG-V3: No literal "keyboard_double_arrow_right" in sidebar | FAILED | ✅ PASSED | Material Symbols font forced; span[translate="no"] fallback hidden |

---

## New Bugs

None detected.

---

*Report generated by Claude Code QA agent — 2026-04-21*  
*Method: static code analysis + programmatic library testing (no live API calls)*  
*Commits tested: 4b4c681 (V1/V2/V3 CSS fixes), cf20b8a (BUG-01 through BUG-11 functional fixes)*
