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
    fig = px.bar(jobs, x="year", y="jobs", title="Frack Jobs per Year") # plotly creates bar chart
    fig.update_layout(height=420, margin=dict(t=50, l=10, r=10, b=10))
    jobs_chart = fig.to_html(full_html=False, include_plotlyjs="cdn") # converts figure to chunk of HTML + Javascipt.

    water = pd.read_csv(DATA / "water_per_year.csv")
    fig = px.line(water, x="year", y="median_mgal", markers=True, title="Median Water Volume per Job", labels={"median_mgal": "Million gallons", "year": "Year"})
    fig.update_layout(height=420, margin=dict(t=50, l=10, r=10, b=10))
    water_chart = fig.to_html(full_html=False, include_plotlyjs=False)

    chem = pd.read_csv(DATA / "top_chemicals.csv")
    fig = px.bar(chem, x="pct", y="chemical", orientation="h",title="Most Common Ingredients (% of jobs with chemical data)", labels={"pct": "% of Jobs", "chemical": ""})
    fig.update_yaxes(autorange="reversed")
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