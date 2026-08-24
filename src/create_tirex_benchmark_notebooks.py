"""
Generates and executes all 12 TiRex-2 benchmark notebooks across ERCOT and IESO datasets.
Collects and displays master benchmark results.
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
output_dir = Path("notebooks/tirex-2")
output_dir.mkdir(parents=True, exist_ok=True)

# Define the 12 scenarios
SCENARIOS = [
    # ERCOT Dallas - Summer 2025 (August)
    {
        "filename": "ercot-univariate-2025-summer.ipynb",
        "title": "ERCOT Dallas Univariate Forecast with TiRex-2 (Summer 2025)",
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
        "title": "ERCOT Dallas Covariate-Aware Forecast with TiRex-2 (Summer 2025)",
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
        "title": "ERCOT Dallas Lean Covariate Forecast with TiRex-2 (Summer 2025)",
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
        "title": "ERCOT Dallas Univariate Forecast with TiRex-2 (Winter/Spring 2026)",
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
        "title": "ERCOT Dallas Covariate-Aware Forecast with TiRex-2 (Winter/Spring 2026)",
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
        "title": "ERCOT Dallas Lean Covariate Forecast with TiRex-2 (Winter/Spring 2026)",
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
        "title": "IESO Toronto Univariate Forecast with TiRex-2 (Winter 2025)",
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
        "title": "IESO Toronto Covariate-Aware Forecast with TiRex-2 (Winter 2025)",
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
        "title": "IESO Toronto Lean Covariate Forecast with TiRex-2 (Winter 2025)",
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
        "title": "IESO Toronto Univariate Forecast with TiRex-2 (Summer 2025)",
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
        "title": "IESO Toronto Covariate-Aware Forecast with TiRex-2 (Summer 2025)",
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
        "title": "IESO Toronto Lean Covariate Forecast with TiRex-2 (Summer 2025)",
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


def build_notebook(scenario: dict) -> nbf.NotebookNode:
    nb = nbf.v4.new_notebook()
    cells = []

    # Title & Markdown
    config_desc = {
        "univariate": "a purely univariate setting (historical load target only)",
        "full_covariates": "a full covariate-aware setting (historical load target + 8 hourly weather features + calendar features)",
        "lean_covariates": "a lean covariate setting (historical load target + key apparent temperature, cloud cover, and calendar features)",
    }[scenario["config_type"]]

    cells.append(nbf.v4.new_markdown_cell(f"""# {scenario['title']}

This notebook runs zero-shot day-ahead energy forecasting using the **TiRex-2** (`NX-AI/TiRex-2`) xLSTM foundation model in {config_desc}.

### Experiment Parameters
- **Data Source**: `{scenario['data_path']}`
- **Model**: `NX-AI/TiRex-2` (xLSTM Architecture)
- **Context Length**: 512 hours (sliding lookback)
- **Forecast Horizon**: 24 hours (day-ahead)
- **Evaluation Period**: {scenario['eval_start']} to {scenario['eval_end']} (daily rolling origin at 00:00)
- **Baseline**: Seasonal Naive (168-hour / 1-week lookback)
- **Probabilistic Calibration**: Nominal 90% Prediction Interval ($q_{{0.05}}$ to $q_{{0.95}}$) and 80% Interval ($q_{{0.10}}$ to $q_{{0.90}}$)
"""))

    # Imports
    cells.append(nbf.v4.new_code_cell("""from __future__ import annotations

import os
import platform
import sys
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

