# Prompt: Comparable Companies & Benchmarks

Generate Section 3 of the PE ops diligence brief — Comparable Companies & Benchmarks.

## Input Context
- Company: {company_name}
- Industry: {industry}
- EV range: {ev_range}
- Research findings: {research_summary}

## Public Comp Data (from SEC EDGAR)
{sec_comps_markdown}

## Labor Benchmark Data (from BLS)
{bls_benchmark_markdown}

## Recent News Sweep
{news_summary_markdown}

## Instructions

Write Section 3 of the brief. This section has two jobs:
1. Contextualize the target against real public comp data
2. Surface any news-driven signals that should inform the risk flags

### Part A — Comparable Companies & Benchmarks

Using the SEC comp table and BLS labor data provided above:
- Present the comp table as-is (it is pulled from real EDGAR data — do not fabricate numbers)
- Write 2–3 sentences interpreting what the benchmarks imply for this target
  - Is the industry margin-rich or thin? What does that mean for value creation headroom?
  - Is labor intensity high? What does the wage benchmark imply for retention risk?
  - Is CapEx intensity high? What does that signal about maintenance vs. growth capex?
- Flag explicitly if comp data is limited or the comps are materially larger than a typical middle-market target

Key framing: the reader is a PE ops partner. They want to know what the benchmarks tell them about the **range of outcomes** for this target, not just what the averages are.

**Important caveats to include:**
- Public comps skew larger and more mature than typical middle-market targets
- Operating margins for the target may differ due to scale, ownership structure, and PE cost discipline
- If fewer than 3 comps are available, note that the benchmark is directional only

### Part B — News Signals

Using the news sweep data:
- Summarize the most important signals in 3–5 bullets (do not just list headlines)
- Elevate anything that maps to a risk flag: leadership change, regulatory issue, workforce unrest, major customer loss
- If news is sparse or unavailable, say so explicitly and note what that implies (private company with low profile, or no material events)
- Do not speculate beyond what the articles support

If news data is empty or minimal, write one sentence acknowledging this and redirect to what to ask management.

## Format

```
### Part A: Public Comp Context

**SIC/Industry:** {{sic code and label}}

{{comp table — paste exactly from input, do not modify numbers}}

**Benchmark interpretation:**
{{2–3 sentences on what the margins, labor costs, and CapEx intensity imply for this target's profile}}

*Note: Public comps skew larger than typical middle-market targets. Use as directional context, not absolute benchmarks.*

---

### Part B: News Sweep Signals

{{3–5 bullet summary of material news signals}}

**News data gap note:** {{if applicable — what couldn't be found and why it matters}}
```

Do not add a section header like "## 3. Comparable Companies & Benchmarks" — the template provides that.
