"""
Generates and executes all 12 TiRex-2 Streaming benchmark notebooks across ERCOT and IESO datasets.
Uses Protocol A: 512h warmup lookback with continuous memory retention across the evaluation month.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path
import nbformat as nbf
from nbclient import NotebookClient
import pandas as pd
import numpy as np

# Ensure target directories exist
output_dir = Path("notebooks/tirex-2-streaming")
output_dir.mkdir(parents=True, exist_ok=True)

# Define the 12 scenarios
SCENARIOS = [
    # ERCOT Dallas - Summer 2025 (August)
    {
        "filename": "ercot-univariate-2025-summer.ipynb",
        "title": "ERCOT Dallas Univariate Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_univariate_2025_summer.csv",
        "config_type": "univariate",
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "MW",
    },
    {
        "filename": "ercot-covariate-2025-summer.ipynb",
        "title": "ERCOT Dallas Covariate-Aware Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_covariate_2025_summer.csv",
        "config_type": "full_covariates",
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "MW",
    },
    {
        "filename": "ercot-covariate-lean-2025-summer.ipynb",
        "title": "ERCOT Dallas Lean Covariate Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_covariate_2025_summer.csv",
        "config_type": "lean_covariates",
        "lean_cols": ["apparent_temperature (°C)", "day_of_week", "is_holiday", "cloud_cover (%)"],
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "MW",
    },
    # ERCOT Dallas - Winter/Spring 2026 (March)
    {
        "filename": "ercot-univariate-2026-winter.ipynb",
        "title": "ERCOT Dallas Univariate Streaming Forecast with TiRex-2 (Winter/Spring 2026)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_univariate_2026.csv",
        "config_type": "univariate",
        "eval_start": "2026-03-01",
        "eval_end": "2026-03-31",
        "in_sample_cutoff": "2026-03-01",
        "target_col": "energy",
        "unit": "MW",
    },
    {
        "filename": "ercot-covariate-2026-winter.ipynb",
        "title": "ERCOT Dallas Covariate-Aware Streaming Forecast with TiRex-2 (Winter/Spring 2026)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_covariate_2026.csv",
        "config_type": "full_covariates",
        "eval_start": "2026-03-01",
        "eval_end": "2026-03-31",
        "in_sample_cutoff": "2026-03-01",
        "target_col": "energy",
        "unit": "MW",
    },
    {
        "filename": "ercot-covariate-lean-2026-winter.ipynb",
        "title": "ERCOT Dallas Lean Covariate Streaming Forecast with TiRex-2 (Winter/Spring 2026)",
        "region_name": "ERCOT Dallas",
        "data_path": "../data/ercot/ercot_dallas_covariate_2026.csv",
        "config_type": "lean_covariates",
        "lean_cols": ["apparent_temperature (°C)", "day_of_week", "is_holiday", "cloud_cover (%)"],
        "eval_start": "2026-03-01",
        "eval_end": "2026-03-31",
        "in_sample_cutoff": "2026-03-01",
        "target_col": "energy",
        "unit": "MW",
    },
    # IESO Toronto - Winter 2025 (February)
    {
        "filename": "ieso-univariate-2025-winter.ipynb",
        "title": "IESO Toronto Univariate Streaming Forecast with TiRex-2 (Winter 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_2025_winter.csv",
        "config_type": "univariate",
        "eval_start": "2025-02-01",
        "eval_end": "2025-02-28",
        "in_sample_cutoff": "2025-02-01",
        "target_col": "energy",
        "unit": "kWh",
    },
    {
        "filename": "ieso-covariate-2025-winter.ipynb",
        "title": "IESO Toronto Covariate-Aware Streaming Forecast with TiRex-2 (Winter 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_covariate_2025_winter.csv",
        "config_type": "full_covariates",
        "eval_start": "2025-02-01",
        "eval_end": "2025-02-28",
        "in_sample_cutoff": "2025-02-01",
        "target_col": "energy",
        "unit": "kWh",
    },
    {
        "filename": "ieso-covariate-lean-2025-winter.ipynb",
        "title": "IESO Toronto Lean Covariate Streaming Forecast with TiRex-2 (Winter 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_covariate_2025_winter.csv",
        "config_type": "lean_covariates",
        "lean_cols": ["apparent_temperature (°C)", "day_of_week", "is_holiday", "cloud_cover (%)"],
        "eval_start": "2025-02-01",
        "eval_end": "2025-02-28",
        "in_sample_cutoff": "2025-02-01",
        "target_col": "energy",
        "unit": "kWh",
    },
    # IESO Toronto - Summer 2025 (August)
    {
        "filename": "ieso-univariate-2025-summer.ipynb",
        "title": "IESO Toronto Univariate Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_2025_summer.csv",
        "config_type": "univariate",
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "kWh",
    },
    {
        "filename": "ieso-covariate-2025-summer.ipynb",
        "title": "IESO Toronto Covariate-Aware Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_covariate_2025_summer.csv",
        "config_type": "full_covariates",
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "kWh",
    },
    {
        "filename": "ieso-covariate-lean-2025-summer.ipynb",
        "title": "IESO Toronto Lean Covariate Streaming Forecast with TiRex-2 (Summer 2025)",
        "region_name": "IESO Toronto",
        "data_path": "../data/ieso/ieso_toronto_covariate_2025_summer.csv",
        "config_type": "lean_covariates",
        "lean_cols": ["apparent_temperature (°C)", "day_of_week", "is_holiday", "cloud_cover (%)"],
        "eval_start": "2025-08-01",
        "eval_end": "2025-08-31",
        "in_sample_cutoff": "2025-08-01",
        "target_col": "energy",
        "unit": "kWh",
    },
]


def build_streaming_notebook(scenario: dict) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    config_desc = {
        "univariate": "a purely univariate streaming setting (historical load target only)",
        "full_covariates": "a full covariate-aware streaming setting (historical load target + 8 hourly weather features + calendar features)",
        "lean_covariates": "a lean covariate streaming setting (historical load target + key apparent temperature, cloud cover, and calendar features)",
    }[scenario["config_type"]]

    model_label = "TiRex-2 Streaming (" + {
        "univariate": "Univariate",
        "full_covariates": "Full Covariates",
        "lean_covariates": "Lean Covariates",
    }[scenario["config_type"]] + ")"

    cells.append(nbf.v4.new_markdown_cell(f"""# {scenario['title']}

