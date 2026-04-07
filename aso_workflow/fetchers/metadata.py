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

def fetch_top_chart_competitors(platform: str, app_id: str) -> list:
    """
    Fetch top chart apps for the DATING category (Android only).
 
    Calls the Top Charts - Current endpoint, strips the target app from
    the result (regardless of position), and returns up to 10 competitor
    app IDs.
 
    Args:
        platform: Must be "android". Returns empty list for iOS.
        app_id:   The target app ID to exclude from results.
 
    Returns:
        List of up to 10 competitor app ID strings.
    """
    if platform.lower() != "android":
        print(f"[TOP CHART] Skipping top chart fetch for platform: {platform}")
        return []
 
    client = AppTweakClient(API_KEY)
 
    # Fetch 11 to account for the target app occupying one slot
    params = {
        "categories": "DATING",
        "types": "free",
        "country": config.COUNTRY,
        "device": config.ANDROID_DEVICE,
        "limit": 11,
        "offset": 0,
    }
 
    print(f"[TOP CHART] Fetching DATING free chart for Android ({config.COUNTRY.upper()})...")
    response = client.get(config.APPTWEAK_TOP_CHARTS_ENDPOINT, params=params)
 
    # Navigate response: result > DATING > free > value
    chart_apps = (
        response.get("result", {})
        .get("DATING", {})
        .get("free", {})
        .get("value", [])
    )
 
    # Strip the target app regardless of position
    competitors = [a for a in chart_apps if str(a) != str(app_id)]
 
    if str(app_id) not in chart_apps:
        print(f"[WARN] Target app {app_id} was not found in the top chart — taking first 10 results as-is")
 
    competitors = competitors[:10]
    print(f"[TOP CHART] Found {len(competitors)} competitors after excluding target app")
 
    return competitors

