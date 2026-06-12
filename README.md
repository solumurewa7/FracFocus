# FracFocus Hydraulic Fracturing Analysis

Interactive dashboard analyzing 247,482 hydraulic fracturing disclosures (7.1 million chemical records) from the FracFocus Chemical Disclosure Registry, covering US frack jobs from 2011 to 2026.

**Live dashboard:** https://fracfocus.onrender.com

Built as a technical case study for Chirality Research: download the raw FracFocus data, store it in an appropriate database, run statistical analysis, visualize the results, and deploy them on a web dashboard.

## Key findings

- **Drilling activity tracks the oil market.** Jobs boomed from 14k/year in 2011 to a peak of about 29k in 2014 while oil sold above $100 a barrel, collapsed by more than half during the 2015-2016 price crash, partially recovered through 2019, cratered to 8.3k during COVID in 2020, and has settled at a steady 12-14k/year since 2021.
- **The typical frack job uses about 12x more water than it did in 2012.** Median water volume per job rose from roughly 1.7 million gallons in 2012-2013 to about 20 million gallons (roughly 30 Olympic pools) by 2025. The driver is the industry shift from vertical wells to horizontal wells with laterals of 2+ miles: longer wells crack more rock and need more water. Notably, water per job kept climbing straight through the 2015-2016 crash, so the technology trend was independent of the oil price. One modern job does the work of several 2012 jobs, which also explains why the job count fell over the same period.
- **About 71% of frack jobs include at least one chemical whose identity is withheld as a trade secret.** Of the 203,642 jobs with chemical records, 144,581 list at least one "Proprietary" ingredient. This is a floor: operators also write values like "Trade Secret" and "Confidential" in the CAS field, which are not counted here.
- **Fracking is geographically concentrated in a handful of basins.** Texas alone accounts for about 49% of all US jobs, and Texas plus New Mexico about 56%, dominated by the Permian Basin. The density map clearly resolves the major plays: the Permian (West Texas / SE New Mexico), the Eagle Ford crescent (South Texas), the Bakken (North Dakota), SCOOP/STACK (Oklahoma), the DJ Basin (Colorado), and the Marcellus (Pennsylvania / West Virginia).

## Architecture

```
FracFocus CSV download (3.3 GB, 15 files)
        |
   load_data.py        chunked ingestion (100k rows at a time) into SQLite
        |
 create_indexes.py     indexes built after the bulk load, not during it
        |
   build_jobs.py       deduplicated, type-cleaned one-row-per-job table
        |
   analysis scripts    SQL for filtering and aggregation, pandas for statistics
        |
  precompute.py        writes 4 small aggregate CSVs (about 100 KB total)
        |
  dashboard/app.py     Flask + Plotly dashboard, deployed on Render
```

The raw data (7.1 million ingredient-level rows) is loaded into SQLite in 100,000-row chunks, so memory usage stays flat regardless of file size. SQLite was chosen because the dataset is static, read-heavy, and single-user: a zero-configuration single-file database fits that exactly, and the standard SQL ports to Postgres if scaling were ever needed. All heavy computation happens locally against the 5 GB database; the deployed app ships only precomputed aggregates totaling about 100 KB, a roughly 50,000:1 reduction with no loss of insight. The database itself never leaves the laptop, which keeps the web app fast and the deploy under half a megabyte.

## Data decisions

- **Jobs are counted as distinct DisclosureId values, never as raw rows.** The data is one row per chemical per job (about 29 rows per job on average), so naive row counts overstate activity by an order of magnitude.
- **Bad dates are filtered at query time, not deleted.** Operator-entered dates include impossible values (the first row inspected claimed a 1955 frack job). Raw data stays intact; every query applies its own date window.
- **Water analysis uses a 90% coverage rule.** A year is included only if at least 90% of its jobs report a water volume. 2011 (about 4% coverage) and 2012 (about 35%, the FracFocus 1.0/2.0 format overlap) are excluded; 2013 onward is about 99%+. The rule makes exclusions principled instead of per-year judgment calls.
- **Medians over means.** The volume field contains physically implausible outliers (single jobs claiming 350-470 million gallons against a credible ceiling near 100 million), which inflate the mean. The median is robust to them.
- **Chemicals are grouped by CAS number, not by free-text name.** Operators spell the same chemical dozens of ways; the CAS registry number is the standardized identifier. Display names for the top chemicals are attached afterward from a verified lookup table.
- **Chemical percentages use an honest denominator.** Shares are computed against the 203,642 jobs that have at least one chemical record, since FracFocus 1.0-era disclosures (2011 to mid-2013) contain no chemical data at all. Validation: water appears in about 97% of jobs under this denominator, matching physical expectation.
- **Partial periods are handled per chart.** 2026 (data through June) is excluded from the jobs-per-year count, where a half year would fake a collapse, but kept in the water series, where a per-job median over six months of jobs is still valid.
- **Map coordinates are sanity-bounded.** Points are restricted to the continental US box (latitude 24-50, longitude -126 to -66), which removes coordinate entry errors. 247,074 of 247,482 jobs (99.84%) plot successfully.

## Repo structure

```
.                      analysis pipeline (run locally against the full data)
  peek.py              first look at the raw CSV header
  load_data.py         CSV -> SQLite chunked loader
  create_indexes.py    index creation
  build_jobs.py        cleaned one-row-per-job table
  explore.py           row counts, jobs per state, jobs per year
  jobs_analysis.py     jobs-per-year chart
  water_analysis.py    water volume statistics and chart
  map_analysis.py      density map with state borders
  chem_analysis.py     top chemicals by CAS number
  precompute.py        writes dashboard/data/*.csv
  us_states.json       state border coordinates for the map
  charts/              static matplotlib outputs
dashboard/             the deployable web app (Flask + Plotly + Render)
  app.py
  Procfile
  requirements.txt
  templates/index.html
  data/                precomputed aggregates (the only data that deploys)
```

## Running locally

The dashboard runs out of the box because the precomputed CSVs are committed:

```
pip install flask pandas plotly
python dashboard/app.py
```

Then open http://127.0.0.1:5000.

To rebuild the full pipeline from raw data:

1. Download the Oil and Gas CSV zip from https://fracfocus.org/data-download and unzip into `FracFocusCSV/` in the project root (about 3.3 GB, 15 registry files).
2. `pip install pandas matplotlib plotly flask`
3. Run in order: `load_data.py`, `create_indexes.py`, `build_jobs.py`, then `precompute.py`. The load takes 10-25 minutes and produces a local `fracfocus.db` of about 5 GB (gitignored, never deployed).
4. The standalone analysis scripts (`explore.py`, `water_analysis.py`, `map_analysis.py`, `chem_analysis.py`) can be run individually to reproduce the charts in `charts/`.
