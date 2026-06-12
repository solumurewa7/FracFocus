# separated heavy analysis from the serving layer. stays fast no matter how big raw data grows

import sqlite3
import pandas as pd
from pathlib import Path

conn = sqlite3.connect("fracfocus.db")
out = Path("dashboard/data")
out.mkdir(parents=True, exist_ok=True)

#NOTES
# summarized a 5 GB database into less than a tenth of a megabyte, a ~50,000x reduction with zero loss of insight.


# 1. Jobs per year (2011-2025, partial 2026 excluded)
jobs_q = """
    SELECT strftime('%Y', JobStartDate) AS year, COUNT(*) AS jobs
    FROM jobs
    WHERE JobStartDate BETWEEN '2011-01-01' AND '2025-12-31'
    GROUP BY year ORDER BY year
"""
pd.read_sql(jobs_q, conn).to_csv(out / "jobs_per_year.csv", index=False)


# 2. Median water per job per year (2013+, coverage rule)
water_q = """
    SELECT strftime('%Y', JobStartDate) AS year, TotalBaseWaterVolume AS gallons
    FROM jobs
    WHERE JobStartDate BETWEEN '2013-01-01' AND '2026-12-31'
      AND TotalBaseWaterVolume IS NOT NULL AND TotalBaseWaterVolume > 0
"""
water = pd.read_sql(water_q, conn)
water_summary = water.groupby("year")["gallons"].median().reset_index()
water_summary["median_mgal"] = water_summary["gallons"] / 1_000_000
water_summary[["year", "median_mgal"]].to_csv(out / "water_per_year.csv", index=False)


# 3. Map, aggregated to a grid
map_q = """
    SELECT Latitude, Longitude FROM jobs
    WHERE Latitude BETWEEN 24 AND 50 AND Longitude BETWEEN -126 AND -66
"""
coords = pd.read_sql(map_q, conn)
coords["lat"] = coords["Latitude"].round(1)
coords["lon"] = coords["Longitude"].round(1)
grid = coords.groupby(["lat", "lon"]).size().reset_index(name="jobs")
grid.to_csv(out / "map_grid.csv", index=False)


# 4. Top chemicals (denominator = jobs with chemical data)

chem_q = """
    SELECT CASNumber, COUNT(DISTINCT DisclosureId) AS jobs
    FROM registry
    WHERE CASNumber IS NOT NULL AND CASNumber != ''
    GROUP BY CASNumber
    ORDER BY jobs DESC
    LIMIT 15
"""

denom_q = """
    SELECT COUNT(DISTINCT DisclosureId) AS n
    FROM registry
    WHERE CASNumber IS NOT NULL AND CASNumber != ''
"""
cas_names = {
    "7732-18-5": "Water",
    "14808-60-7": "Crystalline silica (sand)",
    "64742-47-8": "Petroleum distillates (carrier fluid)",
    "7647-01-0": "Hydrochloric acid",
    "Proprietary": "Trade secret / undisclosed",
    "67-56-1": "Methanol",
    "67-63-0": "Isopropanol",
    "107-21-1": "Ethylene glycol",
    "7647-14-5": "Sodium chloride (salt)",
    "111-30-8": "Glutaraldehyde (biocide)",
    "64-17-5": "Ethanol",
    "9000-30-0": "Guar gum (thickener)",
    "64-19-7": "Acetic acid (vinegar acid)",
    "1310-73-2": "Sodium hydroxide (lye)",
    "7727-54-0": "Ammonium persulfate",
}

denom = pd.read_sql(denom_q, conn)["n"][0]

chem = pd.read_sql(chem_q, conn)
chem["chemical"] = chem["CASNumber"].map(cas_names)
chem["pct"] = chem["jobs"] / denom * 100
chem[["chemical", "pct"]].to_csv(out / "top_chemicals.csv", index=False)

print("jobs_per_year:", len(pd.read_csv(out / "jobs_per_year.csv")), "rows")
print("water_per_year:", len(pd.read_csv(out / "water_per_year.csv")), "rows")
print("map_grid:", len(pd.read_csv(out / "map_grid.csv")), "rows")
print("top_chemicals:", len(pd.read_csv(out / "top_chemicals.csv")), "rows")
conn.close()