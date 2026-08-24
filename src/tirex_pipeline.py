"""
TiRex-2 Forecasting Pipeline Adapter.

Provides a unified interface `TiRexPipeline` with `predict_df` matching the
Chronos-2 `predict_df(context_df, future_df=...)` contract for benchmarking
regional energy forecasting with univariate and covariate data.
"""

from __future__ import annotations

from typing import List, Optional, Union
import numpy as np
import pandas as pd
import torch

from tirex2 import load_model, TimeseriesType


class TiRexPipeline:
    """
    Adapter for NX-AI TiRex-2 foundation model that provides DataFrame-level
    zero-shot forecasting with optional future-known covariates.
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
    ) -> "TiRexPipeline":
        """Instantiate a TiRexPipeline from a Hugging Face model checkpoint."""
        return cls(model_id=model_id, device=device_map)

    def predict_df(
        self,
        context_df: pd.DataFrame,
        future_df: Optional[pd.DataFrame] = None,
        prediction_length: int = 24,
        quantile_levels: Optional[List[float]] = None,
        batch_size: int = 512,
    ) -> pd.DataFrame:
        """
        Run zero-shot forecasts on a batched context DataFrame, with optional future covariates.

        Parameters
        ----------
        context_df : pd.DataFrame
            Must contain 'item_id', 'timestamp', and 'target' columns. If covariates are used,
            it must also contain the covariate feature columns.
        future_df : pd.DataFrame, optional
            If provided, must contain 'item_id', 'timestamp', and all covariate columns
            present in context_df for the prediction window (prediction_length hours).
        prediction_length : int, default=24
            Forecast horizon in steps (e.g. 24 hours).
        quantile_levels : list of float, optional
            Quantile levels to return. Defaults to [0.1, 0.5, 0.9] (or [0.05, 0.5, 0.95] if requested).
        batch_size : int, default=512
            Batch size for model inference.

        Returns
        -------
        pd.DataFrame
            DataFrame containing 'item_id', 'timestamp', 'predictions' (median),
            and columns for each requested quantile level.
        """
        if quantile_levels is None:
            quantile_levels = [0.1, 0.5, 0.9]

        # Preserve item ordering
        item_ids = context_df["item_id"].unique()
        
        # Identify covariate columns if future_df is provided
        covariate_cols = []
        if future_df is not None:
            non_cov_cols = {"item_id", "timestamp", "target"}
            covariate_cols = [c for c in context_df.columns if c not in non_cov_cols]

        timeseries_list: List[TimeseriesType] = []
        future_timestamps_dict = {}

        for item_id in item_ids:
            item_context = context_df[context_df["item_id"] == item_id].sort_values("timestamp")
            target_vals = item_context["target"].astype(np.float32).values
            target_tensor = torch.from_numpy(target_vals).float()

            if future_df is not None and len(covariate_cols) > 0:
                item_future = future_df[future_df["item_id"] == item_id].sort_values("timestamp")
                future_timestamps_dict[item_id] = item_future["timestamp"].values

                # Extract past and future covariates
                past_cov = item_context[covariate_cols].astype(np.float32).values # (context_len, num_cov)
                fut_cov = item_future[covariate_cols].astype(np.float32).values   # (prediction_len, num_cov)

                # Concatenate along time dimension (full horizon: context_len + prediction_len)
                full_cov = np.vstack([past_cov, fut_cov]) # (context_len + prediction_len, num_cov)
                # TiRex-2 expects shape (num_covariates, total_time_length)
                future_cov_tensor = torch.from_numpy(full_cov.T).float()

                ts = TimeseriesType(
                    target=target_tensor,
                    past_covariates=None,
                    future_covariates=future_cov_tensor,
                )
            else:
                # Univariate mode
                last_time = item_context["timestamp"].iloc[-1]
                freq = pd.infer_freq(item_context["timestamp"]) or "1h"
                future_times = pd.date_range(
                    start=last_time + pd.Timedelta(hours=1),
                    periods=prediction_length,
                    freq=freq,
                )
                future_timestamps_dict[item_id] = future_times

                ts = TimeseriesType(
                    target=target_tensor,
                    past_covariates=None,
                    future_covariates=None,
                )

            timeseries_list.append(ts)

        # Run model forecast
        raw_forecasts = self.model.forecast(
            timeseries=timeseries_list,
            prediction_length=prediction_length,
            output_type="numpy",
            batch_size=batch_size,
        )

        results = []
        for i, item_id in enumerate(item_ids):
            # raw_forecast shape: (1, 9, prediction_length)
            item_forecast = raw_forecasts[i][0] # shape: (9, prediction_length)
            item_timestamps = future_timestamps_dict[item_id]

            # 0.5 is median point prediction
            median_idx = self.quantile_to_idx.get(0.5, 4)
            point_pred = item_forecast[median_idx]

            df_dict = {
                "item_id": item_id,
                "timestamp": item_timestamps,
                "predictions": point_pred,
            }

            # Map or interpolate quantiles
            for q in quantile_levels:
                q_round = round(q, 2)
                if q_round in self.quantile_to_idx:
                    df_dict[str(q)] = item_forecast[self.quantile_to_idx[q_round]]
                elif q_round == 0.05:
                    # Linearly extrapolate from 0.10 and 0.20 or clamp
                    q10 = item_forecast[self.quantile_to_idx[0.1]]
                    q20 = item_forecast[self.quantile_to_idx[0.2]]
                    df_dict[str(q)] = q10 - (q20 - q10) * 0.5
                elif q_round == 0.95:
                    # Linearly extrapolate from 0.80 and 0.90
                    q80 = item_forecast[self.quantile_to_idx[0.8]]
                    q90 = item_forecast[self.quantile_to_idx[0.9]]
                    df_dict[str(q)] = q90 + (q90 - q80) * 0.5
                else:
                    # Generic linear interpolation across available quantiles
                    avail_q = np.array(self.default_quantiles)
                    # Interpolate per time step
                    interpolated = np.array([
                        np.interp(q, avail_q, item_forecast[:, t])
                        for t in range(prediction_length)
                    ])
                    df_dict[str(q)] = interpolated

            results.append(pd.DataFrame(df_dict))

        return pd.concat(results, ignore_index=True)
