"""Flask API for the Brent Oil Change Point dashboard (Task 3).

Endpoints
---------
GET /api/health
    Liveness check.

GET /api/prices?start=YYYY-MM-DD&end=YYYY-MM-DD
    Daily Brent price series, optionally filtered to a date range.
    Response: {"dates": [...], "prices": [...]}

GET /api/events?category=<Category>
    Researched events (data/events.csv), optionally filtered by category.
    Response: [{"date", "event", "category", "description", "expected_direction"}, ...]

GET /api/changepoints
    Bayesian change point results (core single-change-point model +
    recursive multi-change-point segmentation with event associations),
    precomputed by scripts/run_change_point_analysis.py.
    Response: {"core_model": {...}, "change_points": [...]}

GET /api/summary?start=YYYY-MM-DD&end=YYYY-MM-DD
    Key indicators for the selected date range: average price, min/max,
    volatility (std of daily log returns), total % change, and counts
    of change points / events falling inside the range.
"""
from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request
from flask_cors import CORS

ROOT = Path(__file__).resolve().parents[1]

app = Flask(__name__)
CORS(app)


def _load_prices() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "BrentOilPrices.csv")
    df["Date"] = pd.to_datetime(df["Date"], format="mixed")
    df = df.sort_values("Date").reset_index(drop=True)
    df["LogReturn"] = np.log(df["Price"]).diff()
    return df


def _load_events() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "events.csv")
    df["Date"] = pd.to_datetime(df["Date"])
    return df


def _load_change_points() -> dict:
    import json
    with open(ROOT / "reports" / "change_points.json") as f:
        return json.load(f)


PRICES_DF = _load_prices()
EVENTS_DF = _load_events()
CHANGE_POINTS = _load_change_points()


def _parse_range(df: pd.DataFrame, date_col: str = "Date"):
    start = request.args.get("start")
    end = request.args.get("end")
    mask = pd.Series(True, index=df.index)
    if start:
        mask &= df[date_col] >= pd.to_datetime(start)
    if end:
        mask &= df[date_col] <= pd.to_datetime(end)
    return df[mask]


@app.route("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.route("/api/prices")
def prices():
    df = _parse_range(PRICES_DF)
    return jsonify({
        "dates": df["Date"].dt.strftime("%Y-%m-%d").tolist(),
        "prices": df["Price"].tolist(),
    })


@app.route("/api/events")
def events():
    df = EVENTS_DF
    category = request.args.get("category")
    if category:
        df = df[df["Category"] == category]
    records = df.to_dict(orient="records")
    for r in records:
        r["Date"] = r["Date"].strftime("%Y-%m-%d") if hasattr(r["Date"], "strftime") else r["Date"]
    return jsonify(records)


@app.route("/api/events/categories")
def event_categories():
    return jsonify(sorted(EVENTS_DF["Category"].unique().tolist()))


@app.route("/api/changepoints")
def changepoints():
    return jsonify(CHANGE_POINTS)


@app.route("/api/summary")
def summary():
    df = _parse_range(PRICES_DF)
    if df.empty:
        return jsonify({"error": "no data in range"}), 404

    start_date = df["Date"].iloc[0]
    end_date = df["Date"].iloc[-1]

    cps_in_range = [
        cp for cp in CHANGE_POINTS["change_points"]
        if str(start_date.date()) <= cp["date"] <= str(end_date.date())
    ]
    events_in_range = EVENTS_DF[(EVENTS_DF["Date"] >= start_date) & (EVENTS_DF["Date"] <= end_date)]

    return jsonify({
        "start": start_date.strftime("%Y-%m-%d"),
        "end": end_date.strftime("%Y-%m-%d"),
        "n_days": int(len(df)),
        "avg_price": round(float(df["Price"].mean()), 2),
        "min_price": round(float(df["Price"].min()), 2),
        "max_price": round(float(df["Price"].max()), 2),
        "pct_change_over_range": round(
            float((df["Price"].iloc[-1] - df["Price"].iloc[0]) / df["Price"].iloc[0] * 100), 2
        ) if len(df) > 1 else 0.0,
        "volatility_annualised_pct": round(
            float(df["LogReturn"].std() * np.sqrt(252) * 100), 2
        ) if len(df) > 1 else 0.0,
        "n_change_points": len(cps_in_range),
        "n_events": int(len(events_in_range)),
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
