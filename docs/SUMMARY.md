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


## 3. `ercot-chronos-univariate-2025-summer.ipynb` & `ercot-chronos-covariate-2025-summer.ipynb`

Purpose:

- Evaluate Chronos-2 on real-world extreme energy demand data (ERCOT Dallas, August 2025).
- Compare zero-shot forecasting performance between purely univariate inputs and covariate-aware inputs (weather + calendar) during high-volatility summer periods.
- Understand the impact of using a subset of "Lean" covariates vs "Full" covariates on prediction interval calibration.

Data and setup:

- Dataset: ERCOT Hourly Energy Demand (NCENT region) joined with Open-Meteo weather features.
- Context window: June 1, 2025 to start of prediction day (`512` hours max).
- Forecast horizon: `24` hourly steps (Day-ahead).
- Evaluation period: `31` days in August 2025.
- Baseline: Seasonal Naive with a `168` hour (7-day) period.

Observed metrics (August 2025 Average):

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| --- | ---: | ---: | ---: | ---: |
| MAE | 906.91 | 535.35 | 588.46 | 1584.17 |
| RMSE | 1422.20 | 753.09 | 785.56 | 2118.32 |
| sMAPE | 4.55% | 2.77% | 3.10% | 8.25% |
| MASE | 0.55 | 0.33 | 0.36 | 0.97 |
| Coverage (90%) | 76.48% | 86.69% | 79.30% | N/A |

What it proves:

- While Chronos-2 can beat the Seasonal Naive baseline in a purely univariate setting, its uncertainty calibration suffers greatly (76.48% coverage) during extreme weather months.
- Providing future-known covariates (like temperatures and holidays) leads to a **massive >40% error reduction** in MAE/RMSE and restores probabilistic calibration (86.69% coverage).
- Unlike milder months (e.g., March) where a "Lean" subset of features can outperform a full set, extreme summer periods require **Full Covariates** (including humidity and shortwave radiation) to properly capture AC-driven demand spikes.


## 4. `ieso-chronos-univariate` & `ieso-chronos-covariate` (Toronto, ON)

Purpose:

- Evaluate the geographical and climatic transferability of Chronos-2 by running the exact same benchmarks on the Independent Electricity System Operator (IESO) grid in Toronto, Ontario.
- Stress-test the model against both Winter (heating) and Summer (cooling) peak periods.

Data and setup:

- Dataset: IESO Hourly Energy Demand (aggregated FSAs starting with 'M') joined with Open-Meteo weather features. Ontario holidays ('holidays.CA(prov="ON")') used for calendar features.
- Context window: `512` hours max.
- Forecast horizon: `24` hourly steps (Day-ahead).
- Evaluation period: February 2025 (Winter) and August 2025 (Summer).
- Baseline: Seasonal Naive with a `168` hour (7-day) period.

### Winter 2025 (February)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| --- | ---: | ---: | ---: | ---: |
| MAE | 21549.75 | 16196.69 | 16245.41 | 45506.55 |
| RMSE | 28988.73 | 21099.33 | 21622.77 | 65669.01 |
| sMAPE | 2.41% | 1.80% | 1.80% | 5.24% |
| MASE | 0.31 | 0.23 | 0.23 | 0.66 |
| Coverage (90%) | 84.52% | 85.71% | 86.90% | N/A |

### Summer 2025 (August)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| --- | ---: | ---: | ---: | ---: |
| MAE | 52074.45 | 31497.49 | 33780.52 | 233703.66 |
| RMSE | 77963.33 | 43310.91 | 47170.08 | 282627.41 |
| sMAPE | 5.33% | 3.40% | 3.53% | 24.09% |
| MASE | 0.20 | 0.12 | 0.13 | 0.88 |
| Coverage (90%) | 89.92% | 89.11% | 89.92% | N/A |

What it proves:

- **Universal Generalization**: The foundation model successfully generalized to a completely different grid operator and climate profile without any fine-tuning.
- **Winter Accuracy**: Using weather covariates dropped the sMAPE to an incredible **1.80%** during the winter heating season.
- **Extreme Volatility Handling**: During the Toronto summer, the Seasonal Naive baseline completely collapsed (24% error). Despite this massive volatility, Chronos-2 maintained an impressive 5.33% error univariate, and dropped to **3.40%** when given full weather covariates, all while achieving near-perfect 89-90% interval coverage.
