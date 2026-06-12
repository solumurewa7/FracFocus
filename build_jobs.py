import sqlite3
import pandas as pd

conn = sqlite3.connect("fracfocus.db")

# returns rows with exact duplicates collapsed into one. We calculated each job header repeats 29 times, so we only return unique ones.
q = """
    SELECT DISTINCT
        DisclosureId, JobStartDate, JobEndDate,
        StateName, CountyName, OperatorName, WellName,
        Latitude, Longitude, TVD, TotalBaseWaterVolume
    FROM registry
"""

# safety net to enssure no duplicates if job header rows werent perfectly identical. 
# forces one row per distinct DisclosureId.
df = pd.read_sql(q, conn)
df = df.drop_duplicates(subset="DisclosureId")

# parse text to real dates. adds saftey net for if date is unparsable to simpley reurn "NaT". returns date only, removes time.
df["JobStartDate"] = pd.to_datetime(df["JobStartDate"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce").dt.date
df["JobEndDate"] = pd.to_datetime(df["JobEndDate"], format="%m/%d/%Y %I:%M:%S %p", errors="coerce").dt.date

for column in ["Latitude", "Longitude", "TVD", "TotalBaseWaterVolume"]:
    df[column] = pd.to_numeric(df[column], errors="coerce") # parsed text to floats. adds saftey net for if number is unparsable to simpley reurn "NaN"

df.to_sql("jobs", conn, if_exists="replace", index=False)

print(f"{len(df)} jobs written")
conn.close()
