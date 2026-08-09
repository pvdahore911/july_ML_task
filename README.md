# CND Subsystem — July Task: Telemetry and Data Foundation

**Name:** _[your name here]_
**Station:** Bhubaneswar (IGRA ID `INM00042971`, WMO 42971)
**Data source:** [NOAA Integrated Global Radiosonde Archive (IGRA)](https://www.ncei.noaa.gov/pub/data/igra/data/data-por/)

## Overview

This repository contains my submission for the CND subsystem's July onboarding task. It covers:

- **Task 1 — Pipeline Orchestration and Data Sanitization** (compulsory) — Levels 1–3
- **Task 3 — Telemetry Intelligence and Modeling** (Track B, ML) — Levels 1–3

Task 2 (web dashboard, Track A) was not attempted.

## Repository Contents

| File | Description |
|---|---|
| `task1_pipeline.ipynb` | Task 1, Levels 1–3: parses the raw fixed-width IGRA file, cleans it, extracts required stats/plot, refactors into a reusable function, and parallelizes + serializes the pipeline to Parquet. |
| `parallel_utils.py` | Worker module for Task 1 / Level 3. Kept as a separate `.py` file (not inline in the notebook) because `ProcessPoolExecutor` needs to pickle the function it sends to each worker process — unreliable for functions defined inside a notebook cell, especially on Windows. |
| `task3_ml.ipynb` | Task 3, Levels 1–3: rolling z-score anomaly detection, a pressure→altitude regression model, and KMeans clustering to discover the troposphere/stratosphere boundary without altitude labels. |
| `altitude_vs_temperature.png` | Output plot from Task 1 / Level 1. |
| `anomaly_detection.png`, `regression_pred_vs_actual.png`, `kmeans_clusters.png` | Output plots from Task 3. |
| `README.md` | This file. |

## Setup / How to Run

1. Download the station data file from NOAA:
   `https://www.ncei.noaa.gov/pub/data/igra/data/data-por/INM00042971-data.txt.zip`
   Unzip it so `INM00042971-data.txt` sits in the same folder as the notebooks.
   I have also uploaded those data files in the same repository.

2. Install dependencies:
   ```
   pip install pandas numpy matplotlib scikit-learn pyarrow
   ```

3. Run `task1_pipeline.ipynb` top to bottom. This produces `bhubaneswar_cleaned.parquet` (used by Task 3) and the Level 1 plot.

4. Run `task3_ml.ipynb` top to bottom. It automatically loads `bhubaneswar_cleaned.parquet` if present, or falls back to re-parsing the raw file.

## Approach Notes

- **Missing values:** IGRA marks missing readings as `-9999`/`-8888`. These are converted to `NaN` (exclusion strategy) rather than interpolated, since interpolating atmospheric readings across large altitude gaps can misrepresent the actual profile.
- **Single-flight stats:** The raw file contains 50,000+ soundings spanning 1971–2026, so Task 1's required stats (max altitude, temperature variance, pressure delta) are computed on one representative, data-dense recent flight rather than the whole archive, since those metrics only make physical sense per-flight.
- **Parallelization approach:** Since only one station file was provided, "multiple historical telemetry logs" is implemented by splitting the multi-decade record into year-range chunks and parsing/cleaning each chunk in a separate process via `ProcessPoolExecutor`, then concatenating and serializing to Parquet.
- **Regression feature choice:** Task 3 / Level 2 regresses altitude on `log(pressure)` rather than raw pressure, since pressure falls off roughly exponentially with altitude (the barometric formula) — this tracks the true physics far better than a plain linear fit.
