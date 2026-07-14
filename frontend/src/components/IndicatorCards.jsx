function StatTile({ label, value, sub }) {
  return (
    <div className="stat-tile">
      <div className="stat-label">{label}</div>
      <div className="stat-value">{value}</div>
      {sub && <div className="stat-sub">{sub}</div>}
    </div>
  );
}

export default function IndicatorCards({ summary }) {
  if (!summary) {
    return (
      <div className="stat-grid">
        <StatTile label="Loading" value="—" />
      </div>
    );
  }

  const changeSign = summary.pct_change_over_range >= 0 ? "+" : "";
  const changeClass = summary.pct_change_over_range >= 0 ? "is-positive" : "is-negative";

  return (
    <div className="stat-grid">
      <StatTile label="Average price" value={`$${summary.avg_price.toFixed(2)}`} sub={`${summary.n_days.toLocaleString()} trading days`} />
      <StatTile label="Range" value={`$${summary.min_price.toFixed(2)} – $${summary.max_price.toFixed(2)}`} />
      <StatTile
        label="Change over range"
        value={<span className={changeClass}>{changeSign}{summary.pct_change_over_range.toFixed(1)}%</span>}
      />
      <StatTile label="Annualised volatility" value={`${summary.volatility_annualised_pct.toFixed(1)}%`} sub="std of daily log returns" />
      <StatTile label="Change points" value={summary.n_change_points} sub="detected in range" />
      <StatTile label="Events" value={summary.n_events} sub="in range" />
    </div>
  );
}
