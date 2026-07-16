# Change Point Analysis and Statistical Modeling of Brent Oil Prices

Birhan Energies — analysing how major geopolitical events, OPEC decisions,
and economic shocks are associated with structural breaks in Brent crude oil
prices (daily, 20-May-1987 to 14-Nov-2022).

**Final report:** [`reports/final_report.md`](reports/final_report.md) ([PDF](reports/final_report.pdf))

## Status

All three tasks are complete:

- **Task 1 (foundation)** — analysis workflow, 17-event dataset, initial EDA.
  See [`reports/interim_report.md`](reports/interim_report.md).
- **Task 2 (Bayesian change point modeling)** — core PyMC single change-point
  model + recursive multi-change-point segmentation, mapped to events. See
  [`notebooks/change_point_model.ipynb`](notebooks/change_point_model.ipynb).
- **Task 3 (dashboard)** — Flask API + React/Recharts frontend. See
  [`backend/README.md`](backend/README.md) and
  [`frontend/README.md`](frontend/README.md).

## Project Structure

```
├── data/
│   ├── BrentOilPrices.csv     # daily Brent price series
│   └── events.csv             # 17 major geopolitical/OPEC/economic events
├── docs/
│   ├── analysis_workflow.md   # planned analysis steps & communication channels
│   └── assumptions_and_limitations.md
├── notebooks/
│   ├── eda.ipynb                    # Task 1 exploratory data analysis (executed)
│   └── change_point_model.ipynb     # Task 2 Bayesian change point model (executed)
├── src/
│   └── change_point.py        # core model + recursive segmentation + event matching
├── scripts/
│   ├── eda.py                       # reproducible CLI version of the EDA
│   ├── run_change_point_analysis.py # reproducible CLI version of Task 2
│   └── generate_pdfs.py             # renders the .md reports to PDF
├── backend/
│   └── app.py                 # Flask API (Task 3)
├── frontend/                  # React + Vite + Recharts dashboard (Task 3)
├── reports/
│   ├── interim_report.md / .pdf     # Task 1 interim submission
│   ├── final_report.md / .pdf       # Final blog-post report
│   ├── change_points.json           # Task 2 results, consumed by the dashboard
│   ├── change_point_summary.md      # human-readable quantified impact statements
│   └── images/                      # all generated plots + dashboard screenshots
├── tests/                     # unit tests
└── .github/workflows/         # CI (unittests)
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt
```

## Reproducing the analysis

```bash
python scripts/eda.py                        # Task 1 EDA -> reports/images/
python scripts/run_change_point_analysis.py   # Task 2 model -> reports/change_points.json
python scripts/generate_pdfs.py               # renders reports to PDF
```

Or open the notebooks directly: `notebooks/eda.ipynb`,
`notebooks/change_point_model.ipynb`.

### Running the dashboard

```bash
# terminal 1
.venv\Scripts\python.exe backend/app.py

# terminal 2
cd frontend && npm install && npm run dev
```

Then open `http://localhost:5173`.

## Data

- **Brent oil prices**: daily USD/barrel prices, `data/BrentOilPrices.csv`.
- **Events**: `data/events.csv` — 17 major geopolitical, OPEC-policy,
  sanctions, and economic-shock events with approximate dates, cross-
  referenced against the detected change points in Task 2.

## Key References

- Bayesian Changepoint Detection with PyMC3 (PyMC docs)
- Machine Learning Mastery — Markov Chain Monte Carlo for Probability
- Fraunhofer IESE — Change Point Detection blog series
