"""
ASO Workflow — App Store Optimization Analysis Pipeline

A modular pipeline for competitive intelligence in App Store Optimization (ASO).
Identifies optimization opportunities through keyword gap analysis and A/B testing intelligence.

Main Modules:
    config: Central configuration for app IDs, API keys, and parameters
    fetchers: Data retrieval from AppTweak API (metadata, rankings, history)
    transformers: Data transformation (keyword gaps, A/B test resolution)

Entry Points:
    run_fetcher.py: Steps 1-3 (metadata & competitor fetching)
    run_track_a.py: Step 4 (keyword gap analysis)
    run_track_b.py: Step 5 (A/B test intelligence)
"""
