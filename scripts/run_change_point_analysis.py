"""Run the full Task 2 change point analysis and export results.

1. Fits the mandatory single change-point model on the full series,
   saves trace/posterior plots and convergence diagnostics.
2. Runs recursive segmentation to find multiple prominent change
   points across the 35-year history.
3. Maps each detected change point to the nearest researched event.
4. Exports reports/change_points.json for the Task 3 dashboard and
   reports/change_point_summary.md with quantified impact statements.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import arviz as az
import pymc as pm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.change_point import fit_single_change_point, recursive_segmentation, nearest_event

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "BrentOilPrices.csv"
EVENTS_PATH = ROOT / "data" / "events.csv"
IMG_DIR = ROOT / "reports" / "images"
IMG_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    df = df.sort_values("Date").reset_index(drop=True)
    return df


def fit_full_series_model(df: pd.DataFrame):
    prices = df["Price"].to_numpy()
    idx = np.arange(len(prices))
    with pm.Model() as model:
        tau = pm.DiscreteUniform("tau", lower=0, upper=len(prices) - 1)
        mu1 = pm.Normal("mu1", mu=prices.mean(), sigma=prices.std() * 2)
        mu2 = pm.Normal("mu2", mu=prices.mean(), sigma=prices.std() * 2)
        sigma = pm.HalfNormal("sigma", sigma=prices.std())
        mu = pm.math.switch(tau >= idx, mu1, mu2)
        pm.Normal("obs", mu=mu, sigma=sigma, observed=prices)
        trace = pm.sample(
            draws=2000, tune=1500, chains=4, random_seed=42,
            progressbar=False, target_accept=0.9,
        )
    return trace


def plot_core_model_diagnostics(df: pd.DataFrame, trace) -> dict:
    summary = az.summary(trace, var_names=["tau", "mu1", "mu2", "sigma"])
    summary.to_csv(ROOT / "reports" / "change_point_core_summary.csv")

    # Trace plot
    az.plot_trace(trace, var_names=["tau", "mu1", "mu2", "sigma"])
    plt.gcf().set_size_inches(11, 8)
    plt.tight_layout()
    plt.savefig(IMG_DIR / "05_trace_plot.png", dpi=150)
    plt.close("all")

    # Posterior of tau, mapped to actual dates
    tau_samples = trace.posterior["tau"].values.flatten()
    tau_dates = df["Date"].iloc[tau_samples].values
    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.hist(tau_dates, bins=60, color="#1f4e79", alpha=0.85)
    ax.set_title("Posterior Distribution of the Change Point (tau)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Posterior draws")
    ax.grid(alpha=0.3)
    fig.autofmt_xdate()
    fig.tight_layout()
    fig.savefig(IMG_DIR / "06_tau_posterior.png", dpi=150)
    plt.close(fig)

    # Price series with the detected mean levels overlaid
    tau_mode = int(pd.Series(tau_samples).mode().iloc[0])
    mu1 = float(trace.posterior["mu1"].values.mean())
    mu2 = float(trace.posterior["mu2"].values.mean())
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], df["Price"], linewidth=0.6, color="#888888", alpha=0.7, label="Observed price")
    ax.hlines(mu1, df["Date"].iloc[0], df["Date"].iloc[tau_mode], color="#1f4e79", linewidth=2.5, label=f"mu1 = ${mu1:.2f}")
    ax.hlines(mu2, df["Date"].iloc[tau_mode], df["Date"].iloc[-1], color="#a83232", linewidth=2.5, label=f"mu2 = ${mu2:.2f}")
    ax.axvline(df["Date"].iloc[tau_mode], color="black", linestyle="--", linewidth=1)
    ax.set_title(f"Single Change Point Model: Detected Break at {df['Date'].iloc[tau_mode].date()}")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.legend()
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "07_single_changepoint_fit.png", dpi=150)
    plt.close(fig)

    return {
        "tau_index": tau_mode,
        "date": df["Date"].iloc[tau_mode].strftime("%Y-%m-%d"),
        "mu1": mu1,
        "mu2": mu2,
        "pct_change": (mu2 - mu1) / mu1 * 100,
        "r_hat_max": float(summary["r_hat"].max()),
        "ess_bulk_min": float(summary["ess_bulk"].min()),
    }


def plot_segmentation(df: pd.DataFrame, results) -> None:
    fig, ax = plt.subplots(figsize=(13, 5.5))
    ax.plot(df["Date"], df["Price"], linewidth=0.6, color="#555555", alpha=0.8)
    colors = plt.cm.tab10(np.linspace(0, 1, max(len(results), 1)))
    for r, c in zip(results, colors):
        ax.axvline(r.date, color=c, linestyle="--", linewidth=1.3)
        ax.annotate(
            r.date.strftime("%Y-%m"),
            xy=(r.date, ax.get_ylim()[1] * 0.95),
            rotation=90, fontsize=7, color=c, ha="right", va="top",
        )
    ax.set_title(f"Recursive Segmentation: {len(results)} Detected Change Points")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "08_multi_changepoints.png", dpi=150)
    plt.close(fig)


def main():
    df = load_data()
    events = pd.read_csv(EVENTS_PATH)

    print("Fitting core single change-point model on full series...")
    trace = fit_full_series_model(df)
    core_result = plot_core_model_diagnostics(df, trace)
    print(json.dumps(core_result, indent=2))

    print("\nRunning recursive segmentation for multiple change points...")
    results = recursive_segmentation(
        df["Date"], df["Price"],
        min_segment=250, effect_size_threshold=0.4, max_points=10,
        draws=1000, tune=1000, chains=4,
    )
    print(f"Found {len(results)} change points.")

    plot_segmentation(df, results)

    rows = []
    for r in results:
        ev = nearest_event(r.date, events, max_days=120)
        rows.append({
            "date": r.date.strftime("%Y-%m-%d"),
            "mu_before": round(r.mu1, 2),
            "mu_after": round(r.mu2, 2),
            "pct_change": round(r.pct_change, 1),
            "effect_size": round(r.effect_size, 2),
            "tau_confidence": round(r.tau_confidence, 2),
            "r_hat_max": round(r.r_hat_max, 3),
            "n_before": r.n_before,
            "n_after": r.n_after,
            "associated_event": ev,
        })

    output = {
        "core_model": core_result,
        "change_points": rows,
    }
    with open(ROOT / "reports" / "change_points.json", "w") as f:
        json.dump(output, f, indent=2)

    # Human-readable quantified impact statements
    lines = ["# Change Point Analysis - Quantified Impact Statements\n"]
    lines.append(
        f"**Core single change-point model** (full series, 1987-2022): detected break at "
        f"**{core_result['date']}**, mean price shifting from **${core_result['mu1']:.2f}** to "
        f"**${core_result['mu2']:.2f}** ({core_result['pct_change']:+.1f}%). "
        f"Convergence: max r_hat = {core_result['r_hat_max']:.3f}, min ESS = {core_result['ess_bulk_min']:.0f}.\n"
    )
    lines.append("\n## Recursive segmentation - major structural breaks\n")
    for row in rows:
        ev = row["associated_event"]
        ev_text = (
            f"associated with **{ev['event']}** ({ev['event_date']}, {ev['days_diff']:+d} days from break)"
            if ev else "no researched event found within 120 days"
        )
        lines.append(
            f"- **{row['date']}**: price shifted from **${row['mu_before']}** to **${row['mu_after']}** "
            f"({row['pct_change']:+.1f}%), {ev_text}. "
            f"[effect size={row['effect_size']}, tau confidence={row['tau_confidence']}, r_hat={row['r_hat_max']}]"
        )
    with open(ROOT / "reports" / "change_point_summary.md", "w") as f:
        f.write("\n".join(lines))

    print("\nWrote reports/change_points.json and reports/change_point_summary.md")


if __name__ == "__main__":
    main()
