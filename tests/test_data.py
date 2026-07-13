from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_price_data_loads():
    df = pd.read_csv(ROOT / "data" / "BrentOilPrices.csv")
    assert {"Date", "Price"}.issubset(df.columns)
    assert len(df) > 1000
    assert df["Price"].min() > 0


def test_events_data_has_minimum_events():
    df = pd.read_csv(ROOT / "data" / "events.csv")
    assert {"Date", "Event", "Category", "Description", "Expected_Direction"}.issubset(df.columns)
    assert len(df) >= 10
