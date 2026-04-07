# Keyword Gap Analysis Guide

## Role & Strategic Context
You are a Senior ASO Specialist. The target app is an established dating brand (e.g., high "App Power"). Your goal is to identify high-value keyword gaps where competitors are winning.

## Metric Definitions
1. **Rank:** The app's current position in search results.
2. **Installs:** Estimated monthly organic downloads driven specifically by that keyword.
3. **Chance:** (1–100) The likelihood of the app ranking in the Top 10 for this term.
4. **KEI (Keyword Efficiency Index):** A balanced score of Volume × Chance. High KEI identifies "Low Hanging Fruit" with high traffic potential.

---

## Analysis Logic
1. **Primary vs. Secondary:** Primary competitors (top 3) are the main signal.
2. **The "No-Brand" Filter:** Explicitly exclude competitor names (e.g., "Tinder", "Hinge"). Focus on **intent** (e.g., "serious dating", "meet singles").
3. **Weighting:** A gap where all 3 Primary competitors rank in the Top 20 is a **Critical Threat**.

---

## Input Data

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
- **Metadata Table:** Platform, Country, Date, Keyword Gaps.
- **Benchmark Guardrails:** Exactly 3 bullets — select the 3 most impactful thresholds that explain why specific KEI or Chance scores were prioritised for this brand. Be concise; one sentence each.

### 2. Scorecard Row + Executive Summary (Side by Side)
Render the summary scorecards (e.g., Total Gaps, Critical Threats, Avg KEI) and a 2–3 sentence Executive Summary in a **two-column layout** within the same section. The summary should state only the dominant gap theme and the single most urgent implication — no sub-bullets, no lists.

### 3. Recommendations & Benchmark Guardrails
**Exactly 5 Recommendations (Strict Format):**
1. **The Core Parity Gap** — Where all primary competitors rank < 20.
2. **The High-Volume Power Play** — High installs, moderate chance, high brand relevance.
3. **The Quick Win** — High Chance > 70, Low Difficulty, Top competitor ranks highly.
4. **Long-Tail Semantic Expansion** — 3+ word phrases like "dating for professionals".
5. **iOS / Android Metadata Optimisation** — iOS: hidden 100-char keyword field. Android: Short Description.

*Each recommendation must follow this exact structure:*
- **Headline:** Action-oriented, one line.
- **Rationale:** Plain prose. E.g., "Competitor X ranks #4 on this term, capturing an estimated Y installs/month."
- **Action:** Start with a verb (e.g., "Implement…", "Test…"). One sentence.

*Formatting rules:*
- All 5 recommendations use the **same card style and colour** — no colour-coding per recommendation.
- The rationale text must be rendered at normal body weight and size, not as a "Why:" label. Omit the "Why:" prefix entirely.

### 4. Keyword Gap Table (Interactive)
**Visual:** Chart.js Horizontal Bar Chart showing the top 10 terms by **Avg KEI**.

**Table Columns:** Term | Top Comp Rank | Avg Installs | Avg KEI | Avg Relevancy | Primary Count | Secondary Count | Ranking Apps
- **Filter:** Show only `rank <= 50` and `relevancy >= 40`.
- **Highlight:** Rows where Primary Count = 3.

### 5. Speculative / Emerging Opportunities
Table for long-tail terms (used by 2+ competitors) that are currently "Low Volume" but show a rising trend in the dating category (e.g., "AI matchmaking", "Verified profiles").

### 6. Competitive Landscape
Table: Competitor | Tier | Unique Gap Terms.
**Narrative:** Which competitor is "owning" the search voice in this specific territory?

---

## Visual & Technical Specs

- **Output:** Single HTML file, CSS/JS embedded. Include both iOS and Android in separate tabs.
- **Charts:** Chart.js via CDN.
- **Font:** Use `Roboto` (via Google Fonts CDN) for all body and UI text. Use `JetBrains Mono` for metric values only.
- **Style:** Clean, minimalist, dark header. Uniform accent colour for all recommendation cards.
- **Constraint:** Do not describe competitor behavior without a "Therefore, the target app should…" conclusion. Use "—" for null data.

---

# Keyword Gap Analysis Report — HTML Specification

## 1. Tech Stack & State Management
* **Framework:** Single self-contained HTML5/CSS3/JS file.
* **Data Structure:** `const REPORT_DATA` must contain two top-level keys: `ios` and `android`.
* **State:** A global `currentPlatform` variable (defaulting to `ios`) triggers a `renderDashboard()` function to update all UI components simultaneously.

