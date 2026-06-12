import sqlite3
import pandas as pd

#NOTES
# 7,166,509 / 247,482 ~ 29 on average, each frack reports 29 ingredient rows

# 121,818 / 247,482 ~ 49% Texas Alone covers almost half of all fracking jobs in America. 
# If New mexico is included 17,165 / 247,482 ~ 7%,(a lot of it is the same Permian Basin that Martin County row came from) 
# then the total rises to about 56% of all jobs done by these two alone.

# q4 data: 
# 2010: 210 jobs. fracfocus launched in 2011 and ealry reports were voluntary. 
# 2011 - 2014: results boom from 14k to 29k jobs/year. Oil sold at over $100 a barrel 
# 2015 - 2016: prices crashed from $100 to $30 and US frackers couldnt make money. 
# 2017 - 2019: there is a partial recovery, with prices increasing to around $50 - $70 range. drilling never reached close to its peak, 28,945 jobs, in 2014. 
# 2020:  8,363 jobs. COVID year caused oil demand to vanish and prices to breifly go negative. drilling stopped. 
# 2021 - 2025: Recovered to a steady 12-14k per year, and the industry drills more carefully now. 
# 2026: Halfway through the year and is following consistent pattern from 2021 - 2025.




conn = sqlite3.connect("fracfocus.db")


q1 = "SELECT COUNT(*) FROM registry" #  counts every row in the registry table
q2 = "SELECT COUNT(DISTINCT DisclosureId) FROM registry" # counts unique DisclosureIds
# sort all rows into buckets. count unique jobs in each bucket. Order descending. renames the count column to jobs. only show the top 10
q3 = """
    SELECT StateName, COUNT(DISTINCT DisclosureId) AS jobs
    FROM registry
    GROUP BY StateName
    ORDER BY jobs DESC
    LIMIT 10
"""
# groups data based on the year. filters for years between 2010 and 2026.
q4 = """
    SELECT strftime('%Y', JobStartDate) AS year,
           COUNT(*) AS jobs
    FROM jobs
    WHERE JobStartDate BETWEEN '2010-01-01' AND '2026-12-31'
    GROUP BY year
    ORDER BY year
"""

print(pd.read_sql(q4, conn))
# print(pd.read_sql(q1, conn))
# print(pd.read_sql(q2, conn))
# print(pd.read_sql(q3, conn))

conn.close()

