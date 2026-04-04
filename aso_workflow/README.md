# ASO Workflow - MVP Implementation

A simple, readable ASO (App Store Optimization) insight workflow using the AppTweak API.

## Project Structure

```
aso_workflow/
├── config.py              # Configuration (app IDs, country, device, etc.)
├── fetchers/
│   ├── __init__.py
│   └── metadata.py        # Fetchers for metadata and competitors
├── data/
│   └── raw/               # Raw JSON responses from API
├── run_example.py         # Example usage script
├── requirements.txt       # Python dependencies
└── .env                   # API key (DO NOT COMMIT)
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
- Country/language (`us`, `en`)
- Device types (`iphone`, `android`)
- History window (90 days)

## Usage

### Run the Example

```bash
python run_example.py
```

This fetches metadata and extracts competitors for both iOS and Android Tinder.

### Use in Your Code

```python
from fetchers.metadata import fetch_current_metadata, extract_competitors
import config

# Fetch metadata
metadata = fetch_current_metadata(
    app_id="com.example.app",
    platform="android",
    country="us",
    language="en",
    device="android",
)

# Extract competitors
competitors = extract_competitors(
    metadata=metadata,
    app_id="com.example.app",
    platform="android",
)
```

## What Gets Saved

### Metadata Response
- **File**: `data/raw/{platform}_{app_id}_metadata.json`
- **Contents**: Full raw API response from AppTweak

### Competitors List
- **File**: `data/raw/{platform}_{app_id}_competitors.json`
- **Format**:
  ```json
  {
    "source_app_id": "com.example.app",
    "platform": "android",
    "extracted_at": "2026-04-04T12:34:56.789012",
    "competitors": [
      {"app_id": "...", "name": "...", "tier": "primary"},
      {"app_id": "...", "name": "...", "tier": "secondary"}
    ]
  }
  ```

## API Reference

Uses AppTweak's **Current App Metadata** endpoint:
- Docs: https://developers.apptweak.com/reference/app-metadata-current.md
- Returns: Latest app metadata, including similar/recommended apps
- Updated: Daily by AppTweak

## Key Implementation Details

- **API Client**: Simple wrapper in `AppTweakClient` with header management
- **Logging**: Prints to stdout (no logging framework for MVP simplicity)
- **File Paths**: Uses `pathlib.Path` for cross-platform compatibility
- **Error Handling**: Raises on non-200 responses with clear error context
- **Competitors**: Extracts top 10, labels first 3 as "primary", rest as "secondary"
- **Raw Storage**: All API responses stored as-is before any transformation

## What Comes Next

This MVP provides the foundation for:
1. Fetching metadata for competitors
2. For Android, fetching metadata history (includes A/B test flags)
3. Transformation script to extract keywords and compute gaps
4. LLM analysis for final keyword gap and A/B strategy reports
