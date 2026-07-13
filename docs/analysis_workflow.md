# Analysis Workflow — Brent Oil Change Point Analysis

Birhan Energies | Task 1: Laying the Foundation for Analysis

## 1. Objective

Quantify how major geopolitical events, OPEC decisions, and economic shocks are
associated with structural shifts in Brent crude oil prices (daily, 20-May-1987
to 14-Nov-2022), and communicate the findings to investors, policymakers, and
energy companies.

## 2. Planned Analysis Steps

1. **Data loading & cleaning** — parse `data/BrentOilPrices.csv`, standardise
   the mixed date formats, sort chronologically, check for gaps/duplicates.
2. **Exploratory data analysis** — plot the raw price series; compute and plot
   log returns `log(price_t) - log(price_{t-1})`; test stationarity (ADF, KPSS)
   on both series; examine volatility clustering via rolling standard
   deviation. (Completed — see `notebooks/eda.ipynb` and
   `reports/interim_report.md`.)
3. **Event research & compilation** — compile a structured list of 15+ major
   events (wars, sanctions, OPEC decisions, financial crises) with
   approximate start dates into `data/events.csv`. (Completed.)
4. **Bayesian change point modeling (Task 2)** — build a PyMC model with a
   discrete-uniform prior over the switch point `tau`, separate "before" and
   "after" mean parameters (`mu_1`, `mu_2`), a `pm.math.switch` function
   linking `tau` to the active mean, and a Normal likelihood. Run MCMC via
   `pm.sample()`.
5. **Convergence & posterior diagnostics** — check `r_hat` ≈ 1.0 via
   `pm.summary()`, inspect trace plots (`pm.plot_trace()`), and plot the
   posterior distribution of `tau` to assess how sharply the change point is
   localised in time.
6. **Event association** — map the posterior mode of `tau` (and any
   additional change points from extended/multiple-change-point models) to
   the nearest entries in `data/events.csv`, and formulate hypotheses about
   which event(s) plausibly triggered each detected shift.
7. **Impact quantification** — for each associated change point, report the
   before/after posterior means, the absolute and percentage change, and a
   probabilistic statement (e.g. "P(mu_2 > mu_1) = 0.98").
8. **Dashboard (Task 3)** — expose the price series, change point results,
   and event correlations via a Flask API, and build a React frontend with
   filtering, event highlighting, and drill-down.
9. **Reporting** — write the final report (blog-post format) with embedded
   visualisations, quantified impact statements, limitations, and future
   work.

## 3. Communication Channels

| Audience | Channel / Format |
|---|---|
| Internal team / tutors | Slack `#all-week10`, GitHub issues & project board for task tracking |
| Investors / analysts | Interactive dashboard (Task 3) for self-service exploration of price vs. events |
| Policymakers / government bodies | Written report (PDF / Medium-style blog post) with plain-language, quantified impact statements and visualisations |
| Energy companies (operational planning) | Summary tables of historical regime shifts and their magnitude/duration, delivered alongside the dashboard |

## 4. References

See the project `README.md` for the full reading list (Bayesian change point
detection, PyMC documentation, MCMC background) used to inform the modeling
approach in Task 2.
