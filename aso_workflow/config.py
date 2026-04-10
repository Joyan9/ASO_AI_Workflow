"""
ASO Workflow Configuration

Simple, swappable config for app IDs, platform, country, and API settings.
"""

from datetime import datetime, timedelta
from pathlib import Path

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
APPTWEAK_TOP_CHARTS_ENDPOINT = "api/public/store/charts/top-results/current.json"
APPTWEAK_HISTORY_ENDPOINT = "api/public/store/apps/metadata/changes.json"

# This gets the directory where config.py lives (aso_workflow/)
BASE_DIR = Path(__file__).resolve().parent

# File paths - for storing raw data
DATA_RAW_DIR = BASE_DIR / "data" / "raw"
DATA_PROCESSED_DIR = BASE_DIR / "data" / "processed"

# Processing settings
TOP_COMPETITORS = 10
PRIMARY_TIER_COUNT = 3

# Keyword ranking settings
KEYWORD_RANKINGS_DRY_RUN = False  # Safety flag: set to False only after reviewing cost estimate
MAX_KEYWORD_LLM_FILTER = 2000 # Max number of keywords to send to LLM for filtering (to control costs)
MAX_SEED_KEYWORDS = 200  # Cap on number of seed keywords to fetch rankings for
KEYWORD_RANKINGS_ENDPOINT = "api/public/store/apps/keywords-rankings/current.json"
KEYWORD_RANKINGS_METRICS = "rank,relevancy,kei,chance"
CREDIT_PER_APP_KEYWORD_METRIC = 10  # Each app/keyword/metric combo costs 10 credits

# Keyword metrics settings
KEYWORD_METRICS_ENDPOINT = "api/public/store/keywords/metrics/current.json"
MIN_VOLUME_THRESHOLD = 6  # Minimum search volume for gap keyword filtering
