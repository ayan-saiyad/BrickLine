import { formatDate } from "../lib";
import type { CalendarItem, LegoSet } from "../types";

interface Props {
  items: CalendarItem[];
  onSelect: (set: LegoSet) => void;
}

export function TimelineView({ items, onSelect }: Props) {
  if (!items.length) {
    return (
      <section className="empty-state">
        <span>0 results</span>
        <h2>Nothing on this stretch of track.</h2>
        <p>Try clearing a filter or searching for another set.</p>
      </section>
    );
  }

  let lastYear = 0;
  return (
    <section className="timeline" aria-label="Release timeline">
      {items.map((item) => {
        const year = item.date.getFullYear();
        const showYear = year !== lastYear;
        lastYear = year;
        return (
          <div key={`${item.set.set_number}-${item.event.event_type}`}>
            {showYear && <h2 className="timeline-year">{year}</h2>}
            <button className="timeline-row" onClick={() => onSelect(item.set)}>
              <time dateTime={item.event.event_date}>
                <strong>{formatDate(item.date, { month: "short" })}</strong>
                <span>{item.date.getDate()}</span>
              </time>
              <i className={`timeline-dot ${item.event.event_type}`} />
              <span className="timeline-copy">
                <b>{item.set.name}</b>
                <small>
                  {item.set.set_number} · {item.set.theme}
                </small>
              </span>
              <span className={`event-label ${item.event.confidence}`}>
                {item.event.confidence === "estimated" ? "Estimated " : ""}
                {item.event.event_type}
              </span>
            </button>
          </div>
        );
      })}
    </section>
  );
}

