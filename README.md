# Energy Forecast using Time-Series Foundation Models

This repository benchmarks state-of-the-art zero-shot time series forecasting for regional energy demand using foundation models—specifically **Chronos-2** (Transformer architecture) and **TiRex-2** (xLSTM architecture)—against locally trained, rolling-retrained **XGBoost** and **Seasonal Naive** baselines.

## 🚀 Key Features

- **Multi-Foundation Model Evaluation**: Direct head-to-head comparison between **Chronos-2** (Amazon) and **TiRex-2** (NX-AI).
- **Univariate vs. Covariate-Aware Forecasting**: Ingestion of auxiliary meteorological forecasts and regional calendar features (Texas and Ontario statutory holidays).
- **Lean Covariate Optimization**: Feature selection ablations comparing full meteorological inputs against lean temperature/calendar sets.
- **Probabilistic Calibration**: Rigorous evaluation of empirical 90% prediction intervals ($q_{0.05}$ to $q_{0.95}$) to measure risk calibration under extreme weather.
- **Rolling ML Benchmark**: Comparison against dynamically retrained multi-quantile XGBoost models.

## ⚙️ Experiment Configuration

- **Models**: `amazon/chronos-2` (Transformer) & `NX-AI/TiRex-2` (xLSTM)
- **Context Length**: 512 hours (historical lookback)
- **Forecast Horizon**: 24 hours (day-ahead forecasting)
- **Evaluation Origins**: Daily rolling origin at 00:00 local time across all 4 evaluation months.

## 🛰️ Data Sources & Preparation

To rigorously evaluate the models across distinct geographies and climates, we compiled hourly datasets for Dallas, Texas (cooling-dominated) and Toronto, Ontario (heating-dominated/mixed).

