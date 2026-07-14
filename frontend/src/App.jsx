import { useEffect, useMemo, useState, useCallback } from "react";
import "./App.css";
import { fetchPrices, fetchEvents, fetchChangePoints, fetchSummary } from "./api";
import PriceChart from "./components/PriceChart";
import IndicatorCards from "./components/IndicatorCards";
import EventList from "./components/EventList";
import Legend from "./components/Legend";
import DateRangeFilter, { DATA_START, DATA_END } from "./components/DateRangeFilter";

function addDays(dateStr, days) {
  const d = new Date(dateStr);
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

function clamp(dateStr, min, max) {
  if (dateStr < min) return min;
  if (dateStr > max) return max;
  return dateStr;
}

export default function App() {
  const [start, setStart] = useState(DATA_START);
  const [end, setEnd] = useState(DATA_END);
  const [activePreset, setActivePreset] = useState("All (1987–2022)");
  const [category, setCategory] = useState(null);
  const [selectedEventDate, setSelectedEventDate] = useState(null);

  const [prices, setPrices] = useState(null);
  const [allEvents, setAllEvents] = useState([]);
  const [changePointData, setChangePointData] = useState(null);
  const [summary, setSummary] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchEvents()
      .then(setAllEvents)
      .catch((e) => setError(e.message));
    fetchChangePoints()
      .then(setChangePointData)
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    let cancelled = false;
    fetchPrices(start, end)
      .then((d) => !cancelled && setPrices(d))
      .catch((e) => !cancelled && setError(e.message));
    fetchSummary(start, end)
      .then((d) => !cancelled && setSummary(d))
      .catch((e) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [start, end]);

  const handleRangeChange = useCallback((newStart, newEnd) => {
    setStart(newStart);
    setEnd(newEnd);
  }, []);

  const eventsInRange = useMemo(() => {
    return allEvents
      .filter((e) => e.Date >= start && e.Date <= end)
      .filter((e) => !category || e.Category === category);
  }, [allEvents, start, end, category]);

  const changePointsInRange = useMemo(() => {
    if (!changePointData) return [];
    return changePointData.change_points.filter((cp) => cp.date >= start && cp.date <= end);
  }, [changePointData, start, end]);

  const handleEventFocus = useCallback((event) => {
    const windowStart = clamp(addDays(event.Date, -365), DATA_START, DATA_END);
    const windowEnd = clamp(addDays(event.Date, 365), DATA_START, DATA_END);
    setStart(windowStart);
    setEnd(windowEnd);
    setActivePreset(null);
    setSelectedEventDate(event.Date);
  }, []);

  return (
    <div className="app">
      <header className="app-header">
        <h1>Brent Oil Price — Change Point &amp; Event Dashboard</h1>
        <p>
          Birhan Energies · Daily Brent crude prices (1987–2022) with Bayesian-detected structural
          breaks and researched geopolitical / OPEC / economic events.
        </p>
      </header>

      {error && <p className="muted">Could not reach the backend API: {error}. Is `backend/app.py` running on port 5000?</p>}

      <div className="filter-row">
        <DateRangeFilter
          start={start}
          end={end}
          onChange={handleRangeChange}
          activePreset={activePreset}
          onPresetChange={setActivePreset}
        />
      </div>

      <IndicatorCards summary={summary} />

      <div className="chart-card">
        <div className="chart-card-header">
          <h2>Price series with detected change points and events</h2>
        </div>
        <Legend activeCategory={category} onSelect={setCategory} />
        <PriceChart
          prices={prices}
          events={eventsInRange}
          changePoints={changePointsInRange}
          onEventClick={handleEventFocus}
          highlightedEventDate={selectedEventDate}
        />
      </div>

      <div className="main-grid">
        <div>
          {changePointData && (
            <div className="chart-card">
              <div className="chart-card-header">
                <h2>Core model: single global change point</h2>
              </div>
              <p style={{ padding: "0 12px 12px", fontSize: 13, color: "var(--text-secondary)" }}>
                The mandatory Task 2 model (discrete-uniform prior on the switch point, two
                regime means, Normal likelihood) detects its single most prominent break on{" "}
                <strong>{changePointData.core_model.date}</strong>: mean price shifted from{" "}
                <strong>${changePointData.core_model.mu1.toFixed(2)}</strong> to{" "}
                <strong>${changePointData.core_model.mu2.toFixed(2)}</strong> (
                {changePointData.core_model.pct_change >= 0 ? "+" : ""}
                {changePointData.core_model.pct_change.toFixed(1)}%). Convergence: max r_hat ={" "}
                {changePointData.core_model.r_hat_max.toFixed(3)}.
              </p>
            </div>
          )}
        </div>
        <aside className="sidebar">
          <h2>Events in range ({eventsInRange.length})</h2>
          <EventList events={eventsInRange} selectedDate={selectedEventDate} onFocus={handleEventFocus} />
        </aside>
      </div>

      <footer className="app-footer">
        Data: Brent daily spot price (USD/barrel), 20-May-1987 to 14-Nov-2022. Change points from
        a PyMC Bayesian model + recursive segmentation (Task 2). Event/change-point proximity is a
        hypothesis-generating signal, not proof of causation — see{" "}
        <code>docs/assumptions_and_limitations.md</code>.
      </footer>
    </div>
  );
}
