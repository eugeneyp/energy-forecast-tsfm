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
- **Evaluation Period**: March 2026

## 📊 Benchmark Results (March 2026)

Our experiments on the March 2026 evaluation period demonstrate significant improvements when transitioning from univariate to covariate-aware forecasting.

| Metric | Univariate | Full Covariates | Lean Covariates | Improvement (Lean vs Univ) |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 749.78 | **565.24** | 574.32 | 23.4% |
| **RMSE** | 1071.88 | 778.52 | **768.51** | 28.3% |
| **sMAPE (%)** | 5.36% | **4.14%** | 4.18% | 22.0% |
| **MASE** | 0.31 | **0.235** | 0.239 | 22.9% |
| **Coverage (90%)** | 85.89% | 87.10% | **87.23%** | +1.34% |

### Key Findings
1. **Full Covariates** provide the best absolute point accuracy (MAE/sMAPE).
2. **Lean Covariates** (Apparent Temperature, Day of Week, Holiday, Cloud Cover) achieve the best **RMSE** and **Calibration**, reducing large outliers and providing more reliable uncertainty intervals.
3. Both covariate configurations outperform the univariate baseline by over **20%** across all major metrics.



## 📊 Benchmark Results (Summer 2025: Extreme Load)

To validate the model under extreme conditions, we evaluated August 2025 during the intense Texas summer heat, comparing the models against a Seasonal Naive (7d) baseline.

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive | Improvement (Full vs Univ) |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **MAE** | 906.91 | **535.35** | 588.46 | 1584.17 | 40.9% |
| **RMSE** | 1422.20 | **753.09** | 785.56 | 2118.32 | 47.0% |
| **sMAPE (%)**| 4.55% | **2.77%** | 3.10% | 8.25% | 39.1% |
| **MASE** | 0.55 | **0.33** | 0.36 | 0.97 | 40.0% |
| **Coverage (90%)**| 76.48% | **86.69%** | 79.30% | N/A | +10.21% |

### Key Findings (Summer 2025)
1. **Massive Error Reduction**: Unlike the milder spring evaluation, providing weather covariates during the summer heat reduced absolute errors by **over 40%**. The univariate model fails to anticipate large AC-driven spikes.
2. **Restored Calibration**: The poor prediction interval coverage of the univariate model (76.48%) was completely fixed by adding covariates, jumping to a much healthier **86.69%**.
3. **Full vs. Lean Configurations**: In extreme weather months, stripping away variables like Humidity and Shortwave Radiation negatively impacts the model. The **Full Covariates model wins across all metrics** during summer, demonstrating that comprehensive weather features are necessary for accurate peak load anticipation.



## 🍁 Benchmark Results (Toronto: Universal Generalization)

To prove geographic transferability, we tested the model zero-shot on the Independent Electricity System Operator (IESO) grid in Toronto, Ontario across both extreme heating (Winter) and cooling (Summer) seasons.

### Winter 2025 (February)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 21549.75 | **16196.69** | 16245.41 | 45506.55 |
| **RMSE** | 28988.73 | **21099.33** | 21622.77 | 65669.01 |
| **sMAPE (%)**| 2.41% | **1.80%** | 1.80% | 5.24% |
| **MASE** | 0.31 | **0.23** | 0.23 | 0.66 |
| **Coverage**| 84.52% | 85.71% | **86.90%** | N/A |

### Summer 2025 (August)
| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | :--- | :--- | :--- | :--- |
| **MAE** | 52074.45 | **31497.49** | 33780.52 | 233703.66 |
| **RMSE** | 77963.33 | **43310.91** | 47170.08 | 282627.41 |
| **sMAPE (%)**| 5.33% | **3.40%** | 3.53% | 24.09% |
| **MASE** | 0.20 | **0.12** | 0.13 | 0.88 |
| **Coverage**| **89.92%** | 89.11% | **89.92%** | N/A |

### Key Findings (Toronto)
1. **Universal Transfer**: The model successfully generalized from Texas to Canada zero-shot. In Winter, weather covariates pushed the error down to a remarkable **1.80% sMAPE**.
2. **Extreme Volatility Resiliency**: During the Toronto summer, the Seasonal Naive baseline completely collapsed (24.09% error). Despite this massive week-over-week volatility, Chronos-2 maintained excellent accuracy (3.40% with covariates) and recognized the uncertainty, achieving near-perfect 89-90% interval coverage.

## 📁 Project Structure

```text
├── data/ercot/
│   ├── ercot_dallas_univariate_2026.csv   # Target energy demand series
│   ├── ercot_dallas_covariate_2026.csv    # Target + Weather/Calendar features
│   └── raw/                               # Original ERCOT and Open-Meteo files
├── notebooks/
│   ├── ercot-univariate-2026-winter.ipynb     # Univariate benchmark
│   ├── ercot-covariate-2026-winter.ipynb      # Full covariate experiment
│   └── ercot-covariate-lean-2026-winter.ipynb # Optimized lean covariate experiment
└── src/
    └── prepare_forecast_data.py           # Data processing and feature engineering
```

## 🛰️ Data Sources

- **ERCOT Hourly Data**: Hourly energy demand specifically for the **Dallas region**, downloaded from the [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Historical Weather Data**: Sourced from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for the Dallas region.

## 📚 References

- **Chronos (2024)**: [Chronos: Learning the Language of Time Series](https://arxiv.org/abs/2403.05950) (Ansari et al.).
- **Chronos-2 (2025)**: [Chronos-2: From Univariate to Universal Forecasting](https://arxiv.org/abs/2510.15821) (Ansari et al.).
- **Energy Load Forecasting (2026)**: [Time Series Foundation Models for Energy Load Forecasting on Consumer Hardware: A Multi-Dimensional Zero-Shot Benchmark](https://arxiv.org/abs/2602.10848) (Luigi Simeone).
