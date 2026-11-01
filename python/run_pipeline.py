"""
RUN THE WHOLE PIPELINE
----------------------
Runs steps 01 -> 04 in order. Use this after you add or delete rows
in data/raw/*.csv, then click Refresh in Power BI.

Run (from the project folder):  python python/run_pipeline.py
"""

import runpy
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))   # so each step can "import config"
STEPS = [
    "step01_load_and_explore.py",
    "step02_clean.py",
    "step03_load_to_sql.py",
    "step04_analysis.py",
]

for step in STEPS:
    print("\n" + "=" * 70)
    print(f"RUNNING {step}")
    print("=" * 70)
    runpy.run_path(str(HERE / step), run_name="__main__")

print("\nPipeline finished. Now open Power BI and click Home -> Refresh.")