This notebook runs zero-shot day-ahead energy forecasting using the **TiRex-2** (`NX-AI/TiRex-2`) foundation model in **True Streaming Mode** ({config_desc}).

### Streaming Experiment Protocol (Protocol A)
- **Data Source**: `{scenario['data_path']}`
- **Model**: `NX-AI/TiRex-2` (xLSTM Architecture)
- **Warmup Lookback**: 512 hours immediately prior to {scenario['eval_start']}
- **Streaming Execution**: Memory accumulates continuously across consecutive daily forecasts (512h to 1,256h)
- **Forecast Horizon**: 24 hours (day-ahead, rolling origin daily at 00:00)
- **Evaluation Period**: {scenario['eval_start']} to {scenario['eval_end']}
- **Baseline**: Seasonal Naive (168-hour lookback)
- **Probabilistic Calibration**: Nominal 90% Prediction Interval ($q_{{0.05}}$ to $q_{{0.95}}$) and 80% Interval ($q_{{0.10}}$ to $q_{{0.90}}$)
"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""from __future__ import annotations

import os
import platform
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import torch
from IPython.display import display

# Add src/ to path
for p in [Path.cwd().parent.parent / "src", Path("src"), Path("../src")]:
    if p.exists() and str(p) not in sys.path:
        sys.path.insert(0, str(p))

from tirex_streaming_pipeline import TiRexStreamingPipeline

plt.style.use("seaborn-v0_8-whitegrid")
pd.set_option("display.max_columns", 20)
"""))

    # Data loading cell
    if scenario["config_type"] == "univariate":
        data_loading_code = f"""# Load data
