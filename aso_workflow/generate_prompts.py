
import json
from pathlib import Path

processed_dir = Path("aso_workflow/data/processed")

# Load iOS data only for faster iteration
with open(processed_dir / "keyword_gaps_ios_547702041.json") as f:
    ios_data = json.load(f)

prompt = f"""Use the /keyword-gap-analysis and /aso-report-design skills to analyze this keyword gap data:

{json.dumps(ios_data, indent=2)}

Generate a single self-contained HTML report for iOS keyword gaps following all requirements from both skills.
Return ONLY the valid HTML file with no explanation.
"""

with open("track_a_analysis_prompt.txt", "w") as f:
    f.write(prompt)

print("✓ Track A analysis prompt generated")
