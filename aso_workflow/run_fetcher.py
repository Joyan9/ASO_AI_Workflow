"""
Example usage of the ASO Workflow - fetches metadata, competitors, and competitor history for Tinder.

Run from the aso_workflow directory:
    python run_example.py
"""

from fetchers.metadata import (
    fetch_current_metadata,
    extract_competitors,
    fetch_competitor_metadata,
    fetch_competitor_history,
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
    
    '''
    # iOS Tinder
    print(">>> Fetching iOS Tinder metadata...")
    
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
    '''
    
    # Android Tinder
    print(">>> Fetching Android Tinder metadata...")
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
    
    # STEP 3: Competitor metadata and history
    #fetch_competitor_metadata("ios")
    fetch_competitor_metadata("android")
    fetch_competitor_history("android")
    
    print()
    print("=" * 60)
    print("All data saved to:", config.DATA_RAW_DIR)
    print("=" * 60)


if __name__ == "__main__":
    main()