candidates = [
    Path("{scenario['data_path']}"),
    Path("{scenario['data_path'].replace('../', '')}"),
    Path("../" + "{scenario['data_path']}"),
]
data_path = next(p for p in candidates if p.exists())
df = pd.read_csv(data_path)

# Prepare dataframe
df["timestamp"] = pd.to_datetime(df["timestamp"])
if "{scenario['target_col']}" in df.columns:
    df = df.rename(columns={{"{scenario['target_col']}": "target"}})
df = df.sort_values("timestamp").reset_index(drop=True)

# Robust hourly resampling
df = df.set_index("timestamp").resample("h").mean().interpolate().reset_index()

covariate_columns = None

print(f"Loaded {{len(df)}} rows of data (after hourly resampling).")
print(f"Date range: {{df['timestamp'].min()}} to {{df['timestamp'].max()}}")
df.head()
"""
    elif scenario["config_type"] == "full_covariates":
        data_loading_code = f"""# Load data
candidates = [
    Path("{scenario['data_path']}"),
    Path("{scenario['data_path'].replace('../', '')}"),
    Path("../" + "{scenario['data_path']}"),
]
data_path = next(p for p in candidates if p.exists())
df = pd.read_csv(data_path)

# Prepare dataframe
df["timestamp"] = pd.to_datetime(df["timestamp"])
if "{scenario['target_col']}" in df.columns:
    df = df.rename(columns={{"{scenario['target_col']}": "target"}})
df = df.sort_values("timestamp").reset_index(drop=True)

# Robust hourly resampling
df = df.set_index("timestamp").resample("h").mean().interpolate().reset_index()

covariate_columns = [
    col for col in df.columns 
    if col not in ["timestamp", "target", "item_id"]
]

print(f"Loaded {{len(df)}} rows of data.")
print(f"Date range: {{df['timestamp'].min()}} to {{df['timestamp'].max()}}")
print(f"Covariates identified: {{covariate_columns}}")
df.head()
"""
    else: # lean_covariates
        lean_cols_repr = repr(scenario["lean_cols"])
        data_loading_code = f"""# Load data
candidates = [
    Path("{scenario['data_path']}"),
    Path("{scenario['data_path'].replace('../', '')}"),
    Path("../" + "{scenario['data_path']}"),
]
data_path = next(p for p in candidates if p.exists())
df = pd.read_csv(data_path)

# Prepare dataframe
df["timestamp"] = pd.to_datetime(df["timestamp"])
if "{scenario['target_col']}" in df.columns:
    df = df.rename(columns={{"{scenario['target_col']}": "target"}})
df = df.sort_values("timestamp").reset_index(drop=True)

# Robust hourly resampling
df = df.set_index("timestamp").resample("h").mean().interpolate().reset_index()

covariate_columns = {lean_cols_repr}

print(f"Loaded {{len(df)}} rows of data.")
print(f"Date range: {{df['timestamp'].min()}} to {{df['timestamp'].max()}}")
print(f"Lean Covariates identified: {{covariate_columns}}")
df.head()
"""

    cells.append(nbf.v4.new_code_cell(data_loading_code))

    # Model loading
    cells.append(nbf.v4.new_code_cell("""def resolve_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

device = resolve_device()
print(f"Loading TiRexStreamingPipeline (NX-AI/TiRex-2) on device='{device}'...")

pipeline = TiRexStreamingPipeline.from_pretrained(
    "NX-AI/TiRex-2",
    device_map=device,
)
print("TiRex-2 Streaming Pipeline successfully loaded.")
"""))

    # Streaming execution
    stream_exec_code = f"""warmup_length = 512
prediction_length = 24
eval_start = "{scenario['eval_start']}"
eval_end = "{scenario['eval_end']}"

print(f"Running True Streaming Forecasting from {{eval_start}} to {{eval_end}}...")
t_start = time.perf_counter()

