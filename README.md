# Energy Forecast using Time-Series Foundation Model

This repository explores state-of-the-art zero-shot time series forecasting for energy demand using the **Chronos-2** foundation model. We compare univariate baselines with covariate-informed models that incorporate weather and calendar data to improve forecasting accuracy and reliability.

## 🚀 Key Features

- **Univariate Forecasting**: Baseline performance using the original Chronos model.
- **Covariate-Aware Forecasting**: Leveraging **Chronos-2**'s ability to ingest auxiliary variables (weather, holidays, day-of-week).
- **Lean Covariate Optimization**: A study on the impact of feature selection (Weather + Calendar) to improve model calibration and robustness.
- **Probabilistic Calibration**: Evaluation of 90% prediction intervals to ensure reliable uncertainty estimation.

## ⚙️ Experiment Configuration

- **Model**: `amazon/chronos-2`
- **Context Length**: 512 hours (historical lookback)
- **Forecast Horizon**: 24 hours (day-ahead forecasting)

## 🛰️ Data Sources & Preparation

To rigorously evaluate the model across distinct geographies and climates, we compiled hourly datasets for Dallas, Texas (cooling-dominated) and Toronto, Ontario (heating-dominated/mixed).

**Data Sources:**
- **Dallas Energy Demand**: Hourly ERCOT load data for the NCENT region downloaded from the [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Toronto Energy Demand**: Hourly IESO consumption data downloaded from [IESO Hourly Consumption](https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/). We aggregated the total demand for all Forward Sortation Areas (FSAs) starting with 'M' (Toronto) across all customer types.
- **Weather Data**: Hourly meteorological data (temperature, humidity, radiation, etc.) for both Dallas and Toronto sourced from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

**Data Preparation:**
- **Timestamp Alignment**: Both ERCOT and IESO report timestamps as "Hour Ending" (hours 1-24). We converted these to standard "Beginning of Hour" `timestamp` format by subtracting one hour to align seamlessly with Open-Meteo weather data.
- **Calendar Features**: Generated regional `day_of_week` and `is_holiday` variables (using Texas holidays for Dallas and Ontario holidays for Toronto).
- **Frequency Handling**: All merged datasets were strictly resampled to an hourly frequency with linear interpolation to handle Daylight Saving Time transitions or missing rows.

## 📊 Benchmark Results: Dallas, Texas (ERCOT)

Our experiments in Dallas compare the transition from univariate to covariate-aware forecasting across a mild spring month and an extreme summer load period.

### Winter/Spring (March 2026)
| Metric | Univariate | Full Covariates | Lean Covariates | Improvement (Lean vs Univ) |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 749.78 | **565.24** | 574.32 | 23.4% |
| **RMSE** | 1071.88 | 778.52 | **768.51** | 28.3% |
| **sMAPE (%)** | 5.36% | **4.14%** | 4.18% | 22.0% |
| **MASE** | 0.31 | **0.235** | 0.239 | 22.9% |
| **Coverage (90%)** | 85.89% | 87.10% | **87.23%** | +1.34% |

### Summer Extreme Load (August 2025)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 906.91 | **535.35** | 588.46 | 1584.17 |
| **RMSE** | 1422.20 | **753.09** | 785.56 | 2118.32 |
| **sMAPE (%)**| 4.55% | **2.77%** | 3.10% | 8.25% |
| **MASE** | 0.55 | **0.33** | 0.36 | 0.97 |
| **Coverage (90%)**| 76.48% | **86.69%** | 79.30% | N/A |

### Key Findings (Dallas)
1. **Massive Summer Error Reduction**: Providing weather covariates during the intense summer heat reduced absolute errors by **over 40%** (2.77% sMAPE). The univariate model fails to anticipate large AC-driven spikes.
2. **Restored Calibration**: The poor prediction interval coverage of the univariate model during extreme heat (76.48%) was completely fixed by adding full covariates (86.69%).
3. **Full vs. Lean Configurations**: In mild months (March), Lean covariates optimized calibration. However, in extreme weather months, the **Full Covariates model wins across all metrics**, demonstrating that comprehensive weather features (humidity, radiation) are necessary for accurate peak load anticipation.

## 🍁 Benchmark Results: Toronto, Ontario (IESO)

To prove geographic and climatic transferability, we tested the model zero-shot on the Toronto grid across both extreme heating (Winter) and cooling (Summer) seasons.

### Winter (February 2025)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 21549.75 | **16196.69** | 16245.41 | 45506.55 |
| **RMSE** | 28988.73 | **21099.33** | 21622.77 | 65669.01 |
| **sMAPE (%)**| 2.41% | **1.80%** | 1.80% | 5.24% |
| **MASE** | 0.31 | **0.23** | 0.23 | 0.66 |
| **Coverage (90%)**| 84.52% | 85.71% | **86.90%** | N/A |

### Summer (August 2025)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 52074.45 | **31497.49** | 33780.52 | 233703.66 |
| **RMSE** | 77963.33 | **43310.91** | 47170.08 | 282627.41 |
| **sMAPE (%)**| 5.33% | **3.40%** | 3.53% | 24.09% |
| **MASE** | 0.20 | **0.12** | 0.13 | 0.88 |
| **Coverage (90%)**| **89.92%** | 89.11% | **89.92%** | N/A |

### Key Findings (Toronto)
1. **Universal Transfer**: The model successfully generalized from Texas to Canada zero-shot. In Winter, adding weather covariates pushed the error down to a remarkable **1.80% sMAPE**.
2. **Extreme Volatility Resiliency**: During the Toronto summer, the Seasonal Naive baseline completely collapsed (24.09% error). Despite this massive week-over-week volatility, Chronos-2 maintained excellent accuracy (3.40% with covariates) and recognized the uncertainty, achieving near-perfect 89-90% interval coverage.

## 📁 Project Structure

```text
├── data/
│   ├── ercot/                             # Processed ERCOT Dallas data
│   ├── ieso/                              # Processed IESO Toronto data
│   └── */raw/                             # Original source files
├── notebooks/
│   ├── ercot-[type]-[year]-[season].ipynb # Dallas benchmark notebooks
│   └── ieso-[type]-[year]-[season].ipynb  # Toronto benchmark notebooks
└── src/
    └── prepare_forecast_data.py           # Data processing and feature engineering
```

## 📚 References

- **Chronos (2024)**: [Chronos: Learning the Language of Time Series](https://arxiv.org/abs/2403.05950) (Ansari et al.).
- **Chronos-2 (2025)**: [Chronos-2: From Univariate to Universal Forecasting](https://arxiv.org/abs/2510.15821) (Ansari et al.).
- **Energy Load Forecasting (2026)**: [Time Series Foundation Models for Energy Load Forecasting on Consumer Hardware: A Multi-Dimensional Zero-Shot Benchmark](https://arxiv.org/abs/2602.10848) (Luigi Simeone).
