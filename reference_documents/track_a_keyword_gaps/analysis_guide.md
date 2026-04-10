---
title: Track A - Keyword Gap Analysis Guide
description: Framework for analyzing and prioritizing keyword gap opportunities
track: Track A
purpose: AI Agent Reference Document
audience: ASO Specialists, Product Managers
output_format: HTML Report with embedded charts
keywords:
  - keyword-gaps
  - aso-strategy
  - competitive-analysis
---

# Keyword Gap Analysis Guide

## Role & Strategic Context
You are a Senior ASO Specialist. The target app is an established dating brand (e.g., high "App Power"). Your goal is to identify high-value keyword gaps where competitors are winning. Your task is output a single self-contained HTML report. All data embedded as JS variables. Chart.js via CDN.

RETURN BACK ONLY THE HTML REPORT.

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
**Exactly 4 Recommendations (Strict Format):**
1. **The Core Parity Gap** — Where all primary competitors rank < 20.
2. **The High-Volume Power Play** — High installs, moderate chance, high brand relevance.
3. **The Quick Win** — High Chance > 70, Low Difficulty, Top competitor ranks highly.
4. **iOS / Android Metadata Optimisation** — iOS: hidden 100-char keyword field. Android: Short Description.

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

### 5. Competitive Landscape
Table: Competitor | Tier | Unique Gap Terms.
**Narrative:** Which competitor is "owning" the search voice in this specific territory?

---

## Visual & Technical Specs

- **Output:** Single HTML file, CSS/JS embedded. Include both iOS and Android in separate tabs.
- **Charts:** Chart.js via CDN.
- **Style:** Distinctive, intentional design (see Production-Grade Design Standards below). Uniform accent colour applied **boldly** for all recommendation cards.
- **Constraint:** Do not describe competitor behavior without a "Therefore, the target app should…" conclusion. Use "—" for null data.

---

# Keyword Gap Analysis Report — HTML Specification

### Design Philosophy (Claude Frontend Design Principles)

Before generating the HTML, commit to a **distinctive aesthetic direction**:
- **Purpose:** Keyword gap intelligence dashboard for ASO specialists
- **Tone:** Strategic + Data-driven. Choose one extreme: editorial sophistication, tech minimalism, brutalist clarity, refined elegance, or bold maximalism
- **Differentiation:** Create an interface competitors won't forget. This is NOT a generic report
- **Critical**: Bold intentionality is key. Execute one clear vision with precision, not scattered generic choices

**AVOID Generic AI Aesthetics:**
- ❌ Overused font combinations (Roboto + JetBrains Mono are now clichéd defaults)
- ❌ Purple gradient accent colors (too predictable)
- ❌ Generic dark/light theme defaults
- ❌ Multiple tier-based colors (--tier1-border, --tier2-border, --tier3-border are cookie-cutter)
- ❌ Timid, evenly-distributed color palettes

**Embrace Creativity:**
- ✅ Distinctive typography: Consider alternatives like Playfair Display, Courier Prime, IBM Plex, Input Mono, Inconsolata
- ✅ Cohesive aesthetic: Commit to one visual language (noir, editorial, retro, tech-minimal, organic, etc.)
- ✅ Intentional motion: Staggered reveals, scroll-triggered animations, hover surprises
- ✅ Unexpected layouts: Asymmetry, diagonal flow, generous negative space, grid-breaking elements
- ✅ Sharp accent color: One dominant hue with bold supporting accents (not timid pastels)

## 1. Tech Stack & State Management
* **Framework:** Single self-contained HTML5/CSS3/JS file.
* **Data Structure:** `const REPORT_DATA` must contain two top-level keys: `ios` and `android`.
* **State:** A global `currentPlatform` variable (defaulting to `ios`) triggers a `renderDashboard()` function to update all UI components simultaneously.

## 2. Design System & Navigation

**Font Strategy:** Select two distinctive fonts that pair well:
- Display font: For hero, section headers, pill badges (characterful, memorable — NOT Roboto)
- Body font: For narrative, tables, detail (refined, readable, intentional)
- Mono font: For metric values only (select for beauty, not just technical fit)

```css
:root {
  /* Choose ONE dominant accent hue + ONE supporting accent */
  /* NOT: generic purple + teal. Instead: bold teal + sharp orange, or deep indigo + bright lime */
  
  --bg-page:        [DARK_NEUTRAL];         /* Intentional BG: charcoal, off-black, deep grey */
  --bg-card:        [CARD_TONE];            /* Subtle depth variation from page BG */
  --border:         [BORDER_TONE];          /* Subtle but intentional */
  
  --accent-primary: [BOLD_PRIMARY];         /* Dominant hue: used consistently */
  --accent-primary-soft: rgba(...0.15);     /* Soft variant for backgrounds */
  --accent-secondary: [SHARP_SECONDARY];    /* Supporting hue: used sparingly */
  --accent-secondary-soft: rgba(...0.12);   /* Soft secondary */
  
  --warn:           [SIGNAL_COLOR];         /* Status/alert indicator */
  --text-primary:   [FOREGROUND_MAIN];      /* Readable, intentional contrast */
  --text-secondary: [FOREGROUND_MUTED];     /* Labeled, secondary info */
  
  --font-display:   '[DISPLAY_FONT]';       /* Distinctive display font */
  --font-body:      '[BODY_FONT]';          /* Refined body font */
  --font-mono:      '[MONO_FONT]';          /* Characterful monospace */
}
```

