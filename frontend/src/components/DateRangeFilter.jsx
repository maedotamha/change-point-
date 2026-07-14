const PRESETS = [
  { label: "All (1987–2022)", years: null },
  { label: "Last 20 years", years: 20 },
  { label: "Last 10 years", years: 10 },
  { label: "Last 5 years", years: 5 },
  { label: "Last 2 years", years: 2 },
];

const DATA_START = "1987-05-20";
const DATA_END = "2022-11-14";

function yearsAgo(n) {
  const end = new Date(DATA_END);
  const d = new Date(end);
  d.setFullYear(d.getFullYear() - n);
  return d.toISOString().slice(0, 10);
}

export default function DateRangeFilter({ start, end, onChange, activePreset, onPresetChange }) {
  return (
    <div className="date-filter">
      <div className="date-filter-presets">
        {PRESETS.map((p) => (
          <button
            type="button"
            key={p.label}
            className={`preset-row ${activePreset === p.label ? "is-active" : ""}`}
            onClick={() => {
              onPresetChange(p.label);
              onChange(p.years ? yearsAgo(p.years) : DATA_START, DATA_END);
            }}
          >
            <span className="preset-check">{activePreset === p.label ? "✓" : ""}</span>
            {p.label}
          </button>
        ))}
      </div>
      <div className="date-filter-custom">
        <label>
          From
          <input
            type="date"
            value={start}
            min={DATA_START}
            max={end}
            onChange={(e) => {
              onPresetChange(null);
              onChange(e.target.value, end);
            }}
          />
        </label>
        <label>
          To
          <input
            type="date"
            value={end}
            min={start}
            max={DATA_END}
            onChange={(e) => {
              onPresetChange(null);
              onChange(start, e.target.value);
            }}
          />
        </label>
      </div>
    </div>
  );
}

export { DATA_START, DATA_END };
