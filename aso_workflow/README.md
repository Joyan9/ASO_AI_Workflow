# ASO Workflow - MVP Implementation

A simple, readable ASO (App Store Optimization) insight workflow using the AppTweak API.

## Project Structure

```
aso_workflow/
├── config.py                      # Configuration (app IDs, country, device, etc.)
├── fetchers/
│   ├── __init__.py
│   ├── metadata.py                # Fetch current app metadata + competitors
│   └── keywords.py                # Fetch keyword metrics
├── transformers/
│   ├── __init__.py
│   └── track_a.py                 # Extract terms, build gap corpus
├── data/
│   ├── raw/                       # Raw JSON responses from API
│   └── processed/                 # Transformed data (keyword gaps)
├── run_example.py                 # Example: fetch Tinder metadata
├── run_step_3_competitors.py      # Step 3: Fetch competitor metadata
├── run_track_a.py                 # Step 4: Transform & fetch keyword metrics
├── requirements.txt               # Python dependencies
├── .env                           # API key (DO NOT COMMIT)
└── README.md
```

## Setup

### 1. Install Dependencies

```bash
cd aso_workflow
pip install -r requirements.txt
```

### 2. Configure API Key

Edit `.env` and add your AppTweak API key:

```
APPTWEAK_API_KEY=your_actual_api_key_here
```

### 3. Customize Config (Optional)

Edit `config.py` to change:
- App IDs (iOS: `547702041`, Android: `com.tinder`)
- Country/language (`us`, `us`)
- Device types (`iphone`, `android`)
- History window (90 days)

## Usage

### Step 1 & 2 — Fetch Your App & Extract Competitors

```bash
python run_example.py
```

Outputs:
- `data/raw/ios_547702041_metadata.json` — Your app metadata
- `data/raw/ios_547702041_competitors.json` — Top 10 competitors (3 primary, 7 secondary)
- Same for Android with package name

### Step 3 — Fetch Competitor Metadata

```bash
python run_step_3_competitors.py
```

Fetches metadata for each of the 10 competitors and saves to:
- `data/raw/{platform}_{competitor_id}_metadata.json`

### Step 4 — Transform & Fetch Keyword Metrics

```bash
python run_track_a.py
```

1. **Transformation** — Extract terms from all apps, build gap corpus
   - Tokenize into unigrams & bigrams from: title, subtitle/short_description, description
   - Weighted by field (title: 5, subtitle: 4, description excerpt: 3, description rest: 1)
   - Filters to gap terms (not in your app), sorted by competitor presence
   - Removes branded terms via substring matching
   
2. **Metrics Fetch** — Enrich gap terms with AppTweak keyword metrics
   - Batches keywords 5 per API call
   - Fetches: volume, difficulty, results, brand status, max reach
   - Caps at top 50 gap terms for MVP
   
3. **Final Output** — Writes `data/processed/keyword_gaps_{platform}_{app_id}.json`

Output structure:
```json
{
  "meta": {
    "app_id": "...",
    "platform": "ios|android",
    "country": "us",
    "run_date": "2026-04-04T13:10:50"
  },
  "your_app": {
    "title": "...",
    "subtitle": "...",
    "description_excerpt": "...",
    "term_count": 411
  },
  "keyword_gaps": [
    {
      "term": "get",
      "primary_competitor_count": 3,
      "secondary_competitor_count": 5,
      "volume": 52,
      "difficulty": 19,
      "results": 192,
      "brand": { "top_app_id": 844091049 },
      "max_reach": null
    }
  ],
  "competitor_summary": [
    {
      "app_id": "930441707",
      "name": "Bumble Dating App: Meet & Date",
      "tier": "primary",
      "title": "Bumble Dating App: Meet & Date",
      "subtitle": "Find new people & chat singles",
      "unique_terms_not_in_your_app": 354
    }
  ]
}
```

## Implementation Details

### Term Extraction (transformers/track_a.py)

- Unigrams & bigrams tokenized via NLTK
- English stopwords removed, punctuation stripped
- **Field weights** (highest wins if term appears in multiple fields):
  - `title`: 5
  - `subtitle` / `short_description`: 4
  - `description` first 250 chars: 3
  - `description` remainder: 1
  - iOS also supports `promotional_text`: 4

- **Platform differences**:
  - iOS: `title`, `subtitle`, `promotional_text`, `description`
  - Android: `title`, `short_description`, `long_description`

### Keyword Metrics (fetchers/keywords.py)

- Batches keywords in groups of 5 (AppTweak API limit)
- Metrics available: `volume`, `difficulty`, `results`, `brand`, `max_reach`
- Sets unavailable metrics to `null` (e.g., `volume` only on iOS in US)
- Includes 0.5s sleep between batches (respectful API usage)

### API Wrapper (fetchers/metadata.py)

- Simple `AppTweakClient` class with:
  - Automatic `X-Apptweak-Key` header injection
  - Raises on non-200 responses with full error context
  - stdout logging (no framework needed)

## What Comes Next

- [ ] Fetch keyword **history** for volume velocity scoring
- [ ] Android-only: Fetch metadata **change history** (A/B test flags)
- [ ] LLM transformation: Convert gap list + competitor context → strategic recommendations
- [ ] Filter & prioritize: Cost-benefit analysis (difficulty vs. volume)
- [ ] Output: Word document with gap analysis + implementation roadmap

## Notes

- **MVP scope**: 50 top gap terms (adjustable in `run_track_a.py`)
- **Data quality**: Raw API responses stored first, never transformed in-place
- **Cross-platform**: Handles iOS bundle IDs and Android package names correctly
- **Reusability**: `AppTweakClient` and metrics fetcher can be extended for other endpoints
