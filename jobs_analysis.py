import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

#NOTES
# 2026 excluded from jobs-per-year chart: year is only half complete (data through June). misleading
# Represented data in Bar chart because each year is a discrete count and bars emphasize comparing individual years
# line implies a continuous quantity flowing between points, which is not the case here

conn = sqlite3.connect("fracfocus.db")

# filters years from 2011 - 2026.
q = """
    SELECT strftime('%Y', JobStartDate) AS year,
        COUNT(*) AS jobs
    FROM jobs
    WHERE JobStartDate BETWEEN '2011-01-01' AND '2025-12-31'
    GROUP BY year
    ORDER BY year
"""

summary = pd.read_sql(q, conn)

print(summary)

summary["jobs_th"] = summary["jobs"] / 1_000


plt.figure(figsize=(10, 5))
plt.bar(summary["year"], summary["jobs_th"])
plt.title("Frack Jobs per year")
plt.xlabel("Year")
plt.ylabel("Thousand Frack Jobs")
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig("charts/jobs_per_year.png", dpi=150)
plt.show()