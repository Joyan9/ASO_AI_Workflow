"""
Step 1-3: Fetch Focus App Metadata, Extract Competitors, and Fetch Competitor Data

Orchestrates the initial three steps of the ASO Workflow pipeline:
    Step 1: Fetch your app's current metadata from AppTweak
    Step 2: Extract competitor app IDs (iOS: from similar_apps; Android: from top charts)
    Step 3: Fetch metadata and 90-day history for all identified competitors

This script handles both iOS and Android platforms and saves raw API responses
to data/raw/ with the following structure:
    - {platform}_{app_id}_metadata.json (your app's metadata)
    - {platform}_{app_id}_competitors.json (list of competitor IDs)
    - competitors/{platform}_{competitor_id}_metadata.json (competitor data)
    - competitors/{platform}_{competitor_id}_history.json (Android only, change history)

Run from the aso_workflow directory:
    python run_fetcher.py
"""

import json
from pathlib import Path

from fetchers.metadata import (
    fetch_current_metadata,
    extract_competitors,
    fetch_competitor_metadata,
    fetch_competitor_history,
    fetch_app_history,
)
import config

def main():
    """Fetch metadata, competitors, and competitor history for Tinder."""
    
    print("=" * 60)
    print("ASO Workflow - Full Pipeline")
    print("=" * 60)
    print()
    
    # STEP 1 & 2: Main app metadata
    print(">>> [STEP 1-2] Fetching main app metadata & extracting competitors...")
    print()
    
    
    # iOS Tinder
    print(f">>> Fetching iOS {config.iOS_APP_ID} metadata...")
    
    ios_metadata = fetch_current_metadata(
        app_id=config.iOS_APP_ID,
        platform="ios",
        country=config.COUNTRY,
        language=config.LANGUAGE,
        device=config.iOS_DEVICE,
    )
   
    print()
    
    print(">>> Extracting competitors from iOS metadata...")
   
    ios_competitors = extract_competitors(
        metadata=ios_metadata,
        app_id=config.iOS_APP_ID,
        platform="ios",
    )
    
    print(f"    Extracted {len(ios_competitors['competitors'])} competitors")
    print()
    
    
    # Android Tinder
    print(f">>> Fetching Android {config.ANDROID_APP_ID} metadata...")
    android_metadata = fetch_current_metadata(
        app_id=config.ANDROID_APP_ID,
        platform="android",
        country=config.COUNTRY,
        language=config.LANGUAGE,
        device=config.ANDROID_DEVICE,
    )
    print()
    
    print(">>> Extracting competitors from Android metadata...")
    android_competitors = extract_competitors(
        metadata=android_metadata,
        app_id=config.ANDROID_APP_ID,
        platform="android",
    )
    print(f"    Extracted {len(android_competitors['competitors'])} competitors")
    print()
    
    # STEP 3: Save our app metadata to our_app subdirectory
    print(">>> [STEP 3] Saving target app metadata to our_app directory...")
    print()
    target_metadata = fetch_current_metadata(
        app_id=config.ANDROID_APP_ID,
        platform="android",
        country=config.COUNTRY,
        language=config.LANGUAGE,
        device=config.ANDROID_DEVICE,
    )
    
    # Save to our_app subdirectory
    our_app_dir = Path(config.DATA_RAW_DIR) / "our_app"
    our_app_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = our_app_dir / "android_metadata.json"
    with open(output_file, "w") as f:
        json.dump(target_metadata, f, indent=2)
    print(f"[SAVE] Target app metadata also saved to {output_file}")
    print()
    
    # STEP 4: Competitor metadata and history
    print(">>> [STEP 4] Fetching competitor metadata and history...")
    fetch_competitor_metadata("ios")
    fetch_competitor_metadata("android")
    fetch_competitor_history("android")
    
    # STEP 5: Target app history
    print(">>> [STEP 5] Fetching target app history...")
    print(f"  Fetching {config.ANDROID_DEVICE.upper()} | {config.ANDROID_APP_ID}")
    fetch_app_history("android", config.ANDROID_APP_ID, save_subdir="our_app")
    print()
    print("=" * 60)
    print("All data saved to:", config.DATA_RAW_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