def extract_competitors(
    metadata: Dict[str, Any],
    app_id: str,
    platform: str,
) -> Dict[str, Any]:
    """
    Extract competitor list from metadata response (iOS) or top charts (Android).
 
    iOS: uses customers_also_bought from the metadata response.
    Android: uses the DATING free top chart via fetch_top_chart_competitors,
             since similar_apps returns poor signal for this category.
 
    Classifies the first 3 as 'primary' and the rest as 'secondary'.
 
    Args:
        metadata: Raw API response from fetch_current_metadata (used for iOS only).
        app_id:   Source app ID.
        platform: "ios" or "android".
 
    Returns:
        Dict with extracted competitors in the standard format.
    """
    if platform.lower() == "android":
        similar_apps = fetch_top_chart_competitors(platform, app_id)
    else:
        # iOS: pull from metadata response
        result = metadata.get("result", {})
        app_metadata = result.get(str(app_id), {}).get("metadata", {})
        similar_apps = app_metadata.get("customers_also_bought", [])
        print(f"[EXTRACT] Found {len(similar_apps)} similar apps in iOS metadata")
 
    top_10 = similar_apps[:10]
    print(f"[EXTRACT] Using top {len(top_10)} competitors for {platform.upper()}")
 
    competitors_list = []
    for idx, competitor_app_id in enumerate(top_10):
        tier = "primary" if idx < config.PRIMARY_TIER_COUNT else "secondary"
        competitors_list.append({
            "app_id": str(competitor_app_id),
            "name": None,  # Resolved later when metadata is fetched per competitor
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
    competitor_files = list(Path(config.DATA_RAW_DIR).glob(f"{platform}_*_competitors.json"))
 
    if not competitor_files:
        print(f"[WARN] No competitor list found for platform: {platform}")
        return
 
    with open(competitor_files[0]) as f:
        competitor_data = json.load(f)
 
    competitors = competitor_data.get("competitors", [])
    print(f"\n[STEP 4a] Fetching metadata for {len(competitors)} {platform.upper()} competitors...")
 
    competitors_dir = Path(config.DATA_RAW_DIR) / "competitors"
    competitors_dir.mkdir(parents=True, exist_ok=True)
 
    client = AppTweakClient(API_KEY)
    device = config.iOS_DEVICE if platform.lower() == "ios" else config.ANDROID_DEVICE
 
    for idx, competitor in enumerate(competitors):
        competitor_app_id = competitor["app_id"]
        competitor_tier = competitor["tier"]
 
        try:
            params = {
                "apps": competitor_app_id,
                "country": config.COUNTRY,
                "language": config.LANGUAGE,
                "device": device,
            }
 
            print(f"  [{idx + 1}/{len(competitors)}] Fetching {competitor_tier:9} | {platform.upper():7} | {competitor_app_id}")
            response = client.get(config.APPTWEAK_METADATA_ENDPOINT, params=params)
 
            output_file = competitors_dir / f"{platform}_{competitor_app_id}_metadata.json"
            with open(output_file, "w") as f:
                json.dump(response, f, indent=2)
 
            print(f"      → Saved to {output_file}")
 
            if idx < len(competitors) - 1:
                time.sleep(1)
 
        except Exception as e:
            print(f"  [ERROR] Failed to fetch metadata for {competitor_app_id}: {e}")
            continue
 
 
def fetch_competitor_history(platform: str) -> None:
    """
    Fetch metadata change history for all competitors (Android only).
    
    Loads competitor list and uses fetch_app_history() to fetch history for each.
    
    Args:
        platform: "ios" or "android"
    
    Saves:
        data/raw/competitors/{platform}_{competitor_app_id}_history.json
    """
    if platform.lower() == "ios":
        print(f"\n[STEP 4b] Skipping history fetch for iOS (Android only)")
        return
    
    competitor_files = list(Path(config.DATA_RAW_DIR).glob(f"{platform}_*_competitors.json"))
    
    if not competitor_files:
        print(f"[WARN] No competitor list found for platform: {platform}")
        return
    
    with open(competitor_files[0]) as f:
        competitor_data = json.load(f)
    
    competitors = competitor_data.get("competitors", [])
    print(f"\n[STEP 4b] Fetching history for {len(competitors)} {platform.upper()} competitors (last 90 days)...")
    
    for idx, competitor in enumerate(competitors):
        competitor_app_id = competitor["app_id"]
        competitor_tier = competitor["tier"]
        
        print(f"  [{idx + 1}/{len(competitors)}] Fetching {competitor_tier:9} | {platform.upper():7} | {competitor_app_id}")
        fetch_app_history(platform, competitor_app_id, save_subdir="competitors")
        
        if idx < len(competitors) - 1:
            time.sleep(1)


def fetch_app_history(platform: str, app_id: str, save_subdir: Optional[str] = None) -> None:
    """
    Generic function to fetch metadata change history for any app (Android only).
    
    Only executes when platform == "android". For iOS, returns silently.
    
    Args:
        platform: "ios" or "android"
        app_id: The app ID (package name or iOS ID) to fetch history for
        save_subdir: Optional subdirectory name to save to (e.g., "competitors" or "our_app")
                     If None, saves to data/raw/ root.
    
    Saves:
        data/raw/{save_subdir}/{platform}_{app_id}_history.json
    """
    if platform.lower() == "ios":
        return
    
    client = AppTweakClient(API_KEY)
    
    # Determine save directory
    if save_subdir:
        save_dir = Path(config.DATA_RAW_DIR) / save_subdir
    else:
        save_dir = Path(config.DATA_RAW_DIR)
    
    save_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        params = {
            "apps": app_id,
            "country": config.COUNTRY,
            "language": config.LANGUAGE,
            "device": config.ANDROID_DEVICE,
            "start_date": config.START_DATE,
            "end_date": config.END_DATE,
        }
        
        response = client.get(config.APPTWEAK_HISTORY_ENDPOINT, params=params)
        
        output_file = save_dir / f"{platform}_{app_id}_history.json"
        with open(output_file, "w") as f:
            json.dump(response, f, indent=2)
        
        print(f"      → Saved to {output_file}")
        
    except Exception as e:
        print(f"  [ERROR] Failed to fetch history for {app_id}: {e}")
