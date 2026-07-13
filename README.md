# Change Point Analysis and Statistical Modeling of Brent Oil Prices

Birhan Energies — analysing how major geopolitical events, OPEC decisions,
and economic shocks are associated with structural breaks in Brent crude oil
prices (daily, 20-May-1987 to 14-Nov-2022).

## Status

- **Task 1 (foundation)** — complete. See
  [`reports/interim_report.md`](reports/interim_report.md) for the interim
  submission: analysis workflow, events dataset, and initial EDA.
- **Task 2 (Bayesian change point modeling)** — in progress.
- **Task 3 (dashboard)** — not started.

## Project Structure

```
├── data/
│   ├── BrentOilPrices.csv     # daily Brent price series
│   └── events.csv             # 17 major geopolitical/OPEC/economic events
├── docs/
│   ├── analysis_workflow.md   # planned analysis steps & communication channels
│   └── assumptions_and_limitations.md
├── notebooks/
│   └── eda.ipynb              # exploratory data analysis (executed)
├── scripts/
│   └── eda.py                 # reproducible CLI version of the EDA
├── reports/
│   ├── interim_report.md      # Task 1 interim submission
│   ├── eda_summary.json       # EDA stats (stationarity tests, etc.)
│   └── images/                # generated EDA plots
├── src/                       # shared analysis code (Task 2+)
├── tests/                     # unit tests
└── .github/workflows/         # CI (unittests)
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Reproducing the EDA

```bash
python scripts/eda.py
# or open notebooks/eda.ipynb
```

This loads `data/BrentOilPrices.csv`, computes log returns, runs ADF/KPSS
stationarity tests, and writes plots to `reports/images/`.

## Data

- **Brent oil prices**: daily USD/barrel prices, `data/BrentOilPrices.csv`.
- **Events**: `data/events.csv` — 17 major geopolitical, OPEC-policy,
  sanctions, and economic-shock events with approximate dates, compiled for
  cross-referencing against detected change points.

## Key References

- Bayesian Changepoint Detection with PyMC3 (PyMC docs)
- Machine Learning Mastery — Markov Chain Monte Carlo for Probability
- Fraunhofer IESE — Change Point Detection blog series
