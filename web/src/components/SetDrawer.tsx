import { useEffect } from "react";
import { formatDate, parseDate } from "../lib";
import type { LegoSet } from "../types";

interface Props {
  legoSet: LegoSet;
  watched: boolean;
  onClose: () => void;
  onToggleWatch: (setNumber: string) => void;
}

export function SetDrawer({ legoSet, watched, onClose, onToggleWatch }: Props) {
  useEffect(() => {
    const closeOnEscape = (event: KeyboardEvent) => {
      if (event.key === "Escape") onClose();
    };
    window.addEventListener("keydown", closeOnEscape);
    return () => window.removeEventListener("keydown", closeOnEscape);
  }, [onClose]);

  return (
    <div className="drawer-layer" role="presentation" onMouseDown={onClose}>
      <aside
        className="set-drawer"
        role="dialog"
        aria-modal="true"
        aria-labelledby="set-title"
        onMouseDown={(event) => event.stopPropagation()}
      >
        <div className="drawer-top">
          <span className={`status-pill ${legoSet.status}`}>{legoSet.status}</span>
          <button className="close-button" onClick={onClose} aria-label="Close details">
            ×
          </button>
        </div>
        <div className="set-art" aria-hidden="true">
          <span>{legoSet.set_number}</span>
          <i />
          <i />
          <i />
          <i />
        </div>
        <span className="set-theme">{legoSet.theme}</span>
        <h2 id="set-title">{legoSet.name}</h2>
        <p className="set-meta">
          Set {legoSet.set_number}
          {legoSet.piece_count ? ` · ${legoSet.piece_count.toLocaleString()} pieces` : ""}
        </p>

        <button
          className={`watch-button ${watched ? "watched" : ""}`}
          onClick={() => onToggleWatch(legoSet.set_number)}
        >
          <span aria-hidden="true">{watched ? "★" : "☆"}</span>
          {watched ? "Watching" : "Add to watchlist"}
        </button>

        <div className="date-list">
          {legoSet.events.map((event) => (
            <div className="date-row" key={event.event_type}>
              <i className={event.event_type} />
              <div>
                <span>{event.event_type}</span>
                <strong>
                  {formatDate(parseDate(event.event_date), {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </strong>
                <small className={event.confidence}>{event.confidence}</small>
              </div>
              <a href={event.source_url} target="_blank" rel="noreferrer">
                {event.source_name} ↗
              </a>
            </div>
          ))}
        </div>
        <p className="estimate-note">
          Estimated dates can move. Brickline keeps the label visible until a source confirms the date.
        </p>
      </aside>
    </div>
  );
}

