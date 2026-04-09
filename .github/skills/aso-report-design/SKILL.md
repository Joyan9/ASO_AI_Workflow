---
name: aso-report-design
description: Create distinctive, production-grade HTML reports for ASO analysis with high-quality frontend design. Use this skill when generating ASO reports, analysis dashboards, or data visualization interfaces to avoid generic AI aesthetics and implement bold, memorable designs.
---

# ASO Report Design Skill

Create distinctive, production-grade HTML reports that avoid generic AI aesthetics and deliver visually striking, memorable interfaces for ASO data analysis.

## Design Philosophy

Before implementing, commit to a **distinctive aesthetic direction**:

- **Purpose:** Intelligence dashboard for ASO specialists
- **Tone:** Choose ONE extreme (editorial sophistication, tech minimalism, brutalist clarity, refined elegance, or bold maximalism)
- **Differentiation:** Create an interface competitors won't forget
- **Execution:** Bold intentionality over scattered generic choices

### Avoid Generic AI Aesthetics

❌ Overused font combinations (Space Grotesk, Roboto, Inter, JetBrains Mono)
❌ Purple gradient accents (too predictable)
❌ Timid, evenly-distributed color palettes
❌ Generic dark/light theme defaults
❌ Cookie-cutter component patterns
❌ Multiple uncoordinated accent hues

### Embrace Creativity

✅ Distinctive typography (Playfair Display, Courier Prime, IBM Plex, Inconsolata)
✅ Cohesive aesthetic (one clear visual language)
✅ Bold accent colors (one dominant + one supporting, sharply defined)
✅ Intentional motion (staggered reveals, scroll triggers, hover surprises)
✅ Unexpected layouts (asymmetry, diagonal flow, grid breaks)
✅ Generous or controlled density (but purposeful, never scattered)

## Design Tokens

Choose ONE dominant accent + ONE supporting accent:

```css
:root {
  --bg-page: [DARK_NEUTRAL];                    /* charcoal, off-black, deep grey */
  --bg-card: [CARD_TONE];                       /* subtle depth variation */
  --border: [BORDER_TONE];                      /* subtle and intentional */
  
  --accent-primary: [BOLD_PRIMARY];             /* dominant hue used consistently */
  --accent-primary-soft: rgba(...0.15);         /* soft variant for backgrounds */
  --accent-secondary: [SHARP_SECONDARY];        /* supporting hue, used sparingly */
  --accent-secondary-soft: rgba(...0.12);       /* soft secondary */
  
  --warn: [SIGNAL_COLOR];                       /* status/alert indicator */
  --text-primary: [FOREGROUND_MAIN];            /* readable, high contrast */
  --text-secondary: [FOREGROUND_MUTED];         /* labels, secondary info */
  
  --font-display: '[DISPLAY_FONT]';             /* distinctive, characterful */
  --font-body: '[BODY_FONT]';                   /* refined, readable, intentional */
  --font-mono: '[MONO_FONT]';                   /* personality-driven monospace */
}
```

**Color Strategy:**
- Dominant accent appears consistently across interactive elements
- Secondary accent used sparingly (badges, call-outs, signals)
- Backgrounds create intentional atmosphere (not flat)
- Text contrast sharp and readable (WCAG AA minimum, AAA preferred)

## Typography Strategy

Select two distinctive fonts that pair well:

| Use | Font | Size | Weight | Notes |
|-----|------|------|--------|-------|
| Display (hero, headers, badges) | Display Font | 32-36px | 700 | Characterful, memorable |
| Body (narrative, tables, detail) | Body Font | 15px | 400-500 | Refined, readable, intentional |
| Mono (code, metric values) | Mono Font | 13px | 400 | Personality-driven monospace |

**Font Pairing Examples:**
- Editorial: Playfair Display + Lora
- Tech-Forward: IBM Plex Sans + IBM Plex Mono
- Noir: Courier Prime + Open Sans
- Retro: Courier + Bodoni MT
- Organic: Faune + Mulish

## Production-Grade Design Standards

### Visual Hierarchy
✅ Clear size and weight differentiation (not evenly distributed)
✅ Intentional spacing that guides the eye
✅ Visual weight concentrated on critical information
✅ Information flows naturally without scattered emphasis

### Color & Contrast
✅ Dominant accent used **boldly and consistently**
✅ Secondary accent used sparingly for emphasis
✅ Text contrast sharp and readable (test WCAG compliance)
✅ Intentional background depth

### Typography
✅ Distinctive display font (not generic defaults)
✅ Refined body font chosen for beauty AND readability
✅ Mono font with personality
✅ Consistent pairing throughout

### Motion & Interaction
✅ High-impact page load (staggered reveals, fade-ins)
✅ Responsive hover and focus states
✅ Keyboard navigation fully accessible
✅ Subtle, purposeful animations (not scattered micro-interactions)

### Layout & Composition
✅ Intentional asymmetry or grid breaks (if part of vision)
✅ Generous OR controlled density (but deliberate)
✅ Clear reading flow and scanability
✅ Cohesive, unified section styling

### Data Visualization
✅ Chart colors match dominant accent (bold, not timid)
✅ Axis labels readable and intentional
✅ No unnecessary gridlines or chart junk
✅ High contrast between data and background

### Code Quality
✅ Self-contained HTML (CSS/JS embedded)
✅ No external resources except Google Fonts + Chart.js CDN
✅ Responsive: mobile, tablet, desktop
✅ Accessible: keyboard nav, screen reader friendly, sufficient contrast
✅ Performance optimized (minimal reflows, efficient DOM)

### Aesthetic Direction

Choose and commit to ONE direction:
- **Editorial Authority** — Sophisticated typography, deep colors, elegant whitespace
- **Tech Minimalism** — Clean lines, restrained palette, intentional negative space
- **Noir Intelligence** — Dark tones, sharp accents, dramatic lighting
- **Data Brutalism** — Raw, direct presentation, bold typography, functional beauty
- **Refined Elegance** — Subtle details, harmonious proportions, premium feel

## Framework Structure

All reports must:
1. Be single self-contained HTML5 files
2. Embed all CSS and JavaScript
3. Use Chart.js via CDN for visualizations
4. Embed data as JavaScript variables
5. Support platform switching (iOS/Android tabs)
6. Render at 1280px+ width (responsive scaling)

## Key Principles to Remember

- **Never be generic** — Every design should feel distinctive and intentional
- **Commit fully to your vision** — Half-measures between extremes fail
- **Typography carries meaning** — Font choices communicate tone and aesthetic
- **Color is powerful** — One bold accent beats multiple timid ones
- **Motion tells a story** — Purposeful animations enhance, scattered ones distract
- **Always test contrast** — Beautiful design that's unreadable defeats itself
- **Results should be memorable** — If it could be any app's report, it needs more personality

The goal is to create an interface that ASO specialists remember because it's distinctive, thoughtful, and visually striking—not another generic data dashboard.