pred_df, step_latencies_ms = pipeline.predict_stream(
    df=df,
    eval_start=eval_start,
    eval_end=eval_end,
    warmup_length=warmup_length,
    prediction_length=prediction_length,
    covariate_cols=covariate_columns,
    quantile_levels=[0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95],
)

total_stream_time = time.perf_counter() - t_start
avg_step_ms = np.mean(step_latencies_ms) if step_latencies_ms else 0.0

print(f"Streaming inference complete in {{total_stream_time:.2f}}s.")
print(f"Average per-step latency: {{avg_step_ms:.1f}} ms ({{len(step_latencies_ms)}} daily steps).")
pred_df.head()
"""
    cells.append(nbf.v4.new_code_cell(stream_exec_code))

    # Seasonal naive baseline
    naive_code = f"""# Seasonal Naive Baseline: Repeat value from 168 hours ago (1 week)
eval_days = pd.date_range(start="{scenario['eval_start']}", end="{scenario['eval_end']}", freq="D")
seasonal_period = 168
baseline_results = []

for target_day in eval_days:
    target_matches = df[df["timestamp"] == target_day].index
    if len(target_matches) == 0:
        continue
    target_idx = target_matches[0]
    target_str = target_day.strftime("%Y-%m-%d")
    
    actual_slice = df.iloc[target_idx : target_idx + prediction_length].copy()
    actual_slice["item_id"] = target_str
    
    lag_start = target_idx - seasonal_period
    lag_end = lag_start + prediction_length
    
    if lag_start >= 0 and lag_end <= len(df):
        baseline_preds = df.iloc[lag_start:lag_end]["target"].values
    else:
        baseline_preds = np.full(prediction_length, np.nan)
        
    baseline_df = actual_slice[["item_id", "timestamp", "target"]].copy()
    baseline_df["baseline_pred"] = baseline_preds
    baseline_results.append(baseline_df)

eval_df = pd.concat(baseline_results).reset_index(drop=True)
eval_df = eval_df.merge(pred_df, on=["item_id", "timestamp"], how="left")
print(f"Merged evaluation dataset: {{len(eval_df)}} hourly predictions.")
eval_df.head()
"""
    cells.append(nbf.v4.new_code_cell(naive_code))

    # Metrics evaluation
    metrics_code = f"""# In-sample seasonal naive MAE for MASE computation
in_sample_df = df[df["timestamp"] < "{scenario['in_sample_cutoff']}"].copy()
if len(in_sample_df) > seasonal_period:
    y_in = in_sample_df["target"].values
    naive_in_sample_mae = np.mean(np.abs(y_in[seasonal_period:] - y_in[:-seasonal_period]))
else:
    naive_in_sample_mae = np.nan

y_true = eval_df["target"].values
y_pred_tirex = eval_df["predictions"].values
y_pred_naive = eval_df["baseline_pred"].values

def compute_metrics(y_t, y_p, naive_mae, q05=None, q10=None, q90=None, q95=None):
    valid = ~np.isnan(y_t) & ~np.isnan(y_p)
    yt, yp = y_t[valid], y_p[valid]
    
    mae = np.mean(np.abs(yt - yp))
    rmse = np.sqrt(np.mean((yt - yp) ** 2))
    smape = 100 * np.mean(2 * np.abs(yt - yp) / (np.abs(yt) + np.abs(yp)))
    mase = mae / naive_mae if not np.isnan(naive_mae) else np.nan
    
    cov_80 = np.mean((yt >= q10[valid]) & (yt <= q90[valid])) * 100 if q10 is not None and q90 is not None else np.nan
    cov_90 = np.mean((yt >= q05[valid]) & (yt <= q95[valid])) * 100 if q05 is not None and q95 is not None else np.nan
    
    return mae, rmse, smape, mase, cov_80, cov_90

tirex_metrics = compute_metrics(
    y_true, y_pred_tirex, naive_in_sample_mae,
    q05=eval_df.get("0.05"), q10=eval_df.get("0.1"),
    q90=eval_df.get("0.9"), q95=eval_df.get("0.95"),
)

naive_metrics = compute_metrics(y_true, y_pred_naive, naive_in_sample_mae)

