"""
TiRex-2 Streaming Forecasting Pipeline Adapter.

Provides TiRexStreamingPipeline for zero-shot time-series forecasting with
continuous memory retention (Protocol A: 512h warmup lookback, accumulating
recurrent state across consecutive daily forecasts).
"""

from __future__ import annotations

import time
from typing import List, Optional, Tuple
import numpy as np
import pandas as pd
import torch

from tirex2 import load_model, TimeseriesType


class TiRexStreamingPipeline:
    """
    Adapter for NX-AI TiRex-2 foundation model that provides streaming zero-shot
    forecasting with cumulative history retention (xLSTM recurrent memory).
    """

    def __init__(self, model_id: str = "NX-AI/TiRex-2", device: Optional[str] = None):
        if device is None:
            if torch.cuda.is_available():
                self.device = "cuda"
            elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
                self.device = "mps"
            else:
                self.device = "cpu"
        else:
            self.device = device

        self.model_id = model_id
        self.model = load_model(model_id, device=self.device)
        self.default_quantiles = self.model._quantile_levels()
        self.quantile_to_idx = {round(q, 2): i for i, q in enumerate(self.default_quantiles)}

    @classmethod
    def from_pretrained(
        cls,
        model_id: str = "NX-AI/TiRex-2",
        device_map: Optional[str] = None,
        **kwargs,
    ) -> "TiRexStreamingPipeline":
        """Instantiate a TiRexStreamingPipeline from a checkpoint."""
        return cls(model_id=model_id, device=device_map)

    def predict_stream(
        self,
        df: pd.DataFrame,
        eval_start: str,
        eval_end: str,
        warmup_length: int = 512,
        prediction_length: int = 24,
        covariate_cols: Optional[List[str]] = None,
        quantile_levels: Optional[List[float]] = None,
        item_id: str = "item_0",
    ) -> Tuple[pd.DataFrame, List[float]]:
        """
        Execute streaming day-ahead forecasting across an evaluation date range with
        continuous historical memory accumulation starting from a 512h warmup lookback.
        """
        if quantile_levels is None:
            quantile_levels = [0.05, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95]

        eval_days = pd.date_range(start=eval_start, end=eval_end, freq="D")
        start_idx = df[df["timestamp"] == eval_days[0]].index[0]
        warmup_start_idx = max(0, start_idx - warmup_length)

        all_records = []
        step_latencies_ms = []

        for target_day in eval_days:
            match = df[df["timestamp"] == target_day]
            if match.empty:
                continue
            target_idx = match.index[0]

            ctx_df = df.iloc[warmup_start_idx:target_idx]
            fut_df = df.iloc[target_idx : target_idx + prediction_length]

            if len(fut_df) < prediction_length:
                continue

            target_tensor = torch.from_numpy(ctx_df["target"].values.astype(np.float32)).float()

            if covariate_cols:
                past_cov = ctx_df[covariate_cols].values.astype(np.float32)
                fut_cov = fut_df[covariate_cols].values.astype(np.float32)
                full_cov = np.vstack([past_cov, fut_cov])
                cov_tensor = torch.from_numpy(full_cov.T).float()
                ts = TimeseriesType(
                    target=target_tensor,
                    past_covariates=None,
                    future_covariates=cov_tensor,
                )
            else:
                ts = TimeseriesType(
                    target=target_tensor,
                    past_covariates=None,
                    future_covariates=None,
                )

            t0 = time.perf_counter()
            forecast_out = self.model.forecast(
                [ts],
                prediction_length=prediction_length,
                output_type="numpy",
            )
            step_latencies_ms.append((time.perf_counter() - t0) * 1000.0)

            fc_quantiles = forecast_out[0][0]  # (9, 24)

            def get_q(q_val: float) -> np.ndarray:
                q_rounded = round(q_val, 2)
                if q_rounded in self.quantile_to_idx:
                    return fc_quantiles[self.quantile_to_idx[q_rounded]]
                elif q_rounded == 0.05:
                    q10 = fc_quantiles[self.quantile_to_idx[0.10]]
                    q20 = fc_quantiles[self.quantile_to_idx[0.20]]
                    return np.maximum(0.0, q10 - 0.5 * (q20 - q10))
                elif q_rounded == 0.95:
                    q90 = fc_quantiles[self.quantile_to_idx[0.90]]
                    q80 = fc_quantiles[self.quantile_to_idx[0.80]]
                    return q90 + 0.5 * (q90 - q80)
                else:
                    return np.quantile(fc_quantiles, q_val, axis=0)

            median_pred = get_q(0.50)
            fut_timestamps = fut_df["timestamp"].values

            current_item_id = target_day.strftime("%Y-%m-%d") if hasattr(target_day, "strftime") else str(target_day)

            for step in range(prediction_length):
                rec = {
                    "item_id": current_item_id,
                    "timestamp": fut_timestamps[step],
                    "predictions": float(median_pred[step]),
                }
                for q in quantile_levels:
                    col_name = str(round(q, 2))
                    rec[col_name] = float(get_q(q)[step])
                all_records.append(rec)

        res_df = pd.DataFrame(all_records)
        return res_df, step_latencies_ms
