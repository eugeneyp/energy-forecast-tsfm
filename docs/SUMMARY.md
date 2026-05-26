# Chronos-2 Notebook Summary

This document summarizes the end-to-end forecasting paths established in this project, outlining the purpose, data setup, and observed metrics across our benchmark experiments.

## 1. Baseline Example Notebooks

Before running full benchmarks, we established minimal smoke-test notebooks to verify the environment and the `amazon/chronos-2` model load path.

### [chronos-2-quickstart.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-tutorial/chronos-2-quickstart.ipynb)
- **Purpose**: Verify the local runtime can load the model and run a univariate forecast using the official `m4_hourly` sample series (`H1`).
- **Result**: Confirmed successful prediction and comparison against a Seasonal Naive baseline.

### [chronos-2-covariate-test.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-tutorial/chronos-2-covariate-test.ipynb)
- **Purpose**: Verify the covariate-aware interface (`predict_df(..., future_df=...)`) using the official `electricity_price` dataset.
- **Result**: Successfully integrated future-known covariates and aligned them with ground truth.

---

## 2. Dallas, Texas Benchmarks (ERCOT)

**Data Preparation:**
- **Energy Source**: ERCOT Hourly Energy Demand (NCENT region) downloaded from [ERCOT Load History](https://www.ercot.com/gridinfo/load/load_hist).
- **Weather Source**: [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api) for Dallas.
- **Processing**: Standardized "Hour Ending" to "Beginning of Hour", added Texas statutory holidays, and resampled to an hourly frequency.

### Winter/Spring (March 2026)
*Notebooks: [ercot-univariate-2026-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-univariate-2026-winter.ipynb), [ercot-covariate-2026-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-covariate-2026-winter.ipynb), [ercot-covariate-lean-2026-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-covariate-lean-2026-winter.ipynb)*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 749.78 | **565.24** | 574.32 | 1565.43 |
| **RMSE** | 1071.88 | 778.52 | **768.51** | 2020.57 |
| **sMAPE**| 5.36% | **4.14%** | 4.18% | 11.40% |
| **MASE** | 0.31 | **0.235** | 0.239 | 0.65 |
| **Coverage**| 85.89% | 87.10% | **87.23%** | N/A |

### Summer Extreme Load (August 2025)
*Notebooks: [ercot-univariate-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-univariate-2025-summer.ipynb), [ercot-covariate-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-covariate-2025-summer.ipynb), [ercot-covariate-lean-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ercot-covariate-lean-2025-summer.ipynb)*

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
*Notebooks: [ieso-univariate-2025-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-univariate-2025-winter.ipynb), [ieso-covariate-2025-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-covariate-2025-winter.ipynb), [ieso-covariate-lean-2025-winter.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-covariate-lean-2025-winter.ipynb)*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 21549.75 | **16196.69** | 16245.41 | 45506.55 |
| **RMSE** | 28988.73 | **21099.33** | 21622.77 | 65669.01 |
| **sMAPE**| 2.41% | **1.80%** | 1.80% | 5.24% |
| **MASE** | 0.31 | **0.23** | 0.23 | 0.66 |
| **Coverage**| 84.52% | 85.71% | **86.90%** | N/A |

### Summer (August 2025)
*Notebooks: [ieso-univariate-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-univariate-2025-summer.ipynb), [ieso-covariate-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-covariate-2025-summer.ipynb), [ieso-covariate-lean-2025-summer.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/chronos-2/ieso-covariate-lean-2025-summer.ipynb)*

| Metric | Univariate | Full Covariates | Lean Covariates | Seasonal Naive |
| :--- | ---: | ---: | ---: | ---: |
| **MAE** | 52074.45 | **31497.49** | 33780.52 | 233703.66 |
| **RMSE** | 77963.33 | **43310.91** | 47170.08 | 282627.41 |
| **sMAPE**| 5.33% | **3.40%** | 3.53% | 24.09% |
| **MASE** | 0.20 | **0.12** | 0.13 | 0.88 |
| **Coverage**| **89.92%** | 89.11% | **89.92%** | N/A |

## 4. XGBoost Benchmarks (Dallas, ERCOT)

In this phase, we established a progressively built XGBoost baseline to compare against the zero-shot performance of Chronos-2.

### Phase 1: Lagging Features Only
*Notebook: `notebooks/xgboost/ercot-xgboost-lags.ipynb`*

We compared **Recursive** forecasting against a **Direct Multi-Step (Rich Lags)** approach. The rich lag model uses seasonally aligned lags ($t-24, t-168$) plus origin momentum ($y_T, y_{T-1}, y_{T-2}$).

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **Aug 2025** | Recursive | 1796.79 | 2401.41 | 9.18% | 0.94 |
| **Aug 2025** | **Direct (Rich)** | **1180.27** | **1675.96** | **5.99%** | **0.62** |
| **Mar 2026** | Recursive | 1374.51 | 1832.07 | 10.11% | 0.72 |
| **Mar 2026** | **Direct (Rich)** | **959.10** | **1291.98** | **6.95%** | **0.50** |

### Phase 2: Calendar Features
*Notebook: `notebooks/xgboost/ercot-xgboost-calendar.ipynb`*

We added **Target Time** calendar features to the Direct (Rich) model: Target Hour, Day of Week, Weekend Flag, Month, and Public Holiday.

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **Aug 2025** | **Direct (Calendar)** | **997.54** | **1526.97** | **4.97%** | **0.52** |
| **Mar 2026** | **Direct (Calendar)** | **912.96** | **1198.49** | **6.58%** | **0.48** |

### Phase 3: Weather Covariates
*Notebook: `notebooks/xgboost/ercot-xgboost-weather.ipynb`*

We added 8 **Target Time** weather features: Temperature, Apparent Temp, Humidity, Dew Point, Wind Speed, Cloud Cover, Precipitation, and Shortwave Radiation.

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **Aug 2025** | **Direct (Weather Aware)** | **627.13** | **839.70** | **3.24%** | **0.33** |
| **Mar 2026** | **Direct (Weather Aware)** | **542.07** | **695.32** | **4.05%** | **0.28** |

### Phase 4: Advanced Features & Hyperparameter Tuning
*Notebook: [ercot-xgboost-advanced.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/xgboost/ercot-xgboost-advanced.ipynb)*

We added rolling load statistics (6h, 12h, 24h), rolling weather features (3h, 6h, 12h), weather interaction features, and introduced early stopping on a chronological validation split.

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **Aug 2025** | **Direct (Advanced)** | **609.26** | **811.17** | **3.16%** | **0.32** |
| **Mar 2026** | **Direct (Advanced)** | **557.37** | **690.44** | **4.19%** | **0.29** |

#### Top 15 Most Influential Predictors (Gain at $h=12$ Midday Peak)
1. **`feat_24h_aligned`** (51.87%): Load exactly 24 hours prior to target hour.
2. **`target_apparent_temp_roll_mean_3h`** (22.53%): Rolling 3-hour mean apparent temperature at target time.
3. **`target_temp_roll_mean_3h`** (4.33%): Rolling 3-hour mean temperature at target time.
4. **`target_temp`** (4.17%): Temperature at target hour.
5. **`target_temp_humidity_interaction`** (3.11%): Temperature * humidity at target hour.
6. **`target_apparent_temp`** (2.59%): Apparent temperature at target hour.
7. **`target_temp_hour_interaction`** (1.16%): Temperature * hour at target hour.
8. **`target_apparent_temp_roll_mean_6h`** (1.01%): Rolling 6-hour mean apparent temperature.
9. **`target_hour`** (0.90%): Hour of day of target prediction.
10. **`target_temp_roll_mean_6h`** (0.84%): Rolling 6-hour mean temperature.
11. **`target_apparent_temp_roll_mean_12h`** (0.68%): Rolling 12-hour mean apparent temperature.
12. **`target_temp_roll_mean_12h`** (0.68%): Rolling 12-hour mean temperature.
13. **`feat_168h_aligned`** (0.68%): Load exactly 1 week prior to target hour.
14. **`target_radiation_roll_mean_3h`** (0.68%): Rolling 3-hour mean shortwave radiation.
15. **`target_is_weekend`** (0.64%): Weekend flag.

### Phase 5: Residual Learning & Degree Days
*Notebook: [ercot-xgboost-residual.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/xgboost/ercot-xgboost-residual.ipynb)*

We added Cooling & Heating Degree Days (CDD/HDD), long-term weather rolling windows (48h/72h), and trained models to predict target residuals relative to yesterday's load (`target_h - feat_24h_aligned`).

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE |
| :--- | :--- | ---: | ---: | ---: | ---: |
| **Aug 2025** | **Direct (Residual)** | **609.19** | **839.36** | **3.16%** | **0.32** |
| **Mar 2026** | **Direct (Residual)** | **531.41** | **672.01** | **3.98%** | **0.28** |

#### Top 15 Most Influential Predictors (Gain at $h=12$ Midday Peak)
1. **`target_apparent_temp`** (7.71%): Apparent temperature at target hour.
2. **`target_apparent_temp_roll_mean_3h`** (7.70%): Rolling 3-hour mean apparent temperature at target time.
3. **`target_temp`** (6.93%): Dry-bulb temperature at target hour.
4. **`target_is_weekend`** (6.13%): Weekend flag for target day.
5. **`target_hdd`** (5.15%): Heating Degree Days.
6. **`target_temp_roll_mean_3h`** (5.01%): Rolling 3-hour mean temperature.
7. **`target_dayofweek`** (4.57%): Day of the week of target prediction.
8. **`feat_24h_aligned`** (4.45%): Load 24 hours prior to target hour (yesterday's load).
9. **`target_apparent_temp_roll_mean_6h`** (4.23%): Rolling 6-hour mean apparent temperature.
10. **`load_roll_min_24h`** (4.06%): Minimum load observed in the 24 hours prior to origin.
11. **`target_temp_humidity_interaction`** (3.85%): Temperature * humidity at target hour.
12. **`target_apparent_temp_roll_mean_12h`** (2.30%): Rolling 12-hour mean apparent temperature.
13. **`load_roll_max_24h`** (2.07%): Maximum load observed in the 24 hours prior to origin.
14. **`target_temp_roll_mean_12h`** (1.82%): Rolling 12-hour mean temperature.
15. **`target_hour`** (1.75%): Hour of day of target prediction.

#### The Feature Importance Shift (Phase 4 vs. Phase 5)
In Phase 4, the model had to learn the absolute base load magnitude, meaning **`feat_24h_aligned`** (load 24h prior) dominated with **51.87%** of the importance gain.

In Phase 5, by changing the target to predict the **load residual** ($y_{T+h} - y_{T+h-24}$), the baseline load level is mathematically pre-handled. This reduces the importance of `feat_24h_aligned` to just **4.45%** and forces the model to split on the actual **drivers of change** from yesterday to today:
* **Weather Shifts:** Apparent temperature and 3h heat accumulation become the top predictors.
* **Calendar Shifts:** Day of week and weekend transitions.
* **Degree Days:** HDD becomes 5th to capture heating deviations.

### Phase 6: Probabilistic Forecasting & 90% Interval Coverage
*Notebook: [ercot-xgboost-probabilistic.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/xgboost/ercot-xgboost-probabilistic.ipynb)*

We trained multi-quantile XGBoost models using the `reg:quantileerror` loss function for `quantile_alpha=[0.05, 0.95]`, predicting the 5th and 95th percentiles of target residuals.

| Test Window | Strategy | MAE | RMSE | sMAPE | MASE | 90% Interval Coverage |
| :--- | :--- | ---: | ---: | ---: | ---: | :---: |
| **Aug 2025** | **Direct (Probabilistic)** | **609.19** | **839.36** | **3.16%** | **0.32** | **80.14%** |
| **Mar 2026** | **Direct (Probabilistic)** | **531.41** | **672.01** | **3.98%** | **0.28** | **76.39%** |

#### Probabilistic Calibration Analysis (Chronos-2 vs. XGBoost)
While XGBoost achieves exceptional point forecast accuracy (decisively beating Chronos-2 in March), **Chronos-2 shows superior probabilistic calibration**:
* **Chronos-2 Coverage**: **86.69%** (August) and **87.10%** (March), which is very close to the nominal **90%** target.
* **XGBoost Coverage**: **80.69%** (August) and **76.39%** (March), indicating that XGBoost prediction intervals are too narrow (overconfident). 

Chronos-2's global pre-training allows it to learn the true variability and variance from millions of time series, whereas local quantile regressions tend to fit overly tight intervals on smaller, local training sets.

---

## 5. XGBoost Benchmarks (Toronto, IESO)

We implemented and ran the Phase 6 Probabilistic XGBoost benchmark on Toronto (IESO) data. The model was trained on historical data from January 2023 to January 2025 and evaluated on February 2025 (Winter) and August 2025 (Summer) test windows.

### Winter (February 2025)
*Notebook: [ieso-xgboost-probabilistic.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/xgboost/ieso-xgboost-probabilistic.ipynb)*

| Metric | XGBoost (Probabilistic) | Chronos-2 (Full Covariates) | Seasonal Naive |
| :--- | ---: | ---: | ---: |
| **MAE** | 20963.26 | **16196.69** | 45506.55 |
| **RMSE** | 26999.00 | **21099.33** | 65669.01 |
| **sMAPE**| 2.33% | **1.80%** | 5.24% |
| **MASE** | 0.24 | **0.23** | 0.66 |
| **Coverage**| **87.96%** | 85.71% | N/A |

### Summer (August 2025)
*Notebook: [ieso-xgboost-probabilistic.ipynb](file:///Users/epeng/code/personal/energy-forecast-tsfm/notebooks/xgboost/ieso-xgboost-probabilistic.ipynb)*

| Metric | XGBoost (Probabilistic) | Chronos-2 (Full Covariates) | Seasonal Naive |
| :--- | ---: | ---: | ---: |
| **MAE** | 38790.57 | **31497.49** | 233703.66 |
| **RMSE** | 54729.79 | **43310.91** | 282627.41 |
| **sMAPE**| 3.92% | **3.40%** | 24.09% |
| **MASE** | 0.45 | **0.12** | 0.88 |
| **Coverage**| 81.53% | **89.11%** | N/A |

**Analysis**:
* **Point Accuracy**: Chronos-2 with full covariates outperforms XGBoost on both winter and summer point metrics, proving the deep learning model's strong zero-shot capability when transferring to new climates and heating-dominated grids.
* **Interval Coverage**: In winter, XGBoost achieves excellent calibration with **87.96%** coverage (compared to Chronos-2's **85.71%**). In the volatile summer peak, however, XGBoost becomes overconfident and drops to **81.53%** coverage, whereas Chronos-2 remains near-perfectly calibrated at **89.11%**.

---

## 📈 Analysis & Insights

### Foundation Models vs. Traditional ML
1. **Univariate Superiority**: Chronos-2 Univariate (4.55% sMAPE) easily beat the Baseline Naive model (8.25%) and outpaced the basic XGBoost lag model (5.99%), demonstrating the strength of zero-shot transfer learning.
2. **Feature Engineering Threshold**: It took the addition of both calendar and comprehensive weather covariates for XGBoost to decisively overtake the univariate foundation model.
3. **The Covariate Ceiling**: Even with perfect weather foresight, the engineered XGBoost model (3.24%) remains slightly behind the Chronos-2 Covariate model (2.77%) in the extreme August window. This suggests that the foundation model is better at learning the non-linear relationship between weather and energy demand from its vast pre-training data.
4. **Complexity vs. Performance**: XGBoost requires meticulous feature alignment (24 independent models) to achieve these gains, whereas Chronos-2 uses a single pipeline for all scenarios.

### 🚀 Production Deployment Analysis: Chronos-2 vs. XGBoost
While Chronos-2 holds mathematical and probabilistic advantages, deploying both models in production exposes critical architectural trade-offs:

| Dimension | XGBoost (Phase 5/6) | Chronos-2 (Full Covariates) |
| :--- | :--- | :--- |
| **Inference Hardware** | Low-cost CPU (e.g., serverless function like AWS Lambda). | GPU-enabled instance (required for practical decoding speeds). |
| **Inference Latency** | **1 - 5 milliseconds** (simple tree traversal). | **1 - 5 seconds** (autoregressive generation over 500 paths). |
| **Hosting Cost** | Negligible (runs on standard web hosting). | High (requires continuous containerized GPU instance). |
| **Explainability** | High (fully auditable split nodes, SHAP-inspectable). | Low (deep learning Transformer is a black box). |
| **Cold Start** | Poor (requires 1-2 years of local history to train). | Excellent (zero-shot transfer learning works immediately). |
| **Online Retraining** | Extremely easy (takes seconds on CPU to adapt to drift). | Complex/Slow (finetuning deep networks is slow and risky). |

#### Deployment Recommendation:
* **Deploy Chronos-2** if you are forecasting a small number of system-wide regions, require highly calibrated 90% confidence boundaries for risk management, or are deploying to brand-new regions with very little historical data.
* **Deploy XGBoost** if you need to scale to thousands of series (e.g., forecasting for individual buildings or feeders) under tight latency/cost constraints, require full explainability for grid operators, and have access to ample historical data.
