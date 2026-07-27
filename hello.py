"""DSO-576 setup test. Run with:  uv run hello.py

If your setup is working you'll see a small table and a success message.
"""
import sys

import pandas as pd

df = pd.DataFrame(
    {"tool": ["Python", "uv", "pandas"], "status": ["works", "works", "works"]}
)
print(df.to_string(index=False))
print()
print(f"SUCCESS — Python {sys.version.split()[0]} and pandas {pd.__version__} are working.")
print("Your Python setup is good to go.")