**Color Strategy:**
- Dominant accent should appear consistently for primary interactive elements (recommendation cards, key metrics)
- Secondary accent used sparingly (tier badges, call-outs, signal indicators)
- Tier-based colors (if needed) should use variations of the primary accent family, NOT multiple uncoordinated hues
- Backgrounds should create intentional atmosphere (not just dark/light toggle)
- Text contrast must be sharp and readable (test WCAG AA minimum)

* **Sidebar Toggle:** A high-visibility "Platform Switcher" at the top of the fixed sidebar.
    * *Design:* A segmented control (pill shape) with "iOS" and "Android" labels — with **intentional visual weight** applied to the active platform
    * *Interaction:* Active platform uses the dominant accent color: bold, not timid

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

### 3e. Section 5: Competitive Landscape
* **Narrative:** Dynamically identify which competitor is "owning" the search voice in this territory.
* **Table rendering:** Display competitor tier, title, and unique gap term count.

## 4. Layout Hierarchy (Refined)
```
<nav> (Sidebar)
  #platform-switcher (iOS | Android Toggle)
  #nav-links (Summary, Recommendations, Gaps, Landscape)
<main>
  #hero (Platform-specific metadata)
  #summary-row (Scorecards + Executive Summary prose, side by side)
  #recommendations-view (5 uniform cards + 3 Benchmark Guardrails)
  #gap-analysis-view (Chart + Filterable Table)
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

---

## Production-Grade Design Standards

**This is NOT a generic report.** Implement with meticulous attention to every detail:

### Visual Hierarchy
- ✅ Clear size and weight differentiation (not evenly distributed)
- ✅ Intentional spacing that guides the eye (generous or tight — but purposeful)
- ✅ Visual weight concentration on critical information (high-KEI gaps, critical threats)
- ❌ Scattered emphasis or competing visual elements

### Color & Contrast
- ✅ Dominant accent used **boldly and consistently** across recommendation cards and key metrics
- ✅ Secondary accent used sparingly (tier badges, signal indicators, subtle emphasis)
- ✅ Text contrast sharp and readable (WCAG AA minimum, ideally AAA)
- ✅ Intentional background depth (not flat, not generic)
- ❌ Timid, evenly-distributed color palette (no pastels or washed-out tones)
- ❌ Multiple uncoordinated accent hues (--tier1-border, --tier2-border patterns are cookie-cutter)

### Typography
- ✅ Distinctive display font that is memorable (NOT Roboto)
- ✅ Refined body font chosen for beauty AND readability
- ✅ Mono font with personality for metric values
- ✅ Consistent font pairing across the entire report
- ❌ Generic serif/sans/mono combinations
- ❌ Default system fonts or overused families like Inter, Arial, or Roboto

### Motion & Interaction
- ✅ High-impact page load (staggered reveals, intentional fade-ins)
- ✅ Platform switcher interaction feels responsive and has visual feedback
- ✅ Hover states on cards, links, and interactive elements feel deliberate
- ✅ Focus states clearly visible for accessibility
- ✅ Subtle, purposeful animations (not scattered micro-interactions)
- ❌ No animation or over-animated distraction
- ❌ Janky or unintentional motion

### Layout & Composition
- ✅ Intentional asymmetry or grid breaks (if part of the aesthetic vision)
- ✅ Generous negative space OR controlled density (but deliberate)
- ✅ Clear reading flow and scanability
- ✅ Cards/sections feel cohesive and unified
- ✅ Platform-specific color shifts feel intentional, not arbitrary
- ❌ Cookie-cutter layouts
- ❌ Predictable, uninspired composition

### Data Visualization (Charts)
- ✅ Bar chart colors match the dominant accent (bold, not timid)
- ✅ Axis labels readable and intentional
- ✅ No unnecessary gridlines or chart junk
- ✅ High contrast between bars and background
- ❌ Generic Chart.js defaults
- ❌ Low-contrast or hard-to-read labels

### Code Quality
- ✅ Self-contained HTML file (all CSS and JS embedded)
- ✅ No external resources except Google Fonts and Chart.js CDN
- ✅ Responsive design: works on mobile, tablet, desktop
- ✅ Accessible: keyboard navigation, screen reader friendly, sufficient contrast
- ✅ Performance: minimal reflows, efficient DOM
- ❌ Messy or unoptimized code
- ❌ Inline styles or scattered CSS

### Overall Aesthetic Direction
Choose ONE clear direction and execute it with precision:
- Examples: **Editorial Authority**, **Tech Minimalism**, **Noir Intelligence**, **Refined Elegance**, **Data Brutalism**, **Retro Data**
- NEVER be generic or in-between
- ALWAYS commit fully to the vision
- Results should feel **intentional, distinctive, and memorable**