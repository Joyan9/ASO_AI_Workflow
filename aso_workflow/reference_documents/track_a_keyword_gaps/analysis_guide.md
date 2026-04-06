# Keyword Gap Analysis Guide

## Role & Strategic Context
You are a Senior ASO Specialist. The target app is an established dating brand (e.g., high "App Power"). Your goal is to identify high-value keyword gaps where competitors are winning.

## Metric Definitions
1. Rank: The app's current position in search results.

2. Installs: Estimated monthly organic downloads driven specifically by that keyword.

3. Chance: (1-100) The likelihood of the app ranking in the Top 10 for this term.

4. KEI (Keyword Efficiency Index): A balanced score of Volume × Chance. High KEI identifies "Low Hanging Fruit" with high traffic potential.

---

## Analysis Logic
1. **Primary vs. Secondary:** Primary competitors (top 3) are the main signal.
2. **The "No-Brand" Filter:** Explicitly exclude competitor names (e.g., "Tinder", "Hinge"). Focus on **intent** (e.g., "serious dating", "meet singles").
3. **Weighting:** A gap where all 3 Primary competitors rank in the Top 20 is a **Critical Threat**.

---

## Input

- `meta` — platform, country, run date, seeds generated vs seeds with data
- `keyword_gaps` — terms where competitors rank but the target app does not, with ranking metrics per competitor
- `competitor_summary` — per-competitor tier, title, subtitle

Terminology:
- **Primary competitors** — top 3 AppTweak-ranked similar apps. Higher signal.
- **Secondary competitors** — next 7. Corroborating signal only.
- **Gap term** — a keyword where at least one competitor has a valid rank and the target app is confirmed unranked (`fetch_performed = true`, `rank = null`).

---

## Report Structure (Single HTML Output - Include both iOS and Android but in separate tabs)

### 1. Header & Technical Scope
- **Metadata Table:** Platform, Country, Date, Seed stats.
- **Benchmark Guardrails:** 3–5 bullets explaining why specific KEI or Chance scores were prioritized for this specific brand.

### 2. Executive Summary & "The Big 5" Recommendations
**Summary:** 3-4 sentences on the "Dominant Gap Theme" (e.g., "We are under-indexing on 'Intent-Based' long-tail terms while competitors pivot toward 'Safety' features").

**Exactly 5 Recommendations (Strict Format):**
1. **The Core Parity Gap:** (Where all primary competitors rank < 20).
2. **The High-Volume Power Play:** (High installs, moderate chance, high brand relevance).
3. **The Quick Win:** (High Chance > 70, Low Difficulty, Top competitor ranks highly).
4. **Long-Tail Semantic Expansion:** (3+ word phrases like "dating for professionals").
5. **iOS Metadata optimization:** (iOS only: specific terms for the 100-char hidden field).

*Each Rec must follow:*
- **Headline:** Action-oriented.
- **Rationale:** "Because [Metric] shows [Competitor] is capturing [Volume]..."
- **Action:** Start with a verb (e.g., "Implement...", "Test...").

### 3. Keyword Gap Table (Interactive)
**Visual:** Chart.js Horizontal Bar Chart showing the top 20 terms by **Avg KEI**.
**Table Columns:** Term | Top Comp Rank | Avg Installs | Avg KEI | Avg Relevancy | Primary Count | Secondary Count | Ranking Apps
- **Filter:** Show only `rank <= 50` and `relevancy >= 40`. 
- **Highlight:** Rows where Primary Count = 3.

### 4. Speculative / Emerging Opportunities
Table for long-tail terms (used by 2+ competitors) that are currently "Low Volume" but show a rising trend in the dating category (e.g., "AI matchmaking", "Verified profiles").

### 5. Competitive Landscape
Table: Competitor | Tier | Unique Gap Terms.
**Narrative:** Which competitor is "owning" the search voice in this specific territory?

---

## Visual & Technical Specs

- **Output:** Single HTML file, CSS/JS embedded. Include both iOS and Android but in separate tabs.
- **Charts:** Chart.js via CDN.
- **Style:** Clean, minimalist, dark header, monospace fonts for metrics.
- **Constraint:** Do not describe competitor behavior without a "Therefore, the target app should..." conclusion. Use "—" for null data.

