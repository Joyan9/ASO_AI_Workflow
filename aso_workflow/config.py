"""
ASO Workflow Configuration

Simple, swappable config for app IDs, platform, country, and API settings.
"""

from datetime import datetime, timedelta

# App IDs for iOS and Android
iOS_APP_ID = "547702041"
ANDROID_APP_ID = "com.tinder"

# Core parameters
COUNTRY = "us"
LANGUAGE = "us"

# Device types
iOS_DEVICE = "iphone"
ANDROID_DEVICE = "android"

# History window: last 90 days
HISTORY_WINDOW_DAYS = 90
START_DATE = (datetime.now() - timedelta(days=HISTORY_WINDOW_DAYS)).strftime("%Y-%m-%d")
END_DATE = datetime.now().strftime("%Y-%m-%d")

# API settings
APPTWEAK_BASE_URL = "https://public-api.apptweak.com"
APPTWEAK_METADATA_ENDPOINT = "api/public/store/apps/metadata.json"

# File paths - for storing raw data
DATA_RAW_DIR = "data/raw"

# Processing settings
TOP_COMPETITORS = 10
PRIMARY_TIER_COUNT = 3
