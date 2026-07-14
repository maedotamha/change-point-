import { CATEGORY_ORDER, CATEGORY_COLORS } from "../categoryColors";

export default function Legend({ activeCategory, onSelect }) {
  return (
    <div className="legend" role="group" aria-label="Event category legend">
      <button
        type="button"
        className={`legend-item ${activeCategory === null ? "is-active" : ""}`}
        onClick={() => onSelect(null)}
      >
        <span className="legend-swatch legend-swatch-line" />
        All categories
      </button>
      {CATEGORY_ORDER.map((cat) => (
        <button
          type="button"
          key={cat}
          className={`legend-item ${activeCategory === cat ? "is-active" : ""}`}
          onClick={() => onSelect(activeCategory === cat ? null : cat)}
        >
          <span className="legend-swatch" style={{ background: CATEGORY_COLORS[cat] }} />
          {cat}
        </button>
      ))}
    </div>
  );
}