from tirex_pipeline import TiRexPipeline

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

    # Batch construction cell
    if scenario["config_type"] == "univariate":
        batch_code = f"""context_length = 512
prediction_length = 24

eval_days = pd.date_range(start="{scenario['eval_start']}", end="{scenario['eval_end']}", freq="D")

contexts = []
actuals = []

for target_day in eval_days:
    # Context: 512 hours before 00:00 of the target day
    context_end_matches = df[df["timestamp"] == target_day].index
    if len(context_end_matches) == 0:
        continue
    context_end_idx = context_end_matches[0]
    context_start_idx = context_end_idx - context_length
    
    if context_start_idx < 0:
        print(f"Warning: Not enough context for {{target_day.date()}}. Skipping.")
        continue
        
    day_context = df.iloc[context_start_idx:context_end_idx].copy()
    day_context["item_id"] = target_day.strftime("%Y-%m-%d")
    contexts.append(day_context)
    
    # Actuals: 24 hours of the target day
    day_actuals = df.iloc[context_end_idx : context_end_idx + prediction_length].copy()
    day_actuals["item_id"] = target_day.strftime("%Y-%m-%d")
    actuals.append(day_actuals)

batched_context_df = pd.concat(contexts).reset_index(drop=True)
batched_actuals_df = pd.concat(actuals).reset_index(drop=True)

print(f"Constructed batched context for {{len(contexts)}} days.")
print(f"Total context rows: {{len(batched_context_df)}}")
print(f"Total actuals rows: {{len(batched_actuals_df)}}")
"""
    else: # covariate
        batch_code = f"""context_length = 512
prediction_length = 24

eval_days = pd.date_range(start="{scenario['eval_start']}", end="{scenario['eval_end']}", freq="D")

contexts = []
futures = []
actuals = []

for target_day in eval_days:
    # Context: 512 hours before 00:00 of the target day
    context_end_matches = df[df["timestamp"] == target_day].index
    if len(context_end_matches) == 0:
        continue
    context_end_idx = context_end_matches[0]
    context_start_idx = context_end_idx - context_length
    
    if context_start_idx < 0:
        print(f"Warning: Not enough context for {{target_day.date()}}. Skipping.")
        continue
        
    item_id = target_day.strftime("%Y-%m-%d")
    
    day_context = df.iloc[context_start_idx:context_end_idx][["timestamp", "target"] + covariate_columns].copy()
    day_context["item_id"] = item_id
    contexts.append(day_context)
    
    # Future: 24 hours of the target day (covariates only)
    day_future = df.iloc[context_end_idx : context_end_idx + prediction_length][["timestamp"] + covariate_columns].copy()
    day_future["item_id"] = item_id
    futures.append(day_future)
    
    # Actuals: 24 hours of the target day
    day_actuals = df.iloc[context_end_idx : context_end_idx + prediction_length].copy()
    day_actuals["item_id"] = item_id
    actuals.append(day_actuals)

batched_context_df = pd.concat(contexts).reset_index(drop=True)
batched_future_df = pd.concat(futures).reset_index(drop=True)
batched_actuals_df = pd.concat(actuals).reset_index(drop=True)

print(f"Constructed batched datasets for {{len(contexts)}} days.")
print(f"Total context rows: {{len(batched_context_df)}}")
print(f"Total future rows:  {{len(batched_future_df)}}")
print(f"Total actuals rows: {{len(batched_actuals_df)}}")
"""
    cells.append(nbf.v4.new_code_cell(batch_code))

    # Model loading
    cells.append(nbf.v4.new_code_cell("""def resolve_device() -> str:
    if torch.cuda.is_available():
        return "cuda"
    if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        return "mps"
    return "cpu"

device = resolve_device()
print(f"Loading NX-AI/TiRex-2 on device='{device}'...")

pipeline = TiRexPipeline.from_pretrained(
    "NX-AI/TiRex-2",
    device_map=device,
)
print("TiRex-2 Pipeline successfully loaded.")
"""))

    # Inference cell
    if scenario["config_type"] == "univariate":
        infer_code = """print("Running batched univariate inference with TiRex-2...")
pred_df = pipeline.predict_df(
    batched_context_df,
    prediction_length=prediction_length,
    quantile_levels=[0.05, 0.1, 0.5, 0.9, 0.95],
)
print("Inference complete.")
"""
    else:
        infer_code = """print("Running batched covariate-aware inference with TiRex-2...")
pred_df = pipeline.predict_df(
    batched_context_df,
    future_df=batched_future_df,
    prediction_length=prediction_length,
    quantile_levels=[0.05, 0.1, 0.5, 0.9, 0.95],
)
print("Inference complete.")
"""
    cells.append(nbf.v4.new_code_cell(infer_code))

    # Seasonal naive baseline
    naive_code = f"""# Seasonal Naive Baseline: Repeat value from 168 hours ago (1 week)
seasonal_period = 168
baseline_results = []

for target_day in eval_days:
    target_matches = df[df["timestamp"] == target_day].index
    if len(target_matches) == 0:
        continue
    target_idx = target_matches[0]
    target_str = target_day.strftime("%Y-%m-%d")
    
    # Get values from 1 week ago
    naive_values = df.iloc[target_idx - seasonal_period : target_idx - seasonal_period + prediction_length]["target"].values
    target_timestamps = df.iloc[target_idx : target_idx + prediction_length]["timestamp"].values
    
    day_baseline = pd.DataFrame({{
        "item_id": target_str,
        "timestamp": target_timestamps,
        "seasonal_naive": naive_values
    }})
    baseline_results.append(day_baseline)

baseline_df = pd.concat(baseline_results).reset_index(drop=True)
baseline_df["timestamp"] = pd.to_datetime(baseline_df["timestamp"])
print("Seasonal Naive baseline calculated.")
"""
    cells.append(nbf.v4.new_code_cell(naive_code))

    # Evaluation cell
    model_name_label = {
        "univariate": "TiRex-2 (Univariate)",
        "full_covariates": "TiRex-2 (Full Covariates)",
        "lean_covariates": "TiRex-2 (Lean Covariates)",
    }[scenario["config_type"]]

    eval_code = f"""# Merge predictions, actuals, and baseline
eval_df = pred_df.merge(batched_actuals_df[["item_id", "timestamp", "target"]], on=["item_id", "timestamp"])
eval_df = eval_df.merge(baseline_df, on=["item_id", "timestamp"])
eval_df = eval_df.rename(columns={{"target": "actual"}})

def calculate_metrics(y_true, y_pred):
    mae = np.mean(np.abs(y_true - y_pred))
    rmse = np.sqrt(np.mean((y_true - y_pred)**2))
    smape = 100 * np.mean(2 * np.abs(y_true - y_pred) / (np.abs(y_true) + np.abs(y_pred)))
    return mae, rmse, smape

tirex_mae, tirex_rmse, tirex_smape = calculate_metrics(eval_df["actual"], eval_df["predictions"])
naive_mae, naive_rmse, naive_smape = calculate_metrics(eval_df["actual"], eval_df["seasonal_naive"])

# Calculate MASE Scale (Seasonal Naive MAE on in-sample data before evaluation window)
m = 168 # 1 week seasonality
in_sample_data = df[df["timestamp"] < "{scenario['in_sample_cutoff']}"]["target"].values
mase_scale = np.mean(np.abs(in_sample_data[m:] - in_sample_data[:-m]))

tirex_mase = tirex_mae / mase_scale
naive_mase = naive_mae / mase_scale

# Empirical Coverage
within_interval_90 = (eval_df["actual"] >= eval_df["0.05"]) & (eval_df["actual"] <= eval_df["0.95"])
coverage_90 = within_interval_90.mean() * 100

within_interval_80 = (eval_df["actual"] >= eval_df["0.1"]) & (eval_df["actual"] <= eval_df["0.9"])
coverage_80 = within_interval_80.mean() * 100

metrics_data = {{
    "Metric": ["MAE", "RMSE", "sMAPE (%)", "MASE", "80% Interval Coverage", "90% Interval Coverage"],
    "{model_name_label}": [tirex_mae, tirex_rmse, tirex_smape, tirex_mase, f"{{coverage_80:.2f}}%", f"{{coverage_90:.2f}}%"],
    "Seasonal Naive (7d)": [naive_mae, naive_rmse, naive_smape, naive_mase, "N/A", "N/A"]
}}

metrics_df = pd.DataFrame(metrics_data)
display(metrics_df)

print(f"{model_name_label} 90% Empirical Coverage: {{coverage_90:.2f}}% (Nominal Target: 90.0%)")
print(f"{model_name_label} 80% Empirical Coverage: {{coverage_80:.2f}}% (Nominal Target: 80.0%)")
"""
    cells.append(nbf.v4.new_code_cell(eval_code))

    # Visualization cell
    plot_code = f"""plt.figure(figsize=(14, 6))

# Plot full evaluation period actuals vs predictions
plt.plot(eval_df["timestamp"], eval_df["actual"], label="Actual Demand", color="black", lw=1.5)
plt.plot(eval_df["timestamp"], eval_df["predictions"], label="{model_name_label} Forecast", color="#1f77b4", lw=1.5)
plt.plot(eval_df["timestamp"], eval_df["seasonal_naive"], label="Seasonal Naive (7d)", color="#999999", linestyle="--", lw=1.0, alpha=0.7)

# 90% Prediction interval
plt.fill_between(
    eval_df["timestamp"],
    eval_df["0.05"],
    eval_df["0.95"],
    color="#1f77b4",
    alpha=0.2,
    label="90% Prediction Interval"
)

plt.title("{scenario['title']}", fontsize=13, fontweight="bold", pad=12)
plt.xlabel("Timestamp", fontsize=11)
plt.ylabel("Electricity Demand ({scenario['unit']})", fontsize=11)
plt.legend(loc="upper right", frameon=True)
plt.tight_layout()
plt.show()
"""
    cells.append(nbf.v4.new_code_cell(plot_code))

    nb.cells = cells
    return nb


def main():
    print("=" * 70)
    print("GENERATING AND EXECUTING 12 TIREX-2 BENCHMARK NOTEBOOKS")
    print("=" * 70)

    results_summary = []

    for i, scenario in enumerate(SCENARIOS, 1):
        nb_filename = scenario["filename"]
        target_path = output_dir / nb_filename
        print(f"\n[{i}/12] Processing {nb_filename}...")
        
        # 1. Build notebook
        nb = build_notebook(scenario)
        with open(target_path, "w", encoding="utf-8") as f:
            nbf.write(nb, f)
            
        # 2. Execute notebook with NotebookClient
        start_t = time.time()
        client = NotebookClient(nb, timeout=600, kernel_name="python3", resources={"metadata": {"path": str(output_dir)}})
        try:
            client.execute()
            with open(target_path, "w", encoding="utf-8") as f:
                nbf.write(nb, f)
            elapsed = time.time() - start_t
            print(f" -> Successfully executed in {elapsed:.2f}s!")
        except Exception as e:
            print(f" -> ERROR executing {nb_filename}: {e}")
            raise e

    print("\nAll 12 notebooks successfully generated and executed!")

if __name__ == "__main__":
    main()
