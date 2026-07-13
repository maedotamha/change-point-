# Assumptions and Limitations

## Assumptions

1. **Event dates are approximate "start dates"** for each entry in
   `data/events.csv`. Real-world events (wars, sanctions regimes, OPEC policy
   shifts) unfold over days to months; a single date is a simplification used
   to align events with the daily price series.
2. **Brent price is treated as a single global benchmark.** We do not adjust
   for inflation, currency effects (all prices are nominal USD/barrel), or
   the fact that Brent, WTI, and OPEC basket prices can diverge during
   regional supply shocks.
3. **A mean-shift change point model is an adequate first approximation.**
   We assume that, locally around a structural break, the price process can
   be summarised by a constant mean plus noise. This is a simplification —
   markets also exhibit trends, mean-reversion, and volatility regimes that
   a single-mean-shift model does not capture.
4. **One (or a small, fixed number of) change point(s) are estimated at a
   time** for interpretability. In reality, the 35-year series plausibly
   contains dozens of regime shifts; the model is extended incrementally
   (see the roadmap in `docs/analysis_workflow.md`) rather than fit with an
   unbounded number of change points in the first pass.
5. **The trading calendar (holidays, weekends, exchange closures) is not
   explicitly modeled.** Gaps between consecutive trading days are treated
   as if they were of equal length.

## Limitations

1. **Correlation in time is not proof of causation.** This is the central
   methodological caveat of the whole analysis and is expanded on below.
2. **Data does not capture magnitude of an event.** `data/events.csv` records
   *that* an event occurred and a qualitative expected direction, not a
   quantitative measure of its severity, so the strength of any detected
   shift cannot be directly attributed to "how big" the event was.
3. **Multiple plausible causes can coincide.** Oil markets are influenced by
   simultaneous macro factors (currency moves, demand shocks, OPEC policy,
   and geopolitical events can overlap within days of each other), which
   makes it difficult to isolate a single "cause" for an inferred change
   point.
4. **Change point models detect breaks in the modeled parameter only**
   (e.g. the mean). They do not, by themselves, explain *why* the break
   occurred — that step always requires the analyst to bring in outside
   context (the event list) and reason qualitatively about plausibility and
   timing.
5. **Look-ahead / hindsight bias risk.** Because the event list is compiled
   with the benefit of hindsight, there is a risk of confirmation bias when
   matching change points to events — i.e., of finding a plausible-sounding
   event near almost any detected change point. We mitigate this by
   requiring temporal proximity (the event should precede or coincide with,
   not follow, the detected shift) and by being explicit that these are
   *hypotheses*, not proven causal claims.

## Correlation vs. Causal Impact

A Bayesian change point model identifies a date (or a posterior distribution
over dates) at which the statistical properties of the price series most
likely shifted, and it quantifies that shift (e.g., the change in mean
price). This is fundamentally a **descriptive, correlational** result: it
tells us *when* the data-generating process changed and by how much.

It does **not**, on its own, establish that a specific real-world event
*caused* that shift. To move from correlation to a causal claim one would
need, at minimum:

- **Temporal precedence** — the event must precede the change point, not
  follow it (we check this, but proximity alone is weak evidence).
- **A plausible mechanism** — a economic/geopolitical channel by which the
  event could move the balance of oil supply, demand, or risk premium.
- **Ruling out confounders** — other events, seasonal effects, or
  macroeconomic shifts occurring in the same window that could equally
  explain the change.
- **Counterfactual reasoning or a natural-experiment design** (e.g.
  difference-in-differences, synthetic control, or event-study methods with
  a control series) to estimate what prices *would have done* absent the
  event — something a single-series change point model cannot provide.

Throughout this project we therefore frame event associations as
**hypotheses consistent with the evidence** ("the detected change point
around [date] is temporally consistent with [event], and a price shift in
the [direction] implied by the event's likely supply/demand effect"), not as
proven causal statements.
