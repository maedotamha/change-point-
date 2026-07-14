import { CATEGORY_COLORS, DEFAULT_CATEGORY_COLOR } from "../categoryColors";

export default function EventList({ events, selectedDate, onFocus }) {
  if (!events || !events.length) {
    return <p className="muted">No events match the current filter.</p>;
  }

  return (
    <ul className="event-list">
      {events.map((e) => {
        const isSelected = selectedDate === e.Date;
        return (
          <li key={`${e.Date}-${e.Event}`}>
            <button
              type="button"
              className={`event-item ${isSelected ? "is-selected" : ""}`}
              onClick={() => onFocus(e)}
              title={`Drill down around ${e.Date}`}
            >
              <span
                className="event-dot"
                style={{ background: CATEGORY_COLORS[e.Category] || DEFAULT_CATEGORY_COLOR }}
              />
              <span className="event-body">
                <span className="event-date">{e.Date}</span>
                <span className="event-name">{e.Event}</span>
                <span className="event-desc">{e.Description}</span>
              </span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
