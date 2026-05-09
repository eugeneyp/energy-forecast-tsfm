# Chronos-2 Notebook Summary

This document summarizes the end-to-end forecasting paths established in this project, outlining the purpose, data setup, and observed metrics across our benchmark experiments.

## 1. Baseline Example Notebooks

Before running full benchmarks, we established minimal smoke-test notebooks to verify the environment and the `amazon/chronos-2` model load path.

### `chronos-2-quickstart.ipynb`
- **Purpose**: Verify the local runtime can load the model and run a univariate forecast using the official `m4_hourly` sample series (`H1`).
- **Result**: Confirmed successful prediction and comparison against a Seasonal Naive baseline.

### `chronos-2-covariate-test.ipynb`
- **Purpose**: Verify the covariate-aware interface (`predict_df(..., future_df=...)`) using the official `electricity_price` dataset.
- **Result**: Successfully integrated future-known covariates and aligned them with ground truth.

---

## 2. Dallas, Texas Benchmarks (ERCOT)

**Data Preparation:**
- **Energy Source**: ERCOT Hourly Energy Demand (NCENT region) downloaded from [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Weather Source**: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for Dallas.
- **Processing**: Standardized "Hour Ending" to "Beginning of Hour", added Texas statutory holidays, and resampled to an hourly frequency.

### Winter/Spring (March 2026)
*Notebooks: `ercot-univariate-2026-winter.ipynb`, `ercot-covariate-2026-winter.ipynb`, `ercot-covariate-lean-2026-winter.ipynb`*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 749.78 | **565.24** | 574.32 | 1565.43 |
| **RMSE** | 1071.88 | 778.52 | **768.51** | 2020.57 |
| **sMAPE**| 5.36% | **4.14%** | 4.18% | 11.40% |
| **MASE** | 0.31 | **0.235** | 0.239 | 0.65 |
| **Coverage**| 85.89% | 87.10% | **87.23%** | N/A |

### Summer Extreme Load (August 2025)
*Notebooks: `ercot-univariate-2025-summer.ipynb`, `ercot-covariate-2025-summer.ipynb`, `ercot-covariate-lean-2025-summer.ipynb`*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 906.91 | **535.35** | 588.46 | 1584.17 |
| **RMSE** | 1422.20 | **753.09** | 785.56 | 2118.32 |
| **sMAPE**| 4.55% | **2.77%** | 3.10% | 8.25% |
| **MASE** | 0.55 | **0.33** | 0.36 | 0.97 |
| **Coverage**| 76.48% | **86.69%** | 79.30% | N/A |

**Analysis**: While Chronos-2 beats the baseline in a purely univariate setting, its uncertainty calibration suffers greatly (76.48%) during extreme summer months. Providing future-known covariates leads to a massive error reduction and restores probabilistic calibration. Extreme summer periods require **Full Covariates** to properly capture AC-driven demand spikes.

---

## 3. Toronto, Ontario Benchmarks (IESO)

**Data Preparation:**
- **Energy Source**: IESO Hourly Consumption downloaded from [IESO Public Reports](https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/). Aggregated all Forward Sortation Areas (FSAs) starting with 'M' (Toronto).
- **Weather Source**: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for Toronto.
- **Processing**: Converted "Hour Ending" (hours 1-24) to "Beginning of Hour" format, applied Ontario statutory holidays (`holidays.CA(prov='ON')`), and aligned with weather data.

### Winter (February 2025)
*Notebooks: `ieso-univariate-2025-winter.ipynb`, `ieso-covariate-2025-winter.ipynb`, `ieso-covariate-lean-2025-winter.ipynb`*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 21549.75 | **16196.69** | 16245.41 | 45506.55 |
| **RMSE** | 28988.73 | **21099.33** | 21622.77 | 65669.01 |
| **sMAPE**| 2.41% | **1.80%** | 1.80% | 5.24% |
| **MASE** | 0.31 | **0.23** | 0.23 | 0.66 |
| **Coverage**| 84.52% | 85.71% | **86.90%** | N/A |

### Summer (August 2025)
*Notebooks: `ieso-univariate-2025-summer.ipynb`, `ieso-covariate-2025-summer.ipynb`, `ieso-covariate-lean-2025-summer.ipynb`*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 52074.45 | **31497.49** | 33780.52 | 233703.66 |
| **RMSE** | 77963.33 | **43310.91** | 47170.08 | 282627.41 |
| **sMAPE**| 5.33% | **3.40%** | 3.53% | 24.09% |
| **MASE** | 0.20 | **0.12** | 0.13 | 0.88 |
| **Coverage**| **89.92%** | 89.11% | **89.92%** | N/A |

**Analysis**: Chronos-2 successfully transfers to a new geography without retraining. In winter, covariates drop the error to a remarkably low 1.80%. In summer, despite extreme volatility breaking the naive baseline entirely, the model maintains high accuracy and near-perfect interval calibration. Consistent with Dallas, the "Lean" configuration optimizes for calibration during stable months, while "Full" covariates provide the best point accuracy during volatile summer months.
