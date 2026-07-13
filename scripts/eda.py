"""Exploratory data analysis for Brent oil daily prices (1987-2022).

Loads data/BrentOilPrices.csv, plots the raw price series and log
returns, and runs stationarity diagnostics. Writes figures to
reports/images/ and a plain-text summary to reports/eda_summary.txt.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller, kpss

ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "BrentOilPrices.csv"
IMG_DIR = ROOT / "reports" / "images"
SUMMARY_PATH = ROOT / "reports" / "eda_summary.json"

IMG_DIR.mkdir(parents=True, exist_ok=True)


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH)
    # The source file mixes two date formats ("20-May-87" and "Apr 22, 2020")
    # from partway through 2020 onward, so we let pandas infer per-row.
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    df = df.sort_values("Date").reset_index(drop=True)
    df["LogPrice"] = np.log(df["Price"])
    df["LogReturn"] = df["LogPrice"].diff()
    return df


def plot_price_series(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], df["Price"], linewidth=0.8, color="#1f4e79")
    ax.set_title("Brent Crude Oil Price, Daily (May 1987 - Sep 2022)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Price (USD/barrel)")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "01_price_series.png", dpi=150)
    plt.close(fig)


def plot_log_returns(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], df["LogReturn"], linewidth=0.4, color="#a83232")
    ax.set_title("Brent Daily Log Returns (Volatility Clustering)")
    ax.set_xlabel("Date")
    ax.set_ylabel("Log Return")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "02_log_returns.png", dpi=150)
    plt.close(fig)


def plot_rolling_volatility(df: pd.DataFrame, window: int = 30) -> None:
    rolling_std = df["LogReturn"].rolling(window).std()
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.plot(df["Date"], rolling_std, linewidth=0.8, color="#2f6b3a")
    ax.set_title(f"{window}-Day Rolling Volatility of Log Returns")
    ax.set_xlabel("Date")
    ax.set_ylabel("Rolling Std. Dev. of Log Returns")
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(IMG_DIR / "03_rolling_volatility.png", dpi=150)
    plt.close(fig)


def plot_price_distribution(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5))
    axes[0].hist(df["Price"], bins=60, color="#1f4e79", alpha=0.8)
    axes[0].set_title("Distribution of Price Levels")
    axes[0].set_xlabel("Price (USD/barrel)")
    axes[1].hist(df["LogReturn"].dropna(), bins=100, color="#a83232", alpha=0.8)
    axes[1].set_title("Distribution of Log Returns")
    axes[1].set_xlabel("Log Return")
    fig.tight_layout()
    fig.savefig(IMG_DIR / "04_distributions.png", dpi=150)
    plt.close(fig)


def stationarity_tests(series: pd.Series) -> dict:
    series = series.dropna()
    adf_stat, adf_p, *_ = adfuller(series, autolag="AIC")
    kpss_stat, kpss_p, *_ = kpss(series, regression="c", nlags="auto")
    return {
        "adf_statistic": float(adf_stat),
        "adf_p_value": float(adf_p),
        "adf_stationary_at_5pct": bool(adf_p < 0.05),
        "kpss_statistic": float(kpss_stat),
        "kpss_p_value": float(kpss_p),
        "kpss_stationary_at_5pct": bool(kpss_p > 0.05),
    }


def main() -> None:
    df = load_data()

    plot_price_series(df)
    plot_log_returns(df)
    plot_rolling_volatility(df)
    plot_price_distribution(df)

    summary = {
        "n_observations": int(len(df)),
        "date_range": [df["Date"].min().strftime("%Y-%m-%d"), df["Date"].max().strftime("%Y-%m-%d")],
        "price_min": float(df["Price"].min()),
        "price_max": float(df["Price"].max()),
        "price_mean": float(df["Price"].mean()),
        "price_std": float(df["Price"].std()),
        "price_level": {
            "adf": stationarity_tests(df["Price"]),
        },
        "log_returns": {
            "adf": stationarity_tests(df["LogReturn"]),
            "mean": float(df["LogReturn"].mean()),
            "std": float(df["LogReturn"].std()),
            "skew": float(df["LogReturn"].skew()),
            "kurtosis": float(df["LogReturn"].kurtosis()),
        },
    }

    with open(SUMMARY_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
