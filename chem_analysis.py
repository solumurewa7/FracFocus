import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

# NOTES

# 203,642 jobs with chemical data

# "Proprietary" appears in 144,581 jobs ~71%.
# ~71% of jobs include at least one ingredient whose identity is legally hidden as a trade secret.
# ~71% is a floor.  Operators also write "Trade Secret", "Confidential", etc. in the CAS field.

# Chemical % denominator = jobs with >=1 chemical record, Filters on the actual condition instead of a date proxy.
# effect: water rose to ~high-90s%, matching physical expectation.


conn = sqlite3.connect("fracfocus.db")

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

# per CAS bucket, finds how many distinct frack jobs does the chemical appears at least once. 
# filters out NULL and empty('') text in registry
q = """
    SELECT CASNumber, COUNT(DISTINCT DisclosureId) AS jobs
    FROM registry
    WHERE CASNumber IS NOT NULL AND CASNumber != ''
    GROUP BY CASNumber
    ORDER BY jobs DESC
    LIMIT 15
"""

# ensures jobs have at least one chemical row in the data.
denom_q = """
    SELECT COUNT(DISTINCT DisclosureId) AS n
    FROM registry
    WHERE CASNumber IS NOT NULL AND CASNumber != ''
"""

denom = pd.read_sql(denom_q, conn)["n"][0]
print(f"{denom} jobs with chemical data")

summary = pd.read_sql(q, conn)
summary["chemical"] = summary["CASNumber"].map(cas_names)
summary["pct"] = summary["jobs"] / denom * 100

plt.figure(figsize=(10, 5))
plt.barh(summary["chemical"], summary["pct"])
plt.gca().invert_yaxis()
plt.title("Most common ingredients in US frack jobs, 2011-2026")
plt.xlabel("Percentage of frack jobs appeared in")
plt.ylabel("")
plt.grid(True, axis="x", alpha=0.3)
plt.tight_layout()
plt.savefig("charts/chemicals_per_job.png", dpi=150)
plt.show()

conn.close()