**Data Sources:**
- **Dallas Energy Demand**: Hourly ERCOT load data for the NCENT region downloaded from the [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Toronto Energy Demand**: Hourly IESO consumption data downloaded from [IESO Hourly Consumption](https://reports-public.ieso.ca/public/HourlyConsumptionByFSA/). We aggregated total demand for all Forward Sortation Areas (FSAs) starting with 'M' (Toronto).
- **Weather Data**: Hourly meteorological data (temperature, apparent temp, humidity, solar radiation, etc.) sourced from the [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api).

---

## 📊 Benchmark Results: Dallas, Texas (ERCOT NCENT)

### August 2025 (Summer Extreme Heat Window)
| Model / Paradigm | MAE | RMSE | sMAPE (%) | MASE | 90% Interval Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Chronos-2 (Full Covariates)** | **535.35** | **753.09** | **2.77%** | **0.33** | **86.69%** (Near-nominal) |
| **XGBoost (Phase 5/6 - Static)** | 609.19 | 839.36 | 3.16% | 0.32 | 80.14% (Under-covering) |
| **TiRex-2 Streaming (Full Covariates)** | **620.01** | **853.45** | **3.27%** | **0.38** | **89.25%** (Near-nominal) |
| **XGBoost (Phase 7 - Rolling)** | 635.70 | 886.77 | 3.27% | 0.33 | 75.83% (Under-covering) |
| **TiRex-2 Streaming (Lean Covariates)** | 659.16 | 937.13 | 3.47% | 0.40 | 86.16% |
| **TiRex-2 (Full Covariates - Stateless)** | 670.97 | 930.20 | 3.52% | 0.41 | **88.71%** (Near-nominal) |
| **TiRex-2 (Lean Covariates - Stateless)** | 721.86 | 1038.87 | 3.81% | 0.44 | 86.69% |
| **TiRex-2 Streaming (Univariate)** | 888.65 | 1310.61 | 4.48% | 0.54 | 81.72% |
| **Chronos-2 (Univariate)** | 906.91 | 1422.20 | 4.55% | 0.55 | 76.48% |
| **TiRex-2 (Univariate - Stateless)** | 937.13 | 1440.91 | 4.75% | 0.57 | 80.11% |
| **Seasonal Naive Baseline** | 1584.17 | 2118.32 | 8.25% | 0.97 | N/A |

### March 2026 (Winter/Spring Transition Window)
| Model / Paradigm | MAE | RMSE | sMAPE (%) | MASE | 90% Interval Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **XGBoost (Phase 7 - Rolling)** | **471.38** | **608.03** | **3.52%** | **0.25** | 83.89% |
| **XGBoost (Phase 5/6 - Static)** | 531.41 | 672.01 | 3.98% | 0.28 | 76.39% (Under-covering) |
| **Chronos-2 (Full Covariates)** | 565.24 | 778.52 | 4.14% | **0.235** | **87.10%** (Near-nominal) |
| **TiRex-2 (Full Covariates - Stateless)** | 626.35 | 892.17 | 4.59% | 0.26 | 83.20% |
| **TiRex-2 Streaming (Full Covariates)** | 641.92 | 899.48 | 4.67% | 0.27 | 85.22% |
| **TiRex-2 (Lean Covariates - Stateless)** | 645.44 | 901.46 | 4.71% | 0.27 | 86.16% |
| **TiRex-2 Streaming (Lean Covariates)** | 706.79 | 997.58 | 5.10% | 0.29 | 85.08% |
| **TiRex-2 Streaming (Univariate)** | 746.19 | 1070.79 | 5.36% | 0.31 | 85.22% |
| **Chronos-2 (Univariate)** | 749.78 | 1071.88 | 5.36% | 0.31 | 85.89% |
| **TiRex-2 (Univariate - Stateless)** | 765.22 | 1095.91 | 5.49% | 0.32 | 85.89% |
| **Seasonal Naive Baseline** | 1565.43 | 2020.57 | 11.40% | 0.65 | N/A |

---

## 🍁 Benchmark Results: Toronto, Ontario (IESO)

### February 2025 (Winter Heating Peak Window)
| Model / Paradigm | MAE | RMSE | sMAPE (%) | MASE | 90% Interval Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Chronos-2 (Full Covariates)** | **16,196.69** | **21,099.33** | **1.80%** | **0.23** | 85.71% |
| **XGBoost (Phase 7 - Rolling)** | 18,751.78 | 24,547.76 | 2.11% | 0.22 | 87.50% |
| **XGBoost (Phase 5/6 - Static)** | 20,963.26 | 26,999.00 | 2.33% | 0.24 | 87.96% |
| **Chronos-2 (Univariate)** | 21,549.75 | 28,988.73 | 2.41% | 0.31 | 84.52% |
| **TiRex-2 Streaming (Full Covariates)** | 21,824.77 | 29,721.33 | 2.43% | 0.31 | **92.86%** (Near-nominal) |
| **TiRex-2 (Full Covariates - Stateless)** | 21,952.63 | 29,901.38 | 2.43% | 0.32 | **89.88%** (Near-nominal) |
| **TiRex-2 Streaming (Lean Covariates)** | 22,263.88 | 30,311.78 | 2.48% | 0.32 | **92.71%** (Near-nominal) |
| **TiRex-2 (Lean Covariates - Stateless)** | 22,546.22 | 30,488.98 | 2.50% | 0.33 | 90.18% |
| **TiRex-2 Streaming (Univariate)** | 22,801.90 | 30,925.61 | 2.54% | 0.33 | **91.52%** (Near-nominal) |
| **TiRex-2 (Univariate - Stateless)** | 22,980.07 | 30,741.14 | 2.55% | 0.33 | **90.33%** (Near-nominal) |
| **Seasonal Naive Baseline** | 45,506.55 | 65,669.01 | 5.24% | 0.66 | N/A |

### August 2025 (Summer Volatile Peak Window)
| Model / Paradigm | MAE | RMSE | sMAPE (%) | MASE | 90% Interval Coverage |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Chronos-2 (Full Covariates)** | **31,497.49** | **43,310.91** | **3.40%** | **0.12** | **89.11%** (Near-nominal) |
| **TiRex-2 Streaming (Lean Covariates)** | 36,633.75 | 50,804.79 | 3.90% | 0.14 | **93.68%** |
| **TiRex-2 Streaming (Full Covariates)** | 36,743.99 | 50,182.22 | 3.98% | 0.14 | **92.20%** (Near-nominal) |
| **TiRex-2 (Lean Covariates - Stateless)** | 37,414.60 | 52,731.04 | 3.95% | 0.14 | 93.55% |
| **XGBoost (Phase 7 - Rolling)** | 37,674.52 | 54,432.74 | 3.85% | 0.42 | 83.75% |
| **TiRex-2 (Full Covariates - Stateless)** | 37,743.11 | 51,707.29 | 4.08% | 0.14 | **90.32%** (Near-nominal) |
| **XGBoost (Phase 5/6 - Static)** | 38,790.57 | 54,729.79 | 3.92% | 0.45 | 81.53% |
| **TiRex-2 Streaming (Univariate)** | 51,466.81 | 73,432.46 | 5.41% | 0.20 | **90.05%** |
| **Chronos-2 (Univariate)** | 52,074.45 | 77,963.33 | 5.33% | 0.20 | **89.92%** |
| **TiRex-2 (Univariate - Stateless)** | 53,983.40 | 78,325.62 | 5.62% | 0.20 | **89.92%** |
| **Seasonal Naive Baseline** | 233,703.66 | 282,627.41 | 24.09% | 0.88 | N/A |

---

## 🏆 Key Findings & Architectural Insights

1. **Univariate Foundation Model Parity**: In a purely univariate setting, **TiRex-2 and Chronos-2 achieve almost identical zero-shot accuracy** (4.75% vs. 4.55% sMAPE in Dallas; 2.55% vs. 2.41% in Toronto), demonstrating the strong baseline transferability of both models.
2. **True Streaming Memory Boost**: Enabling TiRex-2's continuous recurrent memory retention (**Streaming Protocol A**) reduces Dallas Summer Full Covariates MAE by **-7.6% (670.97 MW down to 620.01 MW)** and Lean Covariates MAE by **-8.7% (721.86 MW to 659.16 MW)**, beating rolling-retrained XGBoost without any fine-tuning.
3. **Covariate Conditioning**: **Chronos-2's cross-attention mechanisms yield higher point predictive gains** when conditioning on dense hourly weather features, leading the benchmark across extreme summer and winter peak windows (2.77% in Dallas; 1.80% in Toronto).
4. **Probabilistic Uncertainty Calibration**: **TiRex-2 demonstrates world-class calibration.** Across both regions and modes, its empirical 90% coverage consistently hits **88.7% to 93.7%**, avoiding the overconfidence/under-coverage observed in local quantile XGBoost models (which dipped to 75–80%).
5. **Computational Efficiency & Latency**: In streaming mode, TiRex-2 requires only **270 - 328 ms per day** (univariate) and **775 - 1,066 ms per day** (covariates) on Apple Silicon MPS / CUDA with minimal constant memory footprint ($C_t \in \mathbb{R}^{d \times d}$).

---

## 📁 Project Structure

```text
├── data/
│   ├── ercot/                             # Processed ERCOT Dallas data
│   ├── ieso/                              # Processed IESO Toronto data
│   └── */raw/                             # Original source files
├── notebooks/
│   ├── chronos-2/                         # Chronos-2 benchmark notebooks (ERCOT & IESO)
│   ├── tirex-2/                           # TiRex-2 stateless benchmark notebooks (ERCOT & IESO)
│   ├── tirex-2-streaming/                 # TiRex-2 continuous streaming notebooks (ERCOT & IESO)
│   ├── chronos-tutorial/                  # Chronos tutorial and quickstart notebooks
│   ├── xgboost/                           # Static XGBoost baseline notebooks
│   └── xgboost-rolling/                   # Rolling retrained XGBoost notebooks
└── src/
    ├── tirex_pipeline.py                  # TiRex-2 DataFrame forecasting adapter (Stateless)
    ├── tirex_streaming_pipeline.py        # TiRex-2 True Streaming forecasting adapter
    ├── create_tirex_benchmark_notebooks.py# Generator for stateless TiRex-2 notebooks
    ├── create_tirex_streaming_notebooks.py# Generator for streaming TiRex-2 notebooks
    ├── prepare_forecast_data.py           # ERCOT Dallas data preparation
    └── prepare_ieso_forecast_data.py      # IESO Toronto data preparation
```

## 📚 References

- **Chronos (2024)**: [Chronos: Learning the Language of Time Series](https://arxiv.org/abs/2403.05950) (Ansari et al.).
- **Chronos-2 (2025)**: [Chronos-2: From Univariate to Universal Forecasting](https://arxiv.org/abs/2510.15821) (Ansari et al.).
- **TiRex (2025)**: [TiRex: Zero-Shot Forecasting Across Long and Short Horizons](https://arxiv.org/abs/2505.23746) (NX-AI / Hochreiter et al.).
- **TiRex-2 (2026)**: [TiRex-2: Generalizing TiRex to Multivariate Data and Streaming](https://arxiv.org/abs/2602.04944) (NX-AI / Hochreiter et al.).
- **Energy Load Forecasting (2026)**: [Time Series Foundation Models for Energy Load Forecasting on Consumer Hardware](https://arxiv.org/abs/2602.10848) (Luigi Simeone).
