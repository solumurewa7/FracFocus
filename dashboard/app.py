from pathlib import Path
import pandas as pd
import plotly.express as px
from flask import Flask, render_template

# NOTES
# matplotlib renders static PNGs. 
# Plotly generates client-side JavaScript, so the charts are interactive in the browser without extra work.

app = Flask(__name__) # creates the application object
DATA = Path(__file__).parent / "data"

@app.route("/")
def home():
    jobs = pd.read_csv(DATA / "jobs_per_year.csv")
    wti = {2011: 95, 2012: 94, 2013: 98, 2014: 93, 2015: 49, 2016: 43, 2017: 51,
        2018: 65, 2019: 57, 2020: 39, 2021: 68, 2022: 95, 2023: 78, 2024: 77, 2025: 66}
    jobs["wti"] = jobs["year"].map(wti)
    fig = px.bar(jobs, x="year", y="jobs", title="Frack Jobs per Year vs Oil Price",
                labels={"jobs": "Jobs", "year": "Year"})
    fig.add_scatter(x=jobs["year"], y=jobs["wti"], yaxis="y2", mode="lines+markers",
                    name="WTI avg $/barrel", line=dict(color="#f59e0b", width=3))
    fig.update_layout(height=420, margin=dict(t=50, l=10, r=10, b=10),
                    yaxis2=dict(title="WTI $/barrel", overlaying="y", side="right"),
                    showlegend=False)
    jobs_chart = fig.to_html(full_html=False, include_plotlyjs="cdn") # converts figure to chunk of HTML + Javascipt.

    water = pd.read_csv(DATA / "water_per_year.csv")
    fig = px.line(water, x="year", y=["Median", "Mean"], markers=True, title="Water Volume per Job: Median vs Mean",
              labels={"value": "Million gallons", "year": "Year", "variable": ""})
    fig.update_layout(height=420, margin=dict(t=50, l=10, r=10, b=10))
    water_chart = fig.to_html(full_html=False, include_plotlyjs=False)

    chem = pd.read_csv(DATA / "top_chemicals.csv")
    fig = px.bar(chem, x="pct", y="chemical", orientation="h",title="Most Common Ingredients (% of jobs with chemical data)", labels={"pct": "% of Jobs", "chemical": ""})
    fig.update_yaxes(autorange="reversed")
    colors = ["#6366f1"] * len(chem)
    for i, name in enumerate(chem["chemical"]):
        if name == "Water":
            colors[i] = "#0ea5e9"
        if "Proprietary" in str(name):
            colors[i] = "#f59e0b"
    fig.update_traces(marker_color=colors)
    fig.update_layout(height=420, margin=dict(t=50, l=10, r=10, b=10))
    chem_chart = fig.to_html(full_html=False, include_plotlyjs=False)

    grid = pd.read_csv(DATA / "map_grid.csv")
    fig = px.density_mapbox(grid, lat="lat", lon="lon", z="jobs", radius=6, zoom=3.5, center={"lat": 38, "lon": -97},mapbox_style="open-street-map", 
                            title="Frack Job Density")
    fig.update_layout(height=550, margin=dict(t=50, l=10, r=10, b=10))
    map_chart = fig.to_html(full_html=False, include_plotlyjs=False)
    return render_template("index.html", jobs_chart=jobs_chart, water_chart=water_chart, chem_chart=chem_chart, map_chart=map_chart) #  loads the template and fills in its blanks.

if __name__ == "__main__":
    app.run(debug=True) # development only to show errors in browser