model_label = "{model_label}"

metrics_df = pd.DataFrame({{
    "Metric": ["MAE", "RMSE", "sMAPE (%)", "MASE", "80% Interval Coverage", "90% Interval Coverage", "Step Latency (ms)"],
    model_label: [
        f"{{tirex_metrics[0]:.2f}}",
        f"{{tirex_metrics[1]:.2f}}",
        f"{{tirex_metrics[2]:.2f}}%",
        f"{{tirex_metrics[3]:.3f}}",
        f"{{tirex_metrics[4]:.2f}}%",
        f"{{tirex_metrics[5]:.2f}}%",
        f"{{avg_step_ms:.1f}} ms",
    ],
    "Seasonal Naive (7d)": [
        f"{{naive_metrics[0]:.2f}}",
        f"{{naive_metrics[1]:.2f}}",
        f"{{naive_metrics[2]:.2f}}%",
        f"{{naive_metrics[3]:.3f}}",
        "N/A",
        "N/A",
        "< 0.1 ms",
    ],
}})

print(f"\\n=== FINAL BENCHMARK METRICS: {scenario['title']} ===")
display(metrics_df)
"""
    cells.append(nbf.v4.new_code_cell(metrics_code))

    # Visualization
    plot_code = f"""# Plot Day-Ahead Forecasts
plt.figure(figsize=(15, 6), dpi=100)

plt.plot(eval_df["timestamp"], eval_df["target"], label="Actual Demand", color="black", linewidth=1.5, zorder=4)
plt.plot(eval_df["timestamp"], eval_df["predictions"], label="{model_label} (Median)", color="#1f77b4", linewidth=1.5, zorder=3)
plt.plot(eval_df["timestamp"], eval_df["baseline_pred"], label="Seasonal Naive (168h)", color="gray", linestyle="--", alpha=0.7, zorder=2)

if "0.05" in eval_df.columns and "0.95" in eval_df.columns:
    plt.fill_between(
        eval_df["timestamp"],
        eval_df["0.05"],
        eval_df["0.95"],
        color="#1f77b4",
        alpha=0.15,
        label="90% Prediction Interval",
        zorder=1,
    )

if "0.1" in eval_df.columns and "0.9" in eval_df.columns:
    plt.fill_between(
        eval_df["timestamp"],
        eval_df["0.1"],
        eval_df["0.9"],
        color="#1f77b4",
        alpha=0.25,
        label="80% Prediction Interval",
        zorder=1,
    )

plt.title(f"{scenario['title']} - Rolling Day-Ahead Evaluation", fontsize=14, fontweight="bold", pad=12)
plt.xlabel("Timestamp", fontsize=11)
plt.ylabel(f"Energy Demand ({scenario['unit']})", fontsize=11)
plt.legend(loc="upper left", frameon=True)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.show()
"""
    cells.append(nbf.v4.new_code_cell(plot_code))

    nb["cells"] = cells
    return nb


def main():
    print("=" * 70)
    print("GENERATING AND EXECUTING 12 TIREX-2 STREAMING BENCHMARK NOTEBOOKS")
    print("=" * 70)

    for i, scenario in enumerate(SCENARIOS, 1):
        nb_filename = scenario["filename"]
        nb_path = output_dir / nb_filename
        print(f"\n[{i}/12] Processing {nb_filename}...")

        # 1. Generate notebook node
        nb = build_streaming_notebook(scenario)

        # 2. Save unexecuted notebook
        with open(nb_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        # 3. Execute notebook
        t0 = time.time()
        client = NotebookClient(
            nb,
            timeout=600,
            kernel_name="python3",
            resources={"metadata": {"path": str(output_dir)}},
        )
        client.execute()
        exec_time = time.time() - t0

        # 4. Save executed notebook with outputs and charts
        with open(nb_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)

        print(f" -> Successfully executed in {exec_time:.2f}s!")

    print("\nAll 12 streaming notebooks successfully generated and executed!")


if __name__ == "__main__":
    main()
