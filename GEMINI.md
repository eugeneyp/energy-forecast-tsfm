# Gemini AI Agent Instructions: Energy Forecast TSFM

This file contains project-specific conventions, architecture notes, and workflows to guide AI agents working in this repository.

## Project Overview
This repository benchmarks zero-shot time-series foundation models (specifically `amazon/chronos-2`) for regional energy demand forecasting. It compares purely univariate forecasts against covariate-aware forecasts (weather + calendar features) under various seasonal conditions.

## Repository Structure
- `data/<operator_or_region>/raw/`: Raw energy and weather datasets (Excel, CSV).
- `data/<operator_or_region>/`: Processed, model-ready CSVs (e.g., `ercot_dallas_univariate_2025_summer.csv`, `ercot_dallas_covariate_2025_summer.csv`).
- `notebooks/`: Jupyter notebooks for running experiments and visualizing results.
- `src/`: Python scripts for data preparation and feature engineering.
- `docs/`: Markdown summaries and benchmark tracking.

## Data Engineering Conventions
- **Time Standard**: All data must use a `timestamp` column. Standardize to "Beginning of Hour" (e.g., if source data uses "Hour Ending", subtract 1 hour. "24:00" should map to "00:00" of the next day).
- **Frequency Handling**: Always robustly resample data to hourly frequency (`.resample("h").mean().interpolate()`) to safely handle missing rows or Daylight Saving Time shifts.
- **Target Variable**: The primary energy demand column should be renamed to `target` inside the evaluation notebooks.
- **Calendar Features**: Automatically generate `day_of_week` (0-6) and `is_holiday` (0/1) using the `holidays` Python package tailored to the specific region.

## Forecasting & Evaluation Standards
- **Model Interface**: `amazon/chronos-2` via `BaseChronosPipeline`. Use `predict_df(..., future_df=...)` for covariates.
- **Windowing**: `context_length = 512` (hours), `prediction_length = 24` (Day-ahead forecast).
- **Baseline**: Always compare Chronos-2 against a Seasonal Naive baseline using a 1-week lookback (`seasonal_period = 168`).
- **Metrics**: Calculate and report exactly these metrics: `MAE`, `RMSE`, `sMAPE (%)`, `MASE`, and `Empirical Coverage (90% Interval)`.

## 🚀 Future Context: Toronto, Ontario Benchmark
The next phase of the project extends this benchmark to Toronto, Ontario. 
**Key adjustments required for the Ontario phase:**
- **Directory Structure**: Create and use `data/ieso/` (or `data/ontario/`) and `data/ieso/raw/` for the new region.
- **Holidays Context**: Update the holiday generation logic in the data preparation script to use Canadian/Ontario holidays: `holidays.CA(prov='ON')`.
- **Notebook Templating**: Duplicate the existing `ercot` notebook templates, adjusting data paths, region names in titles/charts (e.g., "IESO Toronto Energy Demand"), and markdown analysis text.
- **Environment**: Always execute Python scripts and notebooks using the project's virtual environment (e.g., `.venv/bin/python3`) so that `pandas`, `holidays`, and `chronos` dependencies resolve correctly.