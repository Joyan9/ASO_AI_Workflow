# Track A: Keyword Gap Analysis Report — HTML Specification

## 1. Tech Stack & State Management
* **Framework:** Single self-contained HTML5/CSS3/JS file.
* **Data Structure:** `const REPORT_DATA` must contain two top-level keys: `ios` and `android`.
* **State:** A global `currentPlatform` variable (defaulting to `ios`) triggers a `renderDashboard()` function to update all UI components simultaneously.

## 2. Design System & Navigation
```css
:root {
  --bg-page:         #0f1117;
  --bg-card:         #1a1d27;
  /* ... [Previous Colors Apply] ... */
  --platform-ios:    #5fc3e4;
  --platform-android:#a4c639;
}
```
* **Sidebar Toggle:** A high-visibility "Platform Switcher" at the top of the fixed sidebar. 
    * *Design:* A segmented control (pill shape) with "iOS" and "Android" labels.
    * *Interaction:* Active platform uses a subtle glow: `box-shadow: 0 0 10px var(--accent-soft)`.

## 3. Component Updates for Dual-Platform
### 3a. Hero Section
* **Dynamic Badges:** Platform-specific metadata (e.g., "Seeds with data: iOS [n] | Android [n]").
* **Platform Indicator:** A large, subtle watermark icon of the Apple or Android logo in the background of the Hero section to provide instant visual context.

### 3b. Section 2: Executive Summary & Recommendations
* **Contextual Recs:** * If **iOS** is active: Include the "iOS Keyword Field" recommendation (Recommendation Type #4).
    * If **Android** is active: Swap Recommendation #4 to "Play Store Description/Short Description" optimization.

### 3c. Section 3: The Gap Table & Chart
* **Dataset Swapping:** The `Chart.js` instance must `.destroy()` and re-initialize with the active platform’s top 20 terms.
* **CSV Export:** Filename must dynamically update to `keyword_gaps_IOS_{date}.csv` or `keyword_gaps_ANDROID_{date}.csv`.

## 4. Layout Hierarchy (Refined)
```
<nav> (Sidebar)
  #platform-switcher (iOS | Android Toggle)
  #nav-links (Summary, Gaps, Long-tail, Landscape)
<main>
  #hero (Platform-specific metadata)
  #summary-cards (Dynamic content based on currentPlatform)
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
      renderRecommendations();
      renderCharts();
      renderTables();
    }
```

* **Data Validation:** If a platform has no data provided in `REPORT_DATA`, the toggle should be disabled (`opacity: 0.5; pointer-events: none;`) with a "Data Unavailable" tooltip.
* **Table Persistence:** Filtering and sorting states should reset when switching platforms to prevent data mismatch.

## 6. Visual Differentiators
* When **iOS** is active: Accents lean toward `--accent` (Purple/Blue).
* When **Android** is active: Accents lean toward `--accent-2` (Green/Teal).
* This provides a cognitive "shortcut" for the user to know which platform they are currently analyzing.