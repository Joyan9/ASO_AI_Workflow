"""
AppTweak API Fetchers - Metadata

Handles fetching current app metadata and extracting competitor information.
Uses the AppTweak Current App Metadata endpoint:
https://developers.apptweak.com/reference/app-metadata-current.md
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv

import config

# Load API key from .env
load_dotenv()
API_KEY = os.getenv("APPTWEAK_API_KEY")

if not API_KEY:
    raise ValueError(
        "APPTWEAK_API_KEY not found in .env file. "
        "Please set it in aso_workflow/.env"
    )


class AppTweakClient:
    """Simple AppTweak API client with header management."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = config.APPTWEAK_BASE_URL

    def _get_headers(self) -> Dict[str, str]:
        """Build headers with API key."""
        return {
            "X-Apptweak-Key": self.api_key,
            "Accept": "application/json",
        }

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make a GET request to the AppTweak API.
        Raises an error if the response is not 200.
        """
        url = f"{self.base_url}/{endpoint}"
        
        print(f"[FETCH] {endpoint} | params: {params}")
        
        response = requests.get(url, headers=self._get_headers(), params=params)
        
        if response.status_code != 200:
            raise RuntimeError(
                f"AppTweak API error: {response.status_code} {response.reason}\n"
                f"URL: {response.url}\n"
                f"Response: {response.text}"
            )
        
        print(f"[OK] Status {response.status_code}")
        return response.json()


def fetch_current_metadata(
    app_id: str,
    platform: str,
    country: str = "us",
    language: str = "en",
    device: str = "iphone",
) -> Dict[str, Any]:
    """
    Fetch current app metadata from AppTweak.
    
    Args:
        app_id: iOS app ID or Android package name
        platform: "ios" or "android" (for logging/context)
        country: ISO country code (e.g., "us")
        language: ISO language code (e.g., "en")
        device: Device type ("iphone", "android", etc.)
    
    Returns:
        Raw API response as dict
    """
    client = AppTweakClient(API_KEY)
    
    # Parameters for the Current App Metadata endpoint
    # Uses the public API: /api/public/store/apps/metadata.json
    params = {
        "apps": app_id,
        "country": country,
        "language": language,
        "device": device,
    }
    
    endpoint = config.APPTWEAK_METADATA_ENDPOINT
    response = client.get(endpoint, params=params)
    
    # Save raw response
    data_dir = Path(config.DATA_RAW_DIR)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = data_dir / f"{platform}_{app_id}_metadata.json"
    with open(output_file, "w") as f:
        json.dump(response, f, indent=2)
    
    print(f"[SAVE] Metadata saved to {output_file}")
    
    return response


def extract_competitors(
    metadata: Dict[str, Any],
    app_id: str,
    platform: str,
) -> Dict[str, Any]:
    """
    Extract competitor list from metadata response.
    
    Takes the similar apps list (customers_also_bought for iOS, similar_apps for Android),
    classifies the first 3 as 'primary' and the rest as 'secondary'.
    
    Args:
        metadata: Raw API response from fetch_current_metadata
        app_id: Source app ID
        platform: "ios" or "android"
    
    Returns:
        Dict with extracted competitors in the specified format
    """
    competitors_list = []
    
    # Navigate to the result structure: result[app_id].metadata
    result = metadata.get("result", {})
    app_metadata = result.get(str(app_id), {}).get("metadata", {})
    
    # iOS uses 'customers_also_bought', Android uses 'similar_apps'
    similar_apps = app_metadata.get("customers_also_bought") or app_metadata.get("similar_apps", [])
    
    # Take top 10
    top_10 = similar_apps[:10]
    
    print(f"[EXTRACT] Found {len(similar_apps)} similar apps, extracting top {len(top_10)}")
    
    for idx, competitor_app_id in enumerate(top_10):
        # Determine tier
        tier = "primary" if idx < config.PRIMARY_TIER_COUNT else "secondary"
        
        competitors_list.append({
            "app_id": str(competitor_app_id),
            "name": None,  # Names not provided by this endpoint
            "tier": tier,
        })
    
    result_dict = {
        "source_app_id": app_id,
        "platform": platform,
        "extracted_at": datetime.now().isoformat(),
        "competitors": competitors_list,
    }
    
    # Save competitors
    data_dir = Path(config.DATA_RAW_DIR)
    output_file = data_dir / f"{platform}_{app_id}_competitors.json"
    with open(output_file, "w") as f:
        json.dump(result_dict, f, indent=2)
    
    print(f"[SAVE] Competitors saved to {output_file}")
    
    return result_dict


def fetch_competitor_metadata(platform: str) -> None:
    """
    Fetch current metadata for all competitors of a given platform.
    
    Loads the competitor list from the saved JSON file, then fetches
    metadata for each competitor using the same endpoint as the main app.
    
    Args:
        platform: "ios" or "android"
    
    Saves:
        data/raw/competitors/{platform}_{competitor_app_id}_metadata.json
    """
    # Load competitor list
    competitor_file = Path(config.DATA_RAW_DIR) / f"{platform}_*_competitors.json"
    competitor_files = list(Path(config.DATA_RAW_DIR).glob(f"{platform}_*_competitors.json"))
    
    if not competitor_files:
        print(f"[WARN] No competitor list found for platform: {platform}")
        return
    
    competitor_data_file = competitor_files[0]
    with open(competitor_data_file) as f:
        competitor_data = json.load(f)
    
    competitors = competitor_data.get("competitors", [])
    print(f"\n[STEP 3a] Fetching metadata for {len(competitors)} {platform.upper()} competitors...")
    
    # Create competitors directory
    competitors_dir = Path(config.DATA_RAW_DIR) / "competitors"
    competitors_dir.mkdir(parents=True, exist_ok=True)
    
    client = AppTweakClient(API_KEY)
    
    # Determine device and language from config
    if platform.lower() == "ios":
        device = config.iOS_DEVICE
    else:
        device = config.ANDROID_DEVICE
    
    for idx, competitor in enumerate(competitors):
        competitor_app_id = competitor["app_id"]
        competitor_tier = competitor["tier"]
        
        try:
            # Build params for metadata endpoint
            params = {
                "apps": competitor_app_id,
                "country": config.COUNTRY,
                "language": config.LANGUAGE,
                "device": device,
            }
            
            # Fetch metadata
            print(f"  [{idx + 1}/{len(competitors)}] Fetching {competitor_tier:9} | {platform.upper():7} | {competitor_app_id}")
            response = client.get(config.APPTWEAK_METADATA_ENDPOINT, params=params)
            
            # Save raw response
            output_file = competitors_dir / f"{platform}_{competitor_app_id}_metadata.json"
            with open(output_file, "w") as f:
                json.dump(response, f, indent=2)
            
            print(f"      → Saved to {output_file}")
            
            # Rate limiting: delay between requests
            if idx < len(competitors) - 1:
                time.sleep(1)
        
        except Exception as e:
            print(f"  [ERROR] Failed to fetch metadata for {competitor_app_id}: {e}")
            continue


def fetch_competitor_history(platform: str) -> None:
    """
    Fetch metadata change history for all competitors (Android only).
    
    Only executes when platform == "android". For iOS, logs and returns early.
    
    Loads the competitor list, then fetches history for each using the
    metadata/changes endpoint with the configured date range (last 90 days).
    
    Args:
        platform: "ios" or "android"
    
    Saves:
        data/raw/competitors/android_{competitor_app_id}_history.json
    """
    if platform.lower() == "ios":
        print(f"\n[STEP 3b] Skipping history fetch for iOS (Android only)")
        return
    
    # Load competitor list
    competitor_files = list(Path(config.DATA_RAW_DIR).glob(f"{platform}_*_competitors.json"))
    
    if not competitor_files:
        print(f"[WARN] No competitor list found for platform: {platform}")
        return
    
    competitor_data_file = competitor_files[0]
    with open(competitor_data_file) as f:
        competitor_data = json.load(f)
    
    competitors = competitor_data.get("competitors", [])
    print(f"\n[STEP 3b] Fetching history for {len(competitors)} {platform.upper()} competitors (last 90 days)...")
    
    # Create competitors directory
    competitors_dir = Path(config.DATA_RAW_DIR) / "competitors"
    competitors_dir.mkdir(parents=True, exist_ok=True)
    
    client = AppTweakClient(API_KEY)
    
    # Determine device from config
    device = config.ANDROID_DEVICE if platform.lower() == "android" else config.iOS_DEVICE
    
    for idx, competitor in enumerate(competitors):
        competitor_app_id = competitor["app_id"]
        competitor_tier = competitor["tier"]
        
        try:
            # Build params for history endpoint
            params = {
                "apps": competitor_app_id,
                "country": config.COUNTRY,
                "language": config.LANGUAGE,
                "device": device,
                "start_date": config.START_DATE,
                "end_date": config.END_DATE,
            }
            
            # Fetch history
            print(f"  [{idx + 1}/{len(competitors)}] Fetching {competitor_tier:9} | {platform.upper():7} | {competitor_app_id}")
            response = client.get("api/public/store/apps/metadata/changes.json", params=params)
            
            # Save raw response
            output_file = competitors_dir / f"{platform}_{competitor_app_id}_history.json"
            with open(output_file, "w") as f:
                json.dump(response, f, indent=2)
            
            print(f"      → Saved to {output_file}")
            
            # Rate limiting: delay between requests
            if idx < len(competitors) - 1:
                time.sleep(1)
        
        except Exception as e:
            print(f"  [ERROR] Failed to fetch history for {competitor_app_id}: {e}")
            continue
