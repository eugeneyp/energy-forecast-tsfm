# Chronos-2 Notebook Summary

This repo currently has two Chronos-2 baseline notebooks in `notebooks/`. Together they establish the first working end-to-end forecasting path for the project: a minimal target-only smoke test and a minimal covariate-aware smoke test.

## 1. `chronos-2-quickstart.ipynb`

Purpose:

- Establish the first operational Chronos-2 baseline in the repo.
- Verify the notebook is attached to the repo `.venv`.
- Confirm the local runtime can load `amazon/chronos-2` and run a forecast end to end.
- Keep the first example small by using one official sample series only.

Data and setup:

- Dataset: official `m4_hourly` sample used by the Chronos quickstart flow.
- Series used: `H1`.
- Forecast horizon: `24` hourly steps.
- Model API: `BaseChronosPipeline.from_pretrained(...)` with `Chronos2Pipeline.predict_df(...)`.
- Device behavior: detects `cuda`, then `mps`, then falls back to `cpu`.

Evaluation and outputs:

- Metrics: `MAE`, `RMSE`, `sMAPE`, `MASE`.
- Baseline: seasonal naive with period `24`.
- Saved notebook output shows the model loaded successfully on `mps` in the current environment.

Observed metrics from the saved notebook output:

| Metric | Chronos-2 | Seasonal Naive 24h |
| --- | ---: | ---: |
| MAE | 13.082306 | 33.500000 |
| RMSE | 18.979121 | 38.955102 |
| sMAPE | 1.841935 | 4.952257 |
| MASE | 0.308754 | 0.790629 |

What it proves:

- The repo environment and Chronos-2 model load path work.
- The long-format dataframe prediction flow works for a single series.
- The project has a small, repeatable, non-energy-specific baseline to compare against later notebooks.

## 2. `chronos-2-covariate-test.ipynb`

Purpose:

- Extend the first notebook into the smallest practical Chronos-2 covariate smoke test.
- Exercise the `future_df` interface that distinguishes Chronos-2 from older target-only workflows.
- Use an official energy-related dataset so the baseline is closer to the repo domain.

Data and setup:

- Dataset: official `electricity_price` Chronos covariate example.
- Train parquet:
  `https://autogluon.s3.amazonaws.com/datasets/timeseries/electricity_price/train.parquet`
- Test parquet:
  `https://autogluon.s3.amazonaws.com/datasets/timeseries/electricity_price/test.parquet`
- Series selection: first sorted `id`, which resolves to `DE` in the current sample.
- Forecast horizon: `24` hourly steps.
- Context data: full available training history for the selected series.
- Future-known covariates supplied through `future_df`:
  `Ampirion Load Forecast` and `PV+Wind Forecast`.

Evaluation and outputs:

- Metrics: `MAE`, `RMSE`, `sMAPE`, `MASE`.
- Baseline: seasonal naive with period `24`.
- Validation behavior:
  - requires exactly `24` forecast rows,
  - merges predictions with ground truth on `id` and `timestamp`,
  - raises an error if any merged `actual` values are missing.
- Visualization:
  - last `7 * 24` context points when available,
  - actual future values,
  - Chronos-2 point forecast,
  - `0.1` to `0.9` prediction interval.

Observed metrics from the saved notebook output:

| Metric | Chronos-2 | Seasonal Naive 24h |
| --- | ---: | ---: |
| MAE | 2.456532 | 11.605000 |
| RMSE | 2.886212 | 15.526155 |
| sMAPE | 8.860987 | 28.878798 |
| MASE | 0.288825 | 1.364449 |

What it proves:

- Chronos-2 covariate forecasting works in this repo through `predict_df(..., future_df=...)`.
- The official energy-related sample loads successfully and aligns cleanly with ground truth.
- The single-series covariate baseline stays small and fast while still testing the main Chronos-2-specific path.

## Shared Conventions Across Both Notebooks

- Both notebooks assume the repo `.venv` is already set up from `requirements.txt`.
- Both notebooks include explicit environment and kernel guidance for VS Code and Jupyter.
- Both notebooks standardize around the same metric set:
  `MAE`, `RMSE`, `sMAPE`, `MASE`.
- Both notebooks explain why `sMAPE` is preferred over plain `MAPE`.
- Both notebooks compare Chronos-2 against a `24`-hour seasonal naive baseline.
- Both notebooks are intentionally single-series and small enough to serve as smoke tests rather than benchmarks.

## Current State

The repo now has:

- a first operational Chronos-2 quickstart notebook,
- a second Chronos-2 covariate notebook using an official energy dataset,
- saved outputs in the covariate notebook,
- a consistent baseline structure that can be scaled later to larger energy forecasting experiments.

## Likely Next Steps

1. Add a multi-series benchmark notebook using the same long-format dataframe interface.
2. Compare target-only and covariate-aware Chronos-2 runs on the same energy split.
3. Add repeatable backtesting instead of a single holdout horizon.
4. Standardize runtime logging and result collection across notebooks.