## 2. Design System & Navigation
```css
:root {
  --bg-page:        #0f1117;
  --bg-card:        #1a1d27;
  --bg-card-alt:    #1f2235;
  --border:         #2a2d3e;
  --accent:         #6c63ff;
  --accent-soft:    rgba(108, 99, 255, 0.15);
  --accent-2:       #00d4a8;
  --accent-2-soft:  rgba(0, 212, 168, 0.12);
  --warn:           #f59e0b;
  --text-primary:   #f0f0f5;
  --text-secondary: #8b8fa8;
  --text-mono:      #a8b2d8;
  --tier1-border:   #6c63ff;
  --tier2-border:   #00d4a8;
  --tier3-border:   #f59e0b;
  --font-sans:      'Roboto', sans-serif;
  --font-mono:      'JetBrains Mono', monospace;
}
```
* **Google Fonts import:** `@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&family=JetBrains+Mono&display=swap');`
* **Sidebar Toggle:** A high-visibility "Platform Switcher" at the top of the fixed sidebar.
    * *Design:* A segmented control (pill shape) with "iOS" and "Android" labels.
    * *Interaction:* Active platform uses a subtle glow: `box-shadow: 0 0 10px var(--accent-soft)`.

## 3. Component Updates for Dual-Platform

### 3a. Hero Section
* **Dynamic Badges:** Platform-specific metadata.

### 3b. Section 2: Scorecard Row + Executive Summary
* Render as a two-column flex/grid layout: scorecards on the left (or top), executive summary prose on the right (or bottom on narrow viewports).
* No lists, labels, or sub-sections inside the summary block — plain paragraph only.

### 3c. Section 3: Recommendations
* All recommendation cards share identical styling — same border colour, same background, same badge style.
* No `Why:` label. Rationale renders as normal paragraph text immediately below the headline.
* If **iOS** is active: Recommendation 5 targets the 100-char hidden keyword field.
* If **Android** is active: Recommendation 5 targets Play Store Short Description.

### 3d. Section 4: The Gap Table & Chart
* **Metric reference:** Column headers display the metric name only. Full definitions are available in the Metric Glossary at the bottom of the report.
* **Dataset Swapping:** The `Chart.js` instance must `.destroy()` and re-initialize with the active platform's top 10 terms.
* **CSV Export:** Filename must dynamically update to `keyword_gaps_IOS_{date}.csv` or `keyword_gaps_ANDROID_{date}.csv`.

## 4. Layout Hierarchy (Refined)
```
<nav> (Sidebar)
  #platform-switcher (iOS | Android Toggle)
  #nav-links (Summary, Recommendations, Gaps, Long-tail, Landscape)
<main>
  #hero (Platform-specific metadata)
  #summary-row (Scorecards + Executive Summary prose, side by side)
  #recommendations-view (5 uniform cards + 3 Benchmark Guardrails)
  #gap-analysis-view (Chart + Filterable Table)
  #longtail-view (Secondary table)
  #landscape-view (Competitor table)
</main>
```

## 5. Functional Requirements (JS Logic)
* **The Switcher:**
```javascript
function switchPlatform(platform) {
  currentPlatform = platform;
  updateThemeColors(platform); // Subtle UI tint shift
  renderHero();
  renderSummary();         // Scorecards + prose, side by side
  renderRecommendations(); // Uniform card style
  renderCharts();          // Re-init Chart.js
  renderTables();          // Column headers with info icons
}
```
* **Data Validation:** If a platform has no data in `REPORT_DATA`, the toggle is disabled (`opacity: 0.5; pointer-events: none;`) with a "Data Unavailable" tooltip.
* **Table Persistence:** Filtering and sorting states reset on platform switch.

## 6. Visual Differentiators
* When **iOS** is active: Accents lean toward `--accent` (Purple/Blue).
* When **Android** is active: Accents lean toward `--accent-2` (Green/Teal).
* Recommendation cards do **not** participate in this colour shift — they remain uniform across both platforms.

## 7. Metric Glossary (Bottom of Report)
Render a static, always-visible glossary card as the last element inside `<main>`, below `#landscape-view`.

| Metric | Definition |
|---|---|
| **Rank** | The app's current position in search results for that keyword. |
| **Installs** | Estimated monthly organic downloads driven specifically by that keyword. |
| **Chance** | Score from 1–100. The likelihood of the app ranking in the Top 10 for this term. |
| **KEI (Keyword Efficiency Index)** | Volume × Chance. High KEI = high traffic potential at achievable difficulty. |
| **Avg Relevancy** | How closely the keyword aligns with the app's core use case, scored 0–100. |
| **Primary Count** | Number of Primary (top 3) competitors ranking for this term. Max = 3. |
| **Secondary Count** | Number of Secondary competitors (next 7) ranking for this term. |

Style: same `--bg-card` background, `--border` border, with a section heading "Metric Glossary" in `--text-secondary`. Table text uses `--font-sans` at 0.875rem.