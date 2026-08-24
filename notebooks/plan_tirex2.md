# Benchmark Evaluation Plan: TiRex-2 vs. Chronos-2 & XGBoost

This document outlines the evaluation plan for benchmarking **TiRex-2** against **Chronos-2**, **XGBoost (Static & Rolling)**, and **Seasonal Naive** baselines on regional energy demand forecasting (ERCOT Dallas and IESO Toronto).

---

## 1. Executive Summary & Background

**TiRex-2** (developed by NX-AI / Hochreiter lab) is a state-of-the-art zero-shot Time-Series Foundation Model (TSFM) built on an **xLSTM (extended LSTM)** architecture. Unlike Transformer-based foundation models like `amazon/chronos-2`, TiRex-2 utilizes matrix memory ($mLSTM$) and scalar memory ($sLSTM$) recurrent cells:
- **Zero-Shot SOTA Performance**: Demonstrated top-tier zero-shot performance across GIFT-Eval and Monash benchmarks, outperforming leading Transformer models.
- **Multivariate & Covariate Conditioning**: Natively ingests both historical past covariates and future-known covariates (meteorological forecasts, day-of-week, statutory holidays).
- **Linear Inference Complexity**: $O(L)$ computational complexity with constant per-step memory footprint, allowing ultra-fast inference and streaming capabilities on edge and consumer hardware (Apple Silicon MPS / CPU / CUDA).
- **Native Probabilistic Quantiles**: Directly produces multi-quantile forecasts for calibrated confidence bounds.

---

## 2. Benchmark Architecture & Alignment Strategy

To maintain strict **apples-to-apples comparability** with existing benchmarks in this repository:

### 2.1 Test Windows & Data Sources
- **ERCOT Dallas, Texas (NCENT)**:
  - **Summer Extreme Load**: August 1, 2025 – August 31, 2025 (31 days)
  - **Winter/Spring Transition**: March 1, 2026 – March 31, 2026 (31 days)
  - *Data files*: `data/ercot/ercot_dallas_univariate_*.csv`, `data/ercot/ercot_dallas_covariate_*.csv`
- **IESO Toronto, Ontario ('M' FSAs)**:
  - **Winter Heating Peak**: February 1, 2025 – February 28, 2025 (28 days)
  - **Summer Cooling Peak**: August 1, 2025 – August 31, 2025 (31 days)
  - *Data files*: `data/ieso/ieso_toronto_univariate_*.csv`, `data/ieso/ieso_toronto_covariate_*.csv`

### 2.2 Standard Experiment Protocol
- **Context Length**: `512` hours (lookback prior to origin).
- **Forecast Horizon**: `24` hours (day-ahead hourly forecast).
- **Evaluation Origin**: Rolling origin daily at 00:00 local time for all days in the target test month.
- **Configurations**:
  1. **Univariate**: Target load only.
  2. **Full Covariates**: Target load + 8 hourly weather features + calendar features (`day_of_week`, `is_holiday`).
  3. **Lean Covariates**: Target load + key temperature features + calendar features.
- **Evaluation Metrics**:
  - `MAE`: Mean Absolute Error
  - `RMSE`: Root Mean Squared Error
  - `sMAPE (%)`: Symmetric Mean Absolute Percentage Error
  - `MASE`: Mean Absolute Scaled Error (scaled by in-sample 168h seasonal naive MAE)
  - `Empirical Coverage (90% Interval)`: Nominal 90% confidence interval ($q_{0.05}$ to $q_{0.95}$)
  - `Inference Latency & Peak Memory`: Per-step decoding time and memory footprint

---

## 3. Step-by-Step Implementation Roadmap

### Phase 1: Environment & Dependency Setup
- Install `tirex-2` and its required dependencies in the virtual environment.
- Verify hardware acceleration (PyTorch MPS on macOS / CUDA / CPU fallback).

### Phase 2: Pipeline Wrapper (`src/tirex_pipeline.py`)
- Create a standardized pipeline wrapper class matching the `predict_df(batched_context_df, future_df=...)` interface used across existing Chronos-2 notebooks.
- Translate Pandas context and future DataFrames into TiRex-2 tensor / `TimeseriesType` structures and convert quantile outputs back to standardized DataFrames.

### Phase 3: Smoke-Test & Quickstart Notebooks
- `notebooks/tirex-2/tirex-2-quickstart.ipynb`: Univariate inference verification and covariate test.

### Phase 4: ERCOT Dallas Benchmark Execution
- `notebooks/tirex-2/ercot-univariate-2025-summer.ipynb`
- `notebooks/tirex-2/ercot-covariate-2025-summer.ipynb`
- `notebooks/tirex-2/ercot-covariate-lean-2025-summer.ipynb`
- `notebooks/tirex-2/ercot-univariate-2026-winter.ipynb`
- `notebooks/tirex-2/ercot-covariate-2026-winter.ipynb`
- `notebooks/tirex-2/ercot-covariate-lean-2026-winter.ipynb`

### Phase 5: IESO Toronto Benchmark Execution
- `notebooks/tirex-2/ieso-univariate-2025-winter.ipynb`
- `notebooks/tirex-2/ieso-covariate-2025-winter.ipynb`
- `notebooks/tirex-2/ieso-covariate-lean-2025-winter.ipynb`
- `notebooks/tirex-2/ieso-univariate-2025-summer.ipynb`
- `notebooks/tirex-2/ieso-covariate-2025-summer.ipynb`
- `notebooks/tirex-2/ieso-covariate-lean-2025-summer.ipynb`

### Phase 6: Multi-Model Benchmark Comparison
Consolidate results into a unified cross-model comparison matrix comparing TiRex-2, Chronos-2, XGBoost (Static & Rolling), and Seasonal Naive.

### Phase 7: Documentation & Insights
- Update `README.md` and `docs/SUMMARY.md`.
- Document architectural trade-offs: Transformer Self-Attention vs. xLSTM Recurrent State Tracking in grid operation environments.
