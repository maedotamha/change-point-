# Frontend (React + Vite dashboard)

Interactive dashboard for exploring Brent oil prices alongside Task 2's
Bayesian change points and researched events.

## Setup & run

```bash
cd frontend
npm install
npm run dev
```

Runs on `http://localhost:5173` and expects the Flask API
(`backend/app.py`) running on `http://127.0.0.1:5000`.

```bash
npm run build     # production build -> dist/
```

## Features

- **Price chart** (Recharts): full 1987-2022 daily Brent series with
  - Vertical dashed lines marking the 10 Bayesian-detected change points
  - Color-coded event markers (by category) in a lane above the price line
  - Custom crosshair tooltip showing price or event detail on hover
- **Date range filter**: preset rows (All / 20y / 10y / 5y / 2y) or a custom
  start/end date picker; every chart, stat, and list re-renders against the
  same range
- **Event drill-down**: clicking an event (in the chart or the sidebar list)
  zooms the chart to a +/-1 year window around it and highlights the event
- **Category filter / legend**: click a category swatch to isolate those
  events; identity is colored consistently (never reassigned when the
  filter changes)
- **Indicator cards**: average/min/max price, % change over range,
  annualised volatility, and change-point/event counts for the current
  selection
- **Responsive**: single-column layout below 900px; tested at desktop
  (1440px), tablet (834px), and mobile (390px) widths
- **Dark mode**: follows `prefers-color-scheme`, validated categorical
  palette for both themes

## Verifying it renders (headless screenshots)

Chrome DevTools/extension access isn't always available in this
environment, so the dashboard was verified with headless Playwright
instead of eyeballing it manually:

```bash
npm install -D playwright
npx playwright install chromium chromium-headless-shell
node screenshot.mjs             # full view, event drill-down, category filter
node screenshot_responsive.mjs  # tablet + mobile viewports
node screenshot_dark.mjs        # dark mode
```

Screenshots are written to `../reports/images/dashboard_*.png` and are
what's embedded in the final report.
