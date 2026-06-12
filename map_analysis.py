import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import json

#NOTES:
# selected lattitude and longtitude between Latitude BETWEEN 24 AND 50 and Longitude BETWEEN -126 AND -66 
# so that it only shows data that is recorded for the United States rougly. 
# Everything outside is either garbage or the small number of Alaska jobs.

# plotting without any mapping libraries by using matplot and latitude/longitude pairs.
# the data draws the United States by itself.

# 247k dots on one chart means dots stack on dots and you get a solid blob.
# made dots tiny and nearly transparent, so data stacks transparency into a dark, dense blob. 
# creates a plot similar to a heat map.

#  247,074 of 247,482 plotted. only ~ 400 jobs (0.16%) had unusable coordinates.

# BASIN GUIDE:
# (-103, 48) Bakken, North Dakota: nearly all 18.5k ND jobs in one tight blob
# (-102, 32) Permian Basin, W Texas + SE New Mexico: densest US oil field; our Martin County row lives here
# (-99, 28.5) Eagle Ford, S Texas: crescent shape literally traces the underground rock formation
# (-97.5, 35.5) SCOOP/STACK plays, Oklahoma
# (-92.5, 35.5) Fayetteville shale, Arkansas
# (-80 to -76, 40-42) Marcellus shale, PA/WV: gas rather than oil
# (-104.8, 40) DJ Basin, Colorado: basically Weld County, most of CO's 22k jobs
# (-119, 35.5) Kern County, California: the lonely west coast blob

conn = sqlite3.connect("fracfocus.db")


q = """
    SELECT Latitude, Longitude
    FROM jobs
    WHERE Latitude BETWEEN 24 AND 50
      AND Longitude BETWEEN -126 AND -66
"""

df = pd.read_sql(q, conn)
print(f"{len(df)} plottable jobs")

plt.figure(figsize=(11, 7))

# GeoJSON gotten from internt list one feature per state, which each has a geometry( coordinates at border points)
with open("us_states.json") as f:
    states = json.load(f)

for feature in states["features"]:
    geom = feature["geometry"]
    # most states are one polygon. but states with islands are MultiPolygon, which is a list of polygons. 
    # line normalizes both cases into the same shape so one loop handles everything. 
    polys = [geom["coordinates"]] if geom["type"] == "Polygon" else geom["coordinates"]
    for poly in polys:
        for ring in poly:
            # split points into x's and y's and draw them as tiny grey lines.
            xs = [point[0] for point in ring]
            ys = [point[1] for point in ring]
            plt.plot(xs, ys, color="gray", linewidth=0.4)

#excludes Alaska and Hawaii which GeoJSON would otherwise include.
plt.xlim(-126, -66)
plt.ylim(24, 50)

# color by the logarithm of the count. a dark-to-bright colormap, dense areas glow. leaves truly empty cells blank instead of coloring them as zero
plt.hexbin(df["Longitude"], df["Latitude"], gridsize=140, bins="log", cmap="inferno", mincnt=1) 
plt.colorbar(label="jobs per cell (log scale)")
plt.gca().set_aspect(1.3) # At US latitudes, one degree of longitude is physically shorter than one degree of latitude.1.3 ≈ the right squeeze factor for ~37°N
plt.title("Frack Job Density, 2011 - 2026")
plt.xlabel("Longitude")
plt.ylabel("Latitude")
plt.tight_layout()
plt.savefig("charts/job_map.png", dpi=150)
plt.show()