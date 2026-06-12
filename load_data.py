import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect("fracfocus.db")
files = sorted(Path("FracFocusCSV").glob("FracFocusRegistry_*.csv"))

for file in files:
    for chunk in pd.read_csv(file, chunksize=100_000, low_memory=False):
        chunk.to_sql("registry", conn, if_exists="append", index=False)
    print(f"Completed: {file.name}")

conn.close()
