"""Bayesian change point detection for the Brent oil price series.

Core model (Task 2, mandatory): a single change point with a
discrete-uniform prior on the switch index `tau`, two regime means
(mu1, mu2), a `pm.math.switch` linking `tau` to the active mean, and a
Normal likelihood.

`recursive_segmentation` extends this by recursively re-applying the
single change-point model to each half of the series, giving a small
set of the most statistically prominent structural breaks across the
full 35-year history (a simple, interpretable form of multiple
change-point detection built directly on top of the mandatory model).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

import numpy as np
import pandas as pd
import pymc as pm
import arviz as az


@dataclass
class ChangePointResult:
    tau_index: int
    date: pd.Timestamp
    mu1: float
    mu2: float
    mu1_hdi: tuple
    mu2_hdi: tuple
    sigma: float
    r_hat_max: float
    tau_confidence: float  # fraction of posterior tau draws within +/-10 days of the mode
    n_before: int
    n_after: int

    @property
    def pct_change(self) -> float:
        return (self.mu2 - self.mu1) / self.mu1 * 100

    @property
    def effect_size(self) -> float:
        """Standardised mean shift (Cohen's d-like), used to gate recursion."""
        return abs(self.mu2 - self.mu1) / self.sigma if self.sigma > 0 else 0.0


def fit_single_change_point(
    dates: pd.Series,
    prices: np.ndarray,
    draws: int = 2000,
    tune: int = 1500,
    chains: int = 4,
    seed: int = 42,
) -> ChangePointResult:
    n = len(prices)
    idx = np.arange(n)
    with pm.Model():
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)
        mu1 = pm.Normal("mu1", mu=prices.mean(), sigma=prices.std() * 2)
        mu2 = pm.Normal("mu2", mu=prices.mean(), sigma=prices.std() * 2)
        sigma = pm.HalfNormal("sigma", sigma=prices.std())
        mu = pm.math.switch(tau >= idx, mu1, mu2)
        pm.Normal("obs", mu=mu, sigma=sigma, observed=prices)
        trace = pm.sample(
            draws=draws, tune=tune, chains=chains, random_seed=seed,
            progressbar=False, target_accept=0.9,
        )

    summary = az.summary(trace, var_names=["tau", "mu1", "mu2", "sigma"])
    tau_samples = trace.posterior["tau"].values.flatten()
    tau_mode = int(pd.Series(tau_samples).mode().iloc[0])
    tau_confidence = float(np.mean(np.abs(tau_samples - tau_mode) <= 10))

    mu1_samples = trace.posterior["mu1"].values.flatten()
    mu2_samples = trace.posterior["mu2"].values.flatten()
    sigma_mean = float(trace.posterior["sigma"].values.mean())

    return ChangePointResult(
        tau_index=tau_mode,
        date=dates.iloc[tau_mode],
        mu1=float(mu1_samples.mean()),
        mu2=float(mu2_samples.mean()),
        mu1_hdi=tuple(az.hdi(mu1_samples, prob=0.94)),
        mu2_hdi=tuple(az.hdi(mu2_samples, prob=0.94)),
        sigma=sigma_mean,
        r_hat_max=float(summary["r_hat"].max()),
        tau_confidence=tau_confidence,
        n_before=tau_mode + 1,
        n_after=n - tau_mode - 1,
    )


def recursive_segmentation(
    dates: pd.Series,
    prices: pd.Series,
    min_segment: int = 250,
    effect_size_threshold: float = 0.4,
    max_points: int = 10,
    draws: int = 1000,
    tune: int = 1000,
    chains: int = 4,
) -> List[ChangePointResult]:
    """Recursively split segments at their most prominent change point.

    Stops splitting a segment when it is shorter than `min_segment`,
    the detected shift's effect size falls below `effect_size_threshold`,
    or `max_points` change points have been collected.
    """
    results: List[ChangePointResult] = []
    queue = [(0, len(prices))]

    while queue and len(results) < max_points:
        start, end = queue.pop(0)
        if end - start < 2 * min_segment:
            continue

        seg_dates = dates.iloc[start:end].reset_index(drop=True)
        seg_prices = prices.iloc[start:end].to_numpy()

        result = fit_single_change_point(seg_dates, seg_prices, draws=draws, tune=tune, chains=chains)

        if result.effect_size < effect_size_threshold:
            continue
        if result.tau_index < min_segment or (end - start - result.tau_index) < min_segment:
            continue

        global_tau = start + result.tau_index
        result.tau_index = global_tau
        result.date = dates.iloc[global_tau]
        results.append(result)

        queue.append((start, global_tau))
        queue.append((global_tau, end))

    results.sort(key=lambda r: r.tau_index)
    return results


def nearest_event(change_date: pd.Timestamp, events: pd.DataFrame, max_days: int = 120):
    events = events.copy()
    events["Date"] = pd.to_datetime(events["Date"])
    events["days_diff"] = (change_date - events["Date"]).dt.days
    candidates = events[events["days_diff"].abs() <= max_days].copy()
    if candidates.empty:
        return None
    candidates["abs_diff"] = candidates["days_diff"].abs()
    best = candidates.sort_values("abs_diff").iloc[0]
    return {
        "event": best["Event"],
        "event_date": best["Date"].strftime("%Y-%m-%d"),
        "category": best["Category"],
        "days_diff": int(best["days_diff"]),
    }
