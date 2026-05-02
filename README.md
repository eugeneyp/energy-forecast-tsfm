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

## 📁 Project Structure

```text
├── data/ercot/
│   ├── ercot_dallas_univariate_2026.csv   # Target energy demand series
│   ├── ercot_dallas_covariate_2026.csv    # Target + Weather/Calendar features
│   └── raw/                               # Original ERCOT and Open-Meteo files
├── notebooks/
│   ├── ercot-chronos-univariate.ipynb     # Univariate benchmark
│   ├── ercot-chronos-covariate.ipynb      # Full covariate experiment
│   └── ercot-chronos-covariate-lean.ipynb # Optimized lean covariate experiment
└── src/
    └── prepare_forecast_data.py           # Data processing and feature engineering
```

## 🛰️ Data Sources

- **ERCOT Hourly Data**: Hourly energy demand specifically for the **Dallas region**, downloaded from the [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Historical Weather Data**: Sourced from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for the Dallas region.

## 📚 References

- **Chronos (2024)**: [Chronos: Learning the Language of Time Series](https://arxiv.org/abs/2403.05950) (Ansari et al.).
- **Chronos-2 (2026)**: [Chronos-2: Multi-dataset Pre-training for Time Series Forecasting](https://arxiv.org/pdf/2602.10848) (Amazon Research).
- **Universal Forecasting**: [ArXiv: 2602.10848](https://arxiv.org/pdf/2602.10848) — Introducing the Group Attention Mechanism for zero-shot covariate integration.
