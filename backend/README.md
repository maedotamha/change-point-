# Backend (Flask API)

Serves the Brent oil price series, researched events, and Bayesian change
point results computed in Task 2 to the React dashboard (Task 3).

## Setup & run

```bash
# from the project root, using the project venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe backend/app.py
```

Runs on `http://127.0.0.1:5000` with CORS enabled for the frontend dev server.

## Endpoints

| Endpoint | Params | Description |
|---|---|---|
| `GET /api/health` | - | Liveness check |
| `GET /api/prices` | `start`, `end` (YYYY-MM-DD, optional) | Daily Brent price series, optionally filtered to a date range |
| `GET /api/events` | `category` (optional) | Researched events from `data/events.csv` |
| `GET /api/events/categories` | - | Distinct event categories, for filter UI |
| `GET /api/changepoints` | - | Core single change-point model result + recursive multi-change-point segmentation, each mapped to its nearest event (from `reports/change_points.json`) |
| `GET /api/summary` | `start`, `end` (optional) | Key indicators for the selected range: avg/min/max price, % change over range, annualised volatility, count of change points and events in range |

All data is loaded once at startup from the `data/` and `reports/` folders
produced by Task 1/2 (no database).
