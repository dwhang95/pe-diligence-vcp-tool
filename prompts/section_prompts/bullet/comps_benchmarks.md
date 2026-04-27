# Prompt: Comparable Companies & Benchmarks (Bullet Mode)

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

## Format Rules — STRICTLY ENFORCE
- Comp table: present exactly as provided, no modifications to numbers.
- Below the table: bullets only. No prose paragraphs.
- Every bullet maximum 25 words.
- No hedging language. State the finding, then the implication.
- News signals: bullets only, max 4 bullets. If sparse, 1 bullet noting the gap.

## Instructions

### Part A — Comp Table + 3 Interpretation Bullets
Present the comp table as-is. Then write exactly 3 bullets interpreting what the benchmarks mean for this target:
- Bullet 1: margin profile implication
- Bullet 2: labor intensity / wage benchmark implication
- Bullet 3: CapEx intensity or valuation multiple implication

Flag if fewer than 3 comps are available (directional only).

### Part B — News Signals
Max 4 bullets. Elevate anything mapping to a risk flag: leadership change, regulatory issue, workforce unrest, customer loss. If news is sparse, one bullet stating so.

## Format

```
### Part A: Public Comp Context

**SIC/Industry:** {{sic code and label}}

{{comp table — paste exactly from input}}

*Public comps skew larger than typical middle-market targets. Directional context only.*

- {{Margin implication — max 25 words}}
- {{Labor/wage implication — max 25 words}}
- {{CapEx or multiple implication — max 25 words}}

---

### Part B: News Sweep Signals

- {{Signal 1 — max 25 words}}
- {{Signal 2 — max 25 words}}
- {{Signal 3 — max 25 words}}
- {{Signal 4 or gap note — max 25 words}}
```

Do not add a section header like "## 3. Comparable Companies & Benchmarks" — the template provides that.
