import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#NOTES

# Coverage rule for water analysis: include only years where >=90% of jobs report water volume.

# 2011 (~4%) and 2012 (~35%, FF 1.0/2.0 format overlap period Nov 2012-May 2013) excluded. 2013+ all ~99%+. 
# Rule chosen so exclusions are principled, not per-year judgment calls.

# In 2011 there were 14,329 jobs, but only 616 have water number filled. 
# WHY: early FracFocus reporting was voluntary and the old 1.0 format barely captured this data. 
# median only represents typical job among 4% who reported, which dosent represent everyone

# 2011 (~4%) and 2012 (~35%, FF 1.0/2.0 format overlap period Nov 2012-May 2013) excluded. 2013+ all ~99%+. 
# Rule chosen so exclusions are principled, not per-year judgment calls.

# Median over time increased by about 12x from 2012 to 2025
# WHY: wells went from vertical to horizontal(2+ miles). Longer well = more rock cracked = more water.
# One modern job does the work of several 2012 jobs. explains why job count fell at the same time.

# Gap beterrn mean and Median is modest(10 - 20%) meaning data isnt wildly corrupted

# Max column for years like 2016 and 2019, show data entries with gallon values at 472 million gallons in 2016, 350M in 2019. 
# The largest credible job runs maybe up to ~ 100M. Values 4x that are almost certainly data entry error

# the growth may finally be leveling off, though 2026 is a partial year

# despite job counts crash in 2015-2016, water per job kept rising right through the crash. 
# signifies technology trend didn't care about the oil price.

conn = sqlite3.connect("fracfocus.db")

# filters years from 2012 - 2026. selected 2012 due to reason stated in notes above. 
# excluded jobs with missing or zero water volume.
q = """
    SELECT strftime('%Y', JobStartDate) AS year,
           TotalBaseWaterVolume AS gallons
    FROM jobs
    WHERE JobStartDate BETWEEN '2013-01-01' AND '2026-12-31'
      AND TotalBaseWaterVolume IS NOT NULL
      AND TotalBaseWaterVolume > 0
"""
df = pd.read_sql(q, conn)

# groups data by year, and returns gallons. computes all four stats per bucket in one shot
summary = df.groupby("year")["gallons"].agg(["count", "median", "mean", "max"])

print(summary)

summary = summary.reset_index()
summary["median_mgal"] = summary["median"] / 1_000_000

plt.figure(figsize=(10, 5))
plt.plot(summary["year"], summary["median_mgal"], marker="o")
plt.title("Median Water Volume per Frack Job")
plt.xlabel("Year")
plt.ylabel("Million gallons")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("charts/water_per_job.png", dpi=150)
plt.